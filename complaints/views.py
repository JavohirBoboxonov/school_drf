from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Complaint
from .serializers import ComplaintSerializer, ComplaintStatusSerializer


class IsAdmin(IsAuthenticated):
    """Faqat admin kirishi mumkin"""
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.role == 'admin'


class ComplaintListCreateView(generics.ListCreateAPIView):
    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Complaint.objects.select_related('student')

        # Student faqat o'z shikoyatlarini ko'radi
        if user.role == 'student':
            qs = qs.filter(student=user)

        # Filter: status bo'yicha
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)

        return qs.order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [IsAuthenticated()]


class ComplaintDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = ComplaintSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Complaint.objects.select_related('student')
        if user.role == 'student':
            qs = qs.filter(student=user)
        return qs

    def destroy(self, request, *args, **kwargs):
        complaint = self.get_object()
        if complaint.student != request.user and request.user.role != 'admin':
            return Response(
                {'detail': "Faqat o'z shikoyatingizni o'chira olasiz."},
                status=status.HTTP_403_FORBIDDEN
            )
        complaint.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ComplaintResolveView(APIView):
    """PATCH /complaints/<pk>/resolve/ — admin shikoyatni yopadi"""
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        try:
            complaint = Complaint.objects.get(pk=pk)
        except Complaint.DoesNotExist:
            return Response(
                {'detail': "Shikoyat topilmadi."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ComplaintStatusSerializer(complaint, data={'status': 'resolved'}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': "Shikoyat yopildi.", 'status': 'resolved'})
