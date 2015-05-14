#coding:utf-8

import memcache
import json

from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.conf import settings
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

from auctionweb.models import Customer, PeelField, Commodity, Invoice
from auctionweb.shortcuts.ajax import ajax_success, ajax_error
from auctionweb import mckeys

@csrf_exempt
def voadd(request, template_name):
    if request.method == "POST":
        new_rate = request.POST.get("newRate")
        lot_nu_invoice = request.POST.get("all_lot_nu")
        comm_list = Commodity.objects.filter(lot__in=lot_nu_invoice.split(","))
