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
from api import views
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static

# Import for swagger
from drf_yasg import openapi
from drf_yasg.views import get_schema_view as swagger_get_schema_view

# Import for simplejwt

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

schema_view = swagger_get_schema_view(
    openapi.Info(
        title="Auxure API",
        default_version="1.0.0",
        description="API documentation for Auxure project",
    ),
    public=True,
)


urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', include('store.urls')),
    
    # API root and documentation
    path('api/v1/', include([path("", include("api.urls")),
                             path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name="swagger_schema"),])),
   
    # Djoser and simplejwt urls

    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.social.urls')),
    path('auth/', include('djoser.urls.jwt')),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
