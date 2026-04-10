from rest_framework import serializers
from .models import Salary
from users.models import User
from django.utils import timezone

class UserShortSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'role']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


class SalarySerializer(serializers.ModelSerializer):
    user_info = UserShortSerializer(source='user', read_only=True)

    class Meta:
        model = Salary
        fields = [
            'id', 'user', 'user_info', 'month',
            'students_count', 'percent', 'base_amount',
            'total_amount', 'is_paid', 'paid_at'
        ]
        extra_kwargs = {
            'user': {'write_only': True},
            'paid_at': {'read_only': True},
        }

class SalaryPaymentSerializer(serializers.ModelSerializer):
    """Maoshni to'langanini belgilash uchun"""
    class Meta:
        model = Salary
        fields = ['is_paid']
