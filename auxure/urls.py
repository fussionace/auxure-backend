"""
URL configuration for auxure project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.shortcuts import render
from api import views
from django.urls import path, include, re_path
# from allauth.account.views import ConfirmEmailView
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.permissions import AllowAny

# Import for swagger
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

# Import for simplejwt

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


# A function to display at the root page
def home(request):
    return render(request, "home.html")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),
    
    # urlpatterns for spectacular swagger documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Swagger UI view url pattern
    path('api/v1/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # Optional: Include ReDoc view
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
   
    # Base api url patter
    path('api/v1/', include('api.urls')),
    
    # Djoser and simplejwt urls

    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.social.urls')),
    path('auth/', include('djoser.urls.jwt')),

    # Social login
    path('accounts/', include('allauth.urls')),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

