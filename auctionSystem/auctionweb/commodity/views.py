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
from django.contrib.auth.decorators import login_required

from auctionweb.models import Customer, PeelField, Commodity, Invoice, AuctionField
from .forms import CommodityForm
from auctionweb.shortcuts.ajax import ajax_success, ajax_error
from auctionweb import mckeys


def add(request, template_name):
    cform = CommodityForm()
    if request.method == "POST":
        mem = memcache.Client(settings.MEMCACHES)
        cform = CommodityForm(request.POST)
        if cform.is_valid():
            try:
                auction_obj = AuctionField.objects.get(name=request.POST.get('auction'))
            except AuctionField.DoesNotExist:
                return Http404
            c_obj = cform.save(commit=False)
            c_obj.auction = auction_obj
            c_obj.save()
            mem.set("last_form", request.POST)
            return redirect("clist")
        print cform.errors
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
    print last_form_data
    cform = CommodityForm(last_form_data)
    html = render_to_string(
        template_name,
        {"cform": cform},
        context_instance=RequestContext(request)
    )
    print html
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

@login_required
def list(request, template_name):
    commodity_list = Commodity.objects.exclude(is_invoice=1).order_by("lot")
    return render(request, template_name, {"c_list": commodity_list})

@csrf_exempt
def get_select(request):
    if request.method == "POST":
        auction = json.loads(request.POST.get("data")).get("auction")
        try:
            auction_obj = AuctionField.objects.get(name=auction)
        except AuctionField.DoesNotExist:
            return ajax_error("auction obj does not exist")
        variety = [v.name for v in auction_obj.variety_set.all()]
        return ajax_success({"id_variety": variety})
    auction_name_list = [auc.name for auc in AuctionField.objects.all()]
    choice_data = {
        "id_auction": auction_name_list,
        "id_size": ['1-20', '20-40', '50-60'],
        "id_level": ["特等品", "一级品", "二级品"],
        "id_color": ["red", "white", "yellow", "golden"],
        "id_definition": ["模糊", "清晰", "微模糊", "微清晰"],
        "id_sex": ["female", "male"]
    }
    return ajax_success(choice_data)
