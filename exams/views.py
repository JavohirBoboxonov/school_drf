from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied

from .models import Exam, ExamResult
from .serializers import ExamSerializer, ExamResultSerializer


class IsTeacherOrAdmin(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role in ('teacher', 'admin')

class ExamListCreateView(generics.ListCreateAPIView):
    serializer_class = ExamSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsTeacherOrAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = Exam.objects.select_related('group', 'created_by')
        user = self.request.user
        
        # Student faqat o'zi a'zo bo'lgan guruh (tasdiqlangan) imtihonlarini ko'ra oladi
        if user.role == 'student':
            qs = qs.filter(group__enrollments__student=user, group__enrollments__status='approved')
        
        group_id = self.request.query_params.get('group')
        exam_type = self.request.query_params.get('type')
        
        if group_id:
            qs = qs.filter(group_id=group_id)
        if exam_type:
            qs = qs.filter(exam_type=exam_type)
            
        return qs.order_by('-date')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ExamDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ExamSerializer
    queryset = Exam.objects.select_related('group', 'created_by')

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsTeacherOrAdmin()]

class ExamResultListCreateView(generics.ListCreateAPIView):
    serializer_class = ExamResultSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsTeacherOrAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = ExamResult.objects.select_related('exam', 'student')
        user = self.request.user

        if user.role == 'student':
            qs = qs.filter(student=user)

        exam_id = self.request.query_params.get('exam')
        student_id = self.request.query_params.get('student')

        if exam_id:
            qs = qs.filter(exam_id=exam_id)
        if student_id and user.role != 'student':
            qs = qs.filter(student_id=student_id)

        return qs

    def perform_create(self, serializer):
        serializer.save()


class ExamResultDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ExamResultSerializer
    queryset = ExamResult.objects.select_related('exam', 'student')

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsTeacherOrAdmin()]
