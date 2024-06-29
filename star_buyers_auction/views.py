from django.shortcuts import render

def index(request):
    return render(request, "star_buyers_auction/index.html")
