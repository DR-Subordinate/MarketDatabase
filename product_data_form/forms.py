from django.forms import ModelForm, DateInput, TextInput, Textarea, Select, FileInput
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
        fields = ["market", "image", "number", "brand_name", "name",
                  "model_number", "serial_number", "material_color",
                  "condition", "detail", "price", "winning_bid"]
        widgets = {
            "market": Select(attrs={"class":"border border-black"}),
            "image": FileInput(attrs={"class":"ml-16"}),
            "number": TextInput(attrs={"class":"border border-black ml-16"}),
            "brand_name": TextInput(attrs={"class":"border border-black ml-4"}),
            "name": TextInput(attrs={"class":"border border-black ml-12"}),
            "model_number": TextInput(attrs={"class":"border border-black ml-16"}),
            "serial_number": TextInput(attrs={"class":"border border-black ml-8"}),
            "material_color": TextInput(attrs={"class":"border border-black"}),
            "condition": TextInput(attrs={"class":"border border-black ml-16"}),
            "detail": Textarea(attrs={"cols":"35", "rows":"5", "class":"border border-black align-middle ml-4"}),
            "price": TextInput(attrs={"class":"border border-black"}),
            "winning_bid": TextInput(attrs={"class":"border border-black"})
        }
