from django.shortcuts import render, redirect
from django.core.files.base import ContentFile
from datetime import datetime
import os
from dotenv import load_dotenv
from .models import Auction, Product
from .scrape_sba import SBA
from .get_storage_info import get_disk_usage
from .compress_images import compress_sba_images

def index(request):
    storage_info = get_disk_usage()
    compression_message = None
    if storage_info['usage_percent'] > 95:
        compress_sba_images()
        storage_info = get_disk_usage()
        compression_message = "空き容量を確保するため、画像を圧縮しました。"

    if request.method == "POST":
        end_date = request.POST.get('auction_end_date')

        try:
            if not load_dotenv(dotenv_path=".env.local"):
                email = os.environ["EMAIL"]
                password = os.environ["PASSWORD"]
            else:
                email = os.environ["EMAIL"]
                password = os.environ["PASSWORD"]

            sba = SBA(
                email=email,
                password=password,
                end_date=end_date,
            )

            if sba.login():
                auction = Auction.objects.create(
                    date=datetime.strptime(end_date, '%Y-%m-%d').date(),
                    name="スタバイ"
                )

                existing_products = set(Product.objects.values_list('product_link', flat=True))

                product_links = sba.collect_product_links()
                product_data = sba.collect_product_data(product_links)

                for item in product_data:
                    if item['product_link'] not in existing_products:
                        image_content, image_name = item['image']
                        Product.objects.create(
                            auction=auction,
                            image=ContentFile(image_content, name=image_name) if image_content else None,
                            brand_name=item['brand_name'],
                            name=item['product_name'],
                            ended_at=datetime.strptime(item['ended_at'], '%Y/%m/%d').date(),
                            rank=item['data_rank'],
                            price=item['price'],
                            current_bidding_price=item['current_bidding_price'],
                            memo=item['memo'],
                            product_link=item['product_link']
                        )
                return redirect('star_buyers_auction:index')
            else:
                return render(request, "star_buyers_auction/index.html",
                            {"error_message": "ログインに失敗しました。"})

        except Exception as e:
            return render(request, "star_buyers_auction/index.html",
                        {"error_message": f"エラーが発生しました: {str(e)}"})

    context = {"storage_info": storage_info, "compression_message": compression_message}
    return render(request, "star_buyers_auction/index.html", context)
