from rest_framework import serializers
from .models import Complaint
from users.models import User


class UserShortSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


class ComplaintSerializer(serializers.ModelSerializer):
    student_info = UserShortSerializer(source='student', read_only=True)

    class Meta:
        model = Complaint
        fields = [
            'id',
            'student',
            'student_info',
            'title',
            'body',
            'status',
            'created_at',
        ]
        extra_kwargs = {
            'student': {'write_only': True},
            'created_at': {'read_only': True},
            'status': {'read_only': True},
        }

    def validate_student(self, user):
        if user.role != 'student':
            raise serializers.ValidationError(
                "Shikoyat faqat student tomonidan yuborilishi mumkin."
            )
        return user


class ComplaintStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = ['status']
