from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Category, Product
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache
from django.conf import settings
import hashlib

def home(request):
    categories = Category.objects.all()
    featured_products = Product.objects.filter(available=True)[:8]
    
    context = {
        'categories': categories,
        'featured_products': featured_products
    }
    return render(request, 'products/home.html', context)

# Cache key generator
def make_cache_key(request, *args, **kwargs):
    # Create a cache key based on the full URL
    url = request.build_absolute_uri()
    user_id = request.user.id if request.user.is_authenticated else 'anonymous'
    cache_key = f'view:{hashlib.md5(f"{url}:{user_id}".encode()).hexdigest()}'
    return cache_key

# Cache time in seconds
CACHE_TTL = getattr(settings, 'CACHE_TIMEOUT', 900)  # 15 minutes default

@cache_page(CACHE_TTL)
def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    paginator = Paginator(products, 12)  # Show 12 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    search_query = request.GET.get('q', None)
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    return render(request, 'products/product_list.html', {
        'category': category,
        'categories': categories,
        'page_obj': page_obj,
        'search_query': search_query
    })

def product_detail(request, id, slug):
    # Try to get product from cache first
    cache_key = f'product:{id}:{slug}'
    product = cache.get(cache_key)
    
    if not product:
        # If not in cache, fetch from database
        product = get_object_or_404(Product, id=id, slug=slug, available=True)
        # Store in cache for future requests
        cache.set(cache_key, product, CACHE_TTL)
    
    # Get related products from the same category (cached)
    related_key = f'related_products:{product.category.id}:{product.id}'
    related_products = cache.get(related_key)
    
    if not related_products:
        related_products = Product.objects.filter(
            category=product.category, 
            available=True
        ).exclude(id=product.id)[:4]
        cache.set(related_key, related_products, CACHE_TTL)
    
    return render(request, 'products/product_detail.html', {
        'product': product,
        'related_products': related_products
    })
