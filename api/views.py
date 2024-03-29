import requests
import paystack
import uuid
import json
import hmac 
import hashlib
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from rest_framework.decorators import api_view
from .serializers import PerfumeSerializer, SimplePerfumeSerializer, CategorySerializer, ReviewSerializer, CartSerializer, CartItemSerializer, AddCartItemSerializer, UpdateCartItemSerializer, OrderSerializer, UpdateOrderSerializer, CreateOrderSerilaizer, CheckoutSerializer
from store.models import Category, Perfume, Review, Cart, Cartitems
from order.models import Order, OrderItem
from rest_framework.response import Response
# Import for the viewset
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
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
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

#userProfile 
from userprofile.models import UserProfile
from .serializers import UserProfileSerializer, UserSerializer
# from rest_framework import viewsets, permissions
from django.contrib.auth.models import User

from django.contrib.auth import login
from rest_framework.permissions import IsAuthenticated

from rest_framework.authtoken.models import Token
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated, IsAdminUser
# Importing custom permissions
from . import permissions

# Import for google login
from rest_framework.views import APIView
from rest_framework.response import Response
from social_django.utils import psa
import jwt
from datetime import datetime, timedelta

from drf_spectacular.utils import extend_schema

import requests
from decouple import config
from django.shortcuts import redirect
from django.http import JsonResponse
from django.urls import reverse 
from django.shortcuts import render

# Create your views here.

# Custom pagination class for perfumes
class CustomPerfumesPagination(PageNumberPagination):
    page_size_query_param = 'size'  # The size parameter comes from what was set in the settings file
    max_page_size = 10  # Maximum page size is adjustable

    def get_next_link(self):
        if not self.page.has_next():
            return None

        url = self.request.build_absolute_uri()
        page_number = self.page.next_page_number()
        size = self.request.query_params.get(self.page_size_query_param, self.page_size)

        # Parsing the URL into its components
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)

        # Updating the 'size' parameter
        query_params[self.page_size_query_param] = size

        # Updating the 'page' parameter
        query_params['page'] = page_number

        # Encoding the updated query parameters and construct the next link
        updated_query = urlencode(query_params, doseq=True)
        url_parts = list(parsed_url)
        url_parts[4] = updated_query  # Update the query component
        return urlunparse(url_parts)


class PerfumesViewSet(ModelViewSet):
    queryset = Perfume.objects.all()
    serializer_class = PerfumeSerializer
    permission_classes = [permissions.IsAdminOrReadOnly]  # Using your custom permission class

    # Implementing filter and search
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PerfumeFilter
    search_fields = ['name', 'description']
    ordering_fields = ['price']  # You can order by any other field or add other fields

    # Set custom pagination class
    pagination_class = CustomPerfumesPagination

    @extend_schema(responses=CategorySerializer)
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        # Fetch similar perfumes based on title and gender
        similar_perfumes = Perfume.objects.filter(
            category__title=instance.category.title,
            category__gender=instance.category.gender,
            price__lte=instance.price + 50,  # Defining the price range
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
    queryset = Category.objects.all()  
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminOrReadOnly]


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    

    # Since we need just specific reviews, so we create a fxn for the queryset
    def get_queryset(self):
        return Review.objects.filter(perfume_id=self.kwargs['perfume_pk'])

    def get_serializer_context(self):
        return {"perfume_id": self.kwargs["perfume_pk"]} # parsing product_id context to the serializers.py file


# Activated if the backend is to handle the cart logic
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
    

# Activated if the frontend is to handle the cart logic
# class CartViewSet(ModelViewSet):
#     permission_classes = [permissions.IsAuthenticated]
#     serializer_class = OrderSerializer

#     def create(self, request, *args, **kwargs):
#         paystack_secret_key = settings.PAYSTACK_SECRET_KEY
#         paystack.initialize(paystack_secret_key)

#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)



class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']
    # Helps us get only items associated to the particular cart
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


   
# class OrderViewSet(ModelViewSet):
#     permission_classes = [IsAuthenticated,]
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializer

#     @action(detail=True, methods=['post'])
#     def complete_order(self,request, pk=None):
#         order = self.get_object()
#         if not order.is_cancelled:
#             order.is_completed = True
#             order.save()
#             return Response({'message': 'Order completed succesfully'})
    
#     @action(detail=True, methods=['post'])
#     def cancel_order(self , request , pk=None):
#         order = self.get_object()
#         if not order.is_completed:
#             order.is_cancelled = True
#             order.save()
#             return Response({'message' : 'Order cancelled'})
        
        

#     def get_queryset(self):
#         queryset = super().get_queryset()
#         queryset = queryset.filter(user=self.request.user)
#         return queryset
    
#     @action(detail=False, methods=['post'])
#     def checkout(self, request):
#         serializer = self.get_serializer(data=request.data)
#         #serializer.is_valid(raise_exeption=True)
#         if serializer.is_valid():
#             validated_data = serializer.validated_data
#         #products = serializer.validated_data['items']
#         #email = serializer.validated_data['email']
#         #total_amount = serializer.validated_data['total_amount']
#             reference = uuid.uuid4()

#             paystack_url = "https://api.paystack.co/transaction/initialize"
#             paystack_secret_key = settings.PAYSTACK_SECRET_KEY

#             order_data = {
#                 "email": validated_data['email'],
#                 "amount": int(validated_data['total_amount']*100),
#                 "reference" : str(reference),
#                 "callback_url": 'https://http://127.0.0.1:8000/paystack/callback'
#             }

#             headers = {
#                 "Authorization" : f"Bearer {paystack_secret_key}",
#                 "Content-Type": "application/json"
#             }

#             response = requests.post(paystack_url, json=order_data, headers=headers)
#             data = response.json()
#             Order = serializer.save(reference=reference)
#             return Response({'payment_url': data['data']['authorization_url']})
       
   
#     @csrf_exempt
#     def dispatch(self, request, *args, **kwargs):
#        return super().dispatch(request, *args, **kwargs)

#     @action (detail=False, methods=['post'], url_path='paystack-callback')
#     def paystack_callback(self, request):
#         callback_data = json.loads(request.body)
#         reference = callback_data['data']['reference']
#         paystack_secret_key = settings.PAYSTACK_SECRET_KEY
#         headers = {
#                 "Authorization" : f"Bearer {paystack_secret_key}",
#             }
#         verify_response = requests.get(f'https://api.paystack.co/transaction/verify/{reference}', headers=headers)
#         verification_data =verify_response.json()
#         if verification_data['data']['status']== 'success':
#             order = Order.objects.get(reference=reference)
#             order.is_completed = True
#             order.save()
#             return HttpResponse(status=200)


             
#     @action(detail=False, methods=['get'])
#     def cancelled_orders(self , request):
#         user = self.request.user
#         cancelled_orders = Order.objects.filter(user=user, is_cancelled=True)
#         serializer = OrderSerializer(cancelled_orders, many=True)
#         return Response(serializer.data)
    
#     @action(detail=False, methods=['get'])
#     def completed_orders(self , request):
#         user = self.request.user
#         completed_orders = Order.objects.filter(user=user, is_completed=True)
#         serializer = OrderSerializer(completed_orders, many=True)
#         return Response(serializer.data)
# def verify_paystack_signature(payload, signature, secret_key):
#     paystack_signature = hmac.new(secret_key.encode('utf8'), msg=payload, digestmod=hashlib.sha256).hexdigest()
#     return paystack_signature == signature




# New Order viewset
class OrderViewSet(ModelViewSet):
    # queryset = Order.objects.all()
    # serializer_class = OrderSerializer
    # permission_classes = [IsAuthenticated, permissions.IsOrderOwnerOrAdmin]

    # NB: Using a queryset method instead of the property will need you to set a basename in the url

    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)


    def create(self, request, *args, **kwargs):
        serilizer = CreateOrderSerilaizer(data=request.data, context={"user_id": self.request.user.id})
        serilizer.is_valid(raise_exception=True)
        order = serilizer.save()
        serializer = OrderSerializer(order)

        return Response(serializer.data)

    # def get_serializer_context(self):
    #     return {"user_id": self.request.user.id}
    
    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateOrderSerilaizer
        elif self.request.method == "PATCH":
            return UpdateOrderSerializer
        return OrderSerializer
    

    # Integrating paystack payment gateway
    @action(detail=True, methods=['get'])
    def initiate_payment(self, request, pk):
        PAYSTACK_SECRET_KEY = config('PAYSTACK_SECRET_KEY')
        order = self.get_object()  # Retrieve the order

        # Check if order.total_amount is not None and is a numeric value
        # Ensure total_amount has some value
        if order.total_amount is not None and isinstance(order.total_amount, (int, float)):
            amount_in_kobo = int(order.total_amount * 100)  # Convert to kobo
        else:
            # Handle the case where order.total_amount is None or not numeric
            return JsonResponse({'error': 'Invalid order total amount'}, status=400)

        # Continue with the rest of the payment initiation logic
        data = {
            "email": order.email,
            "amount": amount_in_kobo,
            "order_id": order.id,
            "callback_url": request.build_absolute_uri(reverse('paystack_callback')),
            # Add any other required fields
        }

        headers = {
            "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post("https://api.paystack.co/transaction/initialize", json=data, headers=headers)

        if response.status_code == 200:
            payment_info = response.json()
            return redirect(payment_info['data']['authorization_url'])
        else:
            return JsonResponse({'error': 'Payment initiation failed'}, status=400)

        
    # Callback method
    def paystack_callback(request):
        PAYSTACK_SECRET_KEY = config('PAYSTACK_SECRET_KEY')
        reference = request.GET.get('reference')
        # Verify the payment with the reference using Paystack API

        data = {
            "reference": reference,
            "authorization_code": request.GET.get('authorization_code')
        }

        headers = {
            "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post("https://api.paystack.co/transaction/verify", json=data, headers=headers)

        if response.status_code == 200:
            payment_info = response.json()
            if payment_info['data']['status'] == 'success':
                # Payment was successful, update your order's status
                order = Order.objects.get(id=payment_info['data']['metadata']['order_id'])
                order.is_completed = True
                order.save()
                return render(request, 'payment_success.html')
            else:
                return render(request, 'payment_failed.html', {'error': 'Payment verification failed'})




# Viewset for updating user profiles
class UserProfileViewSet(ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    
    def get_permissions(self):
        if self.action == 'retrieve' or self.action == 'update':
            return [IsAuthenticated(), permissions.IsProfileOwnerOrAdmin()]
        elif self.action in ['list', 'create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminUser()]
        return super().get_permissions()


# Viewset to handle signup, login and logout
class UserViewSet(ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer

    @action(detail=False, methods=['POST'], permission_classes=[permissions.IsAdminOrReadOnly])
    def register(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username=username).exists():
            return Response({"error": "Username is already taken."}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        request.auth.delete()
        return Response({"message": "User logged out successfully."}, status=status.HTTP_200_OK)


