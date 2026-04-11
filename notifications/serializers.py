from rest_framework import serializers
from .models import Notification
from users.models import User

class UserShortSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username

class NotificationSerializer(serializers.ModelSerializer):
    user_info = UserShortSerializer(source='user', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'user_info', 'title', 
            'body', 'notif_type', 'is_read', 'created_at'
        ]
        extra_kwargs = {
            'user': {'write_only': True},
            'created_at': {'read_only': True},
        }

class NotificationReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['is_read']
