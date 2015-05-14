#coding:utf-8

import os

from django.conf.urls import patterns, include, url

urlpatterns = patterns('auctionweb.invoice.views',
    url(r'^add/', "voadd", {"template_name": "auctionweb/invoice/add.html"}, name="cinvoice"),
)
