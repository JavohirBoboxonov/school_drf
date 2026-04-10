from rest_framework import serializers
from .models import Exam, ExamResult
from users.models import User


class UserShortSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


class ExamSerializer(serializers.ModelSerializer):
    created_by_info = UserShortSerializer(source='created_by', read_only=True)

    class Meta:
        model = Exam
        fields = [
            'id', 'group', 'title', 'exam_type',
            'created_by', 'created_by_info',
            'date', 'max_score'
        ]
        extra_kwargs = {
            'created_by': {'write_only': True},
        }

    def validate(self, attrs):
        max_score = attrs.get('max_score', 100)
        if max_score <= 0:
            raise serializers.ValidationError({"max_score": "Max score 0 dan katta bo'lishi kerak."})
        return attrs


class ExamResultSerializer(serializers.ModelSerializer):
    student_info = UserShortSerializer(source='student', read_only=True)
    
    class Meta:
        model = ExamResult
        fields = [
            'id', 'exam', 'student', 'student_info',
            'score', 'feedback'
        ]
        extra_kwargs = {
            'student': {'write_only': True},
        }

    def validate(self, attrs):
        exam = attrs.get('exam')
        score = attrs.get('score')
        
        if exam and score is not None:
            if score < 0 or score > exam.max_score:
                raise serializers.ValidationError({
                    "score": f"Ball 0 va {exam.max_score} oralig'ida bo'lishi kerak."
                })
        return attrs
