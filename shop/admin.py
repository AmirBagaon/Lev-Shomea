# shop/admin.py
from django.contrib import admin
from .models import Category, Product, CartItem, Order, OrderItem, Marketer, Event, Kashrut

@admin.register(Marketer)
class MarketerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['first_name', 'last_name']
    list_editable = ['is_active']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    list_editable = ['is_active']

@admin.register(Kashrut)
class KashrutAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    list_editable = ['is_active']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'kashrut', 'supplier', 'price', 'stock', 'is_active', 'total_orders', 'created_at']
    list_filter = ['is_active', 'category', 'kashrut', 'created_at', 'unlimited_stock']
    search_fields = ['name', 'supplier']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active', 'price', 'stock']
    readonly_fields = ['total_orders']
    
    fieldsets = (
        ('מידע בסיסי', {
            'fields': ('name', 'slug', 'description')
        }),
        ('קטגוריזציה', {
            'fields': ('category', 'kashrut', 'supplier')
        }),
        ('מחיר ומלאי', {
            'fields': ('price', 'unlimited_stock', 'stock')
        }),
        ('מידע נוסף', {
            'fields': ('image', 'is_active', 'total_orders')
        }),
    )

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ['product', 'quantity', 'price']
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'first_name', 'last_name', 'email', 'total_amount', 'status', 'payment_status', 'marketer', 'event', 'created_at']
    list_filter = ['status', 'payment_status', 'marketer', 'event', 'created_at', 'updated_at']
    search_fields = ['order_number', 'first_name', 'last_name', 'email']
    readonly_fields = ['order_number', 'total_amount', 'total_items', 'created_at', 'updated_at']
    list_editable = ['status', 'payment_status']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('מידע הזמנה', {
            'fields': ('order_number', 'user', 'status', 'payment_status')
        }),
        ('פרטי לקוח', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('כתובת', {
            'fields': ('address', 'city', 'postal_code'),
            'classes': ['collapse']
        }),
        ('פרטי מכירה', {
            'fields': ('marketer', 'event')
        }),
        ('סיכום הזמנה', {
            'fields': ('total_amount', 'total_items')
        }),
        ('תאריכים', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'quantity', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'product__name']

# OrderItem רק יופיע כ-inline, לא צריך admin נפרד
# אבל אם תרצה, אפשר להוסיף:
# @admin.register(OrderItem)
# class OrderItemAdmin(admin.ModelAdmin):
#     list_display = ['order', 'product', 'quantity', 'price']
#     list_filter = ['order__created_at']