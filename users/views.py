from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import Address
from .forms import (
    CustomUserCreationForm, 
    CustomAuthenticationForm, 
    UserProfileForm, 
    AddressForm
)

def login_view(request):
    if request.user.is_authenticated:
        return redirect('products:home')
        
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'products:home')
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect(next_url)
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'users/login.html', {'form': form})

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Account created successfully! Welcome, {user.username}!")
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'users/register.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('users:login')

@login_required
def profile(request):
    """View for user profile page"""
    context = {
        'user': request.user,
    }
    return render(request, 'users/profile.html', context)

@login_required
def edit_profile(request):
    """View to edit user profile information"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    context = {
        'form': form,
    }
    return render(request, 'users/edit_profile.html', context)

@login_required
def address_list(request):
    """View to display user's addresses"""
    addresses = Address.objects.filter(user=request.user)
    
    context = {
        'addresses': addresses,
    }
    return render(request, 'users/address_list.html', context)

@login_required
def add_address(request):
    """View to add a new address"""
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            
            # If this is set as default, unset any existing default
            if address.is_default:
                Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
            
            address.save()
            messages.success(request, 'Address added successfully!')
            return redirect('users:address_list')
    else:
        form = AddressForm()
    
    context = {
        'form': form,
        'title': 'Add Address',
    }
    return render(request, 'users/address_form.html', context)

@login_required
def edit_address(request, address_id):
    """View to edit an existing address"""
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            updated_address = form.save(commit=False)
            
            # If this is set as default, unset any existing default
            if updated_address.is_default:
                Address.objects.filter(user=request.user, is_default=True).exclude(id=address_id).update(is_default=False)
            
            updated_address.save()
            messages.success(request, 'Address updated successfully!')
            return redirect('users:address_list')
    else:
        form = AddressForm(instance=address)
    
    context = {
        'form': form,
        'title': 'Edit Address',
        'address': address,
    }
    return render(request, 'users/address_form.html', context)

@login_required
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
        address.delete()
        messages.success(request, 'Address deleted successfully!')
        return redirect('users:address_list')
    
    context = {
        'address': address,
    }
    return render(request, 'users/delete_address.html', context)

@login_required
def set_default_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    # Unset any existing default
    Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
    
    # Set the selected address as default
    address.is_default = True
    address.save()
    
    messages.success(request, f'"{address}" set as your default address.')
    return redirect('users:address_list')