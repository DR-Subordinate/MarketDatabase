from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, portrait
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

from django.contrib.staticfiles.finders import find

FONT_FILE = "NotoSerifJP-Bold.ttf"
FONT_FILE_PATH = find(FONT_FILE)


def setup_page(pdf_buffer):
    # Create a new A4 PDF file
    page = canvas.Canvas(pdf_buffer, pagesize=portrait(A4))

    pdfmetrics.registerFont(TTFont("NotoSerifJP-Bold", FONT_FILE_PATH))

    page.setFont("NotoSerifJP-Bold", 9)
    page.setStrokeColorRGB(0.0, 0.0, 0.0)
    page.setLineWidth(1)

    return page


def draw_header(page):
    current_date = datetime.now().strftime('%Y/%m/%d')

    page.drawString(450, 750, "発行日") # From bottom left
    page.drawString(500, 750, current_date) # Insert data here (current date)

    page.line(450, 748, 550, 748)

    page.drawString(450, 735, "No 1")
    page.line(450, 733, 550, 733)


def draw_title(page):
    page.setFont("NotoSerifJP-Bold", 18)
    page.drawString(30, 700, "請求書兼納品書")


def draw_client_info(page):
    page.setFont("NotoSerifJP-Bold", 9)
    page.drawString(30, 660, "株式会社 ディーアール")
    page.drawString(300, 660, "御中")
    page.line(30, 655, 330, 655)


def draw_market_info(page, market):
    page.drawString(30, 630, "件名:")
    page.drawString(60, 630, f"{market.name} {market.date}") # Insert data here (market name and date)
    page.line(30, 625, 330, 625)


def draw_invoice_statement(page):
    page.drawString(30, 580, "下記の通りご請求申し上げます。")


def draw_company_info(page):
    page.drawString(450, 660, "株式会社あきんど")
    page.drawString(450, 645, "住所: 〒542-0085")
    page.drawString(450, 630, "大阪市中央区心斎橋筋2-2-14")
    page.drawString(450, 615, "TEL: 06-6211-4711")
    page.drawString(450, 580, "登録番号: T9120001163767")


def draw_total_amount(page, total_amount, tax):
    page.drawString(30, 550, "金額")
    page.setFont("NotoSerifJP-Bold", 14)
    page.drawString(200, 550, f"¥{total_amount + tax:,} (税込)") # Insert data here (total price)
    page.line(30, 540, 330, 540)
    page.line(30, 537, 330, 537)


def create_table_data(bidden_products):
    data = [['ブランド名', '商品名', '数量', '単価', '金額']]
    for product in bidden_products:
        data.append([
            product.brand_name,
            f"{product.name} {product.model_number}",
            '1',
            product.price,
            product.price
        ])
    return data


def create_table_style():
    return TableStyle([
        # Header row (row 0) alignment: center
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'NotoSerifJP-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        
        # Content alignment
        ('ALIGN', (0, 1), (1, -1), 'LEFT'),  # Left align for ブランド名 and 商品名 content
        ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),  # Right align for 数量, 単価, and 金額 content
        
        # Font and size for content
        ('FONTNAME', (0, 1), (-1, -1), 'NotoSerifJP-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
        
        # Grid lines for the entire table
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        
        # Vertical alignment for the entire table
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])


def draw_table(page, data, style):
    table = Table(data, colWidths=[1.3*inch, 3.5*inch, 0.5*inch, 1*inch, 1*inch])
    table.setStyle(style)

    _, table_height = table.wrapOn(page, 7.3*inch, 9*inch) # Adjust width as needed

    # Calculate the starting y-position for the table
    # The "金額" text is at y=550, and I want to start the table a bit below it
    table_start_y = 520 # Adjust this value if needed to fine-tune the position
    # Draw the table on the canvas
    table.drawOn(page, 30, table_start_y - table_height)

    return table_start_y, table_height


def draw_summary(page, table_start_y, table_height, bidden_products, total_amount, tax):
    """Draw the summary section below the table."""
    summary_y = table_start_y - table_height - 10 # 10 is a margin below the table

    page.rect(410, summary_y - 60, 146, 60, fill=0, stroke=1)

    page.setFont("NotoSerifJP-Bold", 9)

    page.rect(349, summary_y - 20, 60, 20, fill=0, stroke=1)
    page.drawString(355, summary_y - 15, "数量")
    page.drawRightString(407, summary_y - 15, str(bidden_products.count())) # Insert data here

    page.drawString(412, summary_y - 15, "小計")
    page.drawRightString(545, summary_y - 15, f"{total_amount:,}") # Insert data here
    page.line(410, summary_y - 20, 555, summary_y - 20)

    page.drawString(412, summary_y - 35, "消費税(10%対象)")
    page.drawRightString(545, summary_y - 35, f"{tax:,}") # Insert data here
    page.line(410, summary_y - 40, 555, summary_y - 40)

    page.setFont("NotoSerifJP-Bold", 10)
    page.drawString(412, summary_y - 55, "税込合計")
    page.drawRightString(545, summary_y - 55, f"¥{total_amount + tax:,}") # Insert data here


def generate_invoice_pdf(pdf_buffer, market, bidden_products):
    page = setup_page(pdf_buffer)

    draw_header(page)
    draw_title(page)
    draw_client_info(page)
    draw_market_info(page, market)
    draw_invoice_statement(page)
    draw_company_info(page)

    total_amount = sum(int(product.price.replace(',', '')) for product in bidden_products)
    tax = int(total_amount * 0.1)

    draw_total_amount(page, total_amount, tax)

    table_data = create_table_data(bidden_products)
    table_style = create_table_style()

    table_start_y, table_height = draw_table(page, table_data, table_style)

    draw_summary(page, table_start_y, table_height, bidden_products, total_amount, tax)

    page.save()


if __name__ == "__main__":
    generate_invoice_pdf()
