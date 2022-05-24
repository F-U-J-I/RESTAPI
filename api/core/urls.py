from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RegisterView, VerifyEmailView, RequestPasswordResetEmailView, PasswordTokenCheckAPI, \
    SetNewPasswordAPIView, CollectionView, ProfileView

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),

    path('register/', RegisterView.as_view()),
    path('email-verify/', VerifyEmailView.as_view(), name="email-verify"),
    path('request-reset-email/', RequestPasswordResetEmailView.as_view(), name="request-reset-email"),
    path('password-reset/<uidb64>/<token>/', PasswordTokenCheckAPI.as_view(), name="password-reset-confirm"),
    path('password-reset-complete/', SetNewPasswordAPIView.as_view(), name="password-reset-complete"),

    path('collections/', CollectionView.as_view({'get': 'list'})),
    path('mini-collections/', CollectionView.as_view({'get': 'list_mini_collection'}), name="mini-collections"),
    path('collection/<slug:path>/', CollectionView.as_view({'get': 'retrieve'})),
    path('collection/<slug:path>/get-update/', CollectionView.as_view({'get': 'get_update_info'})),
    path('collection/<slug:path>/update/', CollectionView.as_view({'patch': 'update_info'})),

    path('profile/<slug:path>/', ProfileView.as_view()),
]
