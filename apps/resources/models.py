from django.db import models
from django.contrib.auth.models import User
from django.core import serializers
import urllib
from xml.dom.minidom import parse, parseString
from resources import isbn
from resources import fields

# Question and resource models store information for testing/studying purposes
class Resource(models.Model):
    def __unicode__(self):
        return self.title
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
                # Convert to ISBN-13 to prevent duplicates in db
                uri[1]=isbn.toI13(uri[1])
                # Get metadata from ISBN database: isbn in urn[1]
                f = urllib.urlopen("http://books.google.com/books/feeds/volumes?q=isbn:" + uri[1])
                # Build DOM for requested data
                metadata = parse(f)
                f.close()
                # Iterate over available fields and pull them into our model
                for tag,field in {'title':'title','description':'description','creator':'author','publisher':'publisher','date':'published'}.items():
                    if metadata.getElementsByTagName('dc:' + tag):
                        self.__setattr__( field, metadata.getElementsByTagName('dc:' + tag)[0].childNodes[0].data )

                # Date format is incorrect, fix before save
                # Google passes either YYYY, YYYY-MM, YYYY-MM-DD formats
                if self.published:
                    d = self.published.split(':')
                    for n in range(len(d), 2):
                        d.append('1') # 1st January
                    self.published = '-'.join(d)

                self.uri = 'isbn:' + uri[1]

        super(Resource, self).save(force_insert, force_update)

    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    # We need to handle ISBN/etc. input here, use own on-save handler for these
    # URN = isbn,etc. URL = webpage
    # If URN provided use that, otherwise use URL
    # when saving, attempt to generate an URN for any URL (e.g. amazon>ISBN)
    namespace = models.CharField(max_length=5, blank=True)
    uri = models.CharField(max_length=50, unique=True)
    # Content descriptors
    mimetype = models.CharField(editable=False,max_length=50)    
    language = models.CharField(max_length=10, blank=True)
    # Author/publisher 
    author =  models.CharField(max_length=50, blank=True)
    publisher = models.CharField(max_length=50, blank=True) 
    published = models.DateField(max_length=50, blank=True, null=True) 
    # Metadata
    meta = fields.MetaDataField(editable=False,blank=True)
    # Positional information of particular bookmarks is stored on use of resource
    # therefore single resource instance for multiple bookmarks (chapters, z-time)

# User's suggested resources (taken from incorrectly answered questions)
# class UserResource




