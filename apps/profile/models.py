from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
# Externals
from countries.models import Country
from datetime import date as _date
# Spenglr
from sq.utils import * 

class UserProfile(models.Model):
    def __unicode__(self):
        return self.fullname()

    def fullname(self):
        if self.user.first_name == "":
            return self.user.username
        else:
            return "%s %s" % (self.user.first_name, self.user.last_name)

    def update_sq(self):
        data = self.user.userquestionattempt_set.values('question__sq').annotate(n=Count('id'),y=Avg('percent_correct'),x=Max('question__sq'))
        self.sq = sq_calculate(data, 'desc') # Descending data set
        self.save()

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

def create_profile(sender, **kw):
    user = kw["instance"]
    if kw["created"]:
        up = UserProfile(user=user)
        up.save()

post_save.connect(create_profile, sender=User)
