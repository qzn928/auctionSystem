#coding:utf-8

import os

from django.conf.urls import patterns, include, url

urlpatterns = patterns('auctionweb.commodity.views',
    url(r'^add/', "add", {"template_name": "auctionweb/commodity/add.html"}, name="cadd"),
    url(r'^change/(?P<lot_nu>\d+)/$', "change", {"template_name": "auctionweb/commodity/add.html"}, name="cchange"),
    url(r'^copy/', "copy_last_form", {"template_name": "auctionweb/commodity/modform.html"}, name="aform"),
    url(r'^ajaxlist/', "ajax_list_data", name="ajax_list"),
    url(r'^delete/', "delete", name="cdel"),
    url(r'^getselect/', "get_select", name="get_field_select"),
)
