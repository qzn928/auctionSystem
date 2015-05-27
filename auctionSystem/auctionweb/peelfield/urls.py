#coding:utf-8

import os

from django.conf.urls import patterns, include, url

urlpatterns = patterns('auctionweb.peelfield.views',
    url(r'^list/', "peel_list", {"template_name": "auctionweb/peelfield/plist.html"}, name="plist"),
    url(r'^predress/', "get_invoice_data", name="pre_dress"),
    url(r'^add/', "add_peel_field", name="add_peel_field"),
    url(r'^classify/', "com_list_by_peelname", {"template_name": "auctionweb/peelfield/pclassify.html"}, name="pclassify"),
    url(r'^cdata/', "get_classify_data", name="cpdata"),
)
