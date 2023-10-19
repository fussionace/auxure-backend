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
router.register(r'orders', views.OrderViewSet, basename='order')

# user profile route
router.register(r'profiles', views.UserProfileViewSet)
router.register(r'users', views.UserViewSet)


# Creating the router to be able to view the particular review for a particular product
# Child routers
# perfume child router
perfume_router = routers.NestedDefaultRouter(router, "perfumes", lookup="perfume")
perfume_router.register("reviews", views.ReviewViewSet, basename="perfume-reviews")


# PERFUMES LIST VIEW ROUTER
# list_router = routers.DefaultRouter()
# list_router.register("perfumes-list-view", views.ListViewSet, basename="perfumes-list-view")


# cart child router
cart_router = routers.NestedDefaultRouter(router, "carts", lookup="cart")
cart_router.register("items", views.CartItemViewSet, basename="cart-items")

users_router = routers.NestedDefaultRouter(router, "users", lookup="users")
# register_router = routers.NestedDefaultRouter(router, "registers", lookup="registers")

# http://127.0.0.1:8000/api/perfumes/a28a9e75-8c04-4754-a931-7f945ab33550/reviews/  
# The id within the url is for the specific product so the review will be automatically dropped for that product
# http://127.0.0.1:8000/api/carts/


urlpatterns = [
    path("", include(router.urls)),
    path("", include(perfume_router.urls)),
    path("", include(cart_router.urls)),
    path("users/", include(users_router.urls)),

    # Paystack urls
    path("orders/<int:pk>/initiate-payment/", views.OrderViewSet.as_view({"get": "initiate_payment"}), name="initiate-payment"),
    path("paystack-callback/", views.OrderViewSet.as_view({"get": "paystack_callback"}), name="paystack-callback"),
    
    # perfumes-list-view pattern
    # path("", include(list_router.urls)), 
]



# # Url patterns for the cart and checkout
# # /carts/ - List and create carts
# # /carts/{cart_pk}/ - Retrieve and delete a specific cart
# # /carts/{cart_pk}/items/ - List and create cart items for a specific cart
# # /carts/{cart_pk}/items/{item_pk}/ - Retrieve, update, and delete a specific cart item
# # /carts/{cart_pk}/checkout/ - Process the checkout for a specific cart (added functionality)

# http://127.0.0.1:8000/api/v1/perfumes-list-view/

# /orders/{order_id}/  e.g # /orders/1/
# Url pattern for order payment
# /orders/{order_id}/initiate-payment/
# Copy the id of an order here: http://127.0.0.1:8000/api/v1/orders/
# And use in the initiate-payment endpoint