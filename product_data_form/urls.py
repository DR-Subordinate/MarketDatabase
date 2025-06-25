from django.urls import path

from . import views

app_name = "product_data_form"
urlpatterns = [
    path("", views.main, name="index"),
    path("main/<str:market_name>_<str:market_date>", views.product_main, name="product_main"),
    path("register/<str:market_name>_<str:market_date>", views.product_register, name="product_register"),
    path("search/", views.search, name="search"),
]
