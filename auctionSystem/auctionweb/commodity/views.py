#coding:utf-8

import memcache
import json

from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.core import serializers
from django.template.loader import render_to_string
from django.conf import settings
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

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
            return redirect("clist")
    C = {"cform": cform}   
    return render(request, template_name, C)

def change(request, lot_nu, template_name):
    try:
        com_obj = Commodity.objects.get(lot=lot_nu)
    except com_obj.DoesNotExist:
        return HttpResponse("does't exist")
    if request.method == "POST":
        cform = CommodityForm(request.POST, instance=com_obj)
        if cform.is_valid():
            cform.save()
            return redirect("clist")
    cform = CommodityForm(instance=com_obj)
    C = {"cform": cform, "modify": "true", "lot_nu": lot_nu}
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
    return ajax_success(html=html)

@csrf_exempt
def delete(request):
    if request.method != "POST":
        raise Http404
    lot_nu_list = [str(lot) for lot in json.loads(request.POST.get("data", ''))]
    del_list = Commodity.objects.filter(lot__in=lot_nu_list)
    del_list.delete()
    return ajax_success()

def ajax_list_data(request):
    commodity_list = Commodity.objects.exclude(is_invoice=1).order_by("lot")
    back_list = [i.toDICT() for i in commodity_list]
    return ajax_success(back_list)

def list(request, template_name):
    commodity_list = Commodity.objects.exclude(is_invoice=1).order_by("lot")
    return render(request, template_name, {"c_list": commodity_list})
