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
    all_peelfield_obj = PeelField.objects.all()
    C = {"all_peelfield_obj": all_peelfield_obj}
    return render(request, template_name, C)

def get_classify_data(request):
    back_data = {}
    all_peelfield_obj = PeelField.objects.all()
    for peel in all_peelfield_obj:
        commodity_list = peel.commodity_set.all()
        back_data[peel.id] = [i.toDICT() for i in commodity_list]
    return ajax_success(back_data)

def get_invoice_data(request):
    '''pre dressing 页面datatables 发票列表信息'''
    invoice_list = Invoice.objects.exclude(is_pre=1)
    back_list = [i.toDICT() for i in invoice_list]
    return ajax_success(back_list)

def add_peel_field(request):
    if request.method != "POST":
        raise Http404
    com_list = json.loads(request.POST.get("com_list"))
    peel_field = request.POST.get("peel_field")
    peel_inform = request.POST.get("peel_inform")
    return ajax_success()
