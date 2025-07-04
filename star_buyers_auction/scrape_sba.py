import os
import re
import io
from urllib.parse import urlparse
import time
import random

import requests
from bs4 import BeautifulSoup
from PIL import Image

import dotenv

class SBA:
    def __init__(self, email, password, end_date):
        """
        Initialize SBA with credentials and image directory

        Args:
            email: Login email
            password: Login password
            end_date: Date string in format 'YYYY-MM-DD' to filter products
        """
        self.base_url = "https://www.starbuyers-global-auction.com"
        self.session = None
        self.headers = {"Accept-Language": "ja"}
        self.email = email
        self.password = password
        self.end_date = end_date

    def login(self):
        """Log into the website"""
        self.session = requests.Session()

        login_url = f"{self.base_url}/login"
        response = self.session.get(login_url)
        soup = BeautifulSoup(response.text, "html.parser")

        login_form = soup.find("form", id="vue-form")
        email_field = login_form.find("input", {"name": "email"})
        password_field = login_form.find("input", {"name": "password"})
        csrf_token = login_form.find("input", {"name": "_token"})

        login_data = {
            email_field.get("name"): self.email,
            password_field.get("name"): self.password,
            csrf_token.get("name"): csrf_token.get("value")
        }

        response = self.session.post(login_url, data=login_data)

        return response.ok

    def collect_product_links(self):
        """
        Collect all product links for a given date
        """
        if not self.session:
            raise ValueError("Not logged in.")

        page_index = 1
        product_links = []

        while True:
            url = f"{self.base_url}/item?limit=100&exhibit_date_to={self.end_date}&has_own_memo=1&page={page_index}"
            response = self.session.get(url, headers=self.headers)

            if not response.ok:
                break

            soup = BeautifulSoup(response.text, "html.parser")
            product_a_tags = soup.select('[class="p-item-list__body__cell -name"] a[class="p-text-link"][href^="https"]')

            if len(product_a_tags) == 0:
                break

            links = [product_a_tag.get("href") for product_a_tag in product_a_tags]
            product_links.extend(links)
            page_index += 1

        return product_links

    def _get_names(self, product_data_string):
        """
        Extract brand name and product name from the product data string.

        Args:
            product_data_string: Raw JavaScript string containing product data

        Returns:
            tuple: A tuple containing (brand_name, product_name),
                   where brand_name is the first word and product_name is the rest
        """
        name_pattern = r"name: '([^']*)'"
        name_match = re.search(name_pattern, product_data_string)
        name_text = name_match.group(1)
        brand_name, product_name = re.split(r"\s", name_text, 1)
        return brand_name, product_name

    def _get_current_bidding_price(self, product_data_string):
        """
        Extract and format the current bidding price from the product data string.

        Args:
            product_data_string: Raw JavaScript string containing product data

        Returns:
            str: Formatted current bidding price with comma separators
        """
        current_bidding_price_pattern = r"current_bidding_price: '(\d+)'"
        current_bidding_price_match = re.search(current_bidding_price_pattern, product_data_string)
        current_bidding_price_text = current_bidding_price_match.group(1)
        current_bidding_price = "{:,}".format(int(current_bidding_price_text))
        return current_bidding_price

    def _get_ended_at(self, product_data_string):
        """
        Extract the end date from the product data string.

        Args:
            product_data_string: Raw JavaScript string containing product data

        Returns:
            str: End date in format 'MM/DD/YY', excluding time component
        """
        ended_at_pattern = r"end_at: '(\d+/\d+/\d+) \d+:\d+'"
        ended_at_match = re.search(ended_at_pattern, product_data_string)
        ended_at = ended_at_match.group(1)
        return ended_at

    def _get_data_rank(self, soup):
        """
        Extract the rank value from the product page HTML.

        Args:
            soup: BeautifulSoup object containing parsed HTML of the product page

        Returns:
            str: Value of the data-rank attribute from the first element with data-rank
        """
        data_rank = soup.select("[data-rank]")[0]
        data_rank_text = data_rank.get("data-rank")
        return data_rank_text

    def _get_memo(self, product_data_string):
        """
        Extract the memo text from the product data string.

        Args:
            product_data_string: Raw JavaScript string containing product data

        Returns:
            str: Memo text contained between backticks
        """
        memo_pattern = r'memo: `([^`]*)`'
        memo_match = re.search(memo_pattern, product_data_string)
        memo = memo_match.group(1)
        return memo

    def _extract_katakana_from_memo(self, memo):
        """
        Extract and validate katakana price code from the memo text.

        Args:
            memo: String containing memo text that may include katakana price code

        Returns:
            str: Valid katakana price code if found, empty string otherwise

        Notes:
            - Handles both regular (-) and full-width (－) hyphens
            - Handles both regular (~) and full-width (～) tildes
            - Valid katakana characters are: カフロクイハメウシ
            - Valid patterns include:
                - Only katakana: "フ-----"
                - Katakana with memo: "カク----　定22別"
                - Only memo: "お気に入り商品" or "アウトレット"

        Example:
            If memo is "カフ----～イハ--- 定価22000"
            Returns: "イハ---"
        """
        if "～" in memo or "~" in memo:
            katakana_pattern = r"[\w\-－]*[~～]([\w\-－]*)(?:\s[\w\W]*)?"
        else:
            katakana_pattern = r"([\w\-－]*)(?:\s[\w\W]*)?"

        katakana_match = re.search(katakana_pattern, memo)
        katakana = katakana_match.group(1)

        valid_chars = set("カフロクイハメウシ-－ミ～~")
        return katakana if all(char in valid_chars for char in katakana) else ""

    def _convert_katakana_into_price(self, katakana):
        """
        Convert katakana price code into formatted price string.

        Args:
            katakana: String containing katakana price code

        Returns:
            str: Formatted price string with comma separators if valid
                 katakana code provided, empty string otherwise

        Example:
            If katakana is "カフ---"
            Returns: "12,000"
        """
        if not katakana:
            return ""

        katakana_map = {
            "カ": "1", "フ": "2", "ロ": "3", "ク": "4", "イ": "5",
            "ハ": "6", "メ": "7", "ウ": "8", "シ": "9", "-": "0",
            "－": "0", "ミ": "0", "～": "", "~": ""
        }
        price = ""

        for char in katakana:
            if char in katakana_map:
                price += katakana_map[char]

        price = "{:,}".format(int(price))

        return price

    def _get_image(self, product_data_string):
        """
        Extract image URL, process the image, and return optimized image content.

        Args:
            product_data_string: Raw JavaScript string containing product data

        Returns:
            tuple: A tuple containing (image_content, filename), where:
                - image_content: Processed image as bytes if successful, None if failed
                - filename: Original filename from URL if successful, None if failed

        Notes:
            - Image is resized to max dimensions of 800x800 pixels
            - Uses LANCZOS resampling for high quality resizing
            - JPEG format with 80% quality and optimization
        """
        image_url_pattern = r"image_urls: JSON\.parse\('\[\\u0022(.*?)\\u0022"
        image_url_match = re.search(image_url_pattern, product_data_string)
        image_url = image_url_match.group(1)
        image_url = image_url.replace("\\\\\\/", "/")

        filename = os.path.basename(urlparse(image_url).path)

        response = requests.get(image_url)
        if response.ok:
            image = Image.open(io.BytesIO(response.content))
            max_size = (800, 800)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)

            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG', optimize=True, quality=80)
            img_byte_arr = img_byte_arr.getvalue()
            return img_byte_arr, filename

        return None, None

    def collect_product_data(self, product_links):
        """
        Collect product data for given product links

        Args:
            product_links: List of product URLs

        Returns:
            list: List of dictionaries containing product data
        """
        if not self.session:
            raise ValueError("Not logged in.")

        product_data = []
        print(f"Starting to process {len(product_links)} products...")

        for i, product_link in enumerate(product_links):
            print(f"Processing {i+1}/{len(product_links)}: {product_link}")

            if i > 0:
                delay = random.uniform(10, 30)
                print(f"  Waiting {delay:.1f} seconds to avoid rate limiting...")
                time.sleep(delay)

            try:
                response = self.session.get(product_link, headers=self.headers)
                if response.ok:
                    print(f"  ✓ Successfully accessed product page")
                    soup = BeautifulSoup(response.text, "html.parser")

                    script_tags = soup.select("script")
                    product_data_string = None

                    for script_tag in script_tags:
                        if script_tag.string and "window.item_data" in script_tag.string:
                            print(f"    Found product data in script tag")
                            product_data_string = script_tag.string
                            break

                    if not product_data_string:
                        print(f"  ✗ No window.item_data found in {len(script_tags)} script tags")
                        continue

                    print(f"  ✓ Product data script found, extracting data...")

                    brand_name, product_name = self._get_names(product_data_string)
                    current_bidding_price = self._get_current_bidding_price(product_data_string)
                    ended_at = self._get_ended_at(product_data_string)
                    data_rank = self._get_data_rank(soup)
                    memo = self._get_memo(product_data_string)
                    katakana = self._extract_katakana_from_memo(memo)
                    price = self._convert_katakana_into_price(katakana)
                    image = self._get_image(product_data_string)

                    product_datum = {
                        "brand_name": brand_name,
                        "product_name": product_name,
                        "current_bidding_price": current_bidding_price,
                        "ended_at": ended_at,
                        "data_rank": data_rank,
                        "memo": memo,
                        "price": price,
                        "image": image,
                        "product_link": product_link
                    }
                    product_data.append(product_datum)
                    print(f"  ✓ Successfully processed: {brand_name} {product_name}")
                else:
                    print(f"  ✗ Failed to access product page: {response.status_code}")
            except Exception as e:
                print(f"  ✗ Error processing product: {str(e)}")
                continue

        print(f"Processing complete. Successfully processed: {len(product_data)} products")
        return product_data


def main():
    dotenv.load_dotenv(dotenv_path=".env.local")
    EMAIL = os.environ["EMAIL"]
    PASSWORD = os.environ["PASSWORD"]
    # Change end_date accordingly if you want to test the script stand-alone.
    sba = SBA(email=EMAIL, password=PASSWORD, end_date="2025-05-17")

    if sba.login():
        product_links = sba.collect_product_links()

        sba.collect_product_data(product_links)

if __name__ == "__main__":
    main()
