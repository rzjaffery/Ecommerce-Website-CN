from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('category/<slug:category_slug>/', views.product_list, name='category_detail'),
    path('product/<slug:product_slug>/', views.product_detail, name='product_detail'),
] 