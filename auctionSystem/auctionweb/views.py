

from django.core import serializers
from django.shortcuts import render
from auctionweb.shortcuts.ajax import ajax_success
import json

# Create your views here.
from auctionweb.models import Customer, PeelField, Commodity, Invoice

def index(request, template_name):
    commodity_list = Commodity.objects.exclude(is_invoice=1).order_by("lot")
    return render(request, template_name, {"c_list": commodity_list})

