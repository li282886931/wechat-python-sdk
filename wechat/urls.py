from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'wechat.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^wangteng/$', 'app.views.main'),
    url(r'^wangteng/user_info/$', 'app.views.user_info'),
    url(r'^wangteng/create_menu/$', 'app.views.create_menu'),
    url(r'^wangteng/qrcode/$', 'app.views.qrcode'),
    url(r'^wangteng/jssdk/$', 'app.views.jssdk'),
    url(r'^wangteng/pay/$', 'app.views.pay'),
    url(r'^wangteng/pay_notify/$', 'app.views.pay_notify'),
)
