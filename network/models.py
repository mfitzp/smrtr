from django.db import models
from django.contrib.auth.models import User
# Externals
from countries.models import Country
from forum.models import Forum
from datetime import date as _date

# Education models contain educational structure from institution to module exam
# INSERT INTO education_institution (name,address_1,address_2,city,state,country_id,postcode,telno,stage) SELECT SCHOOL_NAME as name,STREET as address_1, LOCALITY as address_2, TOWN as city, COUNTY as state, 'GB' as country_id, POSTCODE as postcode, CONCAT(0,TEL_STD,' ',TEL_NO) as telno,stage as stage FROM `school_list` WHERE 1
class Network(models.Model):
    def __unicode__(self):
        return self.name
    name = models.CharField(max_length=200)
    description = models.TextField(blank = True)
    address_1 = models.CharField('Address Line 1', max_length=50, blank = True)
    address_2 = models.CharField('Address Line 1', max_length=50, blank = True)
    city = models.CharField('City', max_length = 50, blank = True)
    state = models.CharField('State/Province/Region', max_length = 50, blank = True)
    postcode = models.CharField('ZIP/Postal Code', max_length = 15, blank = True)
    country = models.ForeignKey(Country, null = True, blank = True)
    telno = models.CharField('Telephone', max_length=50, blank = True)
    TYPE_CHOICES = (
        (0, 'Other'),
        (1, 'Educational Institution'),
        (2, 'Examination Board'),
        (3, 'Organisation'),
        (4, 'Community'),
        (5, 'Network'),
    )
    type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES, null = True, blank = True)
    STAGE_CHOICES = (
        (0, 'Other'),
        (1, 'Preschool'),
        (2, 'Primary'),
        (3, 'Middle'),
        (4, 'Secondary'),
        (5, 'Tertiary'),
        (6, 'Vocational'),
    )
    stage = models.PositiveSmallIntegerField(choices=STAGE_CHOICES, null = True, blank = True)
    members = models.ManyToManyField(User, through='UserNetwork', related_name='networks')


class UserNetwork(models.Model):
    def __unicode__(self):
        return self.network.name
    user = models.ForeignKey(User)
    network = models.ForeignKey(Network, related_name='memberships')
    start_date = models.DateField(editable = False, auto_now_add = True) # Join date for the network
