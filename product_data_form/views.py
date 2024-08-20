from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.forms import modelformset_factory

from .forms import ProductForm, MarketForm
from .models import Product, Market

def main(request):
    markets = Market.objects.all().order_by("-pk")
    market_form = MarketForm()

    if request.method == "POST":
        market_form = MarketForm(request.POST)
        if market_form.is_valid():
            market_form.save()
            return redirect("product_data_form:main")

    context = {"market_form": market_form, "markets": markets}
    return render(request, "product_data_form/main.html", context)

def product_main(request, market_name, market_date):
    market = get_object_or_404(Market, name=market_name, date=market_date)

    ProductFormSetNew = modelformset_factory(Product, form=ProductForm, extra=200)
    ProductFormSetEdit = modelformset_factory(Product, form=ProductForm, extra=0, can_delete=True)

    if request.method == "POST":
        new_formset = ProductFormSetNew(request.POST, request.FILES, prefix='new', queryset=Product.objects.none())
        edit_formset = ProductFormSetEdit(request.POST, request.FILES, prefix='edit', queryset=Product.objects.filter(market=market))

        if new_formset.is_valid() and edit_formset.is_valid():
            new_products = new_formset.save(commit=False)
            for new_product in new_products:
                new_product.market = market
                new_product.save()

            edited_products = edit_formset.save(commit=False)
            for edited_product in edited_products:
                edited_product.market = market
                edited_product.save()

            for deleted_product in edit_formset.deleted_objects:
                deleted_product.delete()

            return redirect("product_data_form:product_main", market_name=market_name, market_date=market_date)
    else:
        new_formset = ProductFormSetNew(queryset=Product.objects.none(), prefix='new')
        edit_formset = ProductFormSetEdit(queryset=Product.objects.filter(market=market), prefix='edit')

    context = {"new_formset": new_formset, "edit_formset": edit_formset, "market": market}
    return render(request, "product_data_form/product_main.html", context)

def product_register(request, market_name, market_date):
    market = get_object_or_404(Market, name=market_name, date=market_date)

    ProductFormSetEdit = modelformset_factory(Product, form=ProductForm, extra=0, can_delete=True)

    if request.method == "POST":
        edit_formset = ProductFormSetEdit(request.POST, request.FILES, prefix='edit', queryset=Product.objects.filter(market=market))

        if edit_formset.is_valid():
            edited_products = edit_formset.save(commit=False)
            for edited_product in edited_products:
                edited_product.market = market
                edited_product.save()

            for deleted_product in edit_formset.deleted_objects:
                deleted_product.delete()

            return redirect("product_data_form:product_register", market_name=market_name, market_date=market_date)
    else:
        edit_formset = ProductFormSetEdit(queryset=Product.objects.filter(market=market), prefix='edit')

    context = {"edit_formset": edit_formset, "market": market}
    return render(request, "product_data_form/product_register.html", context)

def search(request):
    if request.method == "GET":
        search_query = request.GET.get("search-query")
        if search_query:
            products = Product.objects.filter(
                Q(market__name__icontains=search_query) |
                Q(market__date__icontains=search_query) |
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
            ).exclude(winning_bid__isnull=True).exclude(winning_bid__exact='')
        else:
            return render(request, "product_data_form/search.html")
    return render(request, "product_data_form/search.html", {"products": products})
