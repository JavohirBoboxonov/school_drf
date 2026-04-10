from django.urls import path
from .views import (
    HomeworkListCreateView, HomeworkDetailView,
    HomeworkCheckView
)

urlpatterns = [
    path('', HomeworkListCreateView.as_view(), name='homework-list-create'),
    path('<int:pk>/', HomeworkDetailView.as_view(), name='homework-detail'),
    path('<int:pk>/check/', HomeworkCheckView.as_view(), name='homework-check'),
]
