from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg, Max, Min, Count, Sum, StdDev
from django.core.urlresolvers import reverse
from django.db.models.signals import post_save
# Smrtr
from settings import CHALLENGE_TTC_MINIMUM, CHALLENGE_TTC_FAIRNESS_MULTIPLIER
from questions.models import Question
from education.models import Concept
from network.models import Network
from resources.models import Resource
from education.models import Topic, UserTopic
from sq.utils import * 
# External
import datetime
import math

def challenge_file_path(instance=None, filename=None):
    return os.path.join('challenge', str(instance.id), filename)

# Challenges are tests of questions, on a particular topic/etc. created and pre-filled with 
# questions on creation. Once created exists until expire date passed
# Same mechanism is used for individual user's challenges, 
class Challenge(models.Model):
    def __unicode__(self):
        return self.name
        
    def get_absolute_url(self):
        return reverse('challenge-detail',kwargs={'challenge_id':str(self.id)})        

    def generate_questions(self): # Update questions for this challenge, using config settings on the model
        # Limit:
        # - through relationships back to this model ( question > question_concepts > concept > config_concepts )
        # - minSQ and maxSQ if these are set
        # - number of questions specified
        # - randomise order here
        self.questions = Question.objects.filter(
                concepts__challenge=self,
#                sq__gte=self.sq + 20,
#                sq__lte=self.sq - 20
                ).order_by('?')[0:self.total_questions]
        self.total_questions = self.questions.count() # Update total questions to the actual value

        if self.total_questions > 0:
            self.sq = self.questions.aggregate(Avg('sq'))['sq__avg'] # Update SQ to match questions
            # Generate time to complete *1.5, rounded up to nearest minute ( 60 seconds ). Should be fair and tidy
            # Get average of questions in this challenge, * 1.5
            time_to_complete = self.questions.aggregate(Sum('time_to_complete'))['time_to_complete__sum'] * CHALLENGE_TTC_FAIRNESS_MULTIPLIER
            # Set minimum challenge time of 1 minute
            time_to_complete = min( time_to_complete, CHALLENGE_TTC_MINIMUM )
            # Round up to nearest minute
            self.time_to_complete = math.ceil( time_to_complete / 60 ) * 60 # Round to nearest minute
            self.save()
        
    # Auto-generate a name from the current list of concepts
    def generate_name(self):
        c = list()
        for concept in self.concepts.all():
            c.append( concept.name )
        self.name = ', '.join( c )
        
    name = models.CharField(max_length=100)
    description = models.TextField(blank = True)

    # List of questions included in this challenge, used for outputting questions to users
    questions = models.ManyToManyField(Question, editable = False)
    sq = models.IntegerField(editable = False, null = True) # Auto-filled from average of questions on populate

    # Challenge definition: used to build the above questions
    # Only used when editing/updating list, not outputting questions
    concepts = models.ManyToManyField(Concept) # Concepts to source questions from
    total_questions = models.IntegerField(blank = True, null = True, default = 20) # Number of questions
    targetsq = models.IntegerField(blank = False, null = False, default = 100) # Target SQ for questions (Qs chosen will be as close to this as possible)
    # config_types = models.MultipleChoiceField(choices=questiontypes) # Types of questions (mcq, etc-not available yet)

    # Home network for e.g. company-specific challenges,restricted
    network = models.ForeignKey(Network, blank = True, null = True, editable = False) 

    # Created by
    user = models.ForeignKey(User, editable = False)
    created = models.DateTimeField(auto_now_add = True)

    # User's who have attempted this challenge and associated data
    users = models.ManyToManyField(User, through='UserChallenge', related_name='challenges', editable = False)

    # Auto-populated from total of question expected-duration times
    time_to_complete = models.IntegerField(editable = False, null = True )

    image = models.ImageField(max_length=255, upload_to=challenge_file_path, blank=True)

    #privacy = Public, Network, Private


class UserChallenge(models.Model):
    def __unicode__(self):
        if self.topic:
            return self.topic.name
        else:
            return self.challenge.name

    def save(self, force_insert=False, force_update=False):
        if self.id is None: #is new
            super(UserChallenge, self).save(force_insert, force_update)
            self.update_sq()
            
        #self.expires = datetime.datetime.now() + datetime.timedelta(weeks=1) # Default expires in 1 week
            
        super(UserChallenge, self).save(force_insert, force_update)
        
    def update_sq(self):
        # Get user's attempts on this challenges's questions 
        # group by x
        # x = qSQ (question's SQ)
        # y = percent_correct
        # Final Max('usq') is just to rename value, not possible to rename on values bit, which sucks
        data = self.challenge.questions.filter(userquestionattempt__user=self.user).exclude(sq=None).values('sq').annotate(n=Count('id'),y=Avg('userquestionattempt__percent_correct'),x=Max('sq'))
        self.previous_sq = self.sq
        self.sq = sq_calculate(data, 'desc') # Descending data set  
        self.save()

    def start(self):
        # Set values for start
        self.status = 1
        self.started = datetime.datetime.now()
            
    def complete(self):
        # Set values for completion
        self.status = 2
        self.completed = datetime.datetime.now()
        # TODO: Does it make more sense to update a latest_attempt here to determine concept focus or to determine it dynamic at focus-calculation time
        # Update associated userconcepts with last_attempt (now) 
        # for concept in self.challenge.concepts:
        #    uc = concept.userconcept_set.get(user=self.user)
        #    uc.last_attempt = datetime.datetime.now()
        #    # uc.update_sq(): Leave SQ recalculation to cron updates
        #    uc.save()
        
    # Helpers for templates
    def is_new(self):
        return self.status == 0
    def is_active(self):
        return self.status == 1
    def is_complete(self):
        return self.status == 2

    # Provide image for the userchallenge, based on the challenge (if exists), or the user's topic for this challenge
    def image(self):
        if self.challenge.image:
            return self.challenge.image
        else:
            return self.topic.image

        
    user = models.ForeignKey(User)
    challenge = models.ForeignKey(Challenge)
    
    # User's topic this was recommended based on (users can attempt same challenge via different topics)
    topic = models.ForeignKey(Topic, editable = False, null = True)

    STATUS_CHOICES = (
            (0, 'New'),
            (1, 'Active'),
            (2, 'Complete'),
        )

    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, null = False, editable = False, default = 0)

    # SQ for this set of questions
    sq = models.IntegerField(editable = False, null = True)
    previous_sq = models.IntegerField(editable = False, null = True)
    # User's rank on this challenge
    rank = models.IntegerField(editable = False, null = True)

    # Values of the /sucessful/ completion of the attempt
    # Started is update on each attempt start, completed only at finish - used to calculate question duration times
    started = models.DateTimeField(blank = True, null = True, editable = False)
    completed = models.DateTimeField(blank = True, null = True, editable = False)

    #expires = models.DateTimeField(blank = True, editable = False) # Exlucde from listings after this time. If not started by this time+n, remove from listings.




