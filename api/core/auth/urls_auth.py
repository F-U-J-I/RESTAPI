from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views_auth import RegisterView, VerifyEmailView, RequestPasswordResetEmailView, PasswordTokenCheckAPI, \
    SetNewPasswordAPIView, UserAuthView

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),

    path('register/', RegisterView.as_view()),
    path('authentication/', UserAuthView.as_view()),
    path('email-verify/', VerifyEmailView.as_view(), name="email-verify"),
    path('request-reset-email/', RequestPasswordResetEmailView.as_view(), name="request-reset-email"),
    path('password-reset/<uidb64>/<token>/', PasswordTokenCheckAPI.as_view(), name="password-reset-confirm"),
    path('password-reset-complete/', SetNewPasswordAPIView.as_view(), name="password-reset-complete"),
]