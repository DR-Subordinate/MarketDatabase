from django.core.management.base import BaseCommand
from product_data_form.models import Product

class Command(BaseCommand):
    help = 'Normalize text in all existing Product records'

    def handle(self, *args, **options):
        products = Product.objects.all()
        count = 0

        for product in products:
            # Just save each product to trigger the normalization in the mixin
            product.save()
            count += 1

            if count % 100 == 0:
                self.stdout.write(f"Normalized {count} products...")

        self.stdout.write(self.style.SUCCESS(f'Successfully normalized {count} products'))
