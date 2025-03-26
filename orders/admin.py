from django.contrib import admin
from .models import Order, OrderItem, Payment

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price', 'total_price')

class PaymentInline(admin.StackedInline):
    model = Payment
    can_delete = False
    readonly_fields = ('payment_id', 'amount', 'timestamp')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'status', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_status')
    search_fields = ('user__username', 'user__email', 'tracking_number')
    readonly_fields = ('total_amount', 'created_at')
    inlines = [OrderItemInline, PaymentInline]

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Payment)