from django.urls import path, include, re_path
from . import views
# Importing routers for the modelviewsets
from rest_framework.routers import DefaultRouter
# Import for nested routers
from rest_framework_nested import routers


# Url endpoints for modelviewsets

# Parent routers
# Parent router for the nested router
router = routers.DefaultRouter()
# Parent router for the other endpoints
router.register("perfumes", views.PerfumesViewSet)
router.register("categories", views.CategoriesViewSet)
router.register("carts", views.CartViewSet)

# Creating the router to be able to view the particular review for a particular product
# Child routers
# perfume child router
perfume_router = routers.NestedDefaultRouter(router, "perfumes", lookup="perfume")
perfume_router.register("reviews", views.ReviewViewSet, basename="perfume-reviews") 

# cart child router
cart_router = routers.NestedDefaultRouter(router, "carts", lookup="cart")
cart_router.register("items", views.CartItemViewSet, basename="cart-items")

# http://127.0.0.1:8000/api/perfumes/a28a9e75-8c04-4754-a931-7f945ab33550/reviews/  
# The id within the url is for the specific product so the review will be automatically dropped for that product
# http://127.0.0.1:8000/api/carts/

urlpatterns = [
    path("", include(router.urls)),
    path("", include(perfume_router.urls)),
    path("", include(cart_router.urls)),
    
]