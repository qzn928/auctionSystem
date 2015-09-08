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

from auctionweb.models import * 
from auctionweb.shortcuts.ajax import ajax_success, ajax_error
from auctionweb import mckeys
from auctionweb.invoice.forms import InvoiceForm, FinalInvoiceForm

def vlist(request, template_name):
    '''显示初始发票列表，和修改发票信息'''
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

def create_final_invoice(request):
    '''生成最终发票'''
    print request.POST
    invoice_list = json.loads(request.POST.get("data", ''))
    error = False
    for idl in invoice_list:
        try:
           invoice_obj = Invoice.objects.get(pk=idl)
        except Invoice.DoesNotExist:
            error = True
        else:
            invoice_obj.is_pre = 0
            invoice_obj.save()
    if not error:
        return ajax_success()
    else:
        return ajax_error("存在未成功生成最终发票的数据")

def fvlist(request, template_name):
    '''显示最终发票列表'''
    return render(request, template_name)

@csrf_exempt    
def voadd(request, template_name):
    '''接收post请求，生成初始发票'''
    if request.method == "POST":
        post_data = json.loads(request.POST.get("data", ''))
        all_lot_nu = post_data.get("all_lot_nu")
        new_rate = post_data.get("new_rate")
        com_rate = post_data.get("com_rate")
        comm_list = Commodity.objects.filter(lot__in=all_lot_nu)
        invoice_nu = Invoice.get_last_nu()
        form_data = {
            "customer_id": post_data.get("customer_id"),
            "begin_exchange_rate": new_rate,
            "invoice_nu": invoice_nu,
            "goods_nu": 100,
            "dollar_sum": 3000,
            "cost_sum": 2000,
            "commission_rate": com_rate
        }
        iform = InvoiceForm(form_data)
        if iform.is_valid():
            invoice_com = iform.save(commit=False)
            invoice_com.save()
            invoice_com.commodity_set = comm_list
            comm_list.update(is_invoice=1)
            mem = memcache.Client(settings.MEMCACHES)
            mem.set_multi({"begin_rate": new_rate, "commpression_rate": com_rate})
            return ajax_success()
    return ajax_error("检查数据格式")

def vlist_of_json(request):
    '''初始发票, datatable数据获取'''
    all_pre_invoice = Invoice.objects.filter(is_pre=1).order_by("invoice_nu")
    json_list = [i.toDICT() for i in all_pre_invoice]
    return ajax_success(json_list)

def fvlist_of_json(request):
    '''最终发票, datatable数据获取'''
    all_final_invoice = Invoice.objects.filter(is_pre=0).order_by("invoice_nu")
    json_list = [i.toDICT() for i in all_final_invoice]
    return ajax_success(json_list)

def lot_list_invoice(request, invoice_id):
    """发票拆分功能， 获取关于某个初始发票的所有lot信息"""
    try:
        invoice_obj = Invoice.objects.get(pk=invoice_id)
    except Invoice.DoesNotExist:
        return ajax_success([])
    all_lot = invoice_obj.commodity_set.all()
    print all_lot
    json_lot_list = [i.toDICT() for i in all_lot]
    return ajax_success(json_lot_list)

@csrf_exempt
def vmodify(request, invoice_id):
    '''发票拆分后重新生成invoice'''
    if request.method != "POST":
        raise Http404
    try:
        invoice_obj = Invoice.objects.get(pk=invoice_id)
    except Invoice.DoesNotExist:
        return ajax_error("invoice obj does not exist")
    all_in_lot_nu = [com_obj.lot for com_obj in invoice_obj.commodity_set.all()]
    all_post_lot_nu = json.loads(request.POST.get("data", ''))
    all_lot_nu = list(set(all_in_lot_nu)-set(all_post_lot_nu))
    if len(all_lot_nu) == 0:
        invoice_obj.delete()
        return ajax_success()
    form_data = {
        "commodity": ','.join(all_lot_nu),
        "goods_nu": 50,
        "dollar_sum": 300,
        "cost_sum": 200
    }
    [setattr(invoice_obj, key, val) for key, val in form_data.items() ]
    commodity_list = Commodity.objects.filter(lot__in=all_lot_nu)
    invoice_com = invoice_obj.save(commit=False)
    invoice_com.commodity_set.add(commodity_list)
    invoice_com.save()
    Commodity.objects.filter(lot__in=all_post_lot_nu).update(is_invoice=0)
    return ajax_success()

def vmodify_info(request, invoice_id, template_name):
    '''初始发票修改功能'''
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

def add_ship_com(request):
    '''添加发票的货运相关公司'''
    if request.method != "POST":
        raise Http404
    clearance_com = request.POST.get("clearance_company") # 清关公司
    delivery_com = request.POST.get("delivery_company") # 地接公司
    harbour = request.POST.get("harbour") # 港口
    not_net_weight = request.POST.get("not_net_weight") # 港口
    invoice_id_list =  json.loads(request.POST.get("invoice_id_list"))
    update_dict = {
        "clearance_company": Clearance.objects.get(name=clearance_com),
        "delivery_company": Delivery.objects.get(name=delivery_com),
        "harbour": Harbour.objects.get(name=harbour),
        "not_net_weight": not_net_weight
    }
    Invoice.objects.filter(id__in=invoice_id_list).update(**update_dict)
    return ajax_success()
