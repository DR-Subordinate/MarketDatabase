from django.contrib import admin

from .models import Auction, Product

class ProductInline(admin.StackedInline):
    model = Product
    extra = 1

class AuctionAdmin(admin.ModelAdmin):
    inlines = [ProductInline]

admin.site.register(Auction, AuctionAdmin)
admin.site.register(Product)
