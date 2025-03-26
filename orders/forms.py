from django import forms
from users.models import Address

class ShippingAddressForm(forms.Form):
    shipping_address = forms.ModelChoiceField(
        queryset=None,
        widget=forms.RadioSelect,
        label='Shipping Address'
    )
    billing_address = forms.ModelChoiceField(
        queryset=None,
        widget=forms.RadioSelect,
        label='Billing Address'
    )
    payment_method = forms.ChoiceField(
        choices=[
            ('credit_card', 'Credit Card'),
            ('paypal', 'PayPal'),
        ],
        widget=forms.RadioSelect,
        label='Payment Method'
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super