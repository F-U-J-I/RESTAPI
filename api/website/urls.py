
from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import MainView, SignUpView, LoginView


urlpatterns = [
    # path('', MainView, name='main'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='web-login'),
]