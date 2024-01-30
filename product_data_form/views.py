from django.shortcuts import render, redirect

from .forms import ProductForm
from .models import Product

def index(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("product_data_form:index")
    else:
        form = ProductForm()
    return render(request, "product_data_form/index.html", {"form": form})

def search(request):
    pass
