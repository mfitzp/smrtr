from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg, Max, Min, Count
# Spenglr
from questions.models import Question
from education.models import Concept
from network.models import Network
from sq.utils import * 
# External
from datetime import date as _date
from wall.models import Wall

# Challenges are tests of questions, on a particular topic/etc. created and pre-filled with 
# questions on creation. Once created exists until expire date passed
# Same mechanism is used for individual user's challenges, 
class Challenge(models.Model):
    def __unicode__(self):
        return self.name

    def update_questions(self): # Update questions for this challenge, using config settings on the model
        # Limit:
        # - through relationships back to this model ( question > question_concepts > concept > config_concepts )
        # - minSQ and maxSQ if these are set
        # - number of questions specified
        self.questions = Question.objects.filter(sq_gte==self.minsq,sq_lte==self.maxsq)[0:self.config.number]
        
    name = models.CharField(max_length=75)
    description = models.TextField(blank = True)

    # List of questions included in this challenge, used for outputting questions to users
    questions = models.ManyToManyField(Question)

    # Challenge definition: used to build the above questions
    # Only used when editing/updating list, not outputting questions
    config_concepts = models.ManyToManyField(Concept) # Concepts to source questions from
    config_number = models.IntegerField(blank = True, null = True, default = 10) # Number of questions
    config_minsq = models.IntegerField(blank = True, null = True) # Min SQ for questions
    config_maxsq = models.IntegerField(blank = True, null = True) # Max SQ for questions
    # config_types = models.MultipleChoiceField(choices=questiontypes) # Types of questions (mcq, etc-not available yet)

    # Home network for e.g. company-specific challenges,restricted
    network = models.ForeignKey(Network, blank = True, null = True) 

    # Created by
    user = models.ForeignKey(User)

    # User's who have attempted this challenge and associated data
    users = models.ManyToManyField(User, through='UserChallenge', related_name='challenges')

    #privacy = Public, Network, Private


class UserChallenge(models.Model):
    def update_sq(self):
        # Get user's attempts on this challenges's questions 
        # group by x
        # x = qSQ (question's SQ)
        # y = percent_correct
        # Final Max('usq') is just to rename value, not possible to rename on values bit, which sucks
        data = self.challenge.questions.filter(userquestionattempt__user=self.user).values('sq').annotate(n=Count('id'),y=Avg('userquestionattempt__percent_correct'),x=Max('sq'))
        self.sq = sq_calculate(data, 'desc') # Descending data set  
        self.save()
        
    user = models.ForeignKey(User)
    challenge = models.ForeignKey(Challenge)

    # Number of attempts for this set of questions
    attempts = models.IntegerField(editable = False, null = True)
    # SQ for this set of questions
    sq = models.IntegerField(editable = False, null = True)
    # User's rank on this challenge
    rank = models.IntegerField(editable = False, null = True)

    
