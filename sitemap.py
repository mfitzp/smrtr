from django.contrib.sitemaps import Sitemap
# Smrtr
from network.models import Network
from challenge.models import Challenge
from package.models import Package
from profiles.models import UserProfile
from questions.models import Question
# External
from forum.models import Thread, Post


class NetworkSitemap(Sitemap):
    changefreq = "monthly"
    priority = 1
    limit = 1000

    def items(self):
        return Network.objects.all()

    def lastmod(self, obj):
        return obj.updated

class PackageSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5
    limit = 1000
   
    def items(self):
        return Package.objects.all()

    def lastmod(self, obj):
        return obj.updated
        
class ChallengeSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5
    limit = 1000

    def items(self):
        return Challenge.objects.all()

    def lastmod(self, obj):
        return obj.updated
        
class PackageSitemap(Sitemap):
    changefreq = "weekly"
    priority = 1
    limit = 1000

    def items(self):
        return Package.objects.all()

    def lastmod(self, obj):
        return obj.created

class UserProfileSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5
    limit = 1000

    def items(self):
        return UserProfile.objects.all()

    def lastmod(self, obj):
        return obj.user.last_login

class QuestionSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5
    limit = 1000

    def items(self):
        return Question.objects.all()

    def lastmod(self, obj):
        return obj.updated    
            
class ThreadSitemap(Sitemap):
    changefreq = "weekly"
    limit = 1000

    def priority(self, obj):
        return 0.5 + ( (obj.sticky + obj.system) * 0.25 ) # Increase priority to 1 when sticky and system

    def items(self):
        return Thread.objects.all()

    def lastmod(self, obj):
        return obj.latest_post_time
        
class PostSitemap(Sitemap):
    changefreq = "never"
    priority = 0.5
    limit = 1000

    def items(self):
        return Post.objects.all()

    def lastmod(self, obj):
        return obj.time               

