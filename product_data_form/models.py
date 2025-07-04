from django.db import models
from .text_normalization import TextNormalizationMixin

class Market(models.Model):
    date = models.DateField()
    name = models.CharField(max_length=200)
    invoice_pdf = models.FileField(upload_to='invoices/', null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'date'],
                name='unique_market_name_date'
            )
        ]

    def __str__(self):
        return f"{self.name} {self.date}"


class Product(TextNormalizationMixin, models.Model):
    market = models.ForeignKey(Market, on_delete=models.CASCADE, blank=True, null=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    number = models.CharField(max_length=200, blank=True)
    brand_name = models.CharField(max_length=200, blank=True)
    name = models.CharField(max_length=200, blank=True)
    model_number = models.CharField(max_length=200, blank=True)
    serial_number = models.CharField(max_length=200, blank=True)
    material_color = models.CharField(max_length=200, blank=True)
    condition = models.CharField(max_length=200, blank=True)
    detail = models.TextField(blank=True)
    price = models.CharField(max_length=200, blank=True)
    winning_bid = models.CharField(max_length=200, blank=True)
    is_bidden = models.BooleanField(default=False)
    is_inspected = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class InvoicePDF(models.Model):
    market = models.ForeignKey(Market, on_delete=models.CASCADE)
    file = models.FileField(upload_to='invoices/')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
