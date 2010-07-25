from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg, Max, Min, Count
# Spenglr
from network.models import Network,UserNetwork
from resources.models import Resource
from sq.utils import * 
# External
from countries.models import Country
from datetime import datetime, timedelta, date as _date
# Smrtr
from discuss.models import Forum

# Network = Course now e.g. 'Network' for AQA Biology
# Below this modules are the basis of study on that modules may have a home network, be tied to a specific network, or freely open
# Below modules 'elements' define the learning stages associated (e.g. lecture, chapter, issue)

# Definitions of courses available and their constituent concepts
# Subjects are tied to a home network
class Module(models.Model):
    def __unicode__(self):
        return self.name
    # Auto-add a new wall object when creating new Course
    def save(self, force_insert=False, force_update=False):
        if self.id is None: #is new
            super(Module, self).save(force_insert, force_update)
            self.forum = Forum.objects.create(slug='c'+str(self.id),name=self.name)
        super(Module, self).save(force_insert, force_update)

    def update_sq(self):
        # update
        self.sq = self.concepts.aggregate(Avg('sq'))['sq__avg']
        self.save()

    # Home network for e.g. company-specific subjects
    network = models.ForeignKey(Network, blank = True, null = True) 
    # Networks offering this module
    networks = models.ManyToManyField(Network, related_name='modules')
    
    # Users
    users = models.ManyToManyField(User, through='UserModule', related_name='modules')
    
    name = models.CharField(max_length=75)

    description = models.TextField(blank = True)

    sq = models.IntegerField(editable = False, null = True)

    forum = models.OneToOneField(Forum, editable = False, null = True)

# Concepts for this module
    concepts = models.ManyToManyField('Concept', blank=True)
    
    
    

# Element is a defining part of a course 
# Elements are always tied to a specific subject?? Or freely available
# If an individual concept is self-contained area of study e.g. 'thermodynamics' (that's possibly a bit big)
# may be allocated widely, module components?
class Concept(models.Model):
    def __unicode__(self):
        return self.name
    # Auto-add a new wall object when creating new Concept
    def save(self, force_insert=False, force_update=False):
        if self.id is None: #is new
            super(Concept, self).save(force_insert, force_update)
            self.forum = Forum.objects.create(slug='m'+str(self.id),name=self.name)
        super(Concept, self).save(force_insert, force_update)

    def update_sq(self):
        # update
        self.sq = self.question_set.aggregate(Avg('sq'))['sq__avg']
        self.save()

    # Home network for e.g. company-specific concepts
    network = models.ForeignKey(Network, blank = True, null = True) 
    name = models.CharField(max_length=75)
    description = models.TextField(blank = True)
    
    # Users
    users = models.ManyToManyField(User, through='UserConcept', related_name='concepts')

    sq = models.IntegerField(editable = False, null = True)

    forum = models.OneToOneField(Forum, editable = False, null = True)
    
    # Resources (through conceptresource for bookmarks)
    resources = models.ManyToManyField(Resource, through='ConceptResource', related_name='concepts')

# Study models store information about user's experience with education
# Models are ManytoMany through Models (ie they are used as the basis for linking
# other models together, while appending additional information

class UserModule(models.Model):
    def __unicode__(self):
        return self.module.name
        
    def save(self, force_insert=False, force_update=False):
        if self.id is None: #is new
            # Auto-activate all child concepts for this module
            for concept in self.module.concepts.all():
                try:
                    UserConcept(user=self.user, concept=concept).save()
                except:
                    pass
        super(UserModule, self).save(force_insert, force_update)

    # Additional information
    def year_of_study(self):
        return ( ( _date.today() - self.start_date  ).days / 365 )+1
    def is_active(self):
        return ( self.end_date == None ) or ( self.end_date > _date.today() )
    def update_sq(self):
        self.sq = UserConcept.objects.filter(user=self.user, concept__module = self.module).aggregate(Avg('sq'))['sq__avg']
        self.save()
    # Users on this module in this specific context (network:course)
    def members_class(self):
        return User.objects.filter( usercourse__coursei__course=self.course(), 
                                    usernetwork__network=self.network()
                                    ).distinct()
    # Users on this course on any of this user's networks (user(*):course
    def members_network(self):
        return User.objects.filter( usercourse__coursei__course=self.course(), 
                                    usernetwork__network__usernetwork__user=self.user
                                    ).distinct()
    # Users on this course in any context (*:course)
    def members_global(self):
        return User.objects.filter(usercourse__coursei__course=self.coursei.course)

    user = models.ForeignKey(User)
    module = models.ForeignKey(Module)

    start_date = models.DateTimeField(auto_now_add = True)
    end_date = models.DateTimeField(null = True)

    sq = models.IntegerField(editable = False, null = True)

    class Meta:
        unique_together = ("user", "module")

class UserConcept(models.Model):
    def __unicode__(self):
        return self.concept.name
    # Shortcuts through tree
    def network(self):
        return self.usercourse.coursei.network
    def course(self):
        return self.modulei.course
    def module(self):
        return self.modulei.module
    # Additional information
    def week_of_study(self):
        return ( ( _date.today() - self.start_date  ).days / 7 ) + 1
    def is_active(self):
        return ( self.end_date == None ) or ( self.end_date > _date.today() )
    # Update user's SQ value on this concept
    def update_sq(self):
        # Get user's attempts on this concept's questions 
        # group by x
        # x = qSQ (question's SQ)
        # y = percent_correct
        # Final Max('usq') is just to rename value, not possible to rename on values bit, which sucks
        data = self.concept.question_set.filter(userquestionattempt__user=self.user).values('sq').annotate(n=Count('id'),y=Avg('userquestionattempt__percent_correct'),x=Max('sq'))
        self.sq = sq_calculate(data, 'desc') # Descending data set  
        self.save()
    # Update user's focus value for this concept
    # this is used to include in auto-challenges,etc.
    def update_focus(self):
        # Focus is an weighting value, with importance of variables configurable
        # Variables
        # - Time since last attempt (OR none if never attempted): long time = increased likelihood, declines with age
        # - Lowest score (users SQ on this concept vs. SQ of the concept itself): lower = increased likelihood
        # TODO: Should be last_attempt updated whenever this concept is attempted as part of a challenge
 
        try: 
            # This will fail if sq values are not set (None)  
            self.focus = ( datetime.today() - self.start_date ).days + ( self.concept.sq - self.sq )
            # Limit 0-100
            # FIXME: Is there a better way to do this?
            if self.focus > 100:
                self.focus = 100
            else:
                 if self.focus < 0:
                    self.focus = 0
        except:
            # If fail, put to front of queue: SQ is unset or start_date (latest_attempt) unset i.e. is new!!
            self.focus = 100
        self.save()
        
    # Users on this module in this specific context (network:course:module)
    def members_class(self):
        return User.objects.filter( usermodule__modulei__module=self.module(), 
                                    usercourse__coursei__course=self.course(), 
                                    usernetwork__network=self.network()
                                    ).distinct()
    # Users on this module on any of this user's networks (user(*):course:module
    def members_network(self):
        return User.objects.filter( usermodule__modulei__module=self.module(), 
                                    usernetwork__network__usernetwork__user=self.user
                                    ).distinct()
    # Users on this module in any context (*:*:module)
    def members_global(self):
        return User.objects.filter( usermodule__modulei__module=self.module() )
    
    user = models.ForeignKey(User)
    concept = models.ForeignKey(Concept)

    start_date = models.DateTimeField(auto_now_add = True) 
    end_date = models.DateTimeField(null = True) 

    sq = models.IntegerField(editable = False, null = True)
    focus = models.IntegerField( default = 0,editable = False)

    class Meta:
        unique_together = ("user", "concept")




# Resource attached to specific question
# Use this model to specify question-specific bookmarks in the resource, for example 
# page numbers, chapters, timestamp, #anchors etc.??
class ConceptResource(models.Model):
    def __unicode__(self):
        return self.title
        
    resource = models.ForeignKey(Resource)
    concept = models.ForeignKey(Concept)    
    
    class Meta:
        unique_together = ("resource", "concept")
    
