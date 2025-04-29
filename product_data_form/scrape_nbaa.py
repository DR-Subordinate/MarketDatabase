import os
import re
import io
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from PIL import Image

import dotenv

class NBAA:
    def __init__(self, email, password):
        """
        """
        self.base_url = "https://member.nbaa.jp"
        self.session = None
        self.email = email
        self.password = password

    def login(self):
        """Log into the website"""
        self.session = requests.Session()

        login_url = f"{self.base_url}/login"
        response = self.session.get(login_url)
        soup = BeautifulSoup(response.text, "html.parser")

        email_field = soup.find("input", id="mail")
        password_field = soup.find("input", id="password")
        csrf_token = soup.find("input", {"name": "_csrfToken"})

        login_data = {
            email_field.get("name"): self.email,
            password_field.get("name"): self.password,
            csrf_token.get("name"): csrf_token.get("value")
        }

        response = self.session.post(login_url, data=login_data)

        return response.ok

    def _get_winning_bid(self, date, box_number, branch_number):
        """Get winning bid for a specific auction item"""
        if not self.session:
            raise ValueError("Not logged in.")

        url = f"{self.base_url}/values?search_free_word=&search_item_id=&search_brand_name=&search_shuppin_name=&search_model_no=&search_kaisai_date={date}&search_box_no={box_number}&search_eda_no={branch_number}&search_place_from=&search_place_to="
        response = self.session.get(url)

        if not response.ok:
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        winning_bid_elem = soup.find("span", class_="values__list-item-text-price-num")

        if winning_bid_elem:
            winning_bid = winning_bid_elem.text.strip().replace("¥", "")
            return winning_bid

        return None

    def _get_image(self, date, box_number, branch_number):
        """Retrieve and save the image"""
        if not self.session:
            raise ValueError("Not logged in.")

        image_date = date.replace("-", "")  # Convert YYYY-MM-DD to YYYYMMDD
        image_url = f"https://image.nbaa.jp/{image_date}/{box_number}-{branch_number}.jpg"

        response = self.session.get(image_url, stream=True)

        if not response.ok:
            return None

        try:
            image = Image.open(io.BytesIO(response.content))
            filename = f"{image_date}_{box_number}-{branch_number}.jpg"
            image.save(filename)
            return filename
        except Exception as e:
            print(f"Error saving image: {e}")
            return None

    def collect_product_data(self, dates, box_numbers, branch_numbers):
        """Collect data for multiple products"""
        if not self.session:
            raise ValueError("Not logged in.")

        if not (len(dates) == len(box_numbers) == len(branch_numbers)):
            raise ValueError("All input lists must have the same length")

        results = []

        for i in range(len(dates)):
            date = dates[i]
            box_number = box_numbers[i]
            branch_number = branch_numbers[i]

            product_data = {
                "date": date,
                "box_number": box_number,
                "branch_number": branch_number
            }

            # Get winning bid
            winning_bid = self._get_winning_bid(date, box_number, branch_number)
            product_data["winning_bid"] = winning_bid

            # Get and save image
            image_path = self._get_image(date, box_number, branch_number)
            product_data["image_path"] = image_path

            results.append(product_data)
            print(f"Collected data for product {i+1}/{len(dates)}")

        return results




def main():
    dotenv.load_dotenv(dotenv_path=".env.local")
    EMAIL = os.environ["EMAIL_NBAA"]
    PASSWORD = os.environ["PASSWORD_NBAA"]
    nbaa = NBAA(email=EMAIL, password=PASSWORD)

    if nbaa.login():
        print("Successfully logged in!")

        dates = ["2025-03-25", "2025-03-25"]
        box_numbers = ["160", "206"]
        branch_numbers = ["3", "2"]

        products = nbaa.collect_product_data(dates, box_numbers, branch_numbers)

        print("\nScraping Results:")
        for i, product in enumerate(products):
            print(f"\nProduct {i+1}:")
            print(f"Winning Bid: {product['winning_bid']}")
            print(f"Image Path: {product['image_path']}")

if __name__ == "__main__":
    main()
