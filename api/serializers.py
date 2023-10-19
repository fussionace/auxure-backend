from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers
from store.models import Perfume, PerfumeImage, Category, Review, Cart, Cartitems
from order.models import Order, OrderItem

# userProfile models
from userprofile.models import UserProfile

# Djoser authentication imports
from djoser.serializers import UserCreateSerializer

# djoser user serializer
class MyUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = ['id', 'username', 'password', 'email', "first_name", "last_name"]


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'email', 'phone_number', 'shipping_address', 'billing_address', 'profile_picture']
        # read_only_fields = ['user']


# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'username', 'password'] 
#         extra_kwargs = {'password': {'write_only': True}}  # To hide password when serialized

#     def create(self, validated_data):
#         user = User.objects.create_user(**validated_data)
#         return user

class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = User 
        fields = ['id', 'username', 'password', 'email']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category_id', 'title', 'gender', 'slug']


class PerfumeImageSerializer(serializers.ModelSerializer):
        class Meta:
            model = PerfumeImage
            fields = ['id', 'perfume', 'image']



class PerfumeSerializer(serializers.ModelSerializer):
    images = PerfumeImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(max_length=1000000, allow_empty_file=False),
        write_only=True
    )

    class Meta:
        model = Perfume
        fields = ['id', 'name', 'description', 'price', 'category', 'inventory', 'images', 'uploaded_images']

    # category = CategorySerializer()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Update image URLs to use MEDIA_URL
        if data['images']:
            for image_data in data['images']:
                image_data['image'] = self.context['request'].build_absolute_uri(image_data['image'])
        return data

    def create(self, validated_data):
        uploaded_images = validated_data.pop("uploaded_images")
        perfume = Perfume.objects.create(**validated_data)

        for image in uploaded_images:
            new_perfume_image = PerfumeImage.objects.create(perfume=perfume, image=image)

        return perfume

    # category = CategorySerializer()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Update image URLs to use MEDIA_URL
        if data['images']:
            for image_data in data['images']:
                image_data['image'] = self.context['request'].build_absolute_uri(image_data['image'])
        return data

    def create(self, validated_data):
        uploaded_images = validated_data.pop("uploaded_images")
        perfume = Perfume.objects.create(**validated_data)

        for image in uploaded_images:
            new_perfume_image = PerfumeImage.objects.create(perfume=perfume, image=image)

        return perfume


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'date_created', 'customer_name', 'description']
    
    # Fxn below allows you to create the review for the particular perfume
    # The validated_data argument allows you grab all the relevant fields
    def create(self, validated_data):
        perfume_id = self.context["perfume_id"]
        return Review.objects.create(perfume_id = perfume_id, **validated_data)
    

# We need just a few fields to display on the cart, not the entire product fields, hence;
# the need for the simpleproductserializer
class SimplePerfumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfume
        fields = ['id','name', 'description', 'price']



class CartItemSerializer(serializers.ModelSerializer):
    # perfume = PerfumeSerializer(many=False)
    perfume = SimplePerfumeSerializer(many=False)
    sub_total = serializers.SerializerMethodField(method_name="total")
    # Points the sub_total field to the total function below
    class Meta:
        model = Cartitems
        fields = ['id', 'cart', 'perfume', 'quantity', 'sub_total']

    def total(self, cartitem:Cartitems):
            return cartitem.quantity * cartitem.perfume.price


class AddCartItemSerializer(serializers.ModelSerializer):
    perfume_id = serializers.UUIDField()

    # Function to handle errors incase a wrong product id is sent
    def validate_product_id(self, value):
        if not Perfume.objects.filter(pk=value).exists():
            raise serializers.ValidationError("The given Id does not have an associated perfume")
        return value

    # Adding items to cart
    def save(self, **kwargs):
        cart_id = self.context["cart_id"]
        perfume_id = self.validated_data['perfume_id']
        quantity = self.validated_data['quantity']

        try:
            # If the cartitem already exists, d code below will update the quatity of the same item
            cartitem = Cartitems.objects.get(perfume_id=perfume_id, cart_id=cart_id)
            cartitem.quantity += quantity
            cartitem.save()

            self.instance = cartitem
        except:
            # If the item did not exist, a new one will be created
            # self.instance = Cartitems.objects.create(perfume_id=perfume_id, cart_id=cart_id, quantity=quantity)

            # Does the same thing as the above line by unpacking all the data inside the create method
            self.instance = Cartitems.objects.create(cart_id=cart_id, **self.validated_data)
        return self.instance

    class Meta:
        model = Cartitems
        fields = ['id', 'perfume_id', 'quantity']


class UpdateCartItemSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField(read_only=True)
    class Meta:
        model = Cartitems
        fields = ['quantity']


# Created the checkout serializer
class CheckoutSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()
    # Add any additional fields required for the checkout process

    def validate_cart_id(self, value):
        if not Cart.objects.filter(pk=value).exists():
            raise serializers.ValidationError("The given cart id does not exist")
        return value

    def save(self):
        cart_id = self.validated_data['cart_id']
        # Perform the necessary actions for checkout, such as creating an order, processing payment, etc.
        # You can access the cart using Cart.objects.get(pk=cart_id)
        # Implement the checkout logic according to your specific requirements
        # Return any relevant data or success message
        return "Checkout successful"


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    # id should be read only since its generated from within
    items = CartItemSerializer(many=True, read_only=True)
    grand_total = serializers.SerializerMethodField(method_name="cart_total")
    # You can activate the checkout below and then add it to the fields when you're ready
    # checkout = CheckoutSerializer(write_only=True) # Nested serializer for checkout
    class Meta:
        model = Cart
        fields = ['id', 'items', 'grand_total']
        # fields = ['id', 'items', 'grand_total', 'checkout'] # Added the checkout field

    def cart_total(self, cart:Cart):
        items = cart.items.all()
        total = sum([item.quantity * item.perfume.price for item in items])
        return total

    

class OrderItemSerializer(serializers.ModelSerializer):
    perfume = SimplePerfumeSerializer()
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

    class Meta:
        model = OrderItem
        fields = ['id', 'quantity', 'price', 'perfume']
    
    

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    class Meta:
        model = Order
        # fields = ['id','user','first_name','last_name','email','country','city','state','additional_info','address','zipcode','phone','total_amount','items','order_number']
        # The status field below refers to payment status
        fields = ['id', 'user', 'items', 'created_at', 'status']
        read_only_fields = ['status','user','is_completed','is_cancelled']


    def create(self, validated_data):
        items_data = validated_data.pop('items')
        request = self.context.get('request')
        order = Order.objects.create(user=request.user, **validated_data)
        order.order_number = order.generate_order_number()
        order.save()
        
        for item_data in items_data:
            product_id = item_data.pop('product')
            product = Perfume.objects.get(pk=product_id.id)
            quantity = item_data['quantity']
            price = product.price * quantity
            OrderItem.objects.create(order=order,product=product,quantity=quantity,price=price)
        return order
    

class UpdateOrderSerializer(serializers.ModelSerializer):
     class Meta:
          model = Order
          fields = ['status']


class CreateOrderSerilaizer(serializers.Serializer):
     cart_id = serializers.UUIDField()

     def validate_cart_id(self, cart_id):
          if not Cart.objects.filter(pk=cart_id).exists():
               raise serializers.ValidationError("No cart with the given ID was found")
          if Cartitems.objects.filter(cart_id=cart_id).count() == 0:
               raise serializers.ValidationError("The given cart is empty")
          return cart_id

     def save(self, **kwargs):
        #   Wrapping all the code in transaction so they can be excuted at once to avoid
        # inconsistencies in the cases of a failure
          with transaction.atomic():
            cart_id = self.validated_data['cart_id']
        #   print(self.validated_data['cart_id'])
        #   print(self.context['user_id'])

          (user, created) = User.objects.get_or_create(id=self.context['user_id'])
          order = Order.objects.create(user=user)

          cart_items = Cartitems.objects.select_related('perfume').filter(cart_id=cart_id)

          order_items = [
                OrderItem(
                    order = order,
                    perfume = item.perfume,
                    price = item.perfume.price,
                    quantity = item.quantity
                ) for item in cart_items
          ]

          OrderItem.objects.bulk_create(order_items)

        #   Delete the cart after the order has been placed
          Cart.objects.filter(pk=cart_id).delete()

          return order


# userProfile serialization

# class CreateUserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         # fields = ['username', 'password']
#         fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password']
#         extra_kwargs = {'password': {'write_only': True}}
    
    # def create(self, validated_data):
    #     user = User(username=validated_data['username'])
    #     user.set_password(validated_data['password'])
    #     user.save()
    #     return user




