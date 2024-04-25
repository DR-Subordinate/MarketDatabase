from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q

from .forms import ProductForm, MarketForm
from .models import Product, Market

def index(request):
    if request.method == "POST":
        market_form = MarketForm(request.POST)
        if market_form.is_valid():
            market_form.save()
            return redirect("product_data_form:index")
    else:
        market_form = MarketForm()
        markets = Market.objects.all().order_by("-pk")
    context = {"market_form": market_form, "markets": markets}
    return render(request, "product_data_form/index.html", context)

def save_product(request, market_name, market_date):
    market = get_object_or_404(Market, name=market_name, date=market_date)
    if request.method == "POST":
        product_form = ProductForm(request.POST)
        if product_form.is_valid():
            product = product_form.save(commit=False)
            product.market = market
            product.save()
            return redirect("product_data_form:product", market_name=market_name, market_date=market_date)
    else:
        product_form = ProductForm()
    context = {"product_form": product_form, "market": market}
    return render(request, "product_data_form/product.html", context)

def save_price(request):
    if request.method == "POST":
        pk = request.POST.get('primary_key')
        product = Product.objects.get(pk=pk)
        if 'price' in request.POST:
            product.price = request.POST['price']
        elif 'winning_bid' in request.POST:
            product.winning_bid = request.POST['winning_bid']
        product.save()
        return redirect("product_data_form:price")
    else:
        markets = Market.objects.all()
    context = {"markets": markets}
    return render(request, "product_data_form/price.html", context)

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

def edit(request):
    if request.method == "POST":
        pk = request.POST.get('primary_key')
        product = Product.objects.get(pk=pk)
        product.number = request.POST['number']
        product.brand_name = request.POST['brand_name']
        product.name = request.POST['name']
        product.model_number = request.POST['model_number']
        product.serial_number = request.POST['serial_number']
        product.material_color = request.POST['material_color']
        product.condition = request.POST['condition']
        product.detail = request.POST['detail']
        product.price = request.POST['price']
        product.winning_bid = request.POST['winning_bid']
        product.save()
        return redirect("product_data_form:edit")
    else:
        markets = Market.objects.all()
    context = {"markets": markets}
    return render(request, "product_data_form/edit.html", context)
