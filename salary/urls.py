from django.urls import path
from .views import (
    SalaryListCreateView,
    SalaryDetailView,
    SalaryPayView
)

urlpatterns = [
    path('', SalaryListCreateView.as_view(), name='salary-list-create'),
    path('<int:pk>/', SalaryDetailView.as_view(), name='salary-detail'),
    path('<int:pk>/pay/', SalaryPayView.as_view(), name='salary-pay'),
]
