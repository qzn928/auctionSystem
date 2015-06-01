#coding:utf-8

import os

from django.conf.urls import patterns, include, url

urlpatterns = patterns('auctionweb.shiping.views',
    url(r'^list/$', "unshipped_list", {"template_name": "auctionweb/shiping/unshipped_list.html"}, name="unshipped_list"),
    url(r'^jsondata/unshipped/$', "unshipped_data", name="unshipped_data"),
)
