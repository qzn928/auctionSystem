from django.conf.urls import patterns, include, url
from django.conf import settings


#import xadmin
#xadmin.autodiscover()
#
#from xadmin.plugins import xversion
#xversion.register_models()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'auctionSystem.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

  #  url(r'xadmin/', include(xadmin.site.urls)),
)

if settings.DEBUG: #在开发时使用django来返回静态文件
    urlpatterns += patterns(
        'django.views.static',
        url(r'^static/(?P<path>.*)$', 'serve', {'document_root': os.path.join(PROJECTROOT, 'static/')}),
    )   
