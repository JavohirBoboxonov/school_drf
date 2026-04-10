from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import Salary
from .serializers import SalarySerializer, SalaryPaymentSerializer

class IsAdmin(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == 'admin'

class SalaryListCreateView(generics.ListCreateAPIView):
    serializer_class = SalarySerializer

    def get_permissions(self):
        # Maoshlarni faqat admin qo'sha oladi (yoki cronjob avtomatik kiritadi)
        if self.request.method == 'POST':
            return [IsAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        qs = Salary.objects.select_related('user')

        if user.role != 'admin':
            # Har qanday oddiy xodim faqat o'z maoshini ko'ra oladi
            qs = qs.filter(user=user)
        else:
            # Admin filtrlashi mumkin
            employee_id = self.request.query_params.get('user')
            is_paid = self.request.query_params.get('is_paid')
            month = self.request.query_params.get('month') # formato YYYY-MM-DD
            
            if employee_id:
                qs = qs.filter(user_id=employee_id)
            if is_paid is not None:
                is_paid_bool = str(is_paid).lower() in ['true', '1', 'yes']
                qs = qs.filter(is_paid=is_paid_bool)
            if month:
                # Masalan faqat yili va oyi bo'yicha filter kerak bo'lsa month__startswith qilinadi
                qs = qs.filter(month=month)

        return qs.order_by('-month')


class SalaryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SalarySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Salary.objects.select_related('user')
        if user.role != 'admin':
            qs = qs.filter(user=user)
        return qs

    def get_permissions(self):
        # Oddiy foydalanuvchi faqat o'zinikini ko'radi, tahrirlash/o'chirish faqat admin
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsAdmin()]
        return [IsAuthenticated()]


class SalaryPayView(APIView):
    """PATCH /salary/<pk>/pay/ -> Maoshni to'langan qilib belgilash"""
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        try:
            salary = Salary.objects.get(pk=pk)
        except Salary.DoesNotExist:
            return Response({"detail": "Maosh topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        if salary.is_paid:
             return Response({"detail": "Maosh allaqachon to'langan."}, status=status.HTTP_400_BAD_REQUEST)

        # To'langan qilib belgilash va paid_at ni Hozirgi kunga set qilish
        salary.is_paid = request.data.get('is_paid', True)
        if salary.is_paid:
            salary.paid_at = timezone.now()
        salary.save()

        return Response(SalarySerializer(salary).data, status=status.HTTP_200_OK)
