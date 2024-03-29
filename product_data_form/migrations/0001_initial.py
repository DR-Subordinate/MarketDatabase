# Generated by Django 4.2.9 on 2024-01-30 03:38

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('market_name', models.CharField(blank=True, max_length=200)),
                ('number', models.CharField(blank=True, max_length=200)),
                ('brand_name', models.CharField(blank=True, max_length=200)),
                ('name', models.CharField(blank=True, max_length=200)),
                ('model_number', models.CharField(blank=True, max_length=200)),
                ('serial_number', models.CharField(blank=True, max_length=200)),
                ('material_color', models.CharField(blank=True, max_length=200)),
                ('condition', models.CharField(blank=True, max_length=200)),
                ('detail', models.TextField(blank=True)),
                ('price', models.CharField(blank=True, max_length=200)),
                ('winning_bid', models.CharField(blank=True, max_length=200)),
            ],
        ),
    ]
