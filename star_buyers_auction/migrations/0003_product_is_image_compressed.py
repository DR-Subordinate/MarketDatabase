# Generated by Django 4.2.17 on 2024-12-21 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('star_buyers_auction', '0002_product_product_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_image_compressed',
            field=models.BooleanField(default=False),
        ),
    ]