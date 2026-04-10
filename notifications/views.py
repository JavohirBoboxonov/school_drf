from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Notification
from .serializers import NotificationSerializer, NotificationReadSerializer

class IsAdmin(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == 'admin'

class NotificationListCreateView(generics.ListCreateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Notification.objects.select_related('user')

        if user.role != 'admin':
            qs = qs.filter(user=user)
        else:
            user_id = self.request.query_params.get('user')
            if user_id:
                qs = qs.filter(user_id=user_id)

        notif_type = self.request.query_params.get('type')
        is_read = self.request.query_params.get('is_read')
        
        if notif_type:
            qs = qs.filter(notif_type=notif_type)
        if is_read is not None:
            is_read_bool = str(is_read).lower() in ['true', '1', 'yes']
            qs = qs.filter(is_read=is_read_bool)
            
        return qs.order_by('-created_at')

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin()]
        return super().get_permissions()


class NotificationDetailView(generics.RetrieveDestroyAPIView):
    """Notificationni o'qish va uni o'chirish"""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Notification.objects.select_related('user')
        if user.role != 'admin':
            qs = qs.filter(user=user)
        return qs


class NotificationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, user=request.user)
        except Notification.DoesNotExist:
            return Response(
                {"detail": "Bildirishnoma topilmadi."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        return Response({"detail": "Bildirishnoma o'qildi."}, status=status.HTTP_200_OK)


class NotificationMarkAllReadView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        updated_count = Notification.objects.filter(
            user=request.user, is_read=False
        ).update(is_read=True)
        return Response(
            {"detail": f"{updated_count} ta bildirishnoma o'qilgan deb belgilandi."}, 
            status=status.HTTP_200_OK
        )
