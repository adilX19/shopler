from django.urls import path
from . import views

app_name = 'sellers'

urlpatterns = [
    path('dashboard/', views.seller_dashboard, name='dashboard'),
    path('products/', views.seller_products, name='products'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('products/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('orders/', views.seller_orders, name='orders'),
    path('profile/', views.seller_profile, name='profile'),
    path('profile/edit/', views.edit_seller_profile, name='edit_profile'),
    path('analytics/', views.seller_analytics, name='analytics'),
]