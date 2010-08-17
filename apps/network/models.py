import os.path
# Django
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg, Max, Min, Count
from django.core.urlresolvers import reverse
# Externals
from countries.models import Country
from datetime import date as _date
# Smrtr
from discuss.models import Forum


# Network = Course now e.g. 'Network' for AQA Biology
# Network is any grouping of people that exists to support study - for example a course, institution, organisation

TYPE_CHOICES = (
        (0, 'Other'),
        (1, 'Examination Board'),
        (2, 'Educational Institution'),
        (3, 'Organisation'),
        (4, 'Community'),
        (5, 'Course'),
    )

STAGE_CHOICES = (
        (0, 'Other'),
        (1, 'Preschool'),
        (2, 'Primary'),
        (3, 'Middle'),
        (4, 'Secondary'),
        (5, 'Tertiary'),
        (6, 'Vocational'),
    )

def network_file_path(instance=None, filename=None):
    return os.path.join('network', str(instance.id), filename)
    

# Education models contain educational structure from institution to topic exam
# INSERT INTO education_institution (name,address_1,address_2,city,state,country_id,postcode,telno,stage) SELECT SCHOOL_NAME as name,STREET as address_1, LOCALITY as address_2, TOWN as city, COUNTY as state, 'GB' as country_id, POSTCODE as postcode, CONCAT(0,TEL_STD,' ',TEL_NO) as telno,stage as stage FROM `school_list` WHERE 1
class Network(models.Model):
    def __unicode__(self):
        return self.name
        
    def get_absolute_url(self):
        return reverse('network-detail',kwargs={'network_id':str(self.id)})        
        
    # Auto-add a new wall object when saving Network
    def save(self, force_insert=False, force_update=False):
        if self.id is None: #is new
            # Need to save the parent object first to guarantee unique slug
            super(Network, self).save(force_insert, force_update)
            self.forum = Forum.objects.create(title=self.name)
        super(Network, self).save(force_insert, force_update)
        
    def get_absolute_url(self):
        return reverse('network-detail', urlconf=None, args=None, kwargs={ 'network_id':str(self.id) } )

    def locationquery(self):
        query = list()
        query.append(self.name)
        
        if self.address_1:
            query.append(self.address_1)
        if self.address_2:
            query.append(self.address_2)
        if self.city:
            query.append(self.city)
        if self.postcode:
            query.append(self.postcode)
        if self.state:
            query.append(self.state)
        if self.country:
            query.append(self.country.printable_name)
                
        return "".join(["%s, " % (v) for v in query])
            
    def location_is_set(self):
        return ( self.city or self.country_id )

    def memberships(self):
        return UserNetwork.objects.filter(network=self)
        
    def update_sq(self):
        # update
        self.sq = self.members.aggregate(sq=Avg('userprofile__sq'))['sq']
        self.save()

    name = models.CharField(max_length=200)
    description = models.TextField(blank = True)
    address_1 = models.CharField('Address Line 1', max_length=50, blank = True)
    address_2 = models.CharField('Address Line 1', max_length=50, blank = True)
    city = models.CharField('City', max_length = 50, blank = True)
    state = models.CharField('State/Province/Region', max_length = 50, blank = True)
    postcode = models.CharField('ZIP/Postal Code', max_length = 15, blank = True)
    country = models.ForeignKey(Country, null = True, blank = True)
    telno = models.CharField('Telephone', max_length=50, blank = True)
    url = models.URLField(verify_exists = True, blank = True)

    type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES, null = True, blank = True)
    stage = models.PositiveSmallIntegerField(choices=STAGE_CHOICES, null = True, blank = True)

    members = models.ManyToManyField(User, through='UserNetwork', related_name='networks')
    # SQ average of members, rates network intelligence 
    sq = models.IntegerField(blank = True, null = True, editable = False)
    # Optional wall for this object
    forum = models.OneToOneField(Forum, editable = False, null = True)
    # Parent network, courses at universities, or any other hierarchies stuff
    parent = models.ForeignKey('Network', null = True, blank = True)
    # Topics offered on this network - reverse from topic
    # topics = models.ManyToManyField('Topic')
    image = models.ImageField(max_length=255, upload_to=network_file_path, blank=True)

    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)
    
    class Meta:
        ordering = ['name']

class UserNetwork(models.Model):
    def __unicode__(self):
        return self.network.name
    user = models.ForeignKey(User)
    network = models.ForeignKey(Network)
    start_date = models.DateTimeField(editable = False, auto_now_add = True) # Join date for the network

    class Meta:
        unique_together = ("user", "network")
        ordering = ['network']

    
    
