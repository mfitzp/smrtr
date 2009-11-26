from django.db import models
from django.contrib.auth.models import User
# Externals
from countries.models import Country
from datetime import date as _date

class Profile(models.Model):
    def __unicode__(self):
        return "%s %s" % (self.user.first_name, self.user.last_name)
    def user_sq(self):
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
    sq = models.IntegerField()
