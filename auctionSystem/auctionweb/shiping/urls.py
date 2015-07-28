#coding:utf-8

import os

from django.conf.urls import patterns, include, url

urlpatterns = patterns('auctionweb.shiping.views',
    url(r'^unpaid/list/$', "unshipped_list", {"template_name": "auctionweb/shiping/unshipped_list.html"}, name="unshipped_list"),
    url(r'^data/unshipped/$', "unshipped_data", name="unshipped_data"),
    url(r'^data/ship/$', "ship_data", name="ship_data"),
    url(r'^data/classify/$', "classify_data", name="ship_classify_data"),
    url(r'^data/unpaid/$', "unpaid_data", name="unpaid_data"),
    url(r'^create/ship/', "create_ship", name="create_ship"),
    url(r'^ship/info/(?P<ship_nu>\d+)/$', "add_ship_info", name="add_ship_info"),
    url(r'^invoice/(?P<ship_nu>\d+)/$', "ship_invoice", name="ship_invoice"),
    url(r'^add/fee/(?P<ship_nu>\d+)/$', "add_ship_fee", name="add_ship_fee"),
    url(r'^pay/$', "to_pay_shiping", name="to_pay_shiping"),
    url(r'^ship/list/$', "ship_list", {"template_name":"auctionweb/shiping/ship_list.html"}, name="ship_list"),
    url(r'^ship/classify/$', "ship_classify", {"template_name":"auctionweb/shiping/ship_classify.html"}, name="ship_classify"),
    url(r'^ship/harbour/count/$', "ship_harbour_count", {"template_name":"auctionweb/shiping/ship_harbour_count.html"}, name="ship_harbour_count"),
    url(r'^unpaid/items/$', "unpaid_list", {"template_name":"auctionweb/shiping/unpaid_list.html"}, name="unpaid_list")
)
