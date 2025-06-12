from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/<int:pk>/add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/update/<int:pk>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order/<int:order_id>/confirmation/', views.order_confirmation, name='order_confirmation'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('order/<int:order_id>/tracking/', views.order_tracking, name='order_tracking'),
    path('order/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    
    # Admin URLs
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/orders/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
    path('admin-dashboard/products/', views.manage_products, name='manage_products'),
    path('admin-dashboard/products/add/', views.add_product, name='add_product'),
] 