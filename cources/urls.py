from django.urls import path
from .views import (
    CourseListCreateView, CourseDetailView,
    GroupListCreateView, GroupDetailView,
    EnrollmentListCreateView, EnrollmentDetailView, EnrollmentApproveView,
    LessonListCreateView, LessonDetailView
)

urlpatterns = [
    # Courses
    path('courses/', CourseListCreateView.as_view(), name='course-list-create'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course-detail'),

    # Groups
    path('groups/', GroupListCreateView.as_view(), name='group-list-create'),
    path('groups/<int:pk>/', GroupDetailView.as_view(), name='group-detail'),

    # Enrollments
    path('enrollments/', EnrollmentListCreateView.as_view(), name='enrollment-list-create'),
    path('enrollments/<int:pk>/', EnrollmentDetailView.as_view(), name='enrollment-detail'),
    path('enrollments/<int:pk>/approve/', EnrollmentApproveView.as_view(), name='enrollment-approve'),

    # Lessons
    path('lessons/', LessonListCreateView.as_view(), name='lesson-list-create'),
    path('lessons/<int:pk>/', LessonDetailView.as_view(), name='lesson-detail'),
]
