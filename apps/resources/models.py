from django.db import models
from django.contrib.auth.models import User
from django.core import serializers
import urllib
from xml.dom.minidom import parse, parseString

# Question and resource models store information for testing/studying purposes
class Resource(models.Model):
    def __unicode__(self):
        return self.title
    
    # Field name alias for more sensible referencing of data (see x,y,z dimensions below)
    # Standard set for audio/video resources
    def width(self):
        return self.x
    def height(self):
        return self.y
    def duration(self):
        return self.z
    # Text/book/etc. content additional hooks
    def words(self):
        return self.x
    def chapters(self):
        return self.y
    def pages(self):
        return self.z

    # Process submitted URL/URIs for metadata
    def save(self, force_insert=False, force_update=False):
        # If URL provided pull and get metadata
        # for applicable hosts attempt to generate an URN value for this item

        # Use URN to query databases and build complete metadata entries
        if self.uri:
            uri = self.uri.split(':') # split off isbn: > isbn
            # URL based URIs
            
            # URN based URIs
            if uri[0] == 'isbn':    
                # Get metadata from ISBN database: isbn in urn[1]
                f = urllib.urlopen("http://books.google.com/books/feeds/volumes?q=isbn:" + uri[1])
                metadata = parse(f)
                f.close()
                # isbndata now contains the xml for the specified book
                self.title = metadata.getElementsByTagName('dc:title')[0].childNodes[0].data
                self.description = metadata.getElementsByTagName('dc:description')[0].childNodes[0].data
                self.author = metadata.getElementsByTagName('dc:creator')[0].childNodes[0].data
                self.publisher = metadata.getElementsByTagName('dc:publisher')[0].childNodes[0].data

        super(Resource, self).save(force_insert, force_update)

    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    # We need to handle ISBN/etc. input here, use own on-save handler for these
    # URN = isbn,etc. URL = webpage
    # If URN provided use that, otherwise use URL
    # when saving, attempt to generate an URN for any URL (e.g. amazon>ISBN)
    uri = models.CharField()
    mimetype = models.CharField(editable=False,max_length=50)    
    language = models.CharField(max_length=10, blank=True)
    # Metadata
    author =  models.CharField(max_length=50, blank=True)
    publisher = models.CharField(max_length=50, blank=True) 
    # Dimensions of the resource: different meaning depending on resource type
    # audio:                             z = duration (secs)
    # video: x = width  y = height    z = duration (secs)
    # text:  x = words  y = chapters  z = pages
    x = models.IntegerField( editable=False, null=True )
    y = models.IntegerField( editable=False, null=True )
    z = models.IntegerField( editable=False, null=True )
    # Positional information of particular bookmarks is stored on use of resource
    # therefore single resource instance for multiple bookmarks (chapters, z-time)

# User's suggested resources (taken from incorrectly answered questions)
# class UserResource




