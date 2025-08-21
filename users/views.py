from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import UserProfile
from .forms import UserProfileForm

# Create your views here.

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def custom_logout(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')

@login_required
def profile(request):
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, instance=request.user.profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        profile_form = UserProfileForm(instance=request.user.profile)
    
    # Get order history
    orders = request.user.order_set.all().order_by('-created_at')
    
    context = {
        'profile_form': profile_form,
        'orders': orders
    }
    return render(request, 'users/profile.html', context)

def social_login(request):
    """Display social login options page"""
    return render(request, 'users/social_login.html')

def provider_login(request, provider):
    """Handle redirect to provider OAuth login"""
    if provider == 'google':
        return redirect('/accounts/google/login/')
    elif provider == 'facebook':
        return redirect('/accounts/facebook/login/')
    return redirect('login')
