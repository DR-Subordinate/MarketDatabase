from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse
from django.db.models import Q, F, Case, When, Value, IntegerField
from django.forms import modelformset_factory
from django.core.files.base import ContentFile
from django.core.files import File

from .forms import ProductForm, MarketForm
from .models import Product, Market, InvoicePDF

import io
import os
from dotenv import load_dotenv
from datetime import datetime
from itertools import chain
from .generate_invoice_pdf import generate_invoice_pdf
from .scrape_nbaa import NBAA

from star_buyers_auction.models import AuctionProduct

from line_notification.messaging_service import LineMessagingService

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

    if request.method == "POST" and request.POST.get("fetch_market_data") == "true":
        if not load_dotenv(dotenv_path=".env.local"):
            email = os.environ["EMAIL_NBAA"]
            password = os.environ["PASSWORD_NBAA"]
        else:
            email = os.environ["EMAIL_NBAA"]
            password = os.environ["PASSWORD_NBAA"]

        if email and password:
            nbaa = NBAA(email=email, password=password)

            if nbaa.login():
                products_to_update = Product.objects.filter(
                    market=market,
                    number__isnull=False,
                )

                if products_to_update.exists():
                    dates = [market_date] * products_to_update.count()
                    box_numbers = []
                    branch_numbers = []

                    for product in products_to_update:
                        # Assuming product.number format is like "160-3"
                        if "-" in product.number:
                            box, branch = product.number.split("-", 1)
                            box_numbers.append(box.strip())
                            branch_numbers.append(branch.strip())
                        else:
                            # Handle products without proper number format
                            continue

                    # Collect data from NBAA
                    if box_numbers and branch_numbers:
                        scraped_data = nbaa.collect_product_data(dates, box_numbers, branch_numbers)
                        print(scraped_data)

                        # Update products with scraped data
                        for i, product in enumerate(products_to_update):
                            if i < len(scraped_data):
                                data = scraped_data[i]
                                print(data)

                                if data["winning_bid"]:
                                    product.winning_bid = data["winning_bid"]

                                if data["image_path"]:
                                    if os.path.exists(data["image_path"]):
                                        with open(data["image_path"], "rb") as img_file:
                                            product.image.save(
                                                os.path.basename(data["image_path"]),
                                                File(img_file),
                                                save=False
                                            )

                                product.save()

                        # Clean up temporary image files
                        for data in scraped_data:
                            if data["image_path"] and os.path.exists(data["image_path"]):
                                os.remove(data["image_path"])

        return redirect("product_data_form:product_main", market_name=market_name, market_date=market_date)

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

        all_products = Product.objects.filter(market=market)
        products_without_prices_count = all_products.filter(
            Q(price__isnull=True) | Q(price='')
        ).count()

        if products_without_prices_count == 0 and all_products.exists():
            bidden_products = all_products.filter(is_bidden=True)
            non_bidden_products = all_products.filter(is_bidden=False)

            # Custom sort
            def sort_product_numbers(queryset):
                # Convert to list so we can sort
                products = list(queryset)

                def get_sort_key(product):
                    # Handle the case where number might be None
                    if not product.number:
                        return (0, 0)

                    # Split by hyphen if it exists
                    if '-' in product.number:
                        parts = product.number.split('-', 1)
                        try:
                            return (int(parts[0]), int(parts[1]))
                        except ValueError:
                            # If conversion fails, fall back to string comparison
                            return (0, 0)
                    else:
                        # If no hyphen, just use the number
                        try:
                            return (int(product.number), 0)
                        except ValueError:
                            return (0, 0)

                # Sort the products
                products.sort(key=get_sort_key)
                return products

            sorted_bidden = sort_product_numbers(bidden_products)
            sorted_non_bidden = sort_product_numbers(non_bidden_products)

            all_sorted_products = sorted_bidden + sorted_non_bidden

            # Create a list of IDs in the order we want
            ordered_ids = [p.id for p in all_sorted_products]

            if not ordered_ids:
                queryset = Product.objects.none()
            else:
                # Create a Case expression for ordering
                preserved = Case(
                    *[When(id=id, then=Value(i)) for i, id in enumerate(ordered_ids)],
                    output_field=IntegerField()
                )

                # Get the queryset in our custom order
                queryset = Product.objects.filter(id__in=ordered_ids).order_by(preserved)
        else:
            # If any products don't have prices, use the original ordering
            queryset = all_products.order_by('-is_bidden')

        edit_formset = ProductFormSetEdit(queryset=queryset, prefix='edit')

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

            try:
                service = LineMessagingService()
                service.send_to_all(f"請求書が作成されました。{market.name} {market.date}")
            except Exception as e:
                print(f"LINE notification error: {e}")

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
        all_products = Product.objects.filter(market=market)
        products_without_prices_count = all_products.filter(
            Q(price__isnull=True) | Q(price='')
        ).count()

        if products_without_prices_count == 0 and all_products.exists():
            bidden_products = all_products.filter(is_bidden=True)
            non_bidden_products = all_products.filter(is_bidden=False)

            # Custom sort
            def sort_product_numbers(queryset):
                # Convert to list so we can sort
                products = list(queryset)

                def get_sort_key(product):
                    # Handle the case where number might be None
                    if not product.number:
                        return (0, 0)

                    # Split by hyphen if it exists
                    if '-' in product.number:
                        parts = product.number.split('-', 1)
                        try:
                            return (int(parts[0]), int(parts[1]))
                        except ValueError:
                            # If conversion fails, fall back to string comparison
                            return (0, 0)
                    else:
                        # If no hyphen, just use the number
                        try:
                            return (int(product.number), 0)
                        except ValueError:
                            return (0, 0)

                # Sort the products
                products.sort(key=get_sort_key)
                return products

            sorted_bidden = sort_product_numbers(bidden_products)
            sorted_non_bidden = sort_product_numbers(non_bidden_products)

            all_sorted_products = sorted_bidden + sorted_non_bidden

            # Create a list of IDs in the order we want
            ordered_ids = [p.id for p in all_sorted_products]

            if not ordered_ids:
                queryset = Product.objects.none()
            else:
                # Create a Case expression for ordering
                preserved = Case(
                    *[When(id=id, then=Value(i)) for i, id in enumerate(ordered_ids)],
                    output_field=IntegerField()
                )

                # Get the queryset in our custom order
                queryset = Product.objects.filter(id__in=ordered_ids).order_by(preserved)
        else:
            # If any products don't have prices, use the original ordering
            queryset = all_products.order_by('-is_bidden')

        edit_formset = ProductFormSetEdit(queryset=queryset, prefix='edit')

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
                market_products_query &= (
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

                auction_products_query &= (
                    Q(auction__name__icontains=term) |
                    Q(auction__date__icontains=term) |
                    Q(brand_name__icontains=term) |
                    Q(name__icontains=term) |
                    Q(rank__icontains=term) |
                    Q(price__icontains=term) |
                    Q(current_bidding_price__icontains=term) |
                    Q(memo__icontains=term)
                )

            market_products = Product.objects.filter(market_products_query).annotate(
                sort_date=F('market__date')
            )

            auction_products = AuctionProduct.objects.filter(auction_products_query).annotate(
                sort_date=F('auction__date')
            )

            combined_products = sorted(
                chain(market_products, auction_products),
                key=lambda x: x.sort_date,
                reverse=True
            )

            results = {
                'combined_products': combined_products
            }
        else:
            results = None

        return render(request, "product_data_form/search.html", {"results": results})

    return render(request, "product_data_form/search.html")
