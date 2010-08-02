from django.contrib.sitemaps import Sitemap
# Smrtr
from network.models import Network
from education.models import Module, Concept
from challenge.models import Challenge
from profiles.models import UserProfile
from questions.models import Question
from discuss.models import Thread, Post

class NetworkSitemap(Sitemap):
    changefreq = "weekly"
    priority = 1

    def items(self):
        return Network.objects.all()

    # def lastmod(self, obj):
    #    return obj.pub_date

class ModuleSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Module.objects.all()

    # def lastmod(self, obj):
    #    return obj.pub_date

class ConceptSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return Concept.objects.all()

    # def lastmod(self, obj):
    #    return obj.pub_date

class ChallengeSitemap(Sitemap):
    changefreq = "weekly"
    priority = 1

    def items(self):
        return Challenge.objects.all()

    def lastmod(self, obj):
        return obj.created

class UserProfileSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return UserProfile.objects.all()

    def lastmod(self, obj):
        return obj.user.last_login

class QuestionSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return Question.objects.all()

    def lastmod(self, obj):
        return obj.last_updated
        
class ThreadSitemap(Sitemap):
    changefreq = "weekly"

    def priority(self, obj):
        return 0.5 + ( (obj.sticky + obj.system) * 0.25 ) # Increase priority to 1 when sticky and system

    def items(self):
        return Thread.objects.all()

    def lastmod(self, obj):
        return obj.latest_post_created
        
class PostSitemap(Sitemap):
    changefreq = "never"
    priority = 0.5

    def items(self):
        return Post.objects.all()

    def lastmod(self, obj):
        return obj.created               

