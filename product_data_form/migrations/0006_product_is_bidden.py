# Generated by Django 4.2.13 on 2024-08-08 09:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_data_form', '0005_product_image_alter_market_date_alter_market_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_bidden',
            field=models.BooleanField(default=False),
        ),
    ]