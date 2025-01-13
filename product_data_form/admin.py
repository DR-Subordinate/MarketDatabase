from django.contrib import admin

from .models import Market, Product, InvoicePDF

class ProductInline(admin.StackedInline):
    model = Product
    extra = 1

class InvoicePDFInline(admin.TabularInline):
    model = InvoicePDF
    extra = 1

class MarketAdmin(admin.ModelAdmin):
    inlines = [ProductInline, InvoicePDFInline]

admin.site.register(Market, MarketAdmin)
admin.site.register(Product)
admin.site.register(InvoicePDF)
