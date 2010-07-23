from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from django.utils.html import escape
# Externals
from datetime import date as date, datetime, timedelta
from notification import models as notification
# Externals
from tagging.fields import TagField
from tagging.models import Tag

class Forum(models.Model):
    # attached = Reverse linker to parent-object
    title = models.CharField(max_length=100)
    closed = models.BooleanField(default=False, blank=True)
       
    def __unicode__(self):
        return self.title
            
class Thread(models.Model):
    forum = models.ForeignKey(Forum)
    author = models.ForeignKey(User)
    title = models.CharField(max_length=100)

    posts = models.IntegerField(editable=False,default=0)

    # first_post = models.OneToOneField('Post', editable=False, null=True, related_name='_dummy_thread_id1')    
    latest_post = models.OneToOneField('Post', editable=False, null=True, related_name='_dummy_thread_id2')    
    latest_post_created = models.DateTimeField(editable=False, null=True)
    
    sticky = models.BooleanField(default=False)
    system = models.BooleanField(default=False) # System message flag, allow important notices flagged
    
    closed = models.BooleanField(default=False)
    
    tags = TagField()


    class Meta:
        ordering = ('-sticky', '-latest_post_created')

    def __unicode__(self):
        return self.title
        
    def set_tags(self, tags):
        Tag.objects.update_tags(self, tags)
    def get_tags(self):
        return Tag.objects.get_for_object(self)             

class Post(models.Model):
    thread = models.ForeignKey(Thread)
    author = models.ForeignKey(User)
    
    created = models.DateTimeField(auto_now_add=True)
    
    body = models.TextField()
    
    class Meta:
        ordering = ('created',)
        
    def save(self):
        super(Post, self).save() # Call the "real" save() method
        self.thread.latest_post = self
        self.thread.latest_post_created = self.created
        self.thread.save()
        
    def delete(self):
        if self.thread.latest_post == self:
            # We are the latest post
            self.thread.latest_post = Post.objects.exclude(pk=self.id).latest('created')
            self.thread.latest_post_created = self.thread.latest_post.created
            self.thread.save()
        super(Post, self).delete() # Call the "real" delete() method

    def __unicode__(self):
        return u'Post %d on thread "%s"' % (self.id, self.thread.title)

