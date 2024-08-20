from django.urls import path

from . import views

app_name = "product_data_form"
urlpatterns = [
    path("main/", views.main, name="main"),
    path("main/<str:market_name>_<str:market_date>", views.product_main, name="product_main"),
    path("register/<str:market_name>_<str:market_date>", views.product_register, name="product_register"),
    path("", views.index, name="index"),
    path("search/", views.search, name="search"),
]
