#coding:utf-8

import memcache
import json
import datetime

from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.conf import settings
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404
from django.db.models import Count, Avg, Sum

from auctionweb.models import * 
from auctionweb.shortcuts.ajax import ajax_success, ajax_error
from auctionweb import mckeys
from auctionweb.invoice.forms import InvoiceForm, FinalInvoiceForm

def unshipped_list(request, template_name):
    '''unshipped 页面'''
    clearance_obj = Clearance.objects.all()
    delivery_obj = Delivery.objects.all()
    harbour = Harbour.objects.all()
    C = {
        "clearance_obj": clearance_obj,
        "delivery_obj": delivery_obj,
        "harbour": harbour
    }
    return render(request, template_name, C)

def unshipped_data(request):
    '''unshipped 数据信息获取渲染datatables'''
    all_invoice_obj = Invoice.objects.filter(is_pre=0, is_ship=0)
    back_data = []
    for v in all_invoice_obj:
        data = {}
        commodity_info = v.get_commodity_info()
        com_obj = commodity_info.get("commodity")
        peel_name = com_obj.peel_field.name
        data["peel_name"] = peel_name
        data["auction"] = com_obj.auction.name
        data["customer_no"] = com_obj.customer_id
        data.update(v.toDICT())
        back_data.append(data)
    return ajax_success(back_data)

def create_ship(request):
    '''生成货运信息'''
    invoice_id_list = json.loads(request.POST.get("invoice_id_list"))
    ship_invoice_obj = Invoice.objects.filter(id__in=invoice_id_list)
    goods_sum = ship_invoice_obj.aggregate(goods_nu_sum=Sum("goods_nu"),cost_sum=Sum("cost_sum"))
    auction_date = ship_invoice_obj[0].get_commodity_info().get("commodity").auction_time
    print goods_sum
    Shiping.objects.create(
        shiping_nu=Shiping.get_last_nu(),
        com_num=goods_sum.get("goods_nu_sum"),
        invoice_count=goods_sum.get("cost_sum"),
        auction_date=auction_date,
        delivery=ship_invoice_obj[0].delivery_company,
        clearance_company=ship_invoice_obj[0].clearance_company,
        is_ship = 1
    )
    return ajax_success()


def ship_list(request, template_name):
    '''显示货运列表'''
 #   ship_obj_list = Shiping.objects.all(is_ship=1)
    return render(request, template_name)

def ship_data(request):
    ship_obj_list = Shiping.objects.all(is_ship=1)
    back_data = [i.toDICT for i in ship_obj_list]
    return ajax_success(back_data)
