from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny,IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .models import Category,Product,Cart,CartItem,Order,OrderItem
from .serializers import RegisterSerializer,CategorySerializer,ProductSerializer,CartItemSerializer,CartSerializer,OrderSerializer,OrderItemSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter

# Create your views here.
@extend_schema(
    request=RegisterSerializer,
    responses={201: RegisterSerializer},
    description='Register a new user and receive JWT tokens.'
)
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

@extend_schema(methods=['GET'], responses={200: CategorySerializer(many=True)}, description='List all categories. Public endpoint.')
@extend_schema(methods=['POST'], request=CategorySerializer, responses={201: CategorySerializer}, description='Create a category. Admin only.')
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

@extend_schema(methods=['GET'], responses={200: CategorySerializer}, description='Get category details.')
@extend_schema(methods=['PUT'], request=CategorySerializer, responses={200: CategorySerializer}, description='Update category. Admin only.')
@extend_schema(methods=['DELETE'], responses={200: None}, description='Delete category. Admin only.')
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

@extend_schema(methods=['GET'], responses={200: ProductSerializer(many=True)}, description='List all products. Public endpoint.')
@extend_schema(methods=['POST'], request=ProductSerializer, responses={201: ProductSerializer}, description='Create a product. Admin only.')
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

@extend_schema(methods=['GET'], responses={200: ProductSerializer}, description='Get product details. Public endpoint.')
@extend_schema(methods=['PUT'], request=ProductSerializer, responses={200: ProductSerializer}, description='Update product. Admin only.')
@extend_schema(methods=['DELETE'], responses={200: None}, description='Delete product. Admin only.')
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

@extend_schema(
    responses={200: CartSerializer},
    description='Get current user cart. Creates cart automatically if it does not exist.'
)
@api_view(['GET'])
def get_cart(request):
    cart,created = Cart.objects.get_or_create(user=request.user)
    return Response(CartSerializer(cart).data)

@extend_schema(
    responses={201: CartSerializer},
    description='Add a product to cart. If product already in cart, increases quantity by 1.'
)
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

@extend_schema(methods=['PUT'], request=CartItemSerializer, responses={200: CartItemSerializer}, description='Update cart item quantity.')
@extend_schema(methods=['DELETE'], responses={200: None}, description='Remove item from cart.')
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

@extend_schema(
    responses={200: OrderSerializer(many=True)},
    description='List all orders for the current authenticated user.'
)
@api_view(['GET'])
def order_list(request):
    order = Order.objects.filter(user=request.user)
    serializer = OrderSerializer(order,many=True)
    return Response(serializer.data)

@extend_schema(
    responses={201: OrderSerializer},
    description='Checkout cart. Validates stock, creates order, reduces stock, and clears cart atomically.'
)
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

@extend_schema(
    responses={200: OrderSerializer},
    description='Get details of a specific order. Users can only see their own orders.'
)
@api_view(['GET'])
def order_detail(request,pk):
    try:
        order = Order.objects.get(pk=pk,user=request.user)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
    return Response(OrderSerializer(order).data)

@extend_schema(
    responses={200: OrderSerializer},
    description='Update order status. Admin only. Valid values: pending, checking, delivery, done.'
)
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