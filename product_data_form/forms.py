from django.forms import ModelForm, DateInput, TextInput, Textarea
from .models import Product, Market

class MarketForm(ModelForm):
    class Meta:
        model = Market
        fields = ["date", "name"]
        widgets = {
            "date": DateInput(attrs={"type":"date", "class":"border border-black"}),
            "name": TextInput(attrs={"class":"border border-black"})
        }

class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ["number", "brand_name", "name",
                  "model_number", "serial_number", "material_color",
                  "condition", "detail", "price", "winning_bid"]
        widgets = {
            "number": TextInput(attrs={"class":"border border-black"}),
            "brand_name": TextInput(attrs={"class":"border border-black"}),
            "name": TextInput(attrs={"class":"border border-black"}),
            "model_number": TextInput(attrs={"class":"border border-black"}),
            "serial_number": TextInput(attrs={"class":"border border-black"}),
            "material_color": TextInput(attrs={"class":"border border-black"}),
            "condition": TextInput(attrs={"class":"border border-black"}),
            "detail": Textarea(attrs={"class":"border border-black"}),
            "price": TextInput(attrs={"class":"border border-black"}),
            "winning_bid": TextInput(attrs={"class":"border border-black"})
        }
