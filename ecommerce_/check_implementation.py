#!/usr/bin/env python
"""
Implementation Verification Script

This script checks if all the required features have been properly implemented.
"""

import os
import sys
import importlib
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

def check_ssl_configuration():
    """Check if SSL/TLS configuration is set up correctly"""
    print("\n=== SSL/TLS Configuration ===")
    
    # Check if SSL settings exist in settings.py
    secure_proxy_header = hasattr(settings, 'SECURE_PROXY_SSL_HEADER')
    has_ssl_redirect = hasattr(settings, 'SECURE_SSL_REDIRECT')
    has_secure_cookies = hasattr(settings, 'SESSION_COOKIE_SECURE') and hasattr(settings, 'CSRF_COOKIE_SECURE')
    
    print(f" - Proxy SSL header configured: {'Yes' if secure_proxy_header else 'No'}")
    print(f" - SSL redirect configured: {'Yes' if has_ssl_redirect else 'No'}")
    print(f" - Secure cookies configured: {'Yes' if has_secure_cookies else 'No'}")
    
    # Check if certificate files exist
    cert_exists = os.path.exists('certificates/dev-cert.pem')
    key_exists = os.path.exists('certificates/dev-key.pem')
    
    print(f" - SSL certificates exist: {'Yes' if cert_exists and key_exists else 'No'}")
    
    # Check if HTTPS script exists
    https_script = os.path.exists('start_https_server.bat')
    print(f" - HTTPS startup script exists: {'Yes' if https_script else 'No'}")
    
    # Overall assessment
    if all([secure_proxy_header, has_ssl_redirect, has_secure_cookies, https_script]):
        print(" [PASS] SSL/TLS configuration is properly set up")
    else:
        print(" [PARTIAL] SSL/TLS configuration is incomplete")

def check_oauth_configuration():
    """Check if OAuth/JWT configuration is set up correctly"""
    print("\n=== OAuth/JWT Configuration ===")
    
    # Check if django-allauth is installed
    try:
        import allauth
        allauth_installed = True
    except ImportError:
        allauth_installed = False
    
    # Check if allauth is in INSTALLED_APPS
    has_allauth_apps = False
    if hasattr(settings, 'INSTALLED_APPS'):
        has_allauth_apps = all(app in settings.INSTALLED_APPS for app in [
            'allauth',
            'allauth.account',
            'allauth.socialaccount',
        ])
    
    # Check if JWT is set up
    has_jwt_config = False
    if hasattr(settings, 'SIMPLE_JWT'):
        has_jwt_config = all(key in settings.SIMPLE_JWT for key in [
            'ACCESS_TOKEN_LIFETIME',
            'REFRESH_TOKEN_LIFETIME',
            'ALGORITHM',
        ])
    
    print(f" - django-allauth installed: {'Yes' if allauth_installed else 'No'}")
    print(f" - Allauth apps configured: {'Yes' if has_allauth_apps else 'No'}")
    print(f" - JWT configuration set up: {'Yes' if has_jwt_config else 'No'}")
    
    # Check if URLs are configured
    from django.urls import get_resolver
    resolver = get_resolver()
    has_allauth_urls = 'accounts' in [p.pattern.name for p in resolver.url_patterns if hasattr(p.pattern, 'name') and p.pattern.name]
    
    print(f" - Allauth URLs configured: {'Yes' if has_allauth_urls else 'No'}")
    
    # Overall assessment
    if all([allauth_installed, has_allauth_apps, has_jwt_config, has_allauth_urls]):
        print(" [PASS] OAuth/JWT configuration is properly set up")
    else:
        print(" [PARTIAL] OAuth/JWT configuration is incomplete")

def check_load_balancing():
    """Check if load balancing configuration is set up correctly"""
    print("\n=== Load Balancing Configuration ===")
    
    # Check if NGINX configuration exists
    nginx_conf = os.path.exists('nginx/nginx.conf')
    nginx_win_conf = os.path.exists('nginx/nginx.windows.conf')
    
    print(f" - NGINX configuration exists: {'Yes' if nginx_conf else 'No'}")
    print(f" - Windows NGINX configuration exists: {'Yes' if nginx_win_conf else 'No'}")
    
    # Check if Docker configuration exists
    docker_compose = os.path.exists('docker-compose.yml')
    dockerfile = os.path.exists('Dockerfile')
    
    print(f" - Docker Compose configuration exists: {'Yes' if docker_compose else 'No'}")
    print(f" - Dockerfile exists: {'Yes' if dockerfile else 'No'}")
    
    # Check if multi-instance script exists
    multi_instance = os.path.exists('start_multi_instance.bat')
    print(f" - Multi-instance startup script exists: {'Yes' if multi_instance else 'No'}")
    
    # Overall assessment
    if all([nginx_conf, docker_compose, dockerfile, multi_instance]):
        print(" [PASS] Load balancing configuration is properly set up")
    else:
        print(" [PARTIAL] Load balancing configuration is incomplete")

def check_database_optimization():
    """Check if database optimization is set up correctly"""
    print("\n=== Database Optimization ===")
    
    # Check if models have indexes defined
    from django.apps import apps
    
    models_with_indexes = 0
    total_indexes = 0
    total_models = 0
    
    for model in apps.get_models():
        total_models += 1
        has_indexes = hasattr(model._meta, 'indexes') and len(model._meta.indexes) > 0
        if has_indexes:
            models_with_indexes += 1
            total_indexes += len(model._meta.indexes)
    
    print(f" - Models with indexes: {models_with_indexes}/{total_models}")
    print(f" - Total indexes defined: {total_indexes}")
    
    # Check if index management script exists
    index_script = os.path.exists('manage_indexes.py')
    print(f" - Index management script exists: {'Yes' if index_script else 'No'}")
    
    # Overall assessment
    if models_with_indexes >= 3 and total_indexes >= 10 and index_script:
        print(" [PASS] Database indexing is properly set up")
    else:
        print(" [PARTIAL] Database indexing is incomplete")

def check_caching():
    """Check if caching is set up correctly"""
    print("\n=== Caching Configuration ===")
    
    # Check if Redis cache is configured
    has_redis_cache = False
    if hasattr(settings, 'CACHES') and 'default' in settings.CACHES:
        has_redis_cache = 'RedisCache' in settings.CACHES['default'].get('BACKEND', '')
    
    print(f" - Redis cache backend configured: {'Yes' if has_redis_cache else 'No'}")
    
    # Check if SESSION_ENGINE uses cache
    uses_cache_sessions = hasattr(settings, 'SESSION_ENGINE') and 'cache' in settings.SESSION_ENGINE
    print(f" - Cache-based sessions configured: {'Yes' if uses_cache_sessions else 'No'}")
    
    # Check for cache decorators in view code
    cache_use_in_views = 0
    
    from django.views.decorators.cache import cache_page
    
    # Check products views
    try:
        import products.views
        if hasattr(products.views, 'cache_page') or '@cache_page' in open('products/views.py').read():
            cache_use_in_views += 1
    except (ImportError, FileNotFoundError):
        pass
    
    # Check cart views
    try:
        import cart.views
        if 'cache.get' in open('cart/views.py').read() or 'cache.set' in open('cart/views.py').read():
            cache_use_in_views += 1
    except (ImportError, FileNotFoundError):
        pass
    
    # Check chat views
    try:
        import chat.views
        if 'cache.get' in open('chat/views.py').read() or 'cache.set' in open('chat/views.py').read():
            cache_use_in_views += 1
    except (ImportError, FileNotFoundError):
        pass
    
    print(f" - Views using caching: {cache_use_in_views}/3")
    
    # Overall assessment
    if has_redis_cache and uses_cache_sessions and cache_use_in_views >= 2:
        print(" [PASS] Caching is properly configured")
    else:
        print(" [PARTIAL] Caching configuration is incomplete")

def main():
    """Main function to run all checks"""
    print("E-commerce Project Implementation Verification")
    print("==============================================")
    
    check_ssl_configuration()
    check_oauth_configuration()
    check_load_balancing()
    check_database_optimization()
    check_caching()
    
    print("\nVerification complete.")

if __name__ == "__main__":
    main() 