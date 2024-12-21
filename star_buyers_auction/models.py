from django.db import models

class Auction(models.Model):
    date = models.DateField()
    name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.name} {self.date}"


class Product(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, blank=True, null=True)
    image = models.ImageField(upload_to='star_buyers_auction/', null=True, blank=True)
    is_image_compressed = models.BooleanField(default=False)
    brand_name = models.CharField(max_length=200, blank=True)
    name = models.CharField(max_length=200, blank=True)
    ended_at = models.DateField(null=True, blank=True)
    rank = models.CharField(max_length=200, blank=True)
    price = models.CharField(max_length=200, blank=True)
    current_bidding_price = models.CharField(max_length=200, blank=True)
    memo = models.TextField(blank=True)
    product_link = models.CharField(max_length=200, blank=True, unique=True)

    def __str__(self):
        return f"{self.brand_name} {self.name}"
