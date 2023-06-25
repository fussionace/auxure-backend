import requests
from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view
from .serializers import PerfumeSerializer, CategorySerializer, ReviewSerializer, CartSerializer, CartItemSerializer, AddCartItemSerializer, UpdateCartItemSerializer
from store.models import Category, Perfume, Review, Cart, Cartitems
from rest_framework.response import Response
# Import for the viewset
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin,  RetrieveModelMixin, DestroyModelMixin
# Importing django filters
from django_filters.rest_framework import DjangoFilterBackend
# Importing product filters from the filters.py file
from api.filters import PerfumeFilter
# Importing searchfilter orderingfilter to implement search and sorting
from rest_framework.filters import SearchFilter, OrderingFilter
# Importing for pagination
from rest_framework.pagination import PageNumberPagination

# Create your views here.
class PerfumesViewSet(ModelViewSet):
    queryset = Perfume.objects.all()
    serializer_class = PerfumeSerializer
    # Implementing filter and search
    # Line 25 below is giving some issues, rework on it
    # filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PerfumeFilter
    search_fields = ['name', 'description']
    ordering_fields = ['price']     #You can order by any other field or add other fields
    # Implementing Pagination
    pagination_class = PageNumberPagination
    


class CategoriesViewSet(ModelViewSet):
    queryset = Category.objects.all()  #Fetches multiple
    serializer_class = CategorySerializer



class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    # Method to get only the reviews for the particular perfume(single item)
    def get_queryset(self):
        return Review.objects.filter(perfume_id=self.kwargs['perfume_pk'])

    def get_serializer_context(self):
        return {"perfume_id": self.kwargs["perfume_pk"]} # parsing product_id context to the serializers.py file


class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    # Inheriting from the modelviewset will be too heavy (covers 4 operations), the ListViewSet
    # would've allowed users to view other people's cart which is not a good practice
    queryset = Cart.objects.all()
    serializer_class = CartSerializer



class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    # Helps us get only the requested item
    def get_queryset(self):
        return Cartitems.objects.filter(cart_id=self.kwargs['cart_pk'])
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer

        return CartItemSerializer
    
    def get_serializer_context(self):
        return {"cart_id": self.kwargs["cart_pk"]}

