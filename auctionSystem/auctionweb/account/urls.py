#coding:utf-8

import os

from django.conf.urls import patterns, include, url

urlpatterns = patterns('auctionweb.account.views',
    url(r'^$', "account", {"template_name": "auctionweb/account/account.html"}, name="account"),
    url(r'^data/$', "account_data", name="account_data"),
    url(r'^customer/(?P<cus_id>\d+)/charge/$', "cus_charge", name="cus_charge"),
    url(r'^customer/(?P<cus_id>\d+)/transfer/$', "cus_trans", name="cus_trans"),
    url(r'^company/(?P<com_id>\d+)/transfer/$', "com_trans", name="com_trans"),
    url(r'^company/(?P<com_id>\d+)/transothers/$', "com_transothers", name="com_transothers"),
    url(r'^auction/(?P<auc_id>\d+)/transfer/$', "auc_trans", name="auc_trans"),
    url(r'^auction/(?P<auc_id>\d+)/transothers/$', "auc_transothers", name="auc_transothers"),
    url(r'^log/$', "acclog", {"template_name": "auctionweb/account/acclog.html"}, name="acclog"),
    url(r'^log/data/$', "acclog_data", name="acclog_data"),
    url(r'^export/$', "account_export", name="account_export"),
)
