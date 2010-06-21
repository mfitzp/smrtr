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
        # - randomise order here
        self.questions = Question.objects.filter(
                concepts__challenge=self,
#                sq__gte=self.sq + 20,
#                sq__lte=self.sq - 20
                ).order_by('?')[0:self.total_questions]

        self.sq = self.questions.aggregate(Avg('sq'))['sq__avg'] # Update SQ to match questions
        self.save()
        
    # Auto-generate a name from the current list of concepts
    def generate_name(self):
        name = list()
        for concept in self.concepts.all():
            name.append( concept.name )
        self.name = ', '  .join( name )
        self.name = self.name[0:100] # Truncate to field limit
        
    name = models.CharField(max_length=100)
    description = models.TextField(blank = True)

    # List of questions included in this challenge, used for outputting questions to users
    questions = models.ManyToManyField(Question, editable = False)
    sq = models.IntegerField(editable = False, null = True) # Auto-filled from average of questions on populate

    # Challenge definition: used to build the above questions
    # Only used when editing/updating list, not outputting questions
    concepts = models.ManyToManyField(Concept) # Concepts to source questions from
    total_questions = models.IntegerField(blank = True, null = True, default = 10) # Number of questions
    targetsq = models.IntegerField(blank = False, null = False, default = 100) # Target SQ for questions (Qs chosen will be as close to this as possible)
    # config_types = models.MultipleChoiceField(choices=questiontypes) # Types of questions (mcq, etc-not available yet)

    # Home network for e.g. company-specific challenges,restricted
    network = models.ForeignKey(Network, blank = True, null = True, editable = False) 

    # Created by
    user = models.ForeignKey(User, editable = False)

    # User's who have attempted this challenge and associated data
    users = models.ManyToManyField(User, through='UserChallenge', related_name='challenges', editable = False)

    #privacy = Public, Network, Private


class UserChallenge(models.Model):
    def __unicode__(self):
        return self.challenge.name
        
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

    STATUS_CHOICES = (
            (0, 'New'),
            (1, 'Active'),
            (2, 'Complete'),
        )

    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, null = False, editable = False, default = 0)

    # Number of attempts for this set of questions
    attempts = models.IntegerField(editable = False, null = True)
    # SQ for this set of questions
    sq = models.IntegerField(editable = False, null = True)
    # User's rank on this challenge
    rank = models.IntegerField(editable = False, null = True)

    
