import os
import re
import io
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from PIL import Image

import dotenv

class SBA:
    def __init__(self, email, password, end_date, image_directory):
        """
        Initialize SBA with credentials and image directory

        Args:
            email: Login email
            password: Login password
            end_date: Date string in format 'YYYY-MM-DD' to filter products
            image_directory: Directory to save product images
        """
        self.base_url = "https://www.starbuyers-global-auction.com"
        self.session = None
        self.headers = {"Accept-Language": "ja"}
        self.email = email
        self.password = password
        self.end_date = end_date
        self.image_directory = image_directory

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
        ended_at_pattern = r"ended_at: '(\d+/\d+/\d+) \d+:\d+'"
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

    def _save_image(self, product_data_string):
        """
        Extract image URL from product data and save a resized version.

        Args:
            product_data_string: Raw JavaScript string containing product data

        Returns:
            str: Path to saved image file if successful, None otherwise

        Notes:
            - Image is resized to max dimensions of 800x800 pixels
            - Uses LANCZOS resampling for high quality resizing
            - Saved with optimization and 80% JPEG quality
            - Images are saved to self.image_directory path
        """
        image_url_pattern = r"image_urls: JSON\.parse\('\[\\u0022(.*?)\\u0022"
        image_url_match = re.search(image_url_pattern, product_data_string)
        image_url = image_url_match.group(1)
        image_url = image_url.replace("\\\\\\/", "/")

        os.makedirs(self.image_directory, exist_ok=True)
        filename = os.path.basename(urlparse(image_url).path)

        response = requests.get(image_url)
        if response.ok:
            image = Image.open(io.BytesIO(response.content))
            max_size = (800, 800)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            filepath = os.path.join(self.image_directory, filename)
            image.save(filepath, optimize=True, quality=80)
            return filepath # Delete this line later!

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

        for product_link in product_links:
            response = self.session.get(product_link, headers=self.headers)
            if response.ok:
                soup = BeautifulSoup(response.text, "html.parser")
                product_data_string = soup.select("script")[2].string

                brand_name, product_name = self._get_names(product_data_string)
                current_bidding_price = self._get_current_bidding_price(product_data_string)
                ended_at = self._get_ended_at(product_data_string)
                data_rank = self._get_data_rank(soup)
                memo = self._get_memo(product_data_string)
                katakana = self._extract_katakana_from_memo(memo)
                price = self._convert_katakana_into_price(katakana)
                image = self._save_image(product_data_string)

                product_datum = {
                    "brand_name": brand_name,
                    "product_name": product_name,
                    "current_bidding_price": current_bidding_price,
                    "ended_at": ended_at,
                    "data_rank": data_rank,
                    "memo": memo,
                    "price": price,
                    "image": image
                }
                product_data.append(product_datum)

        return product_data


def main():
    dotenv.load_dotenv(dotenv_path=".env.local")
    EMAIL = os.environ["EMAIL"]
    PASSWORD = os.environ["PASSWORD"]
    IMAGE_DIRECTORY = os.environ["IMAGE_DIRECTORY"]
    sba = SBA(email=EMAIL, password=PASSWORD, end_date="2024-12-14", image_directory=IMAGE_DIRECTORY)

    if sba.login():
        product_links = sba.collect_product_links()

        product_data = sba.collect_product_data(product_links)

        print(product_data)
        print(f"Total products found: {len(product_data)}")

if __name__ == "__main__":
    main()
