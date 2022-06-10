from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('website.urls')),
    path('api/', include('core.urls')),

    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name="token"),
    # path('api/auth/', include('rest_auth.urls')),
    path('api/refresh_token/', TokenRefreshView.as_view(), name="refresh_token"),
    path('ckeditor/', include('ckeditor_uploader.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
