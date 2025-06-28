from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *
from .forms import PriceAdminForm, ProductAdminForm


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('role',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Дополнительно', {'fields': ('role',)}),
    )


@admin.register(ProductSuggestion)
class ProductSuggestionAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'status', 'store_text',
                    'category_text', 'user', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'manufacturer', 'store_text',
                     'category_text', 'user__username')
    readonly_fields = ('created_at', 'reviewed_at')


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'address_base', 'phone')


@admin.register(AddressBase)
class AddressBaseAdmin(admin.ModelAdmin):
    list_display = ('city', 'street')
    search_fields = ('city', 'street')
    ordering = ('city', 'street')


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ('name', 'category', 'manufacturer')
    search_fields = ('name', 'category__name', 'manufacturer__name')


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    form = PriceAdminForm
    list_display = ('product', 'store', 'price', 'updated_at')
    list_filter = ('store', 'product')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'store', 'status', 'created_at')
    list_filter = ('status',)


@admin.register(ProductCategory)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(TodoTask)
class TodoTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status', 'created_by', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title',)
    ordering = ('-created_at',)
