#coding:utf-8

import os

from django.conf.urls import patterns, include, url

urlpatterns = patterns('auctionweb.commodity.views',
    url(r'^add/', "add", {"template_name": "auctionweb/commodity/add.html"}, name="cadd"),
    url(r'^copy/', "copy_last_form", {"template_name": "auctionweb/commodity/addform.html"}, name="aform"),
    url(r'^list/', "clist", name="alist"),
)
