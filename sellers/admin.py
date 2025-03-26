from django.contrib import admin
from .models import SellerProfile

class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user', 'is_approved', 'created_at')
    list_filter = ('is_approved',)
    search_fields = ('company_name', 'user__username', 'user__email')

admin.site.register(SellerProfile, SellerProfileAdmin)