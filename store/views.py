from django.http import HttpResponse, HttpRequest
from django.shortcuts import render
from django.db.models.aggregates import Max, Sum, Avg, Count
from django.db.models import Value, Func, F

from rest_framework.response import Response
from .models import Customer, Product, Collection
from django.db.models import Q, F


def index(request: HttpRequest):
    query_set = Collection.objects.all().annotate(new_field=Count("product__title"))
    

    # print(query_set)
    return render(
        request,
        "index.html",
        {"name": "samir", "products": list(query_set)},
    )
