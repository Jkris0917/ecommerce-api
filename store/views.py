from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny,IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .models import Category,Product,Cart,CartItem,Order,OrderItem
from .serializers import RegisterSerializer,CategorySerializer,ProductSerializer,CartItemSerializer,CartSerializer,OrderSerializer,OrderItemSerializer

# Create your views here.
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            "message":"User created successfully",
            "username": user.username,
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        },status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET','POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def category_list(request):
    if request.method == 'GET':
        category = Category.objects.all()
        serializer = CategorySerializer(category,many=True)
        return Response(serializer.data)
    
    if request.method == 'POST':
        if not request.user.is_staff:
            return Response({"error": "Admin only"}, status=status.HTTP_403_FORBIDDEN)
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET','PUT','DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def category_detail(request,pk):
    try:
        category = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        return Response({"error":"Category not found"}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        return Response(CategorySerializer(category).data)
    
    if request.method == 'PUT':
        if not request.user.is_staff:
            return Response({"error":"Admin only"}, status=status.HTTP_403_FORBIDDEN)
        serializer = CategorySerializer(category,data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'DELETE':
        if not request.user.is_staff:
            return Response({"error":"Admin only"}, status=status.HTTP_403_FORBIDDEN)
        category.delete()
        return Response({"message":"Category deleted successfully","id":pk})
    
@api_view(['GET','POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def product_list(request):
    
    if request.method == 'GET':
        product = Product.objects.all()
        serializer = ProductSerializer(product,many=True)
        return Response(serializer.data)
    
    if request.method == 'POST':
        if not request.user.is_staff:
            return Response({"error":"Admin only"}, status=status.HTTP_403_FORBIDDEN)
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
           product = serializer.save()
           return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   
@api_view(['GET','PUT','DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def product_detail(request,pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({"errors":"Product not found"}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        return Response(ProductSerializer(product).data)
    
    if request.method == 'PUT':
        if not request.user.is_staff:
            return Response({"error":"Admin only"}, status=status.HTTP_403_FORBIDDEN)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'DELETE':
        if not request.user.is_staff:
            return Response({"error":"Admin only"}, status=status.HTTP_403_FORBIDDEN)
        product.delete()
        return Response({"message":"Product deleted successfully"})
    
@api_view(['GET'])
def get_cart(request):
    cart,created = Cart.objects.get_or_create(user=request.user)
    return Response(CartSerializer(cart).data)

@api_view(['POST'])
def add_to_cart(request, product_pk):
    try:
        product = Product.objects.get(pk=product_pk)
    except Product.DoesNotExist:
        return Response({"error":"Product not found"}, status=status.HTTP_404_NOT_FOUND)
    
    if product.stock < 1: 
        return Response(
            {"error": "Product is out of stock"}, status=status.HTTP_400_BAD_REQUEST
        )
    
    cart, _= Cart.objects.get_or_create(user=request.user)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
        
    return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)

@api_view(['PUT','DELETE'])
def update_cart_item(request, item_pk):
    try:
        cart_item = CartItem.objects.get(pk=item_pk, cart__user=request.user)
    except CartItem.DoesNotExist:
        return Response({"error": "Cart Item not found"}, status=status.HTTP_404_NOT_FOUND)
       
    if request.method == 'PUT':
        quantity = request.data.get('quantity')
        if quantity is not None and int(quantity) > 0:
            cart_item.quantity = int(quantity)
            cart_item.save()
            return Response(CartItemSerializer(cart_item).data)
        else:
            return Response({"error": "Invalid quantity"}, status=status.HTTP_400_BAD_REQUEST) 
    
    if request.method == 'DELETE':
        cart_item.delete()
        return Response({"message":"Cart item deleted successfully"})
    
@api_view(['GET'])
def order_list(request):
    order = Order.objects.filter(user=request.user)
    serializer = OrderSerializer(order,many=True)
    return Response(serializer.data)

@api_view(['POST'])
def checkout(request):
    from django.db import transaction
    
    cart, _ = Cart.objects.get_or_create(user=request.user)
    
    cart_items = cart.items.all()
    if not cart.items.exists():
        return Response({"error":"Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
    
    with transaction.atomic():
        for item in cart_items:
            if item.product.stock < item.quantity:
                return Response({
                    "error": f"Not enough stock for {item.product.name}"
                },status=status.HTTP_400_BAD_REQUEST)
        
        total = sum(item.product.price * item.quantity for item in cart_items)
        order = Order.objects.create(user=request.user, total_price=total)
        
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price_at_purchase = item.product.price
            )
            item.product.stock -= item.quantity
            item.product.save()
            
        cart_items.delete()
    return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def order_detail(request,pk):
    try:
        order = Order.objects.get(pk=pk,user=request.user)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
    return Response(OrderSerializer(order).data)
    
@api_view(['PUT'])
def update_order_status(request,pk):
    if not request.user.is_staff:
        return Response({"error":"Admin only"}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        order = Order.objects.get(pk=pk)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
    
    requested_status = request.data.get('status')
    valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
    if requested_status not in valid_statuses:
        return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
    order.status = requested_status
    order.save()
    return Response(OrderSerializer(order).data)
