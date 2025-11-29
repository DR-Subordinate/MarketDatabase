import os
from urllib.parse import urljoin
import re

import requests
from bs4 import BeautifulSoup
import dotenv


class Komehyo:
    def __init__(self, email, password):
        """
        Scraper for deal.komehyo-auction.com

        Args:
            email: Login email
            password: Login password
        """
        self.base_url = "https://deal.komehyo-auction.com"
        self.session = None
        self.email = email
        self.password = password

    def login(self):
        """
        Log into the Komehyo auction site.

        Returns:
            bool: True if login appears successful, False otherwise.
        """
        self.session = requests.Session()

        # Minimal headers so we don't look like a bot with no UA
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
        })

        login_url = f"{self.base_url}/login"
        response = self.session.get(login_url)

        print("GET /login status:", response.status_code, response.url)

        if not response.ok:
            # If this still prints, the site is blocking /login for some reason
            return False

        soup = BeautifulSoup(response.text, "html.parser")

        login_form = soup.find("form", id="login")
        if not login_form:
            print("login form not found")
            return False

        token_input = login_form.find("input", {"name": "_token"})
        csrf_token = token_input.get("value") if token_input else None

        if not csrf_token:
            print("csrf token not found")
            return False

        login_data = {
            "email": self.email,
            "password": self.password,
            "_token": csrf_token,
        }

        # Use the form's action explicitly (even though it's the same URL)
        action = login_form.get("action") or login_url
        post_url = action if action.startswith("http") else f"{self.base_url}{action}"

        login_response = self.session.post(post_url, data=login_data)

        print("POST /login status:", login_response.status_code, login_response.url)

        return login_response.ok

    def collect_product_links(self, mylist_url):
        """
        Collect product detail links from a Komehyo mylist / favorites page.
        """
        if not self.session:
            raise ValueError("Not logged in. Call login() first.")

        response = self.session.get(mylist_url)
        if not response.ok:
            print(f"Failed to fetch mylist page: {response.status_code} {response.url}")
            return []

        soup = BeautifulSoup(response.text, "html.parser")

        # <div class="grid-item__img-container ...">
        #   <a href="/item/...">...</a>
        # </div>
        link_tags = soup.select(".grid-item__img-container a[href*='/item/']")

        product_links = []
        for a in link_tags:
            href = a.get("href")
            if not href:
                continue
            product_links.append(urljoin(self.base_url, href))

        # Deduplicate while preserving order
        unique_links = []
        seen = set()
        for url in product_links:
            if url in seen:
                continue
            seen.add(url)
            unique_links.append(url)

        return unique_links

    def _get_lot_no(self, soup):
        """
        Extract ロットNo from the product detail page.
        """
        table = soup.find("table", class_="product-info-tbl")
        if not table:
            return ""

        for row in table.find_all("tr"):
            th = row.find("th")
            td = row.find("td")
            if not th or not td:
                continue

            header = th.get_text(strip=True)
            if header == "ロットNo":
                return td.get_text(strip=True)

        return ""

    def _get_brand_name(self, soup):
        """
        Extract brand name as katakana from the product detail page.

        Strategy:
        - Take the text in .input-price__title
        - Normalize and compare its prefix against BRAND_MAP keys (case-insensitive)
        - If matched, return the katakana name
        - If no match, fall back to the first token (original text) or "".
        """
        BRAND_MAP = {
            "HERMES": "エルメス",
            "LOUIS VUITTON": "ルイヴィトン",
            "GOYARD": "ゴヤール",
            "GUCCI": "グッチ",
            "CHANEL": "シャネル",
            "FENDI": "フェンディ",
            "CELINE": "セリーヌ",
            "CHRISTIAN DIOR": "クリスチャン・ディオール",
            "MIU MIU": "ミュウミュウ",
            "PRADA": "プラダ",
        }
        full = ""

        # 1) Prefer the visible title div
        title_div = soup.find("div", class_="input-price__title")
        if title_div:
            full = title_div.get_text(strip=True)

        # 2) Fallback: any element with data-title
        if not full:
            el = soup.find(attrs={"data-title": True})
            if el:
                full = el.get("data-title", "").strip()

        if not full:
            return ""

        # Normalize spaces and uppercase for comparison
        normalized = " ".join(full.split())  # collapse multiple spaces
        upper = normalized.upper()

        # 3) Try to match dictionary keys as prefix, longest first
        for eng_name in sorted(BRAND_MAP.keys(), key=len, reverse=True):
            if upper.startswith(eng_name):
                return BRAND_MAP[eng_name]

        # 4) Fallback: first token (original text), if you want *something* even for unknown brands
        parts = re.split(r"\s", normalized, maxsplit=1)
        return parts[0] if parts else ""

    def _get_serial_number(self, soup):
        """
        Extract シリアル／製番 from the product detail page.
        """
        table = soup.find("table", class_="product-info-tbl")
        if not table:
            return ""

        for row in table.find_all("tr"):
            th = row.find("th")
            td = row.find("td")
            if not th or not td:
                continue

            header = th.get_text(strip=True)
            if header == "シリアル／製番":
                return td.get_text(strip=True)

        return ""

    def _get_rank(self, soup):
        """
        Extract ランク from the product detail page.
        """
        table = soup.find("table", class_="product-info-tbl")
        if not table:
            return ""

        for row in table.find_all("tr"):
            th = row.find("th")
            td = row.find("td")
            if not th or not td:
                continue

            header = th.get_text(strip=True)
            if header == "ランク":
                return td.get_text(strip=True)

        return ""

    def _get_memo(self, soup):
        """
        Extract メモ from the product detail page.
        """
        memo_container = soup.find("div", class_="memo")
        if not memo_container:
            return ""

        # 1) Prefer the display text node
        text_div = memo_container.find("div", class_="js-memo-text")
        if text_div:
            text = text_div.get_text(strip=True)
            if text:
                return text

        # 2) Fallback: textarea content (e.g. when editing)
        textarea = memo_container.find("textarea", class_="js-memo-input")
        if textarea and textarea.string:
            text = textarea.string.strip()
            if text:
                return text

        return ""

    def _get_current_price(self, soup):
        """
        Extract 現在価格 from the product detail page.

        Returns:
            str: Price with comma separators, e.g. "2,500,000".
        """
        elem = soup.find(attrs={"data-current-price": True})
        if not elem:
            return ""

        raw_val = elem.get("data-current-price")
        if not raw_val:
            return ""

        raw_val = raw_val.strip()

        if not raw_val.isdigit():
            return ""

        return "{:,}".format(int(raw_val))

    def _get_image(self, soup):
        """
        Extract the first (main) product image from the carousel.

        Returns:
            (image_bytes, filename) or (None, None) on failure.
        """
        # Prefer: main carousel active image
        img_tag = soup.select_one(
            "#carousel-image .carousel-item.active img.js-carousel-img"
        )

        # Fallback: any product image from the CDN, just in case the structure changes
        if not img_tag:
            img_tag = soup.find("img", src=re.compile(r"cdn\.deal\.komehyo-auction\.com"))

        if not img_tag:
            return None, None

        src = img_tag.get("src")
        if not src:
            return None, None

        image_url = urljoin(self.base_url, src)

        resp = self.session.get(image_url)
        if not resp.ok:
            print(f"  ✗ Failed to fetch image: {resp.status_code}")
            return None, None

        # Strip query params if they ever exist
        filename = image_url.split("/")[-1].split("?")[0]

        return resp.content, filename

    def collect_product_data(self, product_links):
        """
        Visit each product detail page and collect product data.

        Currently collects:
            - lot_no (ロットNo)
            - brand_name (カタカナ)
            - serial_number (シリアル／製番)
            - rank (ランク)
            - memo (メモ)
            - current_price (現在価格)
            - image (bytes + filename)
            - product_link (for reference)
        """
        if not self.session:
            raise ValueError("Not logged in. Call login() first.")

        results = []
        print(f"Starting to process {len(product_links)} products...")

        for i, url in enumerate(product_links):
            print(f"Processing {i+1}/{len(product_links)}: {url}")

            response = self.session.get(url)
            if not response.ok:
                print(f"  ✗ Failed to access product page: {response.status_code}")
                continue

            soup = BeautifulSoup(response.text, "html.parser")

            lot_no = self._get_lot_no(soup)
            brand_name = self._get_brand_name(soup)
            serial_number = self._get_serial_number(soup)
            rank = self._get_rank(soup)
            memo = self._get_memo(soup)
            current_price = self._get_current_price(soup)
            image_content, image_filename = self._get_image(soup)

            product_data = {
                "lot_no": lot_no,
                "brand_name": brand_name,
                "serial_number": serial_number,
                "rank": rank,
                "memo": memo,
                "current_price": current_price,
                "image": (image_content, image_filename),
                "product_link": url,
            }

            results.append(product_data)
            print(
                f"  ✓ lot_no: {lot_no}, "
                f"brand_name: {brand_name}, "
                f"serial_number: {serial_number}, "
                f"rank: {rank}, "
                f"memo: {memo}, "
                f"current_price: {current_price}, "
                f"image: {bool(image_content)} ({image_filename})"
            )

        print(f"Processing complete. Successfully processed: {len(results)} products")
        return results


def main():
    dotenv.load_dotenv(dotenv_path=".env.local")
    EMAIL_KOMEHYO = os.environ.get("EMAIL_KOMEHYO")
    PASSWORD_KOMEHYO = os.environ.get("PASSWORD_KOMEHYO")

    komehyo = Komehyo(email=EMAIL_KOMEHYO, password=PASSWORD_KOMEHYO)

    if komehyo.login():
        print("Successfully logged in to Komehyo!")

        mylist_url = "https://deal.komehyo-auction.com/mylist/AP0000000737?filter=favorite"
        links = komehyo.collect_product_links(mylist_url)

        print(f"Found {len(links)} product links:")

        products = komehyo.collect_product_data(links)

        for p in products[:3]:
            image_ok = p["image"][0] is not None
            print(
                p["product_link"], "->",
                p["lot_no"], "/",
                p["brand_name"], "/",
                p["serial_number"], "/",
                p["rank"], "/",
                p["memo"], "/",
                p["current_price"], "/",
                f"image_ok={image_ok}, filename={p['image'][1]}"
            )
    else:
        print("Failed to log in to Komehyo.")


if __name__ == "__main__":
    main()
