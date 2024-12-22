from django.contrib import admin

from .models import Auction, AuctionProduct

class AuctionProductInline(admin.StackedInline):
    model = AuctionProduct
    extra = 1

class AuctionAdmin(admin.ModelAdmin):
    inlines = [AuctionProductInline]

admin.site.register(Auction, AuctionAdmin)
admin.site.register(AuctionProduct)
