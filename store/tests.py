import pytest
from django.contrib.auth.models import User
from .models import Category, Product,Cart,CartItem, Order, OrderItem
from decimal import Decimal


def create_category(name='Test Category'):
    return Category.objects.create(name = name)

def create_product(category, name= 'Test Product',price ='10.00', stock=10):
    return Product.objects.create(
        name = name,
        price = Decimal(price),
        stock = stock,
        category = category
    )
    
# ─── Auth Tests ────────────────────────────────────────
@pytest.mark.django_db
def test_register_returns_tokens(api_client):
    response = api_client.post("/api/auth/register/",{
        "username" : "testuser",
        "password" : "testpass123",
        "email" : "test@email.com"
    })
    assert response.status_code == 201
    assert 'access' in response.data
    assert 'refresh' in response.data

@pytest.mark.django_db
def test_login_returns_tokens(api_client, create_user):
    create_user()
    response = api_client.post("/api/auth/login/",{
        "username": "testuser",
        "password": "testpass123"
    })
    assert response.status_code == 200
    assert 'access' in response.data

# ─── Product Tests ─────────────────────────────────────
@pytest.mark.django_db
def test_anyone_can_list_products(api_client):
    response = api_client.get('/api/products/')
    assert response.status_code == 200

@pytest.mark.django_db
def test_admin_can_create_product(admin_client):
    client, admin = admin_client  # ← unpack here
    category = create_category()
    response = client.post("/api/products/", {
        "name": "Test Product",
        "price": "10.00",
        "stock": 10,
        "category_id": category.id
    }, format='json')
    assert response.status_code == 201

@pytest.mark.django_db
def test_non_admin_cannot_create_product(auth_client):
    client, user = auth_client
    category = create_category()
    response = client.post("/api/products/",{
        "name": "Test Product",
        "price": "10.00",
        "stock" : 10,
        "category_id":category.id,
    },format='json')
    assert response.status_code == 403

# ─── Cart Tests ────────────────────────────────────────
@pytest.mark.django_db
def test_get_cart_creates_if_not_exists(auth_client):
    client, user = auth_client
    response = client.get("/api/cart/")
    assert response.status_code == 200
    assert Cart.objects.filter(user=user).exists()

@pytest.mark.django_db
def test_add_product_to_cart(auth_client):
    client, user = auth_client
    category = create_category()
    product = create_product(category)
    response = client.post(f"/api/cart/add/{product.id}/")
    assert response.status_code == 201
    assert CartItem.objects.filter(product=product).exists()

@pytest.mark.django_db
def test_add_same_product_increases_quantity(auth_client):
    client, user = auth_client
    category = create_category()
    product = create_product(category)
    client.post(f"/api/cart/add/{product.id}/")
    client.post(f"/api/cart/add/{product.id}/")
    cart_item = CartItem.objects.get(cart__user=user, product=product)
    assert cart_item.quantity == 2
    

@pytest.mark.django_db
def test_cannot_add_out_of_stock_product(auth_client):
    client, user = auth_client
    category = create_category()
    product = create_product(category, stock=0)
    response = client.post(f"/api/cart/add/{product.id}/")
    assert response.status_code == 400

# ─── Checkout Tests ────────────────────────────────────
@pytest.mark.django_db
def test_checkout_creates_order(auth_client):
    client, user = auth_client
    category = create_category()
    product = create_product(category)
    cart, _ = Cart.objects.get_or_create(user=user)
    CartItem.objects.create(cart=cart, product=product, quantity=1)
    response = client.post("/api/orders/checkout/")
    assert response.status_code == 201
    assert Order.objects.filter(user=user).exists()

@pytest.mark.django_db
def test_checkout_reduces_stock(auth_client):
    client, user = auth_client
    category = create_category()
    product = create_product(category)
    cart, _ = Cart.objects.get_or_create(user=user)
    CartItem.objects.create(cart=cart, product=product, quantity=1)
    initial_stock = product.stock
    response = client.post("/api/orders/checkout/")
    assert response.status_code == 201
    product.refresh_from_db()
    assert product.stock == 9

@pytest.mark.django_db
def test_checkout_clears_cart(auth_client):
    client, user = auth_client
    category = create_category()
    product = create_product(category)
    cart, _ = Cart.objects.get_or_create(user=user)
    CartItem.objects.create(cart=cart, product=product, quantity=1)
    response = client.post("/api/orders/checkout/")
    assert response.status_code == 201
    assert not CartItem.objects.filter(cart__user=user).exists()

@pytest.mark.django_db
def test_checkout_fails_if_cart_empty(auth_client):
    client, user = auth_client
    response = client.post("/api/orders/checkout/")
    assert response.status_code == 400

@pytest.mark.django_db
def test_checkout_fails_if_insufficient_stock(auth_client):
    client, user = auth_client
    category = create_category()
    product = create_product(category, stock=1)  
    cart, _ = Cart.objects.get_or_create(user=user)
    CartItem.objects.create(cart=cart, product=product, quantity=5)  
    response = client.post("/api/orders/checkout/")
    assert response.status_code == 400

# ─── Order Tests ───────────────────────────────────────
@pytest.mark.django_db
def test_user_can_see_own_orders(auth_client):
    client, user = auth_client
    category = create_category()
    product = create_product(category)
    cart, _ = Cart.objects.get_or_create(user=user)
    CartItem.objects.create(cart=cart, product=product, quantity=1)
    client.post("/api/orders/checkout/")

    response = client.get("/api/orders/")
    assert response.status_code == 200
    assert len(response.data) == 1

@pytest.mark.django_db
def test_admin_can_update_order_status(admin_client, create_user):
    client, admin = admin_client

    user = create_user(username='buyer', password='buyerpass123')
    category = create_category()
    product = create_product(category)
    cart, _ = Cart.objects.get_or_create(user=user)
    CartItem.objects.create(cart=cart, product=product, quantity=1)
    order = Order.objects.create(user=user, total_price=Decimal('10.00'))

    response = client.put(f"/api/orders/{order.id}/status/", {
        "status": "checking"
    }, format='json')
    assert response.status_code == 200
    order.refresh_from_db()
    assert order.status == 'checking'
