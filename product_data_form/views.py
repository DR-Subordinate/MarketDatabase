from django.shortcuts import render

from .models import Product

def index(request):
    product_list = Product.objects.all()
    context = {"product_list": product_list}
    return render(request, "product_data_form/index.html", context)
