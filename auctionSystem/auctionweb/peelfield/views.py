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
from .forms import PeelFieldForm
from auctionweb.shortcuts.ajax import ajax_success, ajax_error


def peel_list(request, template_name):
    return render(request, template_name)

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

def get_com_data(request):
    commodity_list = Commodity.objects.order_by("lot")
    back_list = [i.toDICT() for i in commodity_list]
    return ajax_success(back_list)

def add_peel_field(request, template_name):
    if request.method == "POST":
        lot_nu = request.POST.get("lot_nu")
        try:
            c_obj = Commodity.objects.get(lot=lot_nu)
        except Commodity.DoesNotExist:
            return ajax_error("Commodity is not exist")
        form = PeelFieldForm(request.POST)
        if form.is_valid():
            peel_obj = form.save()
            c_obj.peel_field = peel_obj
            c_obj.save()
            return ajax_success()
        else:
            return ajax_error(form.errors)
    form = PeelFieldForm()
    html = render_to_string(
        template_name,
        {"form": form},
        context_instance=RequestContext(request)
    )
    return ajax_success(html=html)
