from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem, WishList
from products.models import Product

def _get_or_create_cart(request):
    """Helper function to get or create a cart for a user or session"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        cart_id = request.session.get('cart_id')
        if cart_id:
            try:
                cart = Cart.objects.get(id=cart_id)
            except Cart.DoesNotExist:
                cart = Cart.objects.create(user=None)
                request.session['cart_id'] = cart.id
        else:
            cart = Cart.objects.create(user=None)
            request.session['cart_id'] = cart.id
    return cart

def cart_detail(request):
    """View to display the cart contents"""
    cart = _get_or_create_cart(request)
    
    context = {
        'cart': cart,
        'cart_items': cart.items.all(),
    }
    return render(request, 'cart/cart_detail.html', context)

def add_to_cart(request, product_id):
    """Add a product to the cart"""
    product = get_object_or_404(Product, id=product_id, is_available=True)
    cart = _get_or_create_cart(request.user)
    
    quantity = int(request.POST.get('quantity', 1))
    
    # Check if product is already in cart
    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        cart_item.quantity += quantity
        cart_item.save()
        messages.success(request, f'Updated {product.name} quantity in your cart.')
    except CartItem.DoesNotExist:
        CartItem.objects.create(cart=cart, product=product, quantity=quantity)
        messages.success(request, f'Added {product.name} to your cart.')
    
    return redirect('cart:cart_detail')

def remove_from_cart(request, item_id):
    """Remove an item from the cart"""
    cart_item = get_object_or_404(CartItem, id=item_id)
    
    # Check if user owns this cart item
    if request.user.is_authenticated and cart_item.cart.user != request.user:
        messages.error(request, 'You do not have permission to modify this cart.')
        return redirect('cart:cart_detail')
    
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'Removed {product_name} from your cart.')
    
    return redirect('cart:cart_detail')

def update_cart(request, item_id):
    """Update cart item quantity"""
    cart_item = get_object_or_404(CartItem, id=item_id)
    
    # Check if user owns this cart item
    if request.user.is_authenticated and cart_item.cart.user != request.user:
        messages.error(request, 'You do not have permission to modify this cart.')
        return redirect('cart:cart_detail')
    
    quantity = int(request.POST.get('quantity', 1))
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, f'Updated {cart_item.product.name} quantity.')
    else:
        product_name = cart_item.product.name
        cart_item.delete()
        messages.success(request, f'Removed {product_name} from your cart.')
    
    return redirect('cart:cart_detail')

@login_required
def wishlist(request):
    """View to display the user's wishlist"""
    wishlist, created = WishList.objects.get_or_create(user=request.user)
    
    context = {
        'wishlist': wishlist,
        'products': wishlist.products.all(),
    }
    return render(request, 'cart/wishlist.html', context)

@login_required
def add_to_wishlist(request, product_id):
    """Add a product to the wishlist"""
    product = get_object_or_404(Product, id=product_id, is_available=True)
    wishlist, created = WishList.objects.get_or_create(user=request.user)
    
    if product in wishlist.products.all():
        messages.info(request, f'{product.name} is already in your wishlist.')
    else:
        wishlist.products.add(product)
        messages.success(request, f'Added {product.name} to your wishlist.')
    
    return redirect('products:product_detail', product_slug=product.slug)

@login_required
def remove_from_wishlist(request, product_id):
    """Remove a product from the wishlist"""
    product = get_object_or_404(Product, id=product_id)
    wishlist = get_object_or_404(WishList, user=request.user)
    
    if product in wishlist.products.all():
        wishlist.products.remove(product)
        messages.success(request, f'Removed {product.name} from your wishlist.')
    
    return redirect('cart:wishlist')
