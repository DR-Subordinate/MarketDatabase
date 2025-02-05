from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse
from django.db.models import Q
from django.forms import modelformset_factory
from django.core.files.base import ContentFile

from .forms import ProductForm, MarketForm
from .models import Product, Market, InvoicePDF

import io
import os
from datetime import datetime
from .generate_invoice_pdf import generate_invoice_pdf

from star_buyers_auction.models import AuctionProduct

def main(request):
    markets = Market.objects.all().order_by("-pk")
    market_form = MarketForm()

    if request.method == "POST":
        if "download_pdf" in request.POST:
            pdf_id = request.POST.get('pdf_id')
            if pdf_id:
                pdf = get_object_or_404(InvoicePDF, id=pdf_id)
                return FileResponse(pdf.file.open('rb'), filename=os.path.basename(pdf.file.name))
        else:
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
        edit_formset = ProductFormSetEdit(request.POST, request.FILES, prefix='edit', queryset=Product.objects.filter(market=market).order_by('-is_bidden'))

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
        edit_formset = ProductFormSetEdit(queryset=Product.objects.filter(market=market).order_by('-is_bidden'), prefix='edit')

    context = {"new_formset": new_formset, "edit_formset": edit_formset, "market": market}
    return render(request, "product_data_form/product_main.html", context)

def product_register(request, market_name, market_date):
    market = get_object_or_404(Market, name=market_name, date=market_date)

    ProductFormSetEdit = modelformset_factory(Product, form=ProductForm, extra=0, can_delete=True)

    if request.method == "POST":
        if 'generate_invoice' in request.POST:
            pdf_buffer = io.BytesIO()
            bidden_products = market.product_set.filter(is_bidden=True)
            generate_invoice_pdf(pdf_buffer, market, bidden_products)
            pdf_buffer.seek(0)
            current_date = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            InvoicePDF.objects.create(
                market=market,
                file=ContentFile(pdf_buffer.getvalue(), name=f'{current_date}.pdf')
            )
            return redirect("product_data_form:product_register", market_name=market_name, market_date=market_date)
        elif "download_pdf" in request.POST:
            pdf_id = request.POST.get("pdf_id")
            if pdf_id:
                pdf = get_object_or_404(InvoicePDF, id=pdf_id)
                return FileResponse(pdf.file.open('rb'), filename=os.path.basename(pdf.file.name))
        else:
            edit_formset = ProductFormSetEdit(request.POST, request.FILES, prefix='edit', queryset=Product.objects.filter(market=market).order_by('-is_bidden'))

            if edit_formset.is_valid():
                edited_products = edit_formset.save(commit=False)
                for edited_product in edited_products:
                    edited_product.market = market
                    edited_product.save()

                for deleted_product in edit_formset.deleted_objects:
                    deleted_product.delete()

                return redirect("product_data_form:product_register", market_name=market_name, market_date=market_date)
    else:
        edit_formset = ProductFormSetEdit(queryset=Product.objects.filter(market=market).order_by('-is_bidden'), prefix='edit')

    context = {"edit_formset": edit_formset, "market": market}
    return render(request, "product_data_form/product_register.html", context)

def search(request):
    if request.method == "GET":
        search_query = request.GET.get("search-query")
        if search_query:

            search_terms = search_query.replace('\u3000', ' ').split()

            market_products_query = Q()
            auction_products_query = Q()

            for term in search_terms:
                market_products_query |= (
                    Q(market__name__icontains=term) |
                    Q(market__date__icontains=term) |
                    Q(number__icontains=term) |
                    Q(brand_name__icontains=term) |
                    Q(name__icontains=term) |
                    Q(model_number__icontains=term) |
                    Q(serial_number__icontains=term) |
                    Q(material_color__icontains=term) |
                    Q(condition__icontains=term) |
                    Q(detail__icontains=term) |
                    Q(price__icontains=term) |
                    Q(winning_bid__icontains=term)
                )

                auction_products_query |= (
                    Q(auction__name__icontains=term) |
                    Q(auction__date__icontains=term) |
                    Q(brand_name__icontains=term) |
                    Q(name__icontains=term) |
                    Q(rank__icontains=term) |
                    Q(price__icontains=term) |
                    Q(current_bidding_price__icontains=term) |
                    Q(memo__icontains=term)
                )

            market_products = Product.objects.filter(market_products_query)
            auction_products = AuctionProduct.objects.filter(auction_products_query)

            results = {
                'market_products': market_products,
                'auction_products': auction_products
            }
        else:
            results = None

        return render(request, "product_data_form/search.html", {"results": results})

    return render(request, "product_data_form/search.html")
