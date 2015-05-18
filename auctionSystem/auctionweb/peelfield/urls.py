#coding:utf-8

import os

from django.conf.urls import patterns, include, url

urlpatterns = patterns('auctionweb.peelfield.views',
    url(r'^list/', "peel_list", {"template_name": "auctionweb/peelfield/plist.html"}, name="plist"),
    url(r'^data/', "get_com_data", name="pdata"),
    url(r'^add/', "add_peel_field", {"template_name": "auctionweb/peelfield/addform.html"}, name="padd"),
    url(r'^classify/', "com_list_by_peelname", {"template_name": "auctionweb/peelfield/pclassify.html"}, name="pclassify"),
    url(r'^cdata/', "get_classify_data", name="cpdata"),
)
