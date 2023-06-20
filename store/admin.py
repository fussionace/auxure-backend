from django.contrib import admin
from .models import Product

# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description', 'discount', 'image', 'price', 'slug', 'inventory', 'top_deal', 'flash_sales']

admin.site.register(Product, ProductAdmin)