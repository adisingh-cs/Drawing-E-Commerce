from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.mail import send_mail
from django.conf import settings
from .models import Product, Order, UserProfile, OrderStatusUpdate
from decimal import Decimal
from django.db import models
from django.db.models import Avg, Count
from django.core.paginator import Paginator

def is_staff(user):
    return user.is_staff

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'store/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

def home(request):
    products = Product.objects.all()
    return render(request, 'store/home.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'store/product_detail.html', {'product': product})

@login_required
def add_to_cart(request, pk):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=pk)
        quantity = int(request.POST.get('quantity', 1))
        
        # Validate stock
        if quantity > product.stock:
            messages.error(request, f'Sorry, only {product.stock} units available in stock.')
            return redirect('product_detail', pk=pk)
        
        cart = request.session.get('cart', {})
        product_id = str(pk)
        
        if product_id in cart:
            # Update quantity if product already in cart
            new_quantity = cart[product_id]['quantity'] + quantity
            if new_quantity > product.stock:
                messages.error(request, f'Sorry, only {product.stock} units available in stock.')
                return redirect('product_detail', pk=pk)
            cart[product_id]['quantity'] = new_quantity
        else:
            # Add new product to cart
            cart[product_id] = {
                'title': product.title,
                'price': str(product.price),
                'quantity': quantity,
                'image_url': product.image_url
            }
        
        request.session['cart'] = cart
        messages.success(request, f'{product.title} added to cart!')
    return redirect('product_detail', pk=pk)

def view_cart(request):
    cart = request.session.get('cart', {})
    total = sum(Decimal(item['price']) * item['quantity'] for item in cart.values())
    return render(request, 'store/cart.html', {'cart': cart, 'total': total})

def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, 'Your cart is empty!')
        return redirect('view_cart')

    total = sum(Decimal(item['price']) * item['quantity'] for item in cart.values())

    if request.method == 'POST':
        # Get or create user profile if user is authenticated
        if request.user.is_authenticated:
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            customer_name = request.user.get_full_name() or request.user.username
            customer_email = request.user.email
            customer_phone = profile.phone or request.POST['customer_phone']
            shipping_address = profile.address or request.POST['shipping_address']
        else:
            customer_name = request.POST['customer_name']
            customer_email = request.POST['customer_email']
            customer_phone = request.POST['customer_phone']
            shipping_address = request.POST['shipping_address']

        # Create order
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            shipping_address=shipping_address,
            product_id=list(cart.keys())[0],  # For MVP, we'll only handle one product per order
            quantity=cart[list(cart.keys())[0]]['quantity'],
            total_amount=total
        )

        # Create initial status update
        OrderStatusUpdate.objects.create(
            order=order,
            status='pending',
            notes='Order placed successfully'
        )

        # Clear cart
        request.session['cart'] = {}
        messages.success(request, 'Order placed successfully! We will contact you for payment confirmation.')
        return redirect('order_confirmation', order_id=order.id)

    # Pre-fill form with user data if authenticated
    initial_data = {}
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
            initial_data = {
                'customer_name': request.user.get_full_name() or request.user.username,
                'customer_email': request.user.email,
                'customer_phone': profile.phone,
                'shipping_address': profile.address
            }
        except UserProfile.DoesNotExist:
            pass

    return render(request, 'store/checkout.html', {
        'cart': cart,
        'total': total,
        'initial_data': initial_data
    })

def order_confirmation(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, 'store/order_confirmation.html', {'order': order})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'store/register.html', {'form': form})

@login_required
def profile(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        profile.phone = request.POST.get('phone')
        profile.address = request.POST.get('address')
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')

    context = {
        'profile': profile,
        'orders': user_orders,
    }
    return render(request, 'store/profile.html', context)

@login_required
def order_tracking(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if order.user != request.user:
        messages.error(request, 'You do not have permission to view this order.')
        return redirect('profile')
    
    status_updates = order.status_updates.all().order_by('-created_at')
    return render(request, 'store/order_tracking.html', {
        'order': order,
        'status_updates': status_updates
    })

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if order.user != request.user:
        messages.error(request, 'You do not have permission to cancel this order.')
        return redirect('profile')
    
    if order.status in ['pending', 'processing']:
        order.status = 'cancelled'
        order.save()
        OrderStatusUpdate.objects.create(
            order=order,
            status='cancelled',
            notes='Order cancelled by customer'
        )
        messages.success(request, 'Order cancelled successfully.')
    else:
        messages.error(request, 'This order cannot be cancelled.')
    
    return redirect('order_tracking', order_id=order_id)

@login_required
@user_passes_test(is_staff)
def admin_dashboard(request):
    try:
        # Sales analytics - only count delivered orders
        total_sales = Order.objects.filter(status='delivered').aggregate(total=models.Sum('total_amount'))['total'] or 0
        monthly_sales = Order.objects.filter(status='delivered').values('created_at__year', 'created_at__month').annotate(
            total=models.Sum('total_amount')
        ).order_by('created_at__year', 'created_at__month')
        
        # Product analytics
        total_drawings = Product.objects.count()
        low_stock_products = Product.objects.filter(stock__lte=5)
        recent_products = Product.objects.order_by('-created_at')[:5]
        
        # Paginate products
        products = Product.objects.all().order_by('-created_at')
        products_paginator = Paginator(products, 10)  # Show 10 products per page
        products_page = request.GET.get('products_page')
        products = products_paginator.get_page(products_page)
        
        # Order analytics
        total_orders = Order.objects.count()
        recent_orders = Order.objects.order_by('-created_at')[:5]
        
        # Paginate orders
        orders = Order.objects.all().order_by('-created_at')
        orders_paginator = Paginator(orders, 10)  # Show 10 orders per page
        orders_page = request.GET.get('orders_page')
        orders = orders_paginator.get_page(orders_page)
        
        order_status_counts = Order.objects.values('status').annotate(count=Count('id'))
        
        # User analytics
        total_users = User.objects.count()
        recent_users = User.objects.order_by('-date_joined')[:5]
        
        # Paginate users
        users = User.objects.all().order_by('-date_joined')
        users_paginator = Paginator(users, 10)  # Show 10 users per page
        users_page = request.GET.get('users_page')
        users = users_paginator.get_page(users_page)
        
        context = {
            'total_sales': total_sales,
            'monthly_sales': monthly_sales,
            'total_drawings': total_drawings,
            'low_stock_products': low_stock_products,
            'recent_products': recent_products,
            'products': products,
            'total_orders': total_orders,
            'recent_orders': recent_orders,
            'orders': orders,
            'order_status_counts': order_status_counts,
            'total_users': total_users,
            'recent_users': recent_users,
            'users': users,
            'order_status_choices': Order.STATUS_CHOICES,
        }
        return render(request, 'store/admin_dashboard.html', context)
    except Exception as e:
        messages.error(request, f'Error loading admin dashboard: {str(e)}')
        return redirect('home')

@login_required
@user_passes_test(is_staff)
def order_list(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'store/order_list.html', {'orders': orders})

@login_required
@user_passes_test(is_staff)
def update_order_status(request, order_id):
    try:
        order = get_object_or_404(Order, pk=order_id)
        if request.method == 'POST':
            new_status = request.POST.get('status')
            if not new_status:
                messages.error(request, 'Status cannot be empty.')
                return redirect('admin_dashboard')
                
            if new_status not in dict(Order.STATUS_CHOICES):
                messages.error(request, 'Invalid status selected.')
                return redirect('admin_dashboard')
                
            # Check if the status transition is valid
            current_status = order.status
            if new_status == current_status:
                messages.warning(request, f'Order #{order.id} is already in {current_status} status.')
                return redirect('admin_dashboard')
            
            order.status = new_status
            order.save()
            
            OrderStatusUpdate.objects.create(
                order=order,
                status=new_status,
                notes=f'Status updated from {current_status} to {new_status}'
            )
            
            messages.success(request, f'Order #{order.id} status updated to {new_status}.')
        return redirect('admin_dashboard')
    except Exception as e:
        messages.error(request, f'Error updating order status: {str(e)}')
        return redirect('admin_dashboard')

@login_required
def manage_inventory(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    products = Product.objects.all().order_by('-created_at')
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        new_stock = request.POST.get('stock')
        
        product = get_object_or_404(Product, id=product_id)
        product.stock = new_stock
        product.save()
        
        messages.success(request, f'Stock updated for {product.title}')
        return redirect('manage_inventory')
    
    return render(request, 'store/manage_inventory.html', {'products': products})

def update_cart(request, pk):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=pk)
        quantity = int(request.POST.get('quantity', 1))
        
        # Validate stock
        if quantity > product.stock:
            messages.error(request, f'Sorry, only {product.stock} units available in stock.')
            return redirect('view_cart')
        
        cart = request.session.get('cart', {})
        product_id = str(pk)
        
        if product_id in cart:
            cart[product_id]['quantity'] = quantity
            request.session['cart'] = cart
            messages.success(request, f'Cart updated successfully!')
    
    return redirect('view_cart')

def remove_from_cart(request, pk):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        product_id = str(pk)
        
        if product_id in cart:
            del cart[product_id]
            request.session['cart'] = cart
            messages.success(request, 'Item removed from cart!')
    
    return redirect('view_cart')

@login_required
@user_passes_test(is_staff)
def manage_products(request):
    try:
        products = Product.objects.all().order_by('-created_at')
        
        if request.method == 'POST':
            action = request.POST.get('action')
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, id=product_id)
            
            if action == 'update':
                # Validate input data
                title = request.POST.get('title', '').strip()
                description = request.POST.get('description', '').strip()
                price = request.POST.get('price')
                stock = request.POST.get('stock')
                image_url = request.POST.get('image_url', '').strip()
                
                if not title:
                    messages.error(request, 'Title cannot be empty.')
                    return redirect('admin_dashboard')
                
                try:
                    price = float(price)
                    if price <= 0:
                        raise ValueError
                except (ValueError, TypeError):
                    messages.error(request, 'Price must be a positive number.')
                    return redirect('admin_dashboard')
                
                try:
                    stock = int(stock)
                    if stock < 0:
                        raise ValueError
                except (ValueError, TypeError):
                    messages.error(request, 'Stock must be a non-negative number.')
                    return redirect('admin_dashboard')
                
                product.title = title
                product.description = description
                product.price = price
                product.stock = stock
                product.image_url = image_url
                product.save()
                messages.success(request, f'Product {product.title} updated successfully!')
            elif action == 'delete':
                product.delete()
                messages.success(request, f'Product {product.title} deleted successfully!')
            
            return redirect('admin_dashboard')
        
        return render(request, 'store/admin_dashboard.html', {'products': products})
    except Exception as e:
        messages.error(request, f'Error managing products: {str(e)}')
        return redirect('admin_dashboard')

@login_required
@user_passes_test(is_staff)
def add_product(request):
    try:
        if request.method == 'POST':
            # Validate input data
            title = request.POST.get('title', '').strip()
            description = request.POST.get('description', '').strip()
            price = request.POST.get('price')
            stock = request.POST.get('stock')
            image_url = request.POST.get('image_url', '').strip()
            
            if not title:
                messages.error(request, 'Title cannot be empty.')
                return redirect('admin_dashboard')
            
            try:
                price = float(price)
                if price <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                messages.error(request, 'Price must be a positive number.')
                return redirect('admin_dashboard')
            
            try:
                stock = int(stock)
                if stock < 0:
                    raise ValueError
            except (ValueError, TypeError):
                messages.error(request, 'Stock must be a non-negative number.')
                return redirect('admin_dashboard')
            
            Product.objects.create(
                title=title,
                description=description,
                price=price,
                stock=stock,
                image_url=image_url
            )
            
            messages.success(request, 'Product added successfully!')
            return redirect('admin_dashboard')
        
        return render(request, 'store/admin_dashboard.html')
    except Exception as e:
        messages.error(request, f'Error adding product: {str(e)}')
        return redirect('admin_dashboard')
