import os
from PIL import Image
from .models import Product

def compress_sba_images():
    """
    Reduces file sizes of all uncompressed JPG images,
    starting from the oldest auction date
    """
    uncompressed_products = Product.objects.filter(
        is_image_compressed=False,
        image__isnull=False
    ).order_by('auction__date')[:100]

    for product in uncompressed_products:
        if product.image and os.path.exists(product.image.path):
            try:
                with Image.open(product.image.path) as img:
                    img.save(product.image.path, optimize=True, quality=50, progressive=True)
                product.is_image_compressed = True
                product.save()
            except Exception as e:
                print(f"Error processing {product.image.name}: {str(e)}")
