#coding:utf-8

import memcache
import json

from django.shortcuts import render, redirect
from django.core import serializers
from django.template.loader import render_to_string
from django.conf import settings
from django.template import RequestContext

from auctionweb.models import Customer, PeelField, Commodity, Invoice
from .forms import CommodityForm
from auctionweb.shortcuts.ajax import ajax_success, ajax_error
from auctionweb import mckeys


def add(request, template_name):
    cform = CommodityForm()
    if request.method == "POST":
        mem = memcache.Client(settings.MEMCACHES)
        cform = CommodityForm(request.POST)
        if cform.is_valid():
            cform.save()
            mem.set("last_form", request.POST)
            return redirect("default")
    C = {"cform": cform}   
    return render(request, template_name, C)

def copy_last_form(request, template_name):
    """复制上一个lotform"""
    mem = memcache.Client(settings.MEMCACHES)
    last_form_data = mem.get(mckeys.COPY_LAST_FORM)
    cform = CommodityForm(last_form_data)
    html = render_to_string(
        template_name,
        {"cform": cform},
        context_instance=RequestContext(request)
    )
    print html
    return ajax_success(html=html)

def clist(request):
    commodity_list = Commodity.objects.exclude(is_invoice=1).order_by("lot")
    back_list = [i.toDICT() for i in commodity_list]
    return ajax_success(back_list)
