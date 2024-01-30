from django.urls import path

from . import views

app_name = "product_data_form"
urlpatterns = [
    path("", views.index, name="index"),
]
