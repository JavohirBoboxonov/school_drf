from rest_framework import serializers
from .models import Certificate
from users.models import User


class UserShortSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


class CertificateSerializer(serializers.ModelSerializer):
    student_info = UserShortSerializer(source='student', read_only=True)

    class Meta:
        model = Certificate
        fields = [
            'id',
            'student',
            'student_info',
            'course',
            'issued_at',
            'pdf_file',
            'qr_code',
            'verification_code',
        ]
        extra_kwargs = {
            'student': {'write_only': True},
            'verification_code': {'read_only': True},
            'issued_at': {'read_only': True},
        }

    def validate_student(self, user):
        if user.role != 'student':
            raise serializers.ValidationError(
                "Sertifikat faqat student uchun berilishi mumkin."
            )
        return user
