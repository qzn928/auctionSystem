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

def vlist(request, template_name):
    if request.method == "POST":
        invoice_id = request.POST.get("invoice_id")
        try:
            invoice_obj = Invoice.objects.get(pk=invoice_id)
        except Invoice.DoesNotExist:
            return ajax_error("invoice id not exist")
        form = FinalInvoiceForm(request.POST, instance=invoice_obj)
        if form.is_valid():
            invoice_obj.modify_date = datetime.datetime.now()
            invoice_obj.modify_times = 1 + (invoice_obj.modify_times if invoice_obj.modify_times else 0)
            invoice_obj.save()
            form.save()
            return ajax_success()
        else:
            return ajax_error(form.errors)
    return render(request, template_name)

def create_final_invoice(request, invoice_id):
    try:
        invoice_obj = Invoice.objects.get(pk=invoice_id)
    except Invoice.DoesNotExist:
        return ajax_error("invoice id not exist")
    invoice_obj.is_pre = 0
    invoice_obj.save()
    return ajax_success()

def fvlist(request, template_name):
    '''
        展示最终发票列表
    '''
    return render(request, template_name)

    
@csrf_exempt
def voadd(request, template_name):
    if request.method == "POST":
        post_data = json.loads(request.POST.get("data", ''))
        all_lot_nu = post_data.get("all_lot_nu")
        new_rate = post_data.get("new_rate")
        comm_list = Commodity.objects.filter(lot__in=all_lot_nu)
        invoice_nu = Invoice.get_last_nu()
        form_data = {
            "commodity": ','.join(all_lot_nu),
            "customer_id": post_data.get("customer_id"),
            "begin_exchange_rate": new_rate,
            "invoice_nu": invoice_nu,
            "goods_type": "ccc",
            "goods_nu": 100,
            "dollar_sum": 3000,
            "cost_sum": 2000
        }
        iform = InvoiceForm(form_data)
        if iform.is_valid():
            iform.save()
            comm_list.update(is_invoice=1)
            return ajax_success()
    return ajax_error()

def vlist_of_json(request):
    all_pre_invoice = Invoice.objects.filter(is_pre=1).order_by("invoice_nu")
    json_list = [i.toDICT() for i in all_pre_invoice]
    return ajax_success(json_list)

def fvlist_of_json(request):
    all_final_invoice = Invoice.objects.filter(is_pre=0).order_by("invoice_nu")
    json_list = [i.toDICT() for i in all_final_invoice]
    return ajax_success(json_list)

def lot_list_invoice(request):
    invoice_id = request.GET.get("invoice_id")
    try:
        invoice_obj = Invoice.objects.get(pk=invoice_id)
    except Invoice.DoesNotExist:
        return ajax_success([])
    all_lot = Commodity.objects.filter(lot__in=invoice_obj.commodity.split(","))
    json_lot_list = [i.toDICT() for i in all_lot]
    return ajax_success(json_lot_list)

@csrf_exempt
def vmodify(request, invoice_id):
    if request.method != "POST":
        raise Http404
    try:
        invoice_obj = Invoice.objects.get(pk=invoice_id)
    except Invoice.DoesNotExist:
        return ajax_error("invoice obj does not exist")
    all_in_lot_nu = invoice_obj.commodity.split(",")
    all_post_lot_nu = json.loads(request.POST.get("data", ''))
    all_lot_nu = list(set(all_in_lot_nu)-set(all_post_lot_nu))
    form_data = {
        "commodity": ','.join(all_lot_nu),
        "goods_nu": 50,
        "dollar_sum": 300,
        "cost_sum": 200
    }
    [setattr(invoice_obj, key, val) for key, val in form_data.items() ]
    invoice_obj.save()
    Commodity.objects.filter(lot__in=all_post_lot_nu).update(is_invoice=0)
    return ajax_success()

def vmodify_info(request, invoice_id, template_name):
    try:
        invoice_obj = Invoice.objects.get(pk=invoice_id)
    except Invoice.DoesNotExist:
        return ajax_error("invoice obj does not exist")
    form = FinalInvoiceForm(instance=invoice_obj)
    html = render_to_string(
        template_name,
        {"form": form},
        context_instance=RequestContext(request)
    )
    return ajax_success(html=html)
