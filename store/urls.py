from django.urls import path
from . import views

urlpatterns = [
    #Register URL
    path('auth/register/', views.register, name='register'),
    
    #Categories URL
    path('categories/', views.category_list, name='category_list'),
    path('categories/<int:pk>/', views.category_detail, name='category_detail'),
    
    #Product URL
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    
    #Cart URL
    path('cart/', views.get_cart, name='get_cart'),
    path('cart/add/<int:product_pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/items/<int:item_pk>/', views.update_cart_item, name='update_cart_item'),
    
    #Orders URL
    path('orders/', views.order_list, name='order_list'),
    path('orders/checkout/', views.checkout, name='checkout'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/<int:pk>/status/', views.update_order_status,name='update_order_status')
]
