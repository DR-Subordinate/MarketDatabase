from django.forms import ModelForm, DateInput
from .models import Product

class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ["number", "brand_name", "name",
                  "model_number", "serial_number", "material_color",
                  "condition", "detail", "price", "winning_bid"]
