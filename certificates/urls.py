from django.urls import path
from .views import (
    CertificateListCreateView,
    CertificateDetailView,
    CertificateVerifyView,
)

urlpatterns = [
    path('', CertificateListCreateView.as_view(), name='certificate-list-create'),
    path('<int:pk>/', CertificateDetailView.as_view(), name='certificate-detail'),
    path('verify/<uuid:verification_code>/', CertificateVerifyView.as_view(), name='certificate-verify'),
]
