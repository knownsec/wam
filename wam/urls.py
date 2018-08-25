from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
)

# Main
urlpatterns += patterns(
    'wam.apps.main.views',
    url(r'^$|^index/$|^index.html$', 'index_view', name='index'),
    url(r'^login/$', 'login_view', name='login'),
    url(r'^logout/$', 'logout_view', name='logout'),
    url(r'^settings/$', 'settings_view'),
    url(r'^settings/am/$', 'set_am'),
    url(r'^settings/idm/$', 'set_idm'),
)

# App Monitoring
urlpatterns += patterns(
    'wam.apps.am.views',
    url(r'^am/$', 'index_view'),
    url(r'^am/diff/$', 'diff_index'),
    url(r'^am/rules/$', 'rules_index'),
    url(r'^am/rules/search$', 'rules_search'),
    url(r'^am/rules/(\d+)', 'rule_find'),
    url(r'^am/rules/vendor/add$', 'vendor_add'),
    url(r'^am/rules/vendor/edit/(\d+)$', 'vendor_edit'),
    url(r'^am/rules/vendor/del/(\d+)', 'vendor_del'),
    url(r'^am/rules/rule/add$', 'rule_add'),
    url(r'^am/rules/rule/edit/(\d+)', 'rule_edit'),
    url(r'^am/rules/rule/del/(\d+)', 'rule_del'),
    url(r'^am/diff/detail/(\d+)', 'diff_detail'),
    url(r'^am/vendor/(\d+)', 'vendor_detail'),
    url(r'^am/vendor/', 'vendor_index'),
    url(r'^am/package/download/(\d+)', 'package_download'),
    url(r'^am/rules/rule/check$', 'check_download_url'),
    url(r'^am/diff/mail/send$', 'send_mail'),
)

# FM
urlpatterns += patterns(
    'wam.apps.idm.views',
    url(r'^idm/$', 'index_view'),
    url(r'^idm/info/$', 'info_view'),
)

# FM
urlpatterns += patterns(
    'wam.apps.fm.views',
    url(r'^fm/$', 'index_view'),
    url(r'^fm/diff/$', 'fdiff_index'),
    url(r'^fm/rules/$', 'frules_index'),
    url(r'^fm/rules/(\d+)$', 'frules_list'),
    url(r'^fm/rules/rule/add$', 'frule_add'),
    url(r'^fm/rules/rule/edit/(\d+)', 'frule_edit'),
    url(r'^fm/rules/rule/del/(\d+)', 'frule_del'),
    url(r'^fm/diff/detail/(\d+)', 'fdiff_detail'),
    url(r'^fm/file/download/(\d+)', 'file_download'),
    url(r'^fm/rules/rule/check$', 'check_file_filter_content'),
)

# VDR
urlpatterns += patterns(
    'wam.apps.vdr.views',
    url(r'^vdr/$', 'index_view'),
    url(r'^vdr/vendor/(\d+)$', 'packages_list'),
    url(r'^vdr/package/edit/(\d+)$', 'package_edit'),
)
