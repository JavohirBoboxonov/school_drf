from rest_framework import serializers
from .models import Attendance
from users.models import User


class UserShortSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'role']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


class AttendanceSerializer(serializers.ModelSerializer):
    student_info = UserShortSerializer(source='student', read_only=True)
    marked_by_info = UserShortSerializer(source='marked_by', read_only=True)

    class Meta:
        model = Attendance
        fields = [
            'id',
            'student',
            'student_info',
            'group',
            'date',
            'status',
            'marked_by',
            'marked_by_info',
        ]
        extra_kwargs = {
            'student': {'write_only': True},
            'marked_by': {'write_only': True},
        }

    def validate(self, attrs):
        student = attrs.get('student')
        marked_by = attrs.get('marked_by')

        if marked_by and marked_by.role not in ('teacher', 'assistant', 'admin'):
            raise serializers.ValidationError(
                {"marked_by": "Faqat o'qituvchi yoki assistant davomat belgilashi mumkin."}
            )

        if student and student.role != 'student':
            raise serializers.ValidationError(
                {"student": "Faqat student uchun davomat belgilanishi mumkin."}
            )

        return attrs


class AttendanceBulkSerializer(serializers.Serializer):
    group = serializers.IntegerField()
    date = serializers.DateField()
    records = serializers.ListField(
        child=serializers.DictField(),
        allow_empty=False
    )

    def validate_records(self, records):
        valid_statuses = {'present', 'absent', 'late'}
        for i, record in enumerate(records):
            if 'student' not in record:
                raise serializers.ValidationError(
                    f"records[{i}]: 'student' maydoni majburiy."
                )
            if 'status' not in record:
                raise serializers.ValidationError(
                    f"records[{i}]: 'status' maydoni majburiy."
                )
            if record['status'] not in valid_statuses:
                raise serializers.ValidationError(
                    f"records[{i}]: status '{record['status']}' noto'g'ri. "
                    f"Ruxsat etilganlar: {valid_statuses}"
                )
        return records
