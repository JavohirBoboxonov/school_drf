from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import Course, Group, Enrollment, Lesson
from .serializers import (
    CourseSerializer, GroupSerializer,
    EnrollmentSerializer, EnrollmentStatusSerializer,
    LessonSerializer,
)


class IsAdmin(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == 'admin'


class IsTeacherOrAdmin(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role in ('teacher', 'admin')


class CourseListCreateView(generics.ListCreateAPIView):
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsTeacherOrAdmin()]
        return [AllowAny()]

    def get_queryset(self):
        qs = Course.objects.select_related('teacher').filter(is_active=True)
        category = self.request.query_params.get('category')
        teacher = self.request.query_params.get('teacher')
        if category:
            qs = qs.filter(category__icontains=category)
        if teacher:
            qs = qs.filter(teacher_id=teacher)
        return qs

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)


class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CourseSerializer
    queryset = Course.objects.select_related('teacher')

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsTeacherOrAdmin()]


class GroupListCreateView(generics.ListCreateAPIView):
    serializer_class = GroupSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = Group.objects.select_related('course', 'teacher', 'assistant')
        user = self.request.user

        if not user.is_authenticated:
            return qs.filter(is_active=True)

        if user.role == 'teacher':
            qs = qs.filter(teacher=user)
        elif user.role == 'assistant':
            qs = qs.filter(assistant=user)
        elif user.role == 'student':
            qs = qs.filter(enrollments__student=user, enrollments__status='approved')

        course_id = self.request.query_params.get('course')
        if course_id:
            qs = qs.filter(course_id=course_id)

        return qs.distinct()


class GroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = GroupSerializer
    permission_classes = [IsAdmin]
    queryset = Group.objects.select_related('course', 'teacher', 'assistant')

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAdmin()]


class EnrollmentListCreateView(generics.ListCreateAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Enrollment.objects.select_related('student', 'group', 'approved_by')
        user = self.request.user
        if user.role == 'student':
            qs = qs.filter(student=user)

        group_id = self.request.query_params.get('group')
        status_f = self.request.query_params.get('status')
        if group_id:
            qs = qs.filter(group_id=group_id)
        if status_f:
            qs = qs.filter(status=status_f)
        return qs.order_by('-enrolled_at')

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class EnrollmentDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Enrollment.objects.select_related('student', 'group', 'approved_by')
        if user.role == 'student':
            return qs.filter(student=user)
        return qs


class EnrollmentApproveView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        try:
            enrollment = Enrollment.objects.get(pk=pk)
        except Enrollment.DoesNotExist:
            return Response({'detail': "Topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status')
        if new_status not in ('approved', 'rejected'):
            return Response(
                {'detail': "'status' qiymati 'approved' yoki 'rejected' bo'lishi kerak."},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = EnrollmentStatusSerializer(
            enrollment,
            data={'status': new_status, 'approved_by': request.user.pk},
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(EnrollmentSerializer(enrollment).data)


class LessonListCreateView(generics.ListCreateAPIView):
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsTeacherOrAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = Lesson.objects.select_related('group')
        group_id = self.request.query_params.get('group')
        if group_id:
            qs = qs.filter(group_id=group_id)
        return qs.order_by('order', 'date')


class LessonDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.select_related('group')

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsTeacherOrAdmin()]
