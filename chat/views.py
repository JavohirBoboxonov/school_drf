from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from .models import Message
from .serializers import MessageSerializer, MessageReadSerializer

class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        msg_type = self.request.query_params.get('type')
        group_id = self.request.query_params.get('group')
        receiver_id = self.request.query_params.get('receiver')

        qs = Message.objects.select_related('sender', 'receiver', 'group').filter(
            Q(sender=user) | Q(receiver=user) | Q(group__students=user) | Q(group__teacher=user)
        ).distinct().order_by('created_at')

        if msg_type:
            qs = qs.filter(msg_type=msg_type)
        if group_id:
            qs = qs.filter(group_id=group_id, msg_type='group')
        if receiver_id:
            qs = qs.filter(
                msg_type='direct'
            ).filter(
                Q(sender=user, receiver_id=receiver_id) |
                Q(sender_id=receiver_id, receiver=user)
            )

        return qs

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

class MessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return MessageReadSerializer
        return MessageSerializer

    def get_queryset(self):
        user = self.request.user
        return Message.objects.select_related('sender', 'receiver', 'group').filter(
            Q(sender=user) | Q(receiver=user) | Q(group__students=user) | Q(group__teacher=user)
        ).distinct()

    def destroy(self, request, *args, **kwargs):
        message = self.get_object()
        if message.sender != request.user:
            return Response(
                {'detail': "Faqat o'z xabaringizni o'chira olasiz."},
                status=status.HTTP_403_FORBIDDEN
            )
        message.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class MessageMarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            message = Message.objects.get(pk=pk, receiver=request.user)
        except Message.DoesNotExist:
            return Response(
                {'detail': "Xabar topilmadi yoki ruxsat yo'q."},
                status=status.HTTP_404_NOT_FOUND
            )
        message.is_read = True
        message.save(update_fields=['is_read'])
        return Response({'detail': "Xabar o'qilgan deb belgilandi."}, status=status.HTTP_200_OK)

class UnreadCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Message.objects.filter(receiver=request.user, is_read=False).count()
        return Response({'unread_count': count})
