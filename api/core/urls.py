from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RegisterView, VerifyEmailView, RequestPasswordResetEmailView, PasswordTokenCheckAPI, \
    SetNewPasswordAPIView, CourseView, CollectionView, ProfileView

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),

    path('register/', RegisterView.as_view()),
    path('email-verify/', VerifyEmailView.as_view(), name="email-verify"),
    path('request-reset-email/', RequestPasswordResetEmailView.as_view(), name="request-reset-email"),
    path('password-reset/<uidb64>/<token>/', PasswordTokenCheckAPI.as_view(), name="password-reset-confirm"),
    path('password-reset-complete/', SetNewPasswordAPIView.as_view(), name="password-reset-complete"),

    path('courses/', CourseView.as_view({'get': 'get_list_course'})),
    path('mini-courses/', CourseView.as_view({'get': 'get_list_mini_course'})),
    path('courses/page/<slug:path>', CourseView.as_view({'get': 'get_page_course'})),

    path('collections/', CollectionView.as_view({'get': 'list'})),
    path('mini-collections/', CollectionView.as_view({'get': 'list_mini_collection'}), name="mini-collections"),
    path('collections/<slug:path>/', CollectionView.as_view({'get': 'get'})),
    path('create/collection/', CollectionView.as_view({'post': 'create_collection'})),
    path('get-update/collections/<slug:path>/', CollectionView.as_view({'get': 'get_update_info'})),
    path('update/collections/<slug:path>/', CollectionView.as_view({'patch': 'update_info'})),
    path('delete/collections/<slug:path>/', CollectionView.as_view({'delete': 'delete_collection'})),

    path('profile/<slug:path>/', ProfileView.as_view()),
]
