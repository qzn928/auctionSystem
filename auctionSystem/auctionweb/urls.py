#coding:utf-8

import os

from django.conf.urls import patterns, include, url
from django.conf import settings

import xadmin
xadmin.autodiscover()
from xadmin.plugins import xversion
xversion.register_models()

PROJECTROOT = os.path.dirname(os.path.abspath(__file__))
urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'auctionSystem.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'mangercenter/', include(xadmin.site.urls)),
    url(r'^$', "auctionweb.commodity.views.list", {"template_name": 'auctionweb/commodity/list.html'}, name="clist"),
    url(r'^commodity/', include("auctionweb.commodity.urls")),
    url(r'^invoice/', include("auctionweb.invoice.urls")),
    url(r'^peelfield/', include("auctionweb.peelfield.urls")),
    url(r'^login/', "auctionweb.views.login", {"template_name": "auctionweb/login.html"}, name="login"),
    url(r'^logout/', "auctionweb.views.logout", name="logout"),
)
if settings.DEBUG: #在开发时使用django来返回静态文件
    urlpatterns += patterns(
        'django.views.static',
        url(r'^static/(?P<path>.*)$', 'serve', {'document_root': os.path.join(PROJECTROOT, 'static/')}),
    )
