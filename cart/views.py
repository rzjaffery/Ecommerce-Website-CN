from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from products.models import Product
from .models import Cart, CartItem, Order, OrderItem
from .forms import OrderForm
from django.urls import reverse
from django.core.cache import cache
from django.conf import settings

# Cache time in seconds
CACHE_TTL = getattr(settings, 'CACHE_TIMEOUT', 900)  # 15 minutes default

# Modified to redirect unauthenticated users to login page with proper next parameter
def cart_detail(request):
    if not request.user.is_authenticated:
        return redirect(f"{reverse('login')}?next={request.path}")
    
    # Cache key specific to this user's cart
    cache_key = f'cart_detail:{request.user.id}'
    
    # Try to get cart data from cache
    cached_data = cache.get(cache_key)
    if cached_data:
        return render(request, 'cart/cart_detail.html', cached_data)
    
    # If not in cache, fetch from database
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    
    context = {
        'cart': cart,
        'cart_items': cart_items
    }
    
    # Cache the cart data (short TTL since cart data changes frequently)
    cache.set(cache_key, context, CACHE_TTL // 6)  # 2.5 minutes
    
    return render(request, 'cart/cart_detail.html', context)

# Modified to redirect unauthenticated users to login page with proper next parameter
def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        next_url = reverse('add_to_cart', args=[product_id])
        return redirect(f"{reverse('login')}?next={next_url}")
    
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        CartItem.objects.create(cart=cart, product=product)
    
    messages.success(request, f"{product.name} added to your cart!")
    return redirect('cart_detail')

def remove_from_cart(request, item_id):
    if not request.user.is_authenticated:
        return redirect(f"{reverse('login')}?next={request.path}")
    
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    
    messages.success(request, "Item removed from your cart!")
    return redirect('cart_detail')

def update_cart(request, item_id):
    if not request.user.is_authenticated:
        return redirect(f"{reverse('login')}?next={request.path}")
    
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
    except ValueError:
        pass
    
    return redirect('cart_detail')

def checkout(request):
    if not request.user.is_authenticated:
        return redirect(f"{reverse('login')}?next={request.path}")
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    
    if not cart_items:
        messages.warning(request, "Your cart is empty!")
        return redirect('cart_detail')
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            
            # Create order items from cart items
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    price=item.product.price,
                    quantity=item.quantity
                )
            
            # Clear the cart
            cart_items.delete()
            
            messages.success(request, "Your order has been placed successfully!")
            return redirect('order_confirmation', order_id=order.id)
    else:
        # Pre-fill the form with user's profile information if available
        initial_data = {}
        if hasattr(request.user, 'profile'):
            initial_data['address'] = request.user.profile.address
            if hasattr(request.user.profile, 'postal_code'):
                initial_data['postal_code'] = request.user.profile.postal_code
            if hasattr(request.user.profile, 'city'):
                initial_data['city'] = request.user.profile.city
        
        if request.user.email:
            initial_data['email'] = request.user.email
        
        if request.user.first_name:
            initial_data['first_name'] = request.user.first_name
            
        if request.user.last_name:
            initial_data['last_name'] = request.user.last_name
            
        form = OrderForm(initial=initial_data)
    
    context = {
        'form': form,
        'cart': cart,
        'cart_items': cart_items
    }
    return render(request, 'cart/checkout.html', context)

def order_confirmation(request, order_id):
    if not request.user.is_authenticated:
        return redirect(f"{reverse('login')}?next={request.path}")
    
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order
    }
    return render(request, 'cart/order_confirmation.html', context)
