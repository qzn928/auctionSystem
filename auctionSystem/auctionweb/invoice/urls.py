#coding:utf-8

import os

from django.conf.urls import patterns, include, url

urlpatterns = patterns('auctionweb.invoice.views',
    url(r'^add/', "voadd", {"template_name": "auctionweb/invoice/add.html"}, name="cinvoice"),
    url(r'^list/', "vlist", {"template_name": "auctionweb/invoice/vlist.html"}, name="vlist"),
    url(r'^flist/', "fvlist", {"template_name": "auctionweb/invoice/fvlist.html"}, name="fvlist"),
    url(r'^jsondata/', "vlist_of_json", name="vjson"),
    url(r'^fvjsondata/', "fvlist_of_json", name="fvjson"),
    url(r'^inlot/', "lot_list_invoice", name="inlot"),
    url(r'^modify/lot/(?P<invoice_id>\d+)', "vmodify", name="vmodify"),
    url(r'^cfinvoice/(?P<invoice_id>\d+)', "create_final_invoice", name="vcf"),
    url(r'^modify/info/(?P<invoice_id>\d+)', "vmodify_info", 
        {"template_name": "auctionweb/invoice/addform.html"}, name="vmodify_info"),
)
