from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.views import login, logout

admin.autodiscover()

urlpatterns = patterns('',
    # Authentication
        
    # Home
    url(r'^$', 'django.views.generic.simple.direct_to_template', {'template': 'home.html'}, name='home'),
    url(r'^home/$', 'django.views.generic.simple.direct_to_template', {'template': 'home.html'}, name='home'),
    
    # Admin
    url(r'^admin/', include(admin.site.urls)),
    )

urlpatterns += patterns('participe.account.views',
    # Account
    url(r'^accounts/login/$', login, {"template_name": "account_login.html",}),
    url(r'^accounts/logout/$', logout, {"next_page": "/home/"}),
    url(r'^accounts/signup/$', 'signup', name='signup'),
    url(r'^accounts/profile/$', 'profile', name='profile'),
    )

urlpatterns += patterns('participe.challenge.views',
    # Challenge
    url(r'^challenges/$', 'challenge_list', name='challenge_list'),
    url(r'^challenges/create/$', 'challenge_create', name='challenge_create'),
    url(r'^challenges/(?P<challenge_id>\d+)/$', 'challenge_detail', name='challenge_detail'),
    )

urlpatterns += patterns('participe.organization.views',
    # Organization
    url(r'^organizations/$', 'organization_list', name='organization_list'),
    url(r'^organizations/create/$', 'organization_create', name='organization_create'),
    url(r'^organizations/(?P<organization_id>\d+)/$', 'organization_detail', name='organization_detail'),
    )

# The big, fat disclaimer
# Using this method is inefficient and insecure.
# Do not use this in a production setting. Use this only for development.
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
    )
