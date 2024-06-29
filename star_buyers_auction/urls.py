from django.urls import path

from . import views

app_name = "star_buyers_auction"
urlpatterns = [
    path("sba/", views.index, name="index"),
]
