from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Order, OrderStatusUpdate, UserProfile

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'stock', 'created_at')
    list_filter = ('created_at', 'stock')
    search_fields = ('title', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'price', 'image_url', 'stock')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def display_image(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image_url)
        return "No image"
    display_image.short_description = 'Preview'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'total_amount', 'status', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('customer_name', 'customer_email', 'customer_phone')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    fieldsets = (
        ('Order Information', {
            'fields': ('product', 'total_amount', 'status')
        }),
        ('Customer Information', {
            'fields': ('customer_name', 'customer_email', 'customer_phone', 'shipping_address')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(OrderStatusUpdate)
class OrderStatusUpdateAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order__id', 'notes')
    readonly_fields = ('created_at',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'created_at')
    search_fields = ('user__username', 'phone', 'address')
    readonly_fields = ('created_at', 'updated_at')
