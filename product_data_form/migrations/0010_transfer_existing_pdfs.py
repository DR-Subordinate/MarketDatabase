from django.db import migrations

def transfer_pdfs(apps, schema_editor):
    Market = apps.get_model('product_data_form', 'Market')
    InvoicePDF = apps.get_model('product_data_form', 'InvoicePDF')
    
    for market in Market.objects.filter(invoice_pdf__isnull=False):
        if market.invoice_pdf:
            InvoicePDF.objects.create(
                market=market,
                file=market.invoice_pdf
            )

def reverse_transfer(apps, schema_editor):
    InvoicePDF = apps.get_model('product_data_form', 'InvoicePDF')
    InvoicePDF.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('product_data_form', '0009_invoicepdf'),  # Replace '0009_invoicepdf' with your last migration name
    ]

    operations = [
        migrations.RunPython(transfer_pdfs, reverse_transfer),
    ]
