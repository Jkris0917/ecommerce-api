# 🛒 E-commerce API

A production-grade RESTful API for e-commerce, built with Django and Django REST Framework. Features JWT authentication, role-based admin controls, cart management, and atomic checkout processing.

## ✨ Features

- **JWT Authentication** — Register, login, logout with refresh token rotation
- **Product Catalog** — Browse products by category, admin-only create/edit/delete
- **Cart System** — Add, update, remove items with stock validation
- **Atomic Checkout** — Stock verification, order creation, and cart clearing in a single transaction
- **Order Management** — Order history, order detail, admin-controlled status updates
- **API Documentation** — Auto-generated Swagger UI and ReDoc via drf-spectacular
- **PostgreSQL** backend with Docker support

## 🔗 Live API

**Base URL:** `coming soon`

**API Docs:** `coming soon`

## 📡 Endpoints

### Auth
| Method | URL | Description | Auth |
|--------|-----|-------------|------|
| POST | `/api/auth/register/` | Register and receive JWT tokens | Public |
| POST | `/api/auth/login/` | Login and receive JWT tokens | Public |
| POST | `/api/auth/logout/` | Blacklist refresh token | Required |
| POST | `/api/auth/refresh/` | Get new access token | Public |

### Categories
| Method | URL | Description | Auth |
|--------|-----|-------------|------|
| GET | `/api/categories/` | List all categories | Public |
| POST | `/api/categories/` | Create category | Admin only |
| GET | `/api/categories/<id>/` | Category detail | Public |
| PUT | `/api/categories/<id>/` | Update category | Admin only |
| DELETE | `/api/categories/<id>/` | Delete category | Admin only |

### Products
| Method | URL | Description | Auth |
|--------|-----|-------------|------|
| GET | `/api/products/` | List all products | Public |
| POST | `/api/products/` | Create product | Admin only |
| GET | `/api/products/<id>/` | Product detail | Public |
| PUT | `/api/products/<id>/` | Update product | Admin only |
| DELETE | `/api/products/<id>/` | Delete product | Admin only |

### Cart
| Method | URL | Description | Auth |
|--------|-----|-------------|------|
| GET | `/api/cart/` | Get my cart | Required |
| POST | `/api/cart/add/<product_id>/` | Add item to cart | Required |
| PUT | `/api/cart/items/<item_id>/` | Update item quantity | Required |
| DELETE | `/api/cart/items/<item_id>/` | Remove item from cart | Required |

### Orders
| Method | URL | Description | Auth |
|--------|-----|-------------|------|
| GET | `/api/orders/` | My order history | Required |
| POST | `/api/orders/checkout/` | Checkout cart | Required |
| GET | `/api/orders/<id>/` | Order detail | Required |
| PUT | `/api/orders/<id>/status/` | Update order status | Admin only |

## 🔐 Permissions

| Action | Public | Authenticated | Admin |
|--------|--------|---------------|-------|
| Browse products & categories | ✅ | ✅ | ✅ |
| Manage cart | ❌ | ✅ | ✅ |
| Checkout | ❌ | ✅ | ✅ |
| View own orders | ❌ | ✅ | ✅ |
| Create/edit/delete products | ❌ | ❌ | ✅ |
| Update order status | ❌ | ❌ | ✅ |

## 🛒 Checkout Flow

1. Add products to cart
2. POST to `/api/orders/checkout/`
3. API verifies stock availability for each item
4. Creates order and order items atomically
5. Reduces stock for each product
6. Clears the cart
7. Returns the created order

> All steps happen inside a database transaction — if anything fails, everything rolls back.

## 🛠 Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3.12 | Language |
| Django 6.0 | Web framework |
| Django REST Framework | API layer |
| djangorestframework-simplejwt | JWT authentication |
| drf-spectacular | OpenAPI 3.0 docs + Swagger UI |
| PostgreSQL | Database |
| Docker + Docker Compose | Containerization |

## ⚙️ Setup (Local)

```bash
git clone https://github.com/Jkris0917/ecommerce-api
cd ecommerce-api
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
```

Create a `.env` file:
```env
DB_NAME=ecommerce
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost 127.0.0.1
```

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## 🐳 Setup (Docker)

```bash
docker compose up --build
docker compose exec web python manage.py createsuperuser
```

## 🧪 Running Tests

```bash
pytest -v
```

## 📖 API Documentation

Start the server and visit:
- **Swagger UI:** `http://localhost:8000/api/docs/`
- **ReDoc:** `http://localhost:8000/api/redoc/`

## 💡 Example Usage

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "secure123", "email": "john@example.com"}'

# Browse products (no token needed)
curl http://localhost:8000/api/products/

# Add to cart
curl -X POST http://localhost:8000/api/cart/add/1/ \
  -H "Authorization: Bearer <access_token>"

# Checkout
curl -X POST http://localhost:8000/api/orders/checkout/ \
  -H "Authorization: Bearer <access_token>"
```

## 📚 What I Learned

- Atomic database transactions for multi-step operations
- Stock validation and race condition awareness at checkout
- Admin-restricted endpoints using `is_staff` checks
- Nested serializers for cart and order items
- `OneToOneField` for user-cart relationship
- `DecimalField` for accurate monetary values
- JWT authentication with refresh token rotation