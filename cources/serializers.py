from rest_framework import serializers
from .models import Course, Group, Enrollment, Lesson
from users.models import User


class UserShortSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


# ──────────────────────────────
#  COURSE
# ──────────────────────────────
class CourseSerializer(serializers.ModelSerializer):
    teacher_info = UserShortSerializer(source='teacher', read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'price',
            'thumbnail', 'teacher', 'teacher_info',
            'category', 'success_rate', 'students_count',
            'is_active', 'created_at',
        ]
        extra_kwargs = {
            'teacher': {'write_only': True},
            'created_at': {'read_only': True},
            'success_rate': {'read_only': True},
            'students_count': {'read_only': True},
        }


# ──────────────────────────────
#  GROUP
# ──────────────────────────────
class GroupSerializer(serializers.ModelSerializer):
    teacher_info = UserShortSerializer(source='teacher', read_only=True)
    assistant_info = UserShortSerializer(source='assistant', read_only=True)

    class Meta:
        model = Group
        fields = [
            'id', 'name', 'course',
            'teacher', 'teacher_info',
            'assistant', 'assistant_info',
            'max_students', 'start_date', 'end_date',
            'schedule_type', 'lesson_start_time',
            'is_active', 'teacher_percent', 'assistant_percent',
        ]
        extra_kwargs = {
            'teacher': {'write_only': True},
            'assistant': {'write_only': True},
        }

    def validate(self, attrs):
        start = attrs.get('start_date')
        end = attrs.get('end_date')
        if start and end and end <= start:
            raise serializers.ValidationError(
                {"end_date": "Tugash sanasi boshlanish sanasidan keyin bo'lishi kerak."}
            )
        teacher_p = attrs.get('teacher_percent', 40)
        assistant_p = attrs.get('assistant_percent', 15)
        if teacher_p + assistant_p > 100:
            raise serializers.ValidationError(
                {"teacher_percent": "Teacher va assistant foizlari yig'indisi 100% dan oshmasligi kerak."}
            )
        return attrs


# ──────────────────────────────
#  ENROLLMENT
# ──────────────────────────────
class EnrollmentSerializer(serializers.ModelSerializer):
    student_info = UserShortSerializer(source='student', read_only=True)
    approved_by_info = UserShortSerializer(source='approved_by', read_only=True)
    remaining_debt = serializers.ReadOnlyField()
    balance_status = serializers.ReadOnlyField()

    class Meta:
        model = Enrollment
        fields = [
            'id', 'student', 'student_info',
            'group', 'status', 'enrolled_at',
            'approved_by', 'approved_by_info',
            'amount_paid', 'remaining_debt', 'balance_status',
        ]
        extra_kwargs = {
            'student': {'write_only': True},
            'approved_by': {'write_only': True},
            'enrolled_at': {'read_only': True},
            'status': {'read_only': True},
        }


class EnrollmentStatusSerializer(serializers.ModelSerializer):
    """Admin uchun — status va approved_by ni yangilash"""
    class Meta:
        model = Enrollment
        fields = ['status', 'approved_by']

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            'id', 'group', 'title', 'description',
            'lesson_type', 'file', 'content',
            'date', 'started_at', 'order', 'created_at',
        ]
        extra_kwargs = {
            'created_at': {'read_only': True},
        }
