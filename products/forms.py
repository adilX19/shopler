from django import forms
from .models import ProductReview, Product
from django.utils.text import slugify

class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, str(i)) for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 4}),
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'category', 'name', 'description', 'price', 
            'discount_price', 'stock', 'is_available'
        ]
        
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'discount_price': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
        labels = {
            'name': 'Product Name',
            'price': 'Regular Price ($)',
            'discount_price': 'Discount Price ($, optional)',
            'stock': 'Stock Quantity',
            'is_available': 'Available for Purchase',
        }
        
        help_texts = {
            'discount_price': 'Leave empty if no discount applies',
            'is_available': 'Uncheck to hide this product from customers',
            'stock': 'How many units are available for sale',
            'description': 'Detailed description of your product',
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if not instance.slug:
            base_slug = slugify(instance.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            instance.slug = slug
        
        if commit:
            instance.save()
        return instance