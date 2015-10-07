#coding:utf-8

import memcache
import json
import datetime

from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.core import serializers
from django.template.loader import render_to_string
from django.conf import settings
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from auctionweb.models import  \
    (Customer, PeelField, Commodity, Invoice, AuctionField, Account, AuctionAccount, TransferRecord)
from auctionweb.shortcuts.ajax import ajax_success, ajax_error
from auctionweb import mckeys


def account(request, template_name):
    accounts = Account.objects.all()
    com_account = accounts.filter(style="COM")
    auc_accounts = AuctionAccount.objects.all()
    am_auc_accounts = auc_accounts.filter(style="AMERICAN")
    other_accounts = accounts.filter(style="OTHER")
    C = {
        "account": com_account, 
        "auc_accounts": auc_accounts,
        "am_auc_accounts": am_auc_accounts,
        "other_accounts": other_accounts
    }
    return render(request, template_name, C)

def account_data(request):
    style = request.GET.get("style")
    accounts = Account.objects.all()
    if not style or style == "customer":
        account = accounts.filter(style="CUS")
    elif style == "company":
        account = accounts.filter(style="COM")
    elif style == "auction":
        account = AuctionAccount.objects.all()
    else:
        account = accounts.filter(style="OTHER")
    res = []
    for ac in account:
        data = {
            "name": ac.name, "balance": ac.balance, 
            "style": ac.style, "id": ac.id
        }
        res.append(data)
    return ajax_success({"account": res})

def cus_charge(request, cus_id):
    '''客户账户充值'''
    balance = request.POST.get("balance")
    if not balance:
        return ajax_error("充值金额不能为空")
    else:
        try:
            balance = int(balance)
        except:
            return ajax_error("请填写正确类型的充值金额")
    try:
        cus_obj = Account.objects.get(pk=cus_id)
    except:
        return ajax_error("账户不存在")
    cus_obj.balance = balance + cus_obj.balance
    cus_obj.save()
    return ajax_success()

def cus_trans(request, cus_id):
    '''客户向公司字账户转账'''
    com_ac_id = request.POST.get("company")
    balance = request.POST.get("balance")
    if not com_ac_id or not balance:
        return ajax_error("公司账户与充值金额不能为空")
    else:
        try:
            balance = int(balance)
        except:
            return ajax_error("请填写正确类型的充值金额")
    try:
        com_ac_obj = Account.objects.get(pk=com_ac_id)
        cus_obj = Account.objects.get(pk=cus_id)
    except:
        return ajax_error("账户不存在")
    com_ac_obj.balance = balance + com_ac_obj.balance
    cus_obj.balance = cus_obj.balance + balance
    com_ac_obj.save()
    cus_obj.save()
    trans_log = TransferRecord(
        fro=cus_obj, to=com_ac_obj, 
        money=balance, date=datetime.datetime.now()
    )
    trans_log.save()
    return ajax_success()

def com_trans(request, com_id):
    '''公司子账户向拍卖行美元账户转账'''
    auc_id = request.POST.get("auction")
    balance = request.POST.get("balance")
    rate = request.POST.get("rate")
    if not auc_id or not balance or not rate:
        return ajax_error("存在为空的项")
    else:
        try:
            balance = int(balance)
            rate = float(rate)
        except ValueError:
            return ajax_error("请填写正确类型的转账金额和汇率")
    try:
        auc_account_obj = AuctionAccount.objects.get(pk=auc_id)
        com_ac_obj = Account.objects.get(pk=com_id)
    except:
        return ajax_error("账户不存在")
    com_ac_obj.balance = com_ac_obj.balance - balance
    auc_account_obj.balance = auc_account_obj.balance + balance*rate
    com_ac_obj.save()
    auc_account_obj.save()
    return ajax_success()

def com_transothers(request, com_id):
    '''公司子账户向其他账户转账'''
    other_id = request.POST.get("other")
    balance = request.POST.get("balance")
    if not other_id or not balance:
        return ajax_error("存在为空的项")
    else:
        try:
            balance = int(balance)
        except ValueError:
            return ajax_error("请填写正确类型的转账金额")
    try:
        other_account_obj = Account.objects.get(pk=other_id)
        com_ac_obj = Account.objects.get(pk=com_id)
    except:
        return ajax_error("账户不存在")
    com_ac_obj.balance = com_ac_obj.balance - balance 
    other_account_obj.balance = other_account_obj.balance + balance
    com_ac_obj.save()
    other_account_obj.save()
    return ajax_success()

def auc_trans(request, auc_id):
    '''拍卖账户向美元账户或本地账户转账'''
    balance = request.POST.get("balance")
    rate = request.POST.get("rate")
    if not balance or not rate:
        return ajax_error("存在为空的项")
    else:
        try:
            balance = int(balance)
            rate = float(rate)
        except ValueError:
            return ajax_error("请填写正确类型的转账金额")
    try:
        auc_account_obj = AuctionAccount.objects.get(pk=auc_id)
        to_account = AuctionAccount.objects.\
            filter(name=auc_account_obj.name).exclude(style=auc_account_obj.style)
    except:
        return ajax_error("账户不存在")
    if to_account:
        to_account = to_account[0]
    else:
        return ajax_error("账户不存在")
    auc_account_obj.balance = auc_account_obj.balance - balance
    to_account.balance = to_account.balance + balance * rate
    auc_account_obj.save()
    to_account.save()
    return ajax_success()

def auc_transothers(request, auc_id):
    '''拍卖行向其他账户转账'''
    balance = request.POST.get("balance")
    if not com_id or not balance:
        return ajax_error("存在为空的项")
    else:
        try:
            balance = int(balance)
        except ValueError:
            return ajax_error("请填写正确类型的转账金额")
    try:
        auc_account_obj = AuctionAccount.objects.get(pk=auc_id)
    except:
        return ajax_error("账户不存在")
    if auc_account_obj.style != "LOCAL":
        return ajax_error("拍卖行本地账户可以转账到其他账户")
    auc_account_obj.balance = auc_account_obj.balance - balance
    auc_account_obj.save()
    return ajax_success()

def acclog(request, template_name):
    return render(request, template_name, {})

def acclog_data(request):
    acclogs = TransferRecord.objects.all()
    data = [i.toDICT() for i in acclogs]
    return ajax_success(data) 
