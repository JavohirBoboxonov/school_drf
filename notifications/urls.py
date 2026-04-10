from django.urls import path
from .views import (
    NotificationListCreateView, 
    NotificationDetailView,
    NotificationMarkReadView,
    NotificationMarkAllReadView
)

urlpatterns = [
    path('', NotificationListCreateView.as_view(), name='notification-list-create'),
    path('read-all/', NotificationMarkAllReadView.as_view(), name='notification-read-all'),
    path('<int:pk>/', NotificationDetailView.as_view(), name='notification-detail'),
    path('<int:pk>/read/', NotificationMarkReadView.as_view(), name='notification-mark-read'),
]
