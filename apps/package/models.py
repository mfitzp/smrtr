import os.path
import datetime
# Django
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg, Max, Min, Count, Sum
from django.core.urlresolvers import reverse
# Smrtr
import package # Basic settings
from network.models import Network,UserNetwork
from resources.models import Resource
from questions.models import Question
from challenge.models import Challenge, UserChallenge
from sq.utils import * 
# External
from countries.models import Country
from easy_thumbnails.fields import ThumbnailerImageField
from wall.models import Wall


# Packages

CHALLENGES_MIN_ACTIVE = 5

CHALLENGE_TTC_MINIMUM = 180 # Minimum time in seconds for a package time limit
CHALLENGE_TTC_FAIRNESS_MULTIPLIER = 3 # Multiple avg by this value to get 'fair' limit

# Network = Course now e.g. 'Network' for AQA Biology
# Below this packages are the basis of study on that packages may have a home network, be tied to a specific network, or freely open
# Below packages 'elements' define the learning stages associated (e.g. lecture, chapter, issue)

def package_file_path(instance=None, filename=None):
    return os.path.join('package', str(instance.id), filename)
 
# Definitions of courses available and their constituent challenges
# Subjects are tied to a home network
class Package(models.Model):
    def __unicode__(self):
        return self.name
        
    def get_absolute_url(self):
        return reverse('package-detail',kwargs={'package_id':str(self.id)})
                
    # Auto-add a new wall object when creating new Course
    def save(self, force_insert=False, force_update=False):
        if self.id is None: #is new
            super(Package, self).save(force_insert, force_update)

            self.wall = Wall.objects.create(name=self.name, slug='package-' + str(self.id))
            self.networks.add(self.network) # Make link to 'offer' this network
                          
        super(Package, self).save(force_insert, force_update)

    def update_sq(self):
        # update
        self.sq = self.challenges.aggregate(Avg('sq'))['sq__avg']
        self.save()

    # Home network for e.g. company-specific subjects
    network = models.ForeignKey(Network, blank = True, null = True) 
    # Networks offering this package
    networks = models.ManyToManyField(Network, related_name='packages')
    
    # Users
    users = models.ManyToManyField(User, through='UserPackage', related_name='packages')
    
    name = models.CharField(max_length=75)
    description = models.TextField(blank = True)

    sq = models.IntegerField(editable = False, null = True)

    wall = models.OneToOneField(Wall, editable = False, null = True)

# Challenges for this package
    challenges = models.ManyToManyField(Challenge, blank=True)
    
    image = ThumbnailerImageField(max_length=255, upload_to=package_file_path, blank=True, resize_source=dict(size=(50, 50), crop=True))
    
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)    
   


class UserPackage(models.Model):
    def __unicode__(self):
        return self.package.name
        
    def save(self, *args, **kwargs):
        if self.id is None: #is new
            # Auto-activate all child challenges for this package
            for challenge in self.package.challenges.all():
                try:
                    UserChallenge(user=self.user, challenge=challenge).save()
                except:
                    pass
            self.update_statistics()
            self.update_sq()
            
        super(UserPackage, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        
        # Clean up removing challenges that the user is *only* studying on this package
        userchallenges = UserChallenge.objects.filter(
                    user=self.user,
                    challenge__userchallenge__user=self.user,
                    challenge__package=self.package,
                    ).annotate(n=Count('challenge__userchallenge')).exclude(n__gt=1).delete()
        super(UserPackage, self).delete(*args, **kwargs)


    def is_active(self):
        return ( self.end_date == None ) or ( self.end_date > datetime.datetime.today() )

    def update_sq(self):
        self.previous_sq = self.sq
        self.sq = UserChallenge.objects.filter(user=self.user, challenge__package = self.package).aggregate(Avg('sq'))['sq__avg']

    def update_statistics(self):
        values = UserChallenge.objects.filter(user=self.user, challenge__package = self.package).aggregate(is_complete=Avg('is_complete'),percent_correct=Avg('percent_correct'))
        # Don't save if null (i.e. no value yet on any challenges)

        if values:
            #assert False, values['is_complete']
            if values['is_complete'] > 0: # Not None
                self.percent_complete = values['is_complete'] * 100
                self.percent_correct = values['percent_correct']
                
                # Send notifications
                if self.percent_complete == 100:
    
                    # Have we only just completed?
                    if self.end_date == None:
                        self.end_date = datetime.datetime.now()
                
                        from wallextend.models import add_extended_wallitem
                
                        # Are we first? (i.e. are there no others)
                        no_of_others = self.package.userpackage_set.filter(percent_complete=100).order_by('end_date').count()
                        if no_of_others == 0:
                            add_extended_wallitem( self.package.wall, self.user, template_name='package_1stcomplete.html', extra_context={'package': self.package, 'userpackage': self, })

                        # Did we ace it?
                        if self.percent_correct == 100:
                            add_extended_wallitem( self.package.wall, self.user, template_name='package_100pc.html', extra_context={'package': self.package, 'userpackage': self, })

     # Used to show %correct as a portion of the percent complete bar
    def percent_complete_correct(self):
        if self.percent_correct:
            return self.percent_complete * ( float(self.percent_correct)/100 )
        else:
            return 0
    
    def time_to_complete(self):
        return self.end_date - self.start_date
        
    def is_new(self):
        return self.percent_complete == 0

    def is_complete(self):
        return self.percent_complete == 100


    user = models.ForeignKey(User)
    package = models.ForeignKey(Package)

    start_date = models.DateTimeField(auto_now_add = True)
    end_date = models.DateTimeField(null = True)

    sq = models.IntegerField(editable = False, null = True)
    previous_sq = models.IntegerField(editable = False, null = True)

    percent_complete = models.IntegerField(editable = False, null = False, default=0)
    percent_correct = models.IntegerField(editable = False, null = True)

    class Meta:
        unique_together = ("user", "package")



