#coding:utf-8

import memcache
import json
import datetime
import xlwt
import StringIO

from django.http import HttpResponse
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
    invoice_list = json.loads(request.POST.get("data", ''))
    error = False
    for idl in invoice_list:
        try:
           invoice_obj = Invoice.objects.get(pk=idl)
           com_list = invoice_obj.commodity_set.all()
        except Invoice.DoesNotExist:
            error = True
        else:
            print invoice_obj.toDICT()
            goods_nu, dollar_sum, cost_sum = invoice_formula(com_list, invoice_obj.toDICT(), False)
            print goods_nu, "222222222222"
            return
            invoice_obj.is_pre = 0
            invoice_obj.goods_nu = goods_nu
            invoice_obj.dollar_sum = dollar_sum
            invoice_obj.cost_sum = cost_sum
            invoice_obj.save()
    if not error:
        return ajax_success()
    else:
        return ajax_error("存在未成功生成最终发票的数据")

def fvlist(request, template_name):
    '''显示最终发票列表'''
    return render(request, template_name)

def invoice_formula(com_list, post_data=None, is_pre=True):
    formula_objs = AuctionFormula.objects.all()
    goods_sum, dollar_sum, cost_sum = 0, 0, 0
    if com_list:
        auction = com_list[0].auction
        try:
            formula_obj = formula_objs.get(auction=auction)
        except AuctionFormula.DoesNotExist:
            print "formula does not exist"
            return '', '', ''
    for com in com_list:
        goods_sum += com.number
        args = com.toDICT()
        if is_pre:
            args["begin_exchange_rate"] = post_data.get("begin_exchange_rate")
        else:
            args["final_exchange_rate"] = post_data.get("final_exchange_rate")
        args["commission_rate"] = post_data.get("commission_rate")
        args["an_rmb_rate"] = post_data.get("an_rmb_rate")
        if com.sex == "male" and is_pre:
            dollar_sum += eval(formula_obj.pre_invoice_dollar_male.format(**args))
            cost_sum += eval(formula_obj.pre_invoice_cost_male.format(**args))
        elif com.sex == "male" and not is_pre:
            dollar_sum += eval(formula_obj.final_invoice_dollar_male.format(**args))
            cost_sum += eval(formula_obj.final_invoice_cost_male.format(**args))
        elif com.sex == "female" and is_pre:
            dollar_sum += eval(formula_obj.pre_invoice_dollar_female.format(**args))
            cost_sum += eval(formula_obj.pre_invoice_cost_female.format(**args))
        else:
            dollar_sum += eval(formula_obj.final_invoice_dollar_female.format(**args))
            cost_sum += eval(formula_obj.final_invoice_cost_female.format(**args))
    return  goods_sum, dollar_sum, cost_sum

            
@csrf_exempt    
def begin_invoice_add(request, template_name):
    '''接收post请求，生成初始发票'''
    if request.method == "POST":
        post_data = json.loads(request.POST.get("data", ''))
        all_lot_nu = post_data.get("all_lot_nu")
        comm_list = Commodity.objects.filter(lot__in=all_lot_nu)
        invoice_nu = Invoice.get_last_nu()
        form_data = {
            "customer_id": post_data.get("customer_id"),
            "invoice_nu": invoice_nu,
            "an_rmb_rate": post_data.get("an_rmb_rate"),
            "commission_rate": post_data.get("commission_rate")
        }
        if post_data.get("begin_exchange_rate"):
            form_data["begin_exchange_rate"] = post_data.get("begin_exchange_rate")
        iform = InvoiceForm(form_data)
        if iform.is_valid():
            invoice_com = iform.save(commit=False)
            goods_nu, dollar_sum, cost_sum = invoice_formula(comm_list, post_data, True)
            invoice_com.goods_nu = goods_nu
            invoice_com.dollar_sum = dollar_sum
            invoice_com.cost_sum = cost_sum
            invoice_com.save()
            invoice_com.commodity_set = comm_list
            comm_list.update(is_invoice=1)
            mem = memcache.Client(settings.MEMCACHES)
            mem.set_multi({
                "begin_rate": post_data.get("begin_exchange_rate"), 
                "commpression_rate": post_data.get("commission_rate"),
                "an_rmb_rate": post_data.get("an_rmb_rate")
            })
            return ajax_success()
        else:print iform.errors
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
    del_com_list = Commodity.objects.filter(lot__in=all_post_lot_nu)
    com_list = Commodity.objects.filter(lot__in=all_lot_nu)
    args = invoice_obj.toDICT()
    goods_nu, dollar_sum, cost_sum = invoice_formula(com_list, args, is_pre)
    form_data = { 
        "goods_nu": goods_nu,
        "dollar_sum": dollar_sum,
        "cost_sum": cost_sum
    }
    [setattr(invoice_obj, key, val) for key, val in form_data.items() ]
    invoice_obj.save()
    invoice_obj.commodity_set.remove(*del_com_list)
    del_com_list.update(is_invoice=0)
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

#打印
def fexcel(request):
    if request.method != "POST":
        with open("/tmp/final_invoice.xls") as f:
            data = f.read()
        response = HttpResponse(data, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment;filename=final_invoice.xls'
        return response
    data = json.loads(request.POST.get("data"))
    wb = xlwt.Workbook(encoding = 'utf-8')
    sheet = wb.add_sheet(u'最终发票清单')
    th = ["发票号", "客户号", "品种", "生皮总额", "美金总额", "修改次数", "修改时间"]
    [sheet.write(0, i, th[i]) for i in range(len(th))]
    row = 1
    all_final_invoice = Invoice.objects.filter(id__in=data.get("id_lis")).order_by("invoice_nu")
    property = [
        "invoice_nu", "customer_id", "goods_type", 
        "goods_nu", "cost_sum", "modify_times", "modify_date"
    ]
    json_list = [i.toDICT() for i in all_final_invoice]
    for lis in json_list:
        [sheet.write(row, i, lis[property[i]]) for i in range(len(property))]
        row = row + 1
    wb.save("/tmp/final_invoice.xls")
    return ajax_success() 

def commission(request, template_name):
    '''佣金模块'''
    return render(request, template_name, {})
