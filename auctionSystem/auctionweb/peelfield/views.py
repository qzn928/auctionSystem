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

from auctionweb.models import *
from .forms import PeelFieldForm
from auctionweb.shortcuts.ajax import ajax_success, ajax_error


def peel_list(request, template_name):
    peel_list = PeelField.objects.all()
    peel_inform_list = PeelInform.objects.all()
    C = {
        "peel_list": peel_list,
        "peel_inform_list": peel_inform_list
    }
    return render(request, template_name, C)

def com_list_by_peelname(request, template_name):
    '''获取所有的削皮场对象, 分类'''
    all_peelfield_obj = PeelField.objects.all()
    C = {"all_peelfield_obj": all_peelfield_obj}
    return render(request, template_name, C)

def get_classify_data(request):
    '''获取peelfield页列表信息'''
    back_data = {}
    all_invoice_obj = Invoice.objects.exclude(is_pre=1)
    for v in all_invoice_obj:
        data = {}
        commodity_info = v.get_commodity_info()
        com_obj = commodity_info.get("commodity")
        peel_id = com_obj.peel_field.pk
        data["auction"] = com_obj.auction.name
        data["peel_inform"] = com_obj.peel_inform.name
        data["peel_price"] = commodity_info.get("peel_price")
        data["peel_status"] = v.get_peel_status
        data.update(v.toDICT())
        if peel_id in back_data:
            back_data[peel_id].append(data)
        else:
            back_data[peel_id] = [data]
    return ajax_success(back_data)

def get_invoice_data(request):
    '''pre dressing 页面datatables 发票列表信息'''
    invoice_list = Invoice.objects.exclude(is_pre=1)
    back_list = [i.toDICT() for i in invoice_list]
    return ajax_success(back_list)

def add_peel_field(request, invoice_id):
    '''添加削皮场和削皮指示, 一张发票相同'''
    if request.method != "POST":
        raise Http404
    peel_field = request.POST.get("peel_field")
    peel_inform = request.POST.get("peel_inform")
    try:
        peel_field_obj = PeelField.objects.get(pk=peel_field)
        peel_inform_obj = PeelInform.objects.get(pk=peel_inform)
        invoice_obj = Invoice.objects.get(pk=invoice_id)
    except:
        return ajax_error("object does not exist")

    com_obj_list =  invoice_obj.commodity_set.all() 
    for com_obj in com_obj_list:
        com_obj.peel_field = peel_field_obj
        com_obj.peel_inform = peel_inform_obj
        com_obj.save()
    return ajax_success()
