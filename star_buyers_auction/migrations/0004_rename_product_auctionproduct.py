# Generated by Django 4.2.17 on 2024-12-22 12:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('star_buyers_auction', '0003_product_is_image_compressed'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Product',
            new_name='AuctionProduct',
        ),
    ]