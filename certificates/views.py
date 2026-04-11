from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404

from .models import Certificate
from .serializers import CertificateSerializer


class IsAdminOrTeacher(IsAuthenticated):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.role in ('admin', 'teacher')
        
class CertificateListCreateView(generics.ListCreateAPIView):
    serializer_class = CertificateSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminOrTeacher()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = Certificate.objects.select_related('student', 'course')
        user = self.request.user

        if user.role == 'student':
            qs = qs.filter(student=user)
        course_id = self.request.query_params.get('course')
        student_id = self.request.query_params.get('student')

        if course_id:
            qs = qs.filter(course_id=course_id)
        if student_id and user.role != 'student':
            qs = qs.filter(student_id=student_id)

        return qs
class CertificateDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CertificateSerializer

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsAdminOrTeacher()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = Certificate.objects.select_related('student', 'course')
        user = self.request.user
        if user.role == 'student':
            qs = qs.filter(student=user)
        return qs

class CertificateVerifyView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, verification_code):
        certificate = get_object_or_404(
            Certificate.objects.select_related('student', 'course'),
            verification_code=verification_code
        )
        serializer = CertificateSerializer(certificate)
        return Response({
            'valid': True,
            'certificate': serializer.data,
        }, status=status.HTTP_200_OK)
