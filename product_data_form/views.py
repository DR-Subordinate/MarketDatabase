from django.shortcuts import render, redirect
from django.db.models import Q

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

def save_price(request):
    if request.method == "POST":
        if 'price' in request.POST:
            pk = request.POST.get('primary_key')
            product = Product.objects.get(pk=pk)
            product.price = request.POST['price']
            product.save()
            return redirect("product_data_form:price")
        elif 'winning_bid' in request.POST:
            pk = request.POST.get('primary_key')
            product = Product.objects.get(pk=pk)
            product.winning_bid = request.POST['winning_bid']
            product.save()
            return redirect("product_data_form:price")
    else:
        form = ProductForm()
        products = Product.objects.filter(winning_bid="")
    return render(request, "product_data_form/price.html", {"products": products, "form": form})

def search(request):
    if request.method == "GET":
        search_query = request.GET.get("search-query")
        if search_query:
            products = Product.objects.filter(
                Q(date__icontains=search_query) |
                Q(market_name__icontains=search_query) |
                Q(number__icontains=search_query) |
                Q(brand_name__icontains=search_query) |
                Q(name__icontains=search_query) |
                Q(model_number__icontains=search_query) |
                Q(serial_number__icontains=search_query) |
                Q(material_color__icontains=search_query) |
                Q(condition__icontains=search_query) |
                Q(detail__icontains=search_query) |
                Q(price__icontains=search_query) |
                Q(winning_bid__icontains=search_query)
            )
        else:
            return render(request, "product_data_form/search.html")
    return render(request, "product_data_form/search.html", {"products": products})
