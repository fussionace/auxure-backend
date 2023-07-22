import requests
from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view
from .serializers import PerfumeSerializer, CategorySerializer, ReviewSerializer, CartSerializer, CartItemSerializer, AddCartItemSerializer, UpdateCartItemSerializer,OrderSerializer
from store.models import Category, Perfume, Review, Cart, Cartitems
from order.models import Order
from rest_framework.response import Response
# Import for the viewset
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin,  RetrieveModelMixin, DestroyModelMixin
# Importing django filters
from django_filters.rest_framework import DjangoFilterBackend
# Importing product filters from the filters.py file
from api.filters import PerfumeFilter
# Importing searchfilter orderingfilter to implement search and sorting
from rest_framework.filters import SearchFilter, OrderingFilter
# Importing for pagination
from rest_framework.pagination import PageNumberPagination



#userProfile 
from userprofile.models import UserProfile
from .serializers import UserProfileSerializer, CreateUserSerializer
# from rest_framework import viewsets, permissions
from django.contrib.auth.models import User
from rest_framework.views import APIView
from django.db import IntegrityError

from rest_framework.authtoken.models import Token
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

from rest_framework_simplejwt.tokens import RefreshToken
# Create your views here.

# The modified view function to also fetch similar perfumes and display on the perfume detail page
class PerfumesViewSet(ModelViewSet):
    queryset = Perfume.objects.all()
    serializer_class = PerfumeSerializer

    # Implementing filter and search
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PerfumeFilter
    search_fields = ['name', 'description']
    ordering_fields = ['price']     #You can order by any other field or add other fields
    # Implementing Pagination - Not necessary except to overide the setting in the restframework dictionary
    # pagination_class = PageNumberPagination
    # page_size = 3

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

# Offed the cartviewset for the one below it to handle checkout process
# class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
#     # Inheriting from the modelviewset will be too heavy (covers 4 operations), the ListViewSet
#     # would've allowed users to view other people's cart which is not a good practice, for that we 
#     # only make use of 3 operations, hence the need to use the mixins in the generic viewset
#     queryset = Cart.objects.all()
#     serializer_class = CartSerializer


class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if 'checkout' in serializer.validated_data:
            # If the request contains 'checkout' data, process the checkout
            checkout_serializer = CheckoutSerializer(data=serializer.validated_data['checkout'])
            checkout_serializer.is_valid(raise_exception=True)
            response = checkout_serializer.save()
            return Response(response, status=status.HTTP_200_OK)
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)



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
    
    
class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(detail=True, methods=['post'])
    def complete_order(self,request, pk=None):
        order = self.get_object()
        if not order.is_cancelled:
            order.is_completed = True
            order.save()
            return Response({'message': 'Oder completed succesfully'})
    
    @action(detail=True, methods=['post'])
    def cancel_order(self , request , pk=None):
        order = self.get_object()
        if not order.is_completed:
            order.is_cancelled = True
            order.save()
            return Response({'message' : 'Order cancelled'})
        
        

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset
    
    @action(detail=False, methods=['get'])
    def cancelled_orders(self , request):
        user = self.request.user
        cancelled_orders = Order.objects.filter(user=user, is_cancelled=True)
        serializer = OrderSerializer(cancelled_orders, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def completed_orders(self , request):
        user = self.request.user
        completed_orders = Order.objects.filter(user=user, is_cancelled=True)
        serializer = OrderSerializer(completed_orders, many=True)
        return Response(serializer.data)



class UserProfileviewSet(ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    # permission_classes = [permissions.IsAuthenticated]


    # def get_queryset(self):
    #     user = self.request.user
    #     return UserProfile.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # def partial_update(self, request, *args, **kwargs):

    #     if not self.request.user.is_authenticated:
    #         raise PermissionDenied("You are not authenticated.")
        
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data, partial=True)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save(user=self.request.user)
    #     return Response(serializer.data)

    # def partial_update(self, request, *args, **kwargs):
    #     user = self.request.user
    #     serializer = self.get_serializer(user, data=request.data, partial=True)

    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)

    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # def partial_update(self, request, *args, **kwargs):
    #     user_profile = self.get_object()
    #     serializer = self.get_serializer(user_profile, data=request.data, partial=True)
        
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
        
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # def partial_update(self, request, *args, **kwargs):
    #     user = self.request.user
    #     user_profile = UserProfile.objects.get(user=user)
    #     serializer = self.get_serializer(user_profile, data=request.data, partial=True)
        
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
        
    #     return Response(serializer.errors)

    # def perform_create(self, serializer):
    #     serializer.save(user=self.request.user)


# class RegisterUserViewSet(ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = CreateUserSerializer


class CreateUser(APIView):

    def post(self, request):
        try:
            username = request.data.get('username')
            first_name = request.data.get('first_name')
            last_name = request.data.get('last_name')
            email = request.data.get('email')
            password = request.data.get('password')

            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, email=email, password=password)

            user_profile = UserProfile.objects.create(user=user)
            serializer = UserProfileSerializer(user_profile)
            
            return Response(serializer.data)
        except IntegrityError:
            return Response({'error': 'Username already exists'})
        

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        # if user:
        #     token, _ = Token.objects.get_or_create(user=user)
        #     return Response({'token': token.key})
        # else:
        #     return Response({'error': 'Invalid credentials'}, status=400)
        
        if user:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return Response({'access_token': access_token})
        else:
            return Response({'error': 'Invalid credentials'}, status=400)