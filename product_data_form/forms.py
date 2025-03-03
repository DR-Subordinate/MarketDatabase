from django.forms import ModelForm, DateInput, TextInput, Textarea, Select, FileInput, CheckboxInput
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
        fields = ["market", "image", "number", "brand_name",
                  "name", "model_number", "serial_number",
                  "material_color", "condition", "detail", "price",
                  "winning_bid", "is_bidden", "is_inspected"]
        widgets = {
            "market": Select(attrs={"class":"border border-black"}),
            "image": FileInput(attrs={"class":" text-xs"}),
            "number": TextInput(attrs={"class":"border border-black text-xs"}),
            "brand_name": TextInput(attrs={"class":"border border-black text-xs"}),
            "name": TextInput(attrs={"class":"border border-black text-xs"}),
            "model_number": TextInput(attrs={"class":"border border-black text-xs"}),
            "serial_number": TextInput(attrs={"class":"border border-black text-xs"}),
            "material_color": TextInput(attrs={"class":"border border-black text-xs"}),
            "condition": TextInput(attrs={"class":"border border-black text-xs"}),
            "detail": Textarea(attrs={"rows":"3", "class":"border border-black align-middle text-xs"}),
            "price": TextInput(attrs={"class":"border border-black text-xs"}),
            "winning_bid": TextInput(attrs={"class":"border border-black text-xs"}),
            "is_bidden": CheckboxInput(attrs={"class":"border border-black"}),
            "is_inspected": CheckboxInput(attrs={"class":"border border-black"})
        }
