import os.path
import datetime
# Django
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg, Max, Min, Count
from django.core.urlresolvers import reverse
# Smrtr
# Externals
from countries.models import Country
from easy_thumbnails.fields import ThumbnailerImageField
from wall.models import Wall


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
            self.wall = Wall.objects.create(name=self.name, slug='network-' + str(self.id))
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
    wall = models.OneToOneField(Wall, editable = False, null = True)
    # Parent network, courses at universities, or any other hierarchies stuff
    parent = models.ForeignKey('Network', null = True, blank = True)
    # Packages offered on this network - reverse from package
    # packages = models.ManyToManyField('Package')
    image = ThumbnailerImageField(max_length=255, upload_to=network_file_path, blank=True, resize_source=dict(size=(50, 50), crop=True))

    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)
    
    class Meta:
        ordering = ['name']

class UserNetwork(models.Model):
    def __unicode__(self):
        return self.network.name
        
    def delete(self, *args, **kwargs):
        # Check if leaving home network
        profile = self.user.get_profile()
        if profile.network == self.network:
            profile.network = None # Set empty
        profile.save()
            
        super(UserNetwork, self).delete(*args, **kwargs)        
        
    user = models.ForeignKey(User)
    network = models.ForeignKey(Network)
    start_date = models.DateTimeField(editable = False, auto_now_add = True) # Join date for the network

    class Meta:
        unique_together = ("user", "network")
        ordering = ['network']

    
    
