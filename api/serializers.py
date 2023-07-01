from django.contrib.auth.models import User
from rest_framework import serializers
from store.models import Perfume, PerfumeImage, Category, Review, Cart, Cartitems
from order.models import Order, OrderItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category_id', 'title', 'slug']


class PerfumeImageSerializer(serializers.ModelSerializer):
        class Meta:
            model = PerfumeImage
            fields = ['id', 'perfume', 'image']



class PerfumeSerializer(serializers.ModelSerializer):
    images = PerfumeImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child = serializers.ImageField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True
    )

    class Meta:
        model = Perfume
        fields = ['id', 'name', 'description', 'price', 'inventory', 'images', 'uploaded_images']

    def create(self, validated_data):
        uploaded_images = validated_data.pop("uploaded_images")
        perfume = Perfume.objects.create(**validated_data) #unpacks the validated data

        for image in uploaded_images:
            new_perfume_image = PerfumeImage.objects.create(perfume=perfume, image=image)

        return perfume
    

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'date_created', 'name', 'description']
    
    # Fxn below allows you to create the review for the particular perfume
    # The validated_data argument allows you grab all the relevant fields
    def create(self, validated_data):
        perfume_id = self.context["perfume_id"]
        return Review.objects.create(perfume_id = perfume_id, **validated_data)
    


class SimplePerfumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfume
        fields = ['id','name', 'description', 'price']



class CartItemSerializer(serializers.ModelSerializer):
    # perfume = PerfumeSerializer(many=False)
    perfume = SimplePerfumeSerializer(many=False)
    sub_total = serializers.SerializerMethodField(method_name="total")
    # Points the sub_total field to the total method below
    class Meta:
        model = Cartitems
        fields = ['id', 'cart', 'product', 'quantity', 'sub_total']

    def total(self, cartitem:Cartitems):
            return cartitem.quantity * cartitem.perfume.price


class AddCartItemSerializer(serializers.ModelSerializer):
    perfume_id = serializers.UUIDField()

    # Function to handle errors incase a wrong product id is sent
    def validate_product_id(self, value):
        if not Perfume.objects.filter(pk=value).exists():
            raise serializers.ValidationError("The given Id does not have an associated product")
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
        fields = ['id', 'product_id', 'quantity']


class UpdateCartItemSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField(read_only=True)
    class Meta:
        model = Cartitems
        fields = ['quantity']


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    # id should be read only since its generated from within
    items = CartItemSerializer(many=True, read_only=True)
    grand_total = serializers.SerializerMethodField(method_name="cart_total")
    class Meta:
        model = Cart
        fields = ['id', 'items', 'grand_total']

    def cart_total(self, cart:Cart):
        items = cart.items.all()
        total = sum([item.quantity * item.perfume.price for item in items])
        return total
    
class OrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem
        fields = ['id','product','price','quantity','sub_total']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ['id','user','first_name','last_name','email','country','city','state','additional_info','address','zipcode','order_number','phone','created_at','total_amount','is_completed','is_cancelled','status','items',]
        read_only_fields = ['order_number','total_amount','status','user','is_completed','is_cancelled']


    def create(self, validated_data):
        user = self.context['request'].user
        cart = Cart.objects.get(user=user)
        order = Order.objects.create(user=user, **validated_data)
        order.save()
        cart_items = cart.items.all()
        for cart_item in cart_items:
            ordered_quantiy = cart_item.quantity
            if ordered_quantiy > 0 :
                product = cart_item.perfume
                product_price = product.price
                OrderItem.objects.create(order=order, product=product,quantity=ordered_quantiy,price=product_price, sub_total=product_price*ordered_quantiy )
                cart_item.quantity -= ordered_quantiy
                cart_item.save()
        order.total_amount = sum(item.subtotal for item in order.items.all())
        order.save()
        return order
