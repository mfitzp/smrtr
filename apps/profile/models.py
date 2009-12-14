from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
# Externals
from countries.models import Country
from datetime import date as _date
from notification import models as notification
from wall.models import Wall, WallItem
# Spenglr
from sq.utils import * 

class UserProfile(models.Model):
    def __unicode__(self):
        return self.fullname()
    # Attach wall for this profile on save
    def save(self, force_insert=False, force_update=False):
        if self.id is None: #is new
            super(UserProfile, self).save(force_insert, force_update)
            self.wall = Wall.objects.create(slug='u'+str(self.user.id),name=self.fullname())
            # Add welcome message to the wall (as this is a new user)
            # Will want to move this out into a helper app with canned messages for output (similar to notifications)
            WallItem.save(WallItem,wall=self.wall,author_id=0,body='Welcome to Spenglr!')

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
        data = self.user.userquestionattempt_set.values('question__sq').annotate(n=Count('id'),y=Avg('percent_correct'),x=Max('question__sq'))
        self.sq = sq_calculate(data, 'desc') # Descending data set
        self.save()
        # Send notification to the user that their SQ has changed
        notification.send([self.user], "user_sq_updated", {"user": self.user})        

    # This is the only required field
    user = models.ForeignKey(User, unique=True)

    # The rest is completely up to you...
    about = models.TextField(blank = True)
    city = models.CharField('City', max_length = 50, blank = True)
    state = models.CharField('State/Province/Region', max_length = 50, blank = True)
    postcode = models.CharField('ZIP/Postal Code', max_length = 15, blank = True)
    country = models.ForeignKey(Country, null = True, blank = True)

    # Email already stored in main user record
    telno = models.CharField('Telephone', max_length=50, blank = True)
    # IM shit in here
    url = models.URLField(verify_exists = True, blank = True)
    sq = models.IntegerField(blank = True, null = True, editable = False)
    # Optional wall for this object
    wall = models.OneToOneField(Wall, editable = False, null = True)

def create_profile(sender, **kw):
    user = kw["instance"]
    if kw["created"]:
        up = UserProfile(user=user)
        up.save()

post_save.connect(create_profile, sender=User)
