from django.contrib import admin
from .models import Category, Brand, Product

admin.site.register(Category)
admin.site.register(Brand)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'brand',
        'category',
        'price',
        'stock'
    )

    search_fields = ('name',)

    list_filter = ('brand', 'category')

from .models import Order, OrderDetail


class OrderDetailInline(admin.TabularInline):
    model = OrderDetail
    extra = 0
    can_delete = False
    readonly_fields = ('product', 'quantity', 'price')

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user',
        'full_name',
        'phone',
        'total_amount',
        'status',
        'created_at'
    )

    list_filter = ('status',)

    search_fields = ('full_name', 'phone')

    list_editable = ('status',)

    readonly_fields = (
        'user', 'full_name', 'phone',
        'address', 'total_amount', 'created_at'
    )

    inlines = [OrderDetailInline]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False