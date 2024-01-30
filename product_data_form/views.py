from django.shortcuts import render

from .forms import ProductForm
from .models import Product

def index(request):
    if request.method == "POST":
        form = ProductForm()
    else:
        form = ProductForm()
    return render(request, "product_data_form/index.html", {"form": form})
