from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('users.urls')),
    path('attendance/', include('attendance.urls')),
    path('certificates/', include('certificates.urls')),
    path('chat/', include('chat.urls')),
    path('complaints/', include('complaints.urls')),
    path('cources/', include('cources.urls')),
    path('exams/', include('exams.urls')),
    path('homework/', include('homework.urls')),
    path('notifications/', include('notifications.urls')),
    path('payments/', include('paymets.urls')),
    path('salary/', include('salary.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Swagger UI interfeysi
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # Redoc (muqobil interfeys)
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
