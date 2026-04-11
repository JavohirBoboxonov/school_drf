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
        if self.request.method == 'POST':
            return [IsAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        qs = Salary.objects.select_related('user')

        if user.role != 'admin':
            qs = qs.filter(user=user)
        else:
            employee_id = self.request.query_params.get('user')
            is_paid = self.request.query_params.get('is_paid')
            month = self.request.query_params.get('month')
            
            if employee_id:
                qs = qs.filter(user_id=employee_id)
            if is_paid is not None:
                is_paid_bool = str(is_paid).lower() in ['true', '1', 'yes']
                qs = qs.filter(is_paid=is_paid_bool)
            if month:
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
        if self.request.method in ('PUT', 'PATCH', 'DELETE'):
            return [IsAdmin()]
        return [IsAuthenticated()]


class SalaryPayView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        try:
            salary = Salary.objects.get(pk=pk)
        except Salary.DoesNotExist:
            return Response({"detail": "Maosh topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        if salary.is_paid:
             return Response({"detail": "Maosh allaqachon to'langan."}, status=status.HTTP_400_BAD_REQUEST)

        salary.is_paid = request.data.get('is_paid', True)
        if salary.is_paid:
            salary.paid_at = timezone.now()
        salary.save()

        return Response(SalarySerializer(salary).data, status=status.HTTP_200_OK)
