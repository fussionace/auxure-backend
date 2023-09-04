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

# from django.contrib.auth.views import LoginView
# from django.contrib.auth.views import LogoutView

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

# Import for swagger
# from drf_yasg import openapi
# from drf_yasg.views import get_schema_view as swagger_get_schema_view
# from drf_yasg.views import get_schema_view

# from rest_framework_swagger.views import get_swagger_view
# from drf_yasg.renderers import SwaggerUIRenderer

# Import for simplejwt

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


# schema_view = swagger_get_schema_view(
#     openapi.Info(
#         title="Auxure API",
#         default_version="1.0.0",
#         description="API documentation for Auxure project",
#     ),
#     public=True,

#     permission_classes=(AllowAny,),
# )

# schema_view = get_swagger_view(title='Your API Documentation')

def home(request):
    return render(request, "home.html")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),
    # path('', include('store.urls')),
    # path('login/', LoginView.as_view(), name='login'),
    # path('logout/', LogoutView.as_view(), name='logout'),
    # API root and documentation
    # path('api/v1/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional: Include Swagger UI view
    # path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/v1/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # Optional: Include ReDoc view
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
   
    path('api/v1/', include('api.urls')),
    
 
    # Djoser and simplejwt urls

    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.social.urls')),
    path('auth/', include('djoser.urls.jwt')),


    path('accounts/', include('allauth.urls')),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
