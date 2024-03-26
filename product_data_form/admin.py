from django.contrib import admin

from .models import Market, Product

class ProductInline(admin.StackedInline):
    model = Product
    extra = 1

class MarketAdmin(admin.ModelAdmin):
    inlines = [ProductInline]

admin.site.register(Market, MarketAdmin)
admin.site.register(Product)
