from django.urls import path
from .views import (
    AttendanceListCreateView,
    AttendanceDetailView,
    AttendanceBulkCreateView,
    AttendanceSummaryView,
)

urlpatterns = [
    path('', AttendanceListCreateView.as_view(), name='attendance-list-create'),
    path('<int:pk>/', AttendanceDetailView.as_view(), name='attendance-detail'),
    path('bulk/', AttendanceBulkCreateView.as_view(), name='attendance-bulk-create'),
    path('summary/', AttendanceSummaryView.as_view(), name='attendance-summary'),
]
