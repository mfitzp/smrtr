import os.path
import datetime
# Django
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg, Max, Min, Count, Q
from django.core.urlresolvers import reverse
# Smrtr
from network.models import Network,UserNetwork
from resources.models import Resource
from questions.models import Question,UserQuestionAttempt
#from package.models import UserPackage
from sq.utils import * 
# External
from countries.models import Country
from easy_thumbnails.fields import ThumbnailerImageField
from wall.models import Wall


CHALLENGES_MIN_ACTIVE = 5

CHALLENGE_TTC_MINIMUM = 180 # Minimum time in seconds for a package time limit
CHALLENGE_TTC_FAIRNESS_MULTIPLIER = 3 # Multiple avg by this value to get 'fair' limit

# Network = Course now e.g. 'Network' for AQA Biology
# Below this packages are the basis of study on that packages may have a home network, be tied to a specific network, or freely open
# Below packages 'elements' define the learning stages associated (e.g. lecture, chapter, issue)

def challenge_file_path(instance=None, filename=None):
    return os.path.join('challenge', str(instance.id), filename)    

# Element is a defining part of a course 
# Elements are always tied to a specific subject?? Or freely available
# If an individual challenge is self-contained area of study e.g. 'thermodynamics' (that's possibly a bit big)
# may be allocated widely, package components?
class Challenge(models.Model):
    def __unicode__(self):
        return self.name
    def get_absolute_url(self):
        return reverse('challenge-detail',kwargs={'challenge_id':str(self.id)})
                
    # Auto-add a new wall object when creating new Challenge
    def save(self, force_insert=False, force_update=False):
        if self.id is None: #is new
            super(Challenge, self).save(force_insert, force_update)
            self.wall = Wall.objects.create(name=self.name, slug='challenge-' + str(self.id))
        super(Challenge, self).save(force_insert, force_update)

    def update_sq(self):
        # update
        self.sq = self.questions.aggregate(Avg('sq'))['sq__avg']
        self.save()

    def update_statistics(self):        
        time_to_complete = self.questions.aggregate(Sum('time_to_complete'))['time_to_complete__sum'] * CHALLENGE_TTC_FAIRNESS_MULTIPLIER
        # Set minimum package time of 1 minute
        time_to_complete = min( time_to_complete, CHALLENGE_TTC_MINIMUM )
        # Round up to nearest minute
        self.time_to_complete = math.ceil( time_to_complete / 60 ) * 60 # Round to nearest minute        

    # Home network for e.g. company-specific challenges
    network = models.ForeignKey(Network, blank = True, null = True) 
    name = models.CharField(max_length=75)
    description = models.TextField(blank = True)
    
    # Users
    users = models.ManyToManyField(User, through='UserChallenge', related_name='challenges')

    total_questions = models.IntegerField(default = 0) # Number of questions
    total_resources = models.IntegerField(default = 0) # Number of resources

    time_to_complete = models.IntegerField(editable = False, default = CHALLENGE_TTC_MINIMUM )
    
    sq = models.IntegerField(editable = False, null = True)

    wall = models.OneToOneField(Wall, editable = False, null = True)
    
    # Resources (through challengeresource for bookmarks)
    resources = models.ManyToManyField(Resource, through='ChallengeResource', related_name='challenges')
    questions = models.ManyToManyField(Question, blank=True, related_name='challenges')

    image = ThumbnailerImageField(max_length=255, upload_to=challenge_file_path, blank=True, resize_source=dict(size=(50, 50), crop=True))
    
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)    

class UserChallenge(models.Model):
    def __unicode__(self):
        return self.challenge.name
        
    # Auto-add a new wall object when creating new Challenge
    def save(self, force_insert=False, force_update=False):
        if self.id is None: #is new
            #If there are no questions on this challenge, we're 100% complete as soon as we start
            if self.challenge.total_questions == 0:
                self.percent_complete=100
            else:
                self.update_statistics()
                self.update_sq()
        super(UserChallenge, self).save(force_insert, force_update)        
        
    # Update user's SQ value on this challenge
    def update_sq(self):
        # Get user's attempts on this challenge's questions 
        # group by x
        # x = qSQ (question's SQ)
        # y = percent_correct
        # Final Max('usq') is just to rename value, not possible to rename on values bit, which sucks
        # Old calc:         data = self.challenge.questions.exclude(sq=None).filter(userquestionattempt__user=self.user).values('sq').annotate(n=Count('id'),y=Avg('userquestionattempt__percent_correct'),x=Max('sq'))

        end_date = datetime.datetime.now()
        start_date = end_date - settings.SQ_CALCULATE_HISTORY
        data = self.user.userquestionattempt_set.filter(created__range=(start_date,end_date)).filter(question__challenges=self.challenge).exclude(question__sq=None).values('question__sq').annotate(n=Count('id'),y=Avg('percent_correct'),x=Max('question__sq'))

        self.previous_sq = self.sq
        self.sq = sq_calculate(data, 'desc') # Descending data set  

    # Update user's focus value for this challenge
    # this is used to include in auto-packages,etc.
    def update_focus(self, last_attempted=None):
        self.focus = 0
        # Focus is an weighting value, with importance of variables configurable
        # Variables
        # - Time since last attempt (OR none if never attempted): long time = increased likelihood, declines with age
        # - Lowest score (users SQ on this challenge vs. SQ of the challenge itself): lower = increased likelihood
        # TODO: Should be last_attempt updated whenever this challenge is attempted as part of a package

        if last_attempted == None:
            last_attempted = self.challenge.userchallengeattempt_set.filter(user=self.user).aggregate(completed__max=Max('completed'))['completed__max']
            #last_attempted = self.package_set.UserPackage.objects.filter(package__challenges=self.challenge, user=self.user).aggregate(Max('completed'))['completed__max']

        if last_attempted:
            # +1 for every hour passed since last attempt
            self.focus = ( datetime.datetime.now() - last_attempted ).seconds / 3600
        else:
            self.focus = 100 # Bump new items to max focus to guarantee first attempt
             
        if self.challenge.sq and self.sq:    
            # +1 for every 1/2 SQ point difference between the uc and the c
            self.focus +=  ( self.challenge.sq - self.sq )/2

        # If done all the questions correctly, ask them less often        
        self.focus -= self.percent_correct / 10 # 100% correct = -10 focus
            
        # Limit 0-100
        self.focus = max( min( self.focus, 100 ), 0 )

    def complete(self):
        self.completed = datetime.datetime.now()
    
    user = models.ForeignKey(User)
    challenge = models.ForeignKey(Challenge)

    completed = models.DateTimeField(null = True) 
    percent_complete = models.IntegerField(editable = False, null = False, default=0)
        
    sq = models.IntegerField(editable = False, null = True)
    previous_sq = models.IntegerField(editable = False, null = True)
   
    focus = models.IntegerField(default = 100, editable = False) # Default to 100 to ensure newly activated are preferentially chosen
    
    percent_correct = models.IntegerField(editable = False, null = True)
    current_streak = models.IntegerField(editable = False, null = False, default=0)    
    total_attempts = models.IntegerField(editable = False, null = False, default=0)    
    
    class Meta:
        unique_together = ("user", "challenge")


class UserChallengeAttempt(models.Model):
    def __unicode__(self):
        return self.challenge.name
                    
    def start(self):
        self.started = datetime.datetime.now()
        
    def complete(self):
        self.completed = datetime.datetime.now()

    user = models.ForeignKey(User)
    challenge = models.ForeignKey(Challenge)
        
    started = models.DateTimeField(auto_now_add = True, null = True) 
    completed = models.DateTimeField(null = True)        

    percent_correct = models.IntegerField(editable = False, null = True)


# Resource attached to specific question
# Use this model to specify question-specific bookmarks in the resource, for example 
# page numbers, chapters, timestamp, #anchors etc.??
class ChallengeResource(models.Model):
    def __unicode__(self):
        return self.title
        
    resource = models.ForeignKey(Resource)
    challenge = models.ForeignKey(Challenge)    
    
    class Meta:
        unique_together = ("resource", "challenge")
    
