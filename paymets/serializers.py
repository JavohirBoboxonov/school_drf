from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    # To obtain information about the enrollment and user, we can add simple fields if needed
    # But for a straightforward DRF we can just return the default, or some extra info:
    student_id = serializers.IntegerField(source='enrollment.student.id', read_only=True)
    group_name = serializers.CharField(source='enrollment.group.name', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'enrollment', 'student_id', 'group_name',
            'amount', 'method', 'transaction_id', 
            'status', 'paid_at'
        ]
        extra_kwargs = {
            'paid_at': {'read_only': True},
            'status': {'read_only': True}, # Status shouldn't be directly dictated by student creating payment initially
        }

class PaymentStatusSerializer(serializers.ModelSerializer):
    """Admin yoki tizim tomonidan to'lov holatini o'zgartirish uchun"""
    class Meta:
        model = Payment
        fields = ['status']
