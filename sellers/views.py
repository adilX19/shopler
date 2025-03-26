from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from .models import SellerProfile
from products.models import Product, ProductImage
from orders.models import Order, OrderItem
from .forms import SellerProfileForm
from products.forms import ProductForm

def seller_required(view_func):
    """Decorator to ensure user is a seller"""
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.user_type != 'seller':
            messages.error(request, 'You need a seller account to access this page.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@seller_required
def seller_dashboard(request):
    """Seller dashboard with overview of products, orders, and analytics"""
    # Get seller profile
    seller_profile, created = SellerProfile.objects.get_or_create(
        user=request.user,
        defaults={'company_name': request.user.username + "'s Store"}
    )
    
    # Get seller's products
    products = Product.objects.filter(seller=request.user)
    
    # Get recent orders for seller's products
    order_items = OrderItem.objects.filter(
        product__seller=request.user
    ).select_related('order', 'product').order_by('-order__created_at')[:10]
    
    # Basic analytics
    total_products = products.count()
    active_products = products.filter(is_available=True).count()
    out_of_stock = products.filter(stock=0).count()
    total_orders = OrderItem.objects.filter(product__seller=request.user).values('order').distinct().count()
    
    # Sales data
    total_sales = OrderItem.objects.filter(
        product__seller=request.user,
        order__payment_status='completed'
    ).aggregate(total=Sum('price'))['total'] or 0
    
    context = {
        'seller_profile': seller_profile,
        'total_products': total_products,
        'active_products': active_products,
        'out_of_stock': out_of_stock,
        'total_orders': total_orders,
        'total_sales': total_sales,
        'recent_orders': order_items,
    }
    return render(request, 'sellers/dashboard.html', context)

@seller_required
def seller_products(request):
    """View to display seller's products"""
    products = Product.objects.filter(seller=request.user).order_by('-created_at')
    
    context = {
        'products': products,
    }
    return render(request, 'sellers/products.html', context)

@seller_required
def add_product(request):
    """View to add a new product"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            
            # Handle product images
            images = request.FILES.getlist('images')
            for i, image in enumerate(images):
                ProductImage.objects.create(
                    product=product,
                    image=image,
                    is_primary=(i == 0)  # First image is primary
                )
            
            messages.success(request, 'Product added successfully!')
            return redirect('sellers:products')
    else:
        form = ProductForm()
    
    context = {
        'form': form,
        'title': 'Add Product',
    }
    return render(request, 'sellers/product_form.html', context)

@seller_required
def edit_product(request, product_id):
    """View to edit an existing product"""
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            
            # Handle product images
            if request.FILES.getlist('images'):
                images = request.FILES.getlist('images')
                for i, image in enumerate(images):
                    ProductImage.objects.create(
                        product=product,
                        image=image,
                        is_primary=False  # New images aren't primary by default
                    )
            
            messages.success(request, 'Product updated successfully!')
            return redirect('sellers:products')
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'title': 'Edit Product',
        'product': product,
        'product_images': product.images.all(),
    }
    return render(request, 'sellers/product_form.html', context)

@seller_required
def delete_product(request, product_id):
    """View to delete a product"""
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('sellers:products')
    
    context = {
        'product': product,
    }
    return render(request, 'sellers/delete_product.html', context)

@seller_required
def seller_orders(request):
    """View to display orders for seller's products"""
    # Get orders containing seller's products
    order_items = OrderItem.objects.filter(
        product__seller=request.user
    ).select_related('order', 'product').order_by('-order__created_at')
    
    # Group by order
    orders_dict = {}
    for item in order_items:
        if item.order.id not in orders_dict:
            orders_dict[item.order.id] = {
                'order': item.order,
                'items': [],
                'total': 0,
            }
        orders_dict[item.order.id]['items'].append(item)
        orders_dict[item.order.id]['total'] += item.total_price
    
    context = {
        'orders': orders_dict.values(),
    }
    return render(request, 'sellers/orders.html', context)

@seller_required
def seller_profile(request):
    """View to display seller profile"""
    profile, created = SellerProfile.objects.get_or_create(
        user=request.user,
        defaults={'company_name': request.user.username + "'s Store"}
    )
    
    context = {
        'profile': profile,
    }
    return render(request, 'sellers/profile.html', context)

@seller_required
def edit_seller_profile(request):
    """View to edit seller profile"""
    profile, created = SellerProfile.objects.get_or_create(
        user=request.user,
        defaults={'company_name': request.user.username + "'s Store"}
    )
    
    if request.method == 'POST':
        form = SellerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('sellers:profile')
    else:
        form = SellerProfileForm(instance=profile)
    
    context = {
        'form': form,
    }
    return render(request, 'sellers/edit_profile.html', context)

@seller_required
def seller_analytics(request):
    """View to display analytics data for seller"""
    # Product statistics
    products = Product.objects.filter(seller=request.user)
    total_products = products.count()
    
    # Sales statistics
    order_items = OrderItem.objects.filter(
        product__seller=request.user,
        order__payment_status='completed'
    )
    
    # Total sales
    total_sales = order_items.aggregate(total=Sum('price'))['total'] or 0
    
    # Sales by product
    sales_by_product = order_items.values(
        'product__id', 'product__name'
    ).annotate(
        total_sales=Sum('price'),
        units_sold=Sum('quantity')
    ).order_by('-total_sales')
    
    # Most popular products
    popular_products = order_items.values(
        'product__id', 'product__name'
    ).annotate(
        units_sold=Sum('quantity')
    ).order_by('-units_sold')[:5]
    
    context = {
        'total_products': total_products,
        'total_sales': total_sales,
        'sales_by_product': sales_by_product,
        'popular_products': popular_products,
    }
    return render(request, 'sellers/analytics.html', context)