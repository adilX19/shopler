from django import forms
from .models import SellerProfile

class SellerProfileForm(forms.ModelForm):
    class Meta:
        model = SellerProfile
        fields = ['company_name', 'description', 'logo', 'website']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://'}),
        }
        labels = {
            'company_name': 'Company/Store Name',
            'logo': 'Company Logo',
            'website': 'Company Website (optional)',
        }
        help_texts = {
            'description': 'Tell customers about your business, products, and services',
            'logo': 'Upload a logo or brand image for your store',
        }