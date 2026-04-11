from rest_framework import serializers
from .models import Homework
from users.models import User


class UserShortSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


class HomeworkSerializer(serializers.ModelSerializer):
    student_info = UserShortSerializer(source='student', read_only=True)
    checked_by_info = UserShortSerializer(source='checked_by', read_only=True)

    class Meta:
        model = Homework
        fields = [
            'id', 'lesson', 'student', 'student_info',
            'file', 'submitted_at', 'grade', 'feedback',
            'checked_by', 'checked_by_info', 'status',
        ]
        extra_kwargs = {
            'student': {'write_only': True},
            'checked_by': {'write_only': True},
            'submitted_at': {'read_only': True},

            'grade': {'read_only': True},
            'feedback': {'read_only': True},
            'status': {'read_only': True},
        }

    def validate_student(self, user):
        if user.role != 'student':
            raise serializers.ValidationError("Faqat student vazifa yuborishi mumkin.")
        return user


class HomeworkCheckSerializer(serializers.ModelSerializer):

    class Meta:
        model = Homework
        fields = ['grade', 'feedback', 'status']

    def validate(self, attrs):
        status = attrs.get('status')

        valid_statuses = ('submitted', 'checked', 'returned')
        if status and status not in valid_statuses:
            raise serializers.ValidationError({"status": f"Ruxsat etilgan statuslar: {valid_statuses}"})
        

        return attrs
