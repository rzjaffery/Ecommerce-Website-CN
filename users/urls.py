from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    
    # Social login URLs
    path('social-login/', views.social_login, name='social_login'),
    path('social-login/<str:provider>/', views.provider_login, name='socialaccount_login'),
] 