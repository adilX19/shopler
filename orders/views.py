from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem, Payment
from .forms import ShippingAddressForm
from cart.models import Cart
from users.models import Address
from django.conf import settings
import time

@login_required
def checkout(request):
    """View for the checkout process"""
    try:
        cart = Cart.objects.get(user=request.user)
        if cart.items.count() == 0:
            messages.warning(request, 'Your cart is empty. Add some products before checking out.')
            return redirect('cart:cart_detail')
    except Cart.DoesNotExist:
        messages.warning(request, 'Your cart is empty. Add some products before checking out.')
        return redirect('cart:cart_detail')
    
    # Get user's addresses
    addresses = Address.objects.filter(user=request.user)
    default_address = addresses.filter(is_default=True).first()
    
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            shipping_address_id = form.cleaned_data.get('shipping_address')
            billing_address_id = form.cleaned_data.get('billing_address')
            payment_method = form.cleaned_data.get('payment_method')
            
            shipping_address = get_object_or_404(Address, id=shipping_address_id, user=request.user)
            billing_address = get_object_or_404(Address, id=billing_address_id, user=request.user)
            
            # Calculate totals
            cart_items = cart.items.all()
            total = sum(item.total_price for item in cart_items)
            shipping_amount = 10.00  # Example shipping fee
            tax_amount = total * 0.1  # Example tax calculation (10%)
            grand_total = total + shipping_amount + tax_amount
            
            # Create order
            order = Order.objects.create(
                user=request.user,
                shipping_address=shipping_address,
                billing_address=billing_address,
                total_amount=grand_total,
                shipping_amount=shipping_amount,
                tax_amount=tax_amount,
                payment_method=payment_method,
                status='pending'
            )
            
            # Create order items
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
            
            # Store order ID in session for payment process
            request.session['order_id'] = order.id
            
            # Clear cart
            cart.items.all().delete()
            
            # Redirect to payment page
            return redirect('orders:payment')
    else:
        form = ShippingAddressForm(initial={
            'shipping_address': default_address.id if default_address else None,
            'billing_address': default_address.id if default_address else None,
        })
    
    context = {
        'form': form,
        'addresses': addresses,
        'cart': cart,
        'cart_items': cart.items.all(),
    }
    return render(request, 'orders/checkout.html', context)

@login_required
def payment(request):
    """Payment processing page"""
    order_id = request.session.get('order_id')
    if not order_id:
        messages.error(request, 'Order not found.')
        return redirect('cart:cart_detail')
    
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if request.method == 'POST':
        # Simulate payment processing
        success = True  # In a real app, this would be determined by payment gateway response
        
        if success:
            # Create payment record
            Payment.objects.create(
                order=order,
                payment_id=f"PAY-{order.id}-{int(time.time())}",  # Generate a dummy payment ID
                amount=order.total_amount
            )
            
            # Update order status
            order.payment_status = 'completed'
            order.status = 'processing'
            order.save()
            
            # Clear session data
            if 'order_id' in request.session:
                del request.session['order_id']
            
            messages.success(request, 'Payment processed successfully!')
            return redirect('orders:order_confirmation', order_id=order.id)
        else:
            messages.error(request, 'Payment processing failed. Please try again.')
    
    context = {
        'order': order,
    }
    return render(request, 'orders/payment.html', context)

@login_required
def order_confirmation(request, order_id):
    """Order confirmation page after successful payment"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
        'items': order.items.all(),
    }
    return render(request, 'orders/order_confirmation.html', context)

@login_required
def order_history(request):
    """View to display user's order history"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'orders/order_history.html', context)

@login_required
def order_detail(request, order_id):
    """View to display detailed information about an order"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
        'items': order.items.all(),
    }
    return render(request, 'orders/order_detail.html', context)