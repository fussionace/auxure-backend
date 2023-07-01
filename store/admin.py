from django.contrib import admin
from .models import Perfume,Category, Cart,Cartitems

# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description', 'discount', 'image', 'price', 'slug', 'inventory', 'top_deal', 'flash_sales']

admin.site.register(Perfume, ProductAdmin)
admin.site.register(Category)
admin.site.register(Cartitems)
admin.site.register(Cart)

