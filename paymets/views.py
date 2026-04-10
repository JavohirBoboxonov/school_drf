from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Payment
from .serializers import PaymentSerializer, PaymentStatusSerializer

class IsAdmin(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == 'admin'

class PaymentListCreateView(generics.ListCreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Payment.objects.select_related('enrollment__student', 'enrollment__group')
        if user.role == 'student':
            qs = qs.filter(enrollment__student=user)
        else:
            student_id = self.request.query_params.get('student')
            enrollment_id = self.request.query_params.get('enrollment')
            
            if student_id:
                qs = qs.filter(enrollment__student_id=student_id)
            if enrollment_id:
                qs = qs.filter(enrollment_id=enrollment_id)

        pay_status = self.request.query_params.get('status')
        if pay_status:
             qs = qs.filter(status=pay_status)

        return qs.order_by('-paid_at')

    def perform_create(self, serializer):
        serializer.save(status='pending')


class PaymentDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Payment.objects.select_related('enrollment__student', 'enrollment__group')
        if user.role == 'student':
            qs = qs.filter(enrollment__student=user)
        return qs

    def destroy(self, request, *args, **kwargs):
        payment = self.get_object()
        if payment.status == 'success' and request.user.role != 'admin':
            return Response(
                {"detail": "Muvaffaqiyatli to'lovni o'chirish faqat adminlarga ruxsat beriladi."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


class PaymentStatusUpdateView(APIView):
    """PATCH /payments/<pk>/status/ -> To'lov holatini yangilash (Faqat tizim / Admin)"""
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        try:
            payment = Payment.objects.get(pk=pk)
        except Payment.DoesNotExist:
            return Response({"detail": "To'lov topilmadi"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PaymentStatusSerializer(payment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        updated_payment = serializer.save()
        if updated_payment.status == 'success':
            enrollment = updated_payment.enrollment
            pass

        return Response({"status": updated_payment.status, "detail": "To'lov holati yangilandi"}, status=status.HTTP_200_OK)
