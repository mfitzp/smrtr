from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()
# Smrtr
from sitemap import *

def i18n_javascript(request):
  return admin.site.i18n_javascript(request)

handler500 = 'core.views.error500' # Override default handler to pass MEDIA_URL

sitemaps = {
    # Structure
    'networks': NetworkSitemap,
    'challenges': ChallengeSitemap, 
    'concepts': ConceptSitemap,
    # Content
    'questions': QuestionSitemap, 
    # Users
    'profiles': UserProfileSitemap, 
    # Discussions
    'threads': ThreadSitemap, 
    'posts': PostSitemap, 
}

urlpatterns = patterns('',
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:

    (r'^admin/jsi18n', i18n_javascript),
    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    url(r'^$', 'core.views.home', name='home'),
    
    url(r'^top10/$', 'core.views.statistics', name='statistics'),
    # Override the account/login view, to provide additional info
    # url(r'^accounts/login/$', 'core.views.login', name='login'),

    (r'^comments/', include('django.contrib.comments.urls')),

    #(r'^login/$', 'spenglr.core.views.loginhandler'),
    #(r'^logout/$', 'spenglr.core.views.logouthandler'),

    (r'^network/', include('network.urls')),
    (r'^challenge/', include('challenge.urls')),
    (r'^concept/', include('concept.urls')),
    (r'^resources/', include('resources.urls')),    
    (r'^questions/', include('questions.urls')),

    #(r'^accounts/intro/$', 'core.views.intro'),
    (r'^accounts/', include('registration.urls')),

    (r'^profile/', include('profiles.urls')),
    (r'^welcome/', include('welcome.urls')),


    (r'^notification/', include('notification.urls')),
   
    (r'^search/', include('haystack.urls')),
    # (r'^avatar/', include('avatar.urls')), Removed, now using custom avatar (in proviles) providing fb support
    (r'^messages/', include('messages.urls')),

    url(r'^wall/(?P<wall_slug>[-\w]+)/$', 'core.views.wall_home_redirect', name="wall_home_redirect"),
    url(r'^wall/add/(?P<slug>[-\w]+)/from-home/$', 'wall.views.add', {'success_url':'/'}, name="add_wall_item_from_home" ),
    (r'^wall/', include('wall.urls')),

    (r'^forum/', include('forum.urls')),


    #(r'^facebook/connect/ChannelFile.htm', 'django.views.generic.simple.direct_to_template', {'template': 'fbchannel.html'}),
    (r'^facebook/connect/', include('facebookconnect.urls')),

    # Direct to template views
    (r'^faq/$', 'django.views.generic.simple.direct_to_template', {'template': 'faq.html'}),
    (r'^about/$', 'django.views.generic.simple.direct_to_template', {'template': 'about.html'}),
    (r'^cg/$', 'django.views.generic.simple.direct_to_template', {'template': 'cg.html'}),

    
    # The following are included for development purposes (i.e. can view/edit error page without creating an error ;)
    (r'^500/$', 'django.views.generic.simple.direct_to_template', {'template': '500.html'}),
    (r'^404/$', 'django.views.generic.simple.direct_to_template', {'template': '404.html'}),
    
    # Sitemaps
    (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.index', {'sitemaps': sitemaps}),
    (r'^sitemap-(?P<section>.+)\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),

    
   
)

