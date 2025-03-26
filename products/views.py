from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, Avg
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Product, Category, ProductReview
from .forms import ProductReviewForm

def home(request):
    """Home page view with featured products and categories"""
    featured_products = Product.objects.filter(is_available=True).order_by('-created_at')[:8]
    categories = Category.objects.filter(parent=None)
    
    context = {
        'featured_products': featured_products,
        'categories': categories,
    }
    return render(request, 'products/home.html', context)

def category_detail(request, category_slug):
    """View to display products from a specific category"""
    category = get_object_or_404(Category, slug=category_slug)
    
    # Get all products from this category and its subcategories
    categories = [category]
    if category.children.exists():
        categories.extend(category.children.all())
    
    products_list = Product.objects.filter(category__in=categories, is_available=True)
    
    # Apply filters
    sort_by = request.GET.get('sort', '-created_at')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    if min_price:
        products_list = products_list.filter(price__gte=min_price)
    if max_price:
        products_list = products_list.filter(price__lte=max_price)
    
    products_list = products_list.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(products_list, 12)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    context = {
        'category': category,
        'products': products,
        'sort_by': sort_by,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'products/category_detail.html', context)

def product_detail(request, product_slug):
    """View to display product details and handle review submission"""
    product = get_object_or_404(Product, slug=product_slug, is_available=True)
    reviews = product.reviews.all().order_by('-created_at')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Handle review form submission
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.warning(request, 'You must be logged in to leave a review.')
            return redirect('account_login')
        
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            # Check if user already reviewed this product
            existing_review = reviews.filter(user=request.user).first()
            if existing_review:
                # Update existing review
                existing_review.rating = form.cleaned_data['rating']
                existing_review.comment = form.cleaned_data['comment']
                existing_review.save()
                messages.success(request, 'Your review has been updated.')
            else:
                # Create new review
                review = form.save(commit=False)
                review.product = product
                review.user = request.user
                review.save()
                messages.success(request, 'Your review has been submitted.')
            return redirect('products:product_detail', product_slug=product_slug)
    else:
        form = ProductReviewForm()
    
    # Related products from same category
    related_products = Product.objects.filter(
        category=product.category, is_available=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_form': form,
        'related_products': related_products,
    }
    return render(request, 'products/product_detail.html', context)

def search_products(request):
    """Search for products"""
    query = request.GET.get('q', '')
    
    products_list = Product.objects.filter(is_available=True)
    if query:
        products_list = products_list.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()
    
    # Apply filters
    sort_by = request.GET.get('sort', '-created_at')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    if min_price:
        products_list = products_list.filter(price__gte=min_price)
    if max_price:
        products_list = products_list.filter(price__lte=max_price)
    
    products_list = products_list.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(products_list, 12)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    context = {
        'products': products,
        'query': query,
        'sort_by': sort_by,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'products/search_results.html', context)