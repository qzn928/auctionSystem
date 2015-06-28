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
        try:
            peel_name = com_obj.peel_field.name
        except AttributeError:
            data["peel_name"] = ''
        else:
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
    ship_obj = Shiping.objects.create(
        shiping_nu=Shiping.get_last_nu(),
        com_num=goods_sum.get("goods_nu_sum"),
        invoice_count=goods_sum.get("cost_sum"),
    )
    ship_invoice_obj.update(is_ship=1, ship=ship_obj)
    ship_obj.save()
    return ajax_success()


def ship_list(request, template_name):
    '''显示货运列表'''
 #   ship_obj_list = Shiping.objects.all(is_ship=1)
    foreign_ship = ForeignShip.objects.all()
    return render(request, template_name, {"foreign_ship": foreign_ship})

def ship_data(request):
    '''获取ship的datatables信息'''
    ship_obj_list = Shiping.objects.all()
    back_data = []
    for ship_obj in ship_obj_list:
        data = ship_obj.toDICT()
        data.update({"status": ship_obj.get_ship_status})
        back_data.append(data)
    return ajax_success(back_data)

def add_ship_info(request, ship_nu):
    '''接收ship的post信息，并保存'''
    try:
        ship_obj = Shiping.objects.get(pk=ship_nu)
    except Shiping.DoesNotExist:
        raise Http404
    foreign_ship = ForeignShip.objects.get(name=request.POST.get("foreign_ship"))
    data = {}
    for key, val in request.POST.items():
        data[key] = val
    data["foreign_ship"] = foreign_ship
    [setattr(ship_obj, key, val) for key, val in data.items()]
    ship_obj.save()
    return ajax_success()

def ship_invoice(request, ship_nu):
    '''获取货运发票详情'''
    try:
        ship_obj = Shiping.objects.get(pk=ship_nu)
    except Shiping.DoesNotExist:
        raise Http404
    invoice_obj = ship_obj.invoice_set.all()
    print invoice_obj
    back_data = []
    for invo in invoice_obj:
        data = {}
        com_obj = invo.get_commodity_info().get("commodity")
        data["auction"] = com_obj.auction.name
        data["customer_id"] = com_obj.customer_id
        data["invoice_nu"] = invo.invoice_nu
        data["goods_num"] = invo.goods_nu
        data["invoice_count"] = invo.cost_sum
        back_data.append(data)
    return ajax_success(back_data)

def unpaid_list(request, template_name):
    '''未付款货运清单'''
    return render(request, template_name, {})

def unpaid_data(request):
    '''unpaid ship datatables data'''
    ship_obj_list = Shiping.objects.all()
    back_data = [i.toDICT() for i in ship_obj_list]
    return ajax_success(back_data)

def add_ship_fee(request, ship_nu):
    '''添加货运付费详情'''
    try:
        ship_obj = Shiping.objects.get(pk=ship_nu)
    except Shiping.DoesNotExist:
        raise Http404
    invoice_nu = request.POST.get("invoice_nu") # 货运单发票号
    total_fee = request.POST.get("total_fee") # 运费总金额
    delivery_fee = request.POST.get("delivery_fee") # 地接费
    proxy_fee = request.POST.get("proxy_fee") # 代理费
    ship_obj.invoice_nu = invoice_nu
    ship_obj.total_fee = total_fee
    ship_obj.delivery_fee = delivery_fee
    ship_obj.proxy_fee = proxy_fee
    ship_obj.save()
    return ajax_success()

def ship_classify(request, template_name):
    '''货运分类显示关于各公司的付账情况'''
    foreign_ship = ForeignShip.objects.all()
    return render(request, template_name, {"foreign_ship": foreign_ship})

def classify_data(request):
    '''分类显示货运数据'''
    back_data = {}
    ship_obj = Shiping.objects.all()
    for ship in ship_obj:
        data = ship.toDICT()
        if data.get("foreign_ship") in back_data:
            back_data[data.get("foreign_ship")].append(data)
        else:
            back_data[data.get("foreign_ship")] = [data]
    return ajax_success(back_data)

def to_pay_shiping(request):
    '''货运分类付费'''
    # 类别
    com_pro = request.GET.get("company")
    com_id = request.GET.get("idl")
    credit_note = request.POST.get("credit_note")
    payment = request.POST.get("payment")
    if not payment:
        return ajax_error("payment不能为空!!!")
    if not com_pro or not com_id:
        return ajax_error("异常请求")
    if com_pro == "ship":
        try:
            ship_obj = ForeignShip.objects.get(id=com_id)
        except ForeignShip.DoesNotExist:
            return ajax_error("异常请求")
        ship_obj.account.balance = ship_obj.account.balance - \
            int(credit_note) if credit_note else 0 - int(payment)
        ship_obj.account.save()
        PaymentOrder(
            account=ship_obj.account, 
            credit_note=credit_note if credit_note else '',
            payment=payment
        ).save()
    return ajax_success({"blance": ship_obj.account.balance})
