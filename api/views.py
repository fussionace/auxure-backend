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
# Initial view function, but did not allow the display of recommended products
# class PerfumesViewSet(ModelViewSet):
#     queryset = Perfume.objects.all()
#     serializer_class = PerfumeSerializer
#      Implementing filter and search
#     filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
#     filterset_class = PerfumeFilter
#     search_fields = ['name', 'description']
#     ordering_fields = ['price']     You can order by any other field or add other fields
#      Implementing Pagination
#     pagination_class = PageNumberPagination



# The modified view function to also fetch similar perfumes and display on the perfume detail page
class PerfumesViewSet(ModelViewSet):
    queryset = Perfume.objects.all()
    serializer_class = PerfumeSerializer

    # Implementing filter and search
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PerfumeFilter
    search_fields = ['name', 'description']
    ordering_fields = ['price']     #You can order by any other field or add other fields
    # Implementing Pagination
    pagination_class = PageNumberPagination

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        # Fetch similar perfumes based on title and gender
        similar_perfumes = Perfume.objects.filter(
            category__title=instance.category.title,
            category__gender=instance.category.gender,
            price__lte=instance.price + 50,   #Define your price range here
            price__gte=instance.price - 50
        ).exclude(id=instance.id)

        similar_perfume_serializer = PerfumeSerializer(similar_perfumes, many=True)

        # Combine the perfume details and similar perfumes in the response
        response_data = {
            'perfume': serializer.data,
            'similar_perfumes': similar_perfume_serializer.data
        }

        return Response(response_data)


class CategoriesViewSet(ModelViewSet):
    queryset = Category.objects.all()  #Fetches multiple
    serializer_class = CategorySerializer



class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    # Since we need just specific reviews, so we create a fxn for the queryset
    def get_queryset(self):
        return Review.objects.filter(perfume_id=self.kwargs['perfume_pk'])

    def get_serializer_context(self):
        return {"perfume_id": self.kwargs["perfume_pk"]} # parsing product_id context to the serializers.py file


class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    # Inheriting from the modelviewset will be too heavy (covers 4 operations), the ListViewSet
    # would've allowed users to view other people's cart which is not a good practice, for that we 
    # only make use of 3 operations, hence the need to use the mixins in the generic viewset
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

