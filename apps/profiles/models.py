from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
# Externals
from countries.models import Country
from datetime import date as date, datetime, timedelta
from notification import models as notification
from wall.models import Wall, WallItem
# Spenglr
from sq.utils import * 

class UserProfile(models.Model):
    def __unicode__(self):
        return self.fullname()
    # Attach wall for this profile on save new profile
    def save(self, force_insert=False, force_update=False):
        if self.id is None: #is new
            super(UserProfile, self).save(force_insert, force_update)
            # Attach wall item
            self.wall = Wall.objects.create(slug='u'+str(self.user.id),name=self.fullname())
            # Add welcome message to the wall (as this is a new user)
            # Will want to move this out into a helper app with canned messages for output (similar to notifications)
            item = WallItem(wall=self.wall,author_id=0,body='Welcome to Spenglr!')
            item.save()
            # Auto-join networks smrtr Start and smrtr Study
            from network.models import Network, UserNetwork
            UserNetwork(user=self.user, network=Network.objects.get(pk=1)).save()
            UserNetwork(user=self.user, network=Network.objects.get(pk=2)).save()
        super(UserProfile, self).save(force_insert, force_update)

    def fullname(self):
        if self.user.first_name == "":
            return self.user.username
        else:
            return "%s %s" % (self.user.first_name, self.user.last_name)

    def locationquery(self):
        if self.postcode:
            return self.postcode
        else:
            return self.city + ', ' + self.country.printable_name

    def update_sq(self):
        # Only calculate if questions have been attempted
        if self.user.userquestionattempt_set.count() > 0:
            # Retrieve records for past 6 months
            start_date = datetime.now() - timedelta(weeks=52)
            end_date = datetime.now()
            data = self.user.userquestionattempt_set.filter(created__range=(start_date,end_date)).values('question__sq').annotate(n=Count('id'),y=Avg('percent_correct'),x=Max('question__sq'))
            self.sq = sq_calculate(data, 'desc') # Descending data set
            self.save()
            # Send notification to the user if their SQ has changed
            if self.sq != prev_sq:
                notification.send([self.user], "user_sq_updated", {"user": self.user})        
                
    user = models.ForeignKey(User, unique=True, editable = False)

    # Information
    about = models.TextField(blank = True)
    # Location
    city = models.CharField('City', max_length = 50, blank = True)
    state = models.CharField('State/Province/Region', max_length = 50, blank = True)
    postcode = models.CharField('ZIP/Postal Code', max_length = 15, blank = True)
    country = models.ForeignKey(Country, null = True, blank = True)
    # Contact (email already in user model)
    telno = models.CharField('Telephone', max_length=50, blank = True)
    url = models.URLField(verify_exists = True, blank = True)
    sq = models.IntegerField(blank = True, null = True, editable = False)
    # Wall for this user
    wall = models.OneToOneField(Wall, editable = False, null = True)
    
def create_profile(sender, **kw):
    user = kw["instance"]
    if kw["created"]:
        up = UserProfile(user=user)
        up.save()

post_save.connect(create_profile, sender=User)
