from django.urls import path
from .views import (
    ExamListCreateView, ExamDetailView,
    ExamResultListCreateView, ExamResultDetailView
)

urlpatterns = [

    path('', ExamListCreateView.as_view(), name='exam-list-create'),
    path('<int:pk>/', ExamDetailView.as_view(), name='exam-detail'),


    path('results/', ExamResultListCreateView.as_view(), name='exam-result-list-create'),
    path('results/<int:pk>/', ExamResultDetailView.as_view(), name='exam-result-detail'),
]
