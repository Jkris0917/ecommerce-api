from rest_framework import serializers
from .models import Category,Product,Cart,CartItem,Order,OrderItem
from django.contrib.auth.models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['username','email','password']
        
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description','created_at', 'updated_at']
        read_only_fields = ['id','created_at', 'updated_at']
        
class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category',write_only=True)
    class Meta:
        model = Product
        fields = ['id', 'name', 'description','price','stock','category','category_id','image','created_at','updated_at']
        read_only_fields = ['id','created_at','updated_at']
        
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(),source='product', write_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity']
        read_only_fields = ['id','created_at', 'updated_at']
        
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id','user','items','created_at','updated_at']
        read_only_fields = ['id','user','created_at', 'updated_at']
        
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price_at_purchase']
        read_only_fields = ['id','price_at_purchase']
        
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'total_price', 'items',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'total_price', 'created_at', 'updated_at']