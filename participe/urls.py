from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.views import login, logout

admin.autodiscover()

urlpatterns = patterns('',
    # i18n
    url(r'^i18n/', include('django.conf.urls.i18n')),
    
    # Home
    url(r'^$', 'django.views.generic.simple.direct_to_template',
            {'template': 'home.html'}, name='home'),
    url(r'^home/$', 'django.views.generic.simple.direct_to_template',
            {'template': 'home.html'}, name='home'),
    url(r'^tnc/$', 'django.views.generic.simple.direct_to_template',
            {'template': 'terms_and_conditions.html'},
            name='terms_and_conditions'),
    
    # Take into account, that Avatar templates are overridden here
    #url(r'^avatar/', include('avatar.urls')),
    #url(r'^avatar_crop/', include('avatar_crop.urls')),
    url(r'', include('social_auth.urls')),
    url(r'^captcha/', include('captcha.urls')),
    
    # Admin
    url(r'^admin/', include(admin.site.urls)),
    )

urlpatterns += patterns('participe.account.views',
    # Account
    url(r'^accounts/login/$', login, {"template_name": "account_login.html",}),
    url(r'^accounts/logout/$', logout, {"next_page": "/"}),
    url(r'^accounts/$', 'account_list', name='account_list'),
    url(r'^accounts/signup/$', 'signup', name='signup'),
    url(r'^accounts/profile/view/$', 'view_myprofile', name='view_myprofile'),
    url(r'^accounts/profile/view/(?P<user_id>[\w_-]+)/$', 'view_profile',
            name='view_profile'),
    url(r'^accounts/profile/edit/$', 'edit_profile', name='edit_profile'),
    url(r'^accounts/profile/delete/$', 'delete_profile',
            name='delete_profile'),
    url(r'^accounts/password/reset/$', 'reset_password',
            name='reset_password'),
    url(r'^account/confirmation/(?P<confirmation_code>[0-9a-zA-Z-_:]+)/$',
            'email_confirmation',
            name='email_confirmation'),
    url(r'^accounts/avatar/change$', 'change_avatar', name='change_avatar'),
    )

urlpatterns += patterns('participe.challenge.views',
    # Challenge
    url(r'^challenges/$', 'challenge_list', name='challenge_list'),
    url(r'^challenges/create/$', 'challenge_create', name='challenge_create'),
    url(r'^challenges/(?P<challenge_id>\d+)/$', 'challenge_detail',
            name='challenge_detail'),
    )

urlpatterns += patterns('participe.organization.views',
    # Organization
    url(r'^organizations/$', 'organization_list', name='organization_list'),
    url(r'^organizations/create/$', 'organization_create',
            name='organization_create'),
    url(r'^organizations/(?P<organization_id>\d+)/$', 'organization_detail',
            name='organization_detail'),
    )

# The big, fat disclaimer
# Using this method is inefficient and insecure.
# Do not use this in a production setting. Use this only for development.
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
    )
