from django.urls import path

from . import views

app_name = "product_data_form"
urlpatterns = [
    path("", views.index, name="index"),
    path("<str:market_name> <str:market_date>", views.save_product, name="product"),
    path("price/", views.save_price, name="price"),
    path("search/", views.search, name="search"),
    path("edit/", views.edit, name="edit"),
]
