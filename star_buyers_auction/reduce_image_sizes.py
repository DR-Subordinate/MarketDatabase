import os
from PIL import Image
from django.conf import settings

def reduce_sba_image_sizes():
    """
    Reduces file sizes of JPG images in star_buyers_auction directory through compression
    """
    star_buyers_auction_dir = os.path.join(settings.MEDIA_ROOT, 'star_buyers_auction')

    if not os.path.exists(star_buyers_auction_dir):
        return

    for filename in os.listdir(star_buyers_auction_dir):
        if filename.lower().endswith(('.jpg', '.jpeg')):
            filepath = os.path.join(star_buyers_auction_dir, filename)

            try:
                with Image.open(filepath) as img:
                    img.save(filepath, optimize=True, quality=50, progressive=True)
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
