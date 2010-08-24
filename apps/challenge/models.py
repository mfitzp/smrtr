import os.path
import datetime
# Django
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg, Max, Min, Count, Sum
from django.core.urlresolvers import reverse
# Smrtr
import challenge # Basic settings
from network.models import Network,UserNetwork
from resources.models import Resource
from questions.models import Question
from concept.models import Concept, UserConcept
from sq.utils import * 
# External
from countries.models import Country
from easy_thumbnails.fields import ThumbnailerImageField
from wall.models import Wall


# Challenges

CHALLENGES_MIN_ACTIVE = 5

CHALLENGE_TTC_MINIMUM = 60 # Minimum time in seconds for a challenge time limit
CHALLENGE_TTC_FAIRNESS_MULTIPLIER = 1.5 # Multiple avg by this value to get 'fair' limit

# Network = Course now e.g. 'Network' for AQA Biology
# Below this challenges are the basis of study on that challenges may have a home network, be tied to a specific network, or freely open
# Below challenges 'elements' define the learning stages associated (e.g. lecture, chapter, issue)

def challenge_file_path(instance=None, filename=None):
    return os.path.join('challenge', str(instance.id), filename)
 
# Definitions of courses available and their constituent concepts
# Subjects are tied to a home network
class Challenge(models.Model):
    def __unicode__(self):
        return self.name
        
    def get_absolute_url(self):
        return reverse('challenge-detail',kwargs={'challenge_id':str(self.id)})
                
    # Auto-add a new wall object when creating new Course
    def save(self, force_insert=False, force_update=False):
        if self.id is None: #is new
            super(Challenge, self).save(force_insert, force_update)

            self.wall = Wall.objects.create(name=self.name, slug='challenge-' + str(self.id))
            self.networks.add(self.network) # Make link to 'offer' this network
                          
        super(Challenge, self).save(force_insert, force_update)

    def update_sq(self):
        # update
        self.sq = self.concepts.aggregate(Avg('sq'))['sq__avg']
        self.save()

    # Home network for e.g. company-specific subjects
    network = models.ForeignKey(Network, blank = True, null = True) 
    # Networks offering this challenge
    networks = models.ManyToManyField(Network, related_name='challenges')
    
    # Users
    users = models.ManyToManyField(User, through='UserChallenge', related_name='challenges')
    
    name = models.CharField(max_length=75)
    description = models.TextField(blank = True)

    sq = models.IntegerField(editable = False, null = True)

    wall = models.OneToOneField(Wall, editable = False, null = True)

# Concepts for this challenge
    concepts = models.ManyToManyField(Concept, blank=True)
    
    image = ThumbnailerImageField(max_length=255, upload_to=challenge_file_path, blank=True, resize_source=dict(size=(50, 50), crop=True))
    
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)    
   
# Study models store information about user's experience with education
# Models are ManytoMany through Models (ie they are used as the basis for linking
# other models together, while appending additional information

class UserChallenge(models.Model):
    def __unicode__(self):
        return self.challenge.name
        
    def save(self, force_insert=False, force_update=False):
        if self.id is None: #is new
            # Auto-activate all child concepts for this challenge
            for concept in self.challenge.concepts.all():
                try:
                    UserConcept(user=self.user, concept=concept).save()
                except:
                    pass

            # Get primary challengeset for this (cannot be Null)
            self.generate_challengeset()
        super(UserChallenge, self).save(force_insert, force_update)

    def is_active(self):
        return ( self.end_date == None ) or ( self.end_date > _date.today() )

    def update_sq(self):
        self.previous_sq = self.sq
        self.sq = UserConcept.objects.filter(user=self.user, concept__challenge = self.challenge).aggregate(Avg('sq'))['sq__avg']
        self.save()

    def update_statistics(self):
        values = UserConcept.objects.filter(user=self.user, concept__challenge = self.challenge).aggregate(percent_complete=Avg('percent_complete'),percent_correct=Avg('percent_correct'))
        # Don't save if null (i.e. no value yet on any concepts)

        if values:
            if values['percent_complete'] > 0: # Not None
                self.percent_complete = values['percent_complete']
                self.percent_correct = values['percent_correct']
                
                # Send notifications
                if self.percent_complete == 100:
    
                    # Have we only just completed?
                    if self.end_date == None:
                        self.end_date = datetime.datetime.now()
                
                        # Are we first?
                        if self.user == self.challenge.userchallenge_set.filter(percent_complete=100).order_by('completed')[0]:
                            add_extended_wallitem( self.challenge.wall, self.user, template_name='challenge_1stcomplete.html', extra_context={'challenge': self.challenge, 'userchallenge': self, })

                        # Did we ace it?
                        if self.percent_correct == 100:
                                add_extended_wallitem( self.challenge.wall, self.user, template_name='challenge_100pc.html', extra_context={'challenge': self.challenge, 'userchallenge': self, })

                self.save()

        # Don't save if null (i.e. no value yet on any concepts)
        if percent_complete:
            self.percent_complete = percent_complete
            

            self.save()

            
    def generate_challengeset(self, exclude_current_challengeset=None):
    
        # Get the list of concepts that we are going to use
        # Concepts available on the challenge, ordered by the user's focus
        # get the top 3(?) and put them into a challengeset
        concepts = Concept.objects.filter(userconcept__user=self.user).filter(challenge=self.challenge).exclude(total_questions=0).order_by('-userconcept__focus','?')

        # Generate something without the current challengeset's concepts in it ('I don't like this' link)
        if exclude_current_challengeset:
            for concept in self.challengeset.concepts.all():
                concepts = concepts.exclude(pk=concept.id)              

        if concepts:
            concepts = concepts[0:3] # Top 3 concepts (by focus)
        else:
            return False

        # Look for already existing matching challengeset's the user has 
        cs = ChallengeSet.objects.exclude(userchallengeset__user=self.user)
        
        for concept in concepts:
            cs = cs.filter(concepts=concept)              
            
        if cs: # We have something left after all that filtering
            challengeset=cs[0]
        else:
            challengeset = ChallengeSet(challenge=self.challenge)
            challengeset.save() # Save so can attach objects to it
            
            for concept in concepts:
                challengeset.concepts.add(concept)            

            challengeset.generate_description()
            challengeset.generate_questions()
            challengeset.generate_resources()                       
            challengeset.save()

        # We have the challengeset found/generated. Now add it to the userchallenge object            
        self.challengeset = challengeset
        self.save()
            
    # Used to show %correct as a portion of the percent complete bar
    def percent_complete_correct(self):
        return percent_complete * (percent_correct/100)
    
    def time_to_complete(self):
        return end_date - start_date
        
    def is_new(self):
        return self.percent_complete == 0

    def is_complete(self):
        return self.percent_complete == 100


    user = models.ForeignKey(User)
    challenge = models.ForeignKey(Challenge)
    challengeset = models.ForeignKey('ChallengeSet')

    start_date = models.DateTimeField(auto_now_add = True)
    end_date = models.DateTimeField(null = True)

    sq = models.IntegerField(editable = False, null = True)
    previous_sq = models.IntegerField(editable = False, null = True)

    percent_complete = models.IntegerField(editable = False, null = False, default=0)
    percent_correct = models.IntegerField(editable = False, null = False, default=0)

    class Meta:
        unique_together = ("user", "challenge")



class ChallengeSet(models.Model):
    def __unicode__(self):
        return self.name
        
    def get_absolute_url(self):
        return reverse('challenge-detail',kwargs={'challenge_id':str(self.id)})        

    def generate_description(self):
        c = list()
        self.description = ''
        for concept in self.concepts.all():
            c.append( concept.name )
            self.description = ', '.join( c )

    def generate_questions(self): # Update questions for this challenge, using config settings on the model
        # Limit:            self.generate_description()
        # - through relationships back to this model ( question > question_concepts > concept > config_concepts )
        # - minSQ and maxSQ if these are set
        # - number of questions specified
        # - randomise order here
        self.questions = Question.objects.filter(
                concepts__challengeset=self,
#                sq__gte=self.sq + 20,
#                sq__lte=self.sq - 20
                ).order_by('?') #[0:self.total_questions]
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
       
    def generate_resources(self):
        self.total_resources = Resource.objects.filter(concepts__challengeset=self).count()
       
    challenge = models.ForeignKey(Challenge)
    description = models.TextField(blank = True)

    # Challenge definition: used to build the above questions
    # Only used when editing/updating list, not outputting questions
    concepts = models.ManyToManyField(Concept) # Concepts to source questions from
    questions = models.ManyToManyField(Question, editable = False)

    sq = models.IntegerField(editable = False, null = True) # Auto-filled from average of questions on populate

    time_to_complete = models.IntegerField(editable = False, null = True )

    total_questions = models.IntegerField(blank = True, default = 20) # Number of questions
    total_resources = models.IntegerField(blank = True, default = 0) # Number of resources (show prepare link?)

    #percent_correct = models.IntegerField(editable = False, null = True)

    created = models.DateTimeField(auto_now_add=True)



class UserChallengeSet(models.Model):

    def time_taken(self):
        return self.completed - self.started
        
    def start(self):
        self.started = datetime.datetime.now()
        
    def complete(self):
        self.completed = datetime.datetime.now()
        
    user = models.ForeignKey(User)
    challengeset = models.ForeignKey(ChallengeSet)

    percent_correct = models.IntegerField(null = True)

    started = models.DateTimeField(auto_now_add=True)
    completed = models.DateTimeField()

    class Meta:
        # Can only attempt a set of questions once
        unique_together = ("user", "challengeset")    

