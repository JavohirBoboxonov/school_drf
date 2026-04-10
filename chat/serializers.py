from rest_framework import serializers
from .models import Message
from users.models import User


class UserShortSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


class MessageSerializer(serializers.ModelSerializer):
    sender_info = UserShortSerializer(source='sender', read_only=True)
    receiver_info = UserShortSerializer(source='receiver', read_only=True)

    class Meta:
        model = Message
        fields = [
            'id',
            'sender',
            'sender_info',
            'receiver',
            'receiver_info',
            'group',
            'content',
            'msg_type',
            'is_read',
            'created_at',
        ]
        extra_kwargs = {
            'sender': {'write_only': True},
            'receiver': {'write_only': True},
            'created_at': {'read_only': True},
        }

    def validate(self, attrs):
        msg_type = attrs.get('msg_type', 'direct')
        receiver = attrs.get('receiver')
        group = attrs.get('group')

        if msg_type == 'direct' and not receiver:
            raise serializers.ValidationError(
                {"receiver": "Direct xabarda receiver majburiy."}
            )
        if msg_type == 'group' and not group:
            raise serializers.ValidationError(
                {"group": "Group xabarda group majburiy."}
            )
        if msg_type == 'direct' and group:
            raise serializers.ValidationError(
                {"group": "Direct xabarda group bo'lmasligi kerak."}
            )
        if msg_type == 'group' and receiver:
            raise serializers.ValidationError(
                {"receiver": "Group xabarda receiver bo'lmasligi kerak."}
            )
        return attrs


class MessageReadSerializer(serializers.ModelSerializer):
    """Faqat is_read maydonini yangilash uchun"""
    class Meta:
        model = Message
        fields = ['is_read']
