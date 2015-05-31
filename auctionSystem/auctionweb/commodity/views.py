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

def add(request, auction_id, template_name):
    cform = CommodityForm()
    request.session["auction_id"] = auction_id
    try:
        auc_obj = AuctionField.objects.get(pk=auction_id)
    except AuctionField.DoesNotExist:
        raise Http404
    auc_varietys = auc_obj.variety_set.all()
    if request.method == "POST":
        mem = memcache.Client(settings.MEMCACHES)
        cform = CommodityForm(request.POST)
        if cform.is_valid():
            c_obj = cform.save(commit=False)
            c_obj.auction = auc_obj
            c_obj.save()
            mem.set("last_form", request.POST)
            return ajax_success({"success": True})
        else:
            html = render_to_string(
                "auctionweb/commodity/modform.html",
                {"cform": cform, "auc_varietys": auc_varietys}, 
                context_instance=RequestContext(request)
            )
            return ajax_success({"html": html})
    C = {"cform": cform, "auc_varietys": auc_varietys}   
    return render(request, template_name, C)

def change(request, lot_nu, template_name):
    try:
        com_obj = Commodity.objects.get(pk=lot_nu)
    except Commodity.DoesNotExist:
        raise Http404
    if request.method == "POST":
        print "22222222"
        cform = CommodityForm(request.POST, instance=com_obj)
        if cform.is_valid():
            cform.save()
            return ajax_success({"modify": True})
        else:
            print cform.errors
    auc_varietys = com_obj.auction.variety_set.all()
    cform = CommodityForm(instance=com_obj)
    C = {
        "cform": cform, 
        "variety": com_obj.types,
        "auc_varietys": auc_varietys
    }
    return render(request, template_name, C)

def copy_last_form(request, template_name):
    """复制上一个lotform"""
    auction_id = request.session.get("auction_id")
    try:
        auc_obj = AuctionField.objects.get(pk=auction_id)
        varietys = auc_obj.variety_set.all()
    except AuctionField.DoesNotExist:
        raise Http404
    print varietys
    mem = memcache.Client(settings.MEMCACHES)
    last_form_data = mem.get(mckeys.COPY_LAST_FORM)
    copy_form_data = last_form_data.copy()
    copy_form_data.pop("lot")
    cform = CommodityForm(copy_form_data)
    html = render_to_string(
        template_name,
        {
            "cform": cform, 
            "auc_varietys": varietys
        },
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

def ajax_list_data(request, auction_id):
    commodity_list = Commodity.objects.filter(auction__id=auction_id).exclude(is_invoice=1).order_by("lot")
    back_list = [i.toDICT() for i in commodity_list]
    return ajax_success(back_list)

@login_required
def list(request, template_name):
    mem = memcache.Client(settings.MEMCACHES)
    begin_rate = mem.get("begin_rate")
    com_rate = mem.get("commpression_rate")
    auction_list = AuctionField.objects.all().order_by("id")
    C = {
        "begin_rate": begin_rate if begin_rate else '',
        "com_rate": com_rate if com_rate else '',
        "auctions": auction_list
    }
    print template_name
    return render(request, template_name, C)

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
