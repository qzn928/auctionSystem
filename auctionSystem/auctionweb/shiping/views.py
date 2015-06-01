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

from auctionweb.models import Customer, PeelField, Commodity, Invoice
from auctionweb.shortcuts.ajax import ajax_success, ajax_error
from auctionweb import mckeys
from auctionweb.invoice.forms import InvoiceForm, FinalInvoiceForm

def unshipped_list(request, template_name):
    '''unshipped 页面'''
    return render(request, template_name)

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
    
