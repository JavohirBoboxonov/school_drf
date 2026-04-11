from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Attendance
from .serializers import AttendanceSerializer, AttendanceBulkSerializer


class IsTeacherOrAdmin(IsAuthenticated):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.role in ('teacher', 'assistant', 'admin')

class AttendanceListCreateView(generics.ListCreateAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Attendance.objects.select_related('student', 'group', 'marked_by')
        user = self.request.user

        if user.role == 'student':
            qs = qs.filter(student=user)

        group_id = self.request.query_params.get('group')
        date     = self.request.query_params.get('date')
        status_  = self.request.query_params.get('status')
        student  = self.request.query_params.get('student')

        if group_id:
            qs = qs.filter(group_id=group_id)
        if date:
            qs = qs.filter(date=date)
        if status_:
            qs = qs.filter(status=status_)
        if student and user.role != 'student':
            qs = qs.filter(student_id=student)

        return qs

    def perform_create(self, serializer):
        serializer.save(marked_by=self.request.user)

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsTeacherOrAdmin()]
        return [IsAuthenticated()]


class AttendanceDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Attendance.objects.select_related('student', 'group', 'marked_by')
        user = self.request.user
        if user.role == 'student':
            qs = qs.filter(student=user)
        return qs

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsTeacherOrAdmin()]
        return [IsAuthenticated()]

class AttendanceBulkCreateView(APIView):
    permission_classes = [IsTeacherOrAdmin]

    def post(self, request):
        serializer = AttendanceBulkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        group_id = data['group']
        date = data['date']
        records = data['records']
        marked_by = request.user

        created = []
        updated = []
        errors = []

        for record in records:
            student_id = record['student']
            rec_status = record['status']

            try:
                obj, is_created = Attendance.objects.update_or_create(
                    student_id=student_id,
                    group_id=group_id,
                    date=date,
                    defaults={
                        'status': rec_status,
                        'marked_by': marked_by,
                    }
                )
                if is_created:
                    created.append(student_id)
                else:
                    updated.append(student_id)
            except Exception as e:
                errors.append({'student': student_id, 'error': str(e)})

        return Response({
            'created': len(created),
            'updated': len(updated),
            'errors':  errors,
        }, status=status.HTTP_207_MULTI_STATUS if errors else status.HTTP_201_CREATED)

class AttendanceSummaryView(APIView):
    permission_classes = [IsTeacherOrAdmin]

    def get(self, request):
        group_id = request.query_params.get('group')
        date = request.query_params.get('date')

        if not group_id or not date:
            return Response(
                {'detail': "'group' va 'date' parametrlari majburiy."},
                status=status.HTTP_400_BAD_REQUEST
            )

        qs = Attendance.objects.filter(group_id=group_id, date=date)

        summary = {
            'group':group_id,
            'date':date,
            'total':qs.count(),
            'present':qs.filter(status='present').count(),
            'absent':qs.filter(status='absent').count(),
            'late':qs.filter(status='late').count(),
        }

        return Response(summary)
