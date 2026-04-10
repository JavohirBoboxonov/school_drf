from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from .models import Homework
from .serializers import HomeworkSerializer, HomeworkCheckSerializer


class IsTeacherOrAdminOrAssistant(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role in ('teacher', 'assistant', 'admin')


class HomeworkListCreateView(generics.ListCreateAPIView):
    serializer_class = HomeworkSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Homework.objects.select_related('student', 'lesson', 'checked_by')
        user = self.request.user

        # O'quvchi faqat o'z vazifalarini ko'radi
        if user.role == 'student':
            qs = qs.filter(student=user)
        # O'qituvchi / assistant faqat o'zlari tekshirishi kerak bo'lgan guruhlarni ko'rishini filter qilish mumkin
        # Hozircha query params orqali limitlanadi
        elif user.role in ('teacher', 'assistant'):
            pass # Qanday qilsa ham bo'ladi, masalan qs.filter(lesson__group__teacher=user)

        lesson_id = self.request.query_params.get('lesson')
        student_id = self.request.query_params.get('student')
        status_f = self.request.query_params.get('status')

        if lesson_id:
            qs = qs.filter(lesson_id=lesson_id)
        if status_f:
            qs = qs.filter(status=status_f)
        if student_id and user.role != 'student':
            qs = qs.filter(student_id=student_id)

        return qs.order_by('-submitted_at')

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != 'student':
            raise PermissionDenied("Faqat uquvchilar uy vazifasini topshira oladi.")
        serializer.save(student=user)


class HomeworkDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = HomeworkSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Homework.objects.select_related('student', 'lesson', 'checked_by')
        if user.role == 'student':
            return qs.filter(student=user)
        return qs

    def destroy(self, request, *args, **kwargs):
        homework = self.get_object()
        # O'quvchi tekshirilgan vazifani o'chira olmasligi kerak
        if request.user.role == 'student' and homework.status == 'checked':
            return Response(
                {"detail": "Tekshirilgan vazifani o'chirish mumkin emas."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


class HomeworkCheckView(APIView):
    """PATCH /homework/<pk>/check/ — O'qituvchi yoki Assistant tekshiradi"""
    permission_classes = [IsTeacherOrAdminOrAssistant]

    def patch(self, request, pk):
        try:
            homework = Homework.objects.get(pk=pk)
        except Homework.DoesNotExist:
            return Response({"detail": "Vazifa topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        serializer = HomeworkCheckSerializer(homework, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # Yangilamoqda tekshiruvchini o'rnatish
        homework_obj = serializer.save(checked_by=request.user)

        # Agar holat `checked` dbda o'z-o'zidan emas, API jo'natganda qilingan bo'lsa
        if request.data.get('grade') is not None and not request.data.get('status'):
            homework_obj.status = 'checked'
            homework_obj.save(update_fields=['status'])

        return Response(HomeworkSerializer(homework_obj).data)
