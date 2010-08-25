import os.path
import datetime
# Django
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg, Max, Min, Count
from django.core.urlresolvers import reverse
# Smrtr
from network.models import Network,UserNetwork
from resources.models import Resource
from questions.models import Question
#from challenge.models import UserChallenge
from sq.utils import * 
# External
from countries.models import Country
from easy_thumbnails.fields import ThumbnailerImageField
from wall.models import Wall


# Network = Course now e.g. 'Network' for AQA Biology
# Below this challenges are the basis of study on that challenges may have a home network, be tied to a specific network, or freely open
# Below challenges 'elements' define the learning stages associated (e.g. lecture, chapter, issue)

def concept_file_path(instance=None, filename=None):
    return os.path.join('concept', str(instance.id), filename)    

# Element is a defining part of a course 
# Elements are always tied to a specific subject?? Or freely available
# If an individual concept is self-contained area of study e.g. 'thermodynamics' (that's possibly a bit big)
# may be allocated widely, challenge components?
class Concept(models.Model):
    def __unicode__(self):
        return self.name
    def get_absolute_url(self):
        return reverse('concept-detail',kwargs={'concept_id':str(self.id)})
                
    # Auto-add a new wall object when creating new Concept
    def save(self, force_insert=False, force_update=False):
        if self.id is None: #is new
            super(Concept, self).save(force_insert, force_update)
            self.wall = Wall.objects.create(name=self.name, slug='concept-' + str(self.id))
        super(Concept, self).save(force_insert, force_update)

    def update_sq(self):
        # update
        self.sq = self.questions.aggregate(Avg('sq'))['sq__avg']
        self.save()

    # Home network for e.g. company-specific concepts
    network = models.ForeignKey(Network, blank = True, null = True) 
    name = models.CharField(max_length=75)
    description = models.TextField(blank = True)
    
    # Users
    users = models.ManyToManyField(User, through='UserConcept', related_name='concepts')

    total_questions = models.IntegerField(default = 0) # Number of questions
    sq = models.IntegerField(editable = False, null = True)

    wall = models.OneToOneField(Wall, editable = False, null = True)
    
    # Resources (through conceptresource for bookmarks)
    resources = models.ManyToManyField(Resource, through='ConceptResource', related_name='concepts')
    questions = models.ManyToManyField(Question, blank=True, related_name='concepts')

    image = ThumbnailerImageField(max_length=255, upload_to=concept_file_path, blank=True, resize_source=dict(size=(50, 50), crop=True))
    
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)    

class UserConcept(models.Model):
    def __unicode__(self):
        return self.concept.name
    # Shortcuts through tree
    def network(self):
        return self.usercourse.coursei.network
    def course(self):
        return self.challengei.course
    def challenge(self):
        return self.challengei.challenge
    # Additional information
    def week_of_study(self):
        return ( ( datetime.datetime.today() - self.start_date  ).days / 7 ) + 1
    def is_active(self):
        return ( self.end_date == None ) or ( self.end_date > datetime.datetime.today() )
    # Update user's SQ value on this concept
    def update_sq(self):
        # Get user's attempts on this concept's questions 
        # group by x
        # x = qSQ (question's SQ)
        # y = percent_correct
        # Final Max('usq') is just to rename value, not possible to rename on values bit, which sucks
        # Old calc:         data = self.concept.questions.exclude(sq=None).filter(userquestionattempt__user=self.user).values('sq').annotate(n=Count('id'),y=Avg('userquestionattempt__percent_correct'),x=Max('sq'))

        end_date = datetime.datetime.now()
        start_date = end_date - settings.SQ_CALCULATE_HISTORY
        data = self.user.userquestionattempt_set.filter(created__range=(start_date,end_date)).filter(question__concepts=self.concept).exclude(question__sq=None).values('question__sq').annotate(n=Count('id'),y=Avg('percent_correct'),x=Max('question__sq'))

        self.previous_sq = self.sq
        self.sq = sq_calculate(data, 'desc') # Descending data set  

    # Update user's focus value for this concept
    # this is used to include in auto-challenges,etc.
    def update_focus(self, last_attempted=None):
        self.focus = 0
        # Focus is an weighting value, with importance of variables configurable
        # Variables
        # - Time since last attempt (OR none if never attempted): long time = increased likelihood, declines with age
        # - Lowest score (users SQ on this concept vs. SQ of the concept itself): lower = increased likelihood
        # TODO: Should be last_attempt updated whenever this concept is attempted as part of a challenge

        if last_attempted == None:
            last_attempted = self.concept.challengeset_set.filter(userchallengeset__user=self.user).aggregate(completed__max=Max('userchallengeset__completed'))['completed__max']
            #last_attempted = self.challenge_set.UserChallenge.objects.filter(challenge__concepts=self.concept, user=self.user).aggregate(Max('completed'))['completed__max']

        if last_attempted:
            # +1 for every hour passed since last attempt
            self.focus = ( datetime.datetime.now() - last_attempted ).seconds / 3600
        else:
            self.focus = 100 # Bump new items to max focus to guarantee first attempt
             
        if self.concept.sq and self.sq:    
            # +1 for every 1/2 SQ point difference between the uc and the c
            self.focus +=  ( self.concept.sq - self.sq )/2

        # If done all the questions, ask them less often        
        self.focus -= self.percent_complete / 10 # 100% complete = -10 focus
            
        # Limit 0-100
        self.focus = max( min( self.focus, 100 ), 0 )

        
    def update_statistics(self):
        # We get a list of all attempts, 1 record per question attempted. The count of these is the total attempted questions (magic)
        # FIXME: Is there an neater way to do this?
        questions_attempted = self.concept.questions.filter(userquestionattempt__user=self.user).values('id').annotate(attempts=Count('id')).count()

        if questions_attempted > 0:
            self.percent_complete = (self.concept.total_questions / questions_attempted) * 100
            # Limit 0-100 (in case the total_questions count is off)
            self.percent_complete = max( min( self.percent_complete, 100 ), 0 )
            
            tally = 0
            for question in self.concept.questions.all():
                latest = question.userquestionattempt_set.filter(user=self.user).latest('created')
                tally += latest.percent_correct
            
            self.percent_correct = tally / questions_attempted

            print self.percent_correct

    # Used to show %correct as a portion of the percent complete bar
    def percent_complete_correct(self):
        return percent_complete * (percent_correct/100)
    
    user = models.ForeignKey(User)
    concept = models.ForeignKey(Concept)

    start_date = models.DateTimeField(auto_now_add = True) 
    end_date = models.DateTimeField(null = True) 

    sq = models.IntegerField(editable = False, null = True)
    previous_sq = models.IntegerField(editable = False, null = True)
   
    focus = models.IntegerField(default = 100, editable = False) # Default to 100 to ensure newly activated are preferentially chosen
    
    percent_complete = models.IntegerField(editable = False, null = False, default=0)
    percent_correct = models.IntegerField(editable = False, null = False, default=0)

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
    
