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
    'modules': ModuleSitemap, 
    'concepts': ConceptSitemap,
    # Content
    'questions': QuestionSitemap, 
    'challenges': ChallengeSitemap, 
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
    url(r'^top5/$', 'core.views.statistics', name='statistics'),
    # Override the account/login view, to provide additional info
    # url(r'^accounts/login/$', 'core.views.login', name='login'),

    (r'^comments/', include('django.contrib.comments.urls')),

    #(r'^login/$', 'spenglr.core.views.loginhandler'),
    #(r'^logout/$', 'spenglr.core.views.logouthandler'),

    (r'^network/', include('network.urls')),
    (r'^education/', include('education.urls')),
    (r'^resources/', include('resources.urls')),    
    (r'^challenge/', include('challenge.urls')),

    #(r'^accounts/intro/$', 'core.views.intro'),
    (r'^accounts/', include('registration.urls')),

    (r'^profile/', include('profiles.urls')),
    (r'^welcome/', include('welcome.urls')),

    (r'^questions/', include('questions.urls')),

    (r'^notification/', include('notification.urls')),

    url(r'^discuss/(?P<forum_id>[-\w]+)/$', 'core.views.forum_parent_redirect', name="discuss_forum"),
    (r'^discuss/', include('discuss.urls')),
    
    (r'^search/', include('haystack.urls')),
    (r'^avatar/', include('avatar.urls')),
    (r'^messages/', include('messages.urls')),


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

