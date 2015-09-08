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
#    all_invoice_obj = Invoice.objects.exclude(is_pre=1)
#    print all_invoice_obj
#    args_pid = request.GET.get("peel_id")
#    for v in all_invoice_obj:
#        try:
#            data = {}
#            commodity_info = v.get_commodity_info()
#            com_obj = commodity_info.get("commodity")
#            peel_id = com_obj.peel_field.pk
#            data["auction"] = com_obj.auction.name
#            data["peel_inform"] = com_obj.peel_inform.name
#            data["peel_price"] = commodity_info.get("peel_price")
#            data["peel_status"] = v.get_peeltime_status
#            data.update(v.toDICT())
#            if peel_id in back_data:
#                back_data[str(peel_id)].append(data)
#            else:
#                back_data[str(peel_id)] = [data]
#        except Exception, e:
#            print str(e)
#    if args_pid:
#        back_data = back_data.get(str(args_pid))
    args_pid = request.GET.get("peel_id")
    all_com_obj = Commodity.objects.exclude(invoice__is_pre=1)
    print all_com_obj
    back_data = {}
    for v in all_com_obj:
        try:
            peel_id = v.peel_field.pk
            if peel_id in back_data:
                back_data[peel_id].append(v.toDICT())
            else:
                back_data[peel_id] = []
        except Exception, e:
            print str(e)
    if args_pid:
        back_data = back_data.get(int(args_pid))
    return ajax_success(back_data)

def add_peel_time(request, com_id):
    '''添加发票的削皮场流程时间参数'''
    if request.method != "POST":
        raise Http404
    try:
        com_obj = Commodity.objects.get(pk=com_id)
    except Commodity.DoesNotExist:
        return ajax_error("commodity obj does not exist")
    data = request.POST.copy()
    data.pop('csrfmiddlewaretoken')
    [setattr(invoice_obj, key, val) for key, val in data.items() if val]
    com_obj.save()
    return ajax_success()

def get_invoice_data(request):
    '''pre dressing 页面datatables 发票列表信息'''
    invoice_list = Invoice.objects.exclude(is_pre=1)
    back_list = [i.toDICT() for i in invoice_list]
    return ajax_success(back_list)

def add_peel_field(request, invoice_id):
    '''添加削皮场和削皮指示'''
    if request.method != "POST":
        raise Http404
    post_data = request.POST
    lot_id_lis = json.loads(request.POST.get("lot_id_arr"))
    try:
        peel_field_obj = PeelField.objects.get(pk=post_data.get("peel_field"))
        peel_inform_obj = PeelInform.objects.get(pk=post_data.get("peel_inform"))
    except:
        return ajax_error("object does not exist")
    com_list = Commodity.objects.filter(id__in=lot_id_lis)
    for com in com_list:
        com.peel_field = peel_field_obj
        com.peel_inform = peel_inform_obj
        com.peel_mo_num = com.peel_mo_num + 1
        com.peel_mo_time = datetime.datetime.now()
        com.peel_comment = post_data.get("peel_comment")
        com.peel_time_flag = post_data.get("peel_time_flag")
        com.peel_level = post_data.get("peel_level")
        com.save()
    return ajax_success()
