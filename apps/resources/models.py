from django.db import models
from django.contrib.auth.models import User
# Serialisation
from django.core import serializers
import urllib, re
from xml.dom.minidom import parse, parseString
# Spenglr
from resources import isbn
# External
from picklefield.fields import PickledObjectField, PickledObject


# Question and resource models store information for testing/studying purposes
class Resource(models.Model):
    def __unicode__(self):
        return self.title

    def __init__(self, *args, **kwargs):
        self.meta=dict()
        super(Resource, self).__init__(*args, **kwargs) 

    # Generate an URL for this resource object - these are standard resource
    # urls (not amazon/etc. which are handled by the template)
    def url(self):
        if self.namespace=='':
            return self.uri
        elif self.namespace == 'isbn':
            return "http://books.google.com/books?as_isbn=%s" % self.uri
        elif self.namespace == 'issn':
            return "http://books.google.com/books?as_issn=%s" % self.uri


    # Autopopulate fields from the url/uri via webservices or direct request
    def autopopulate(self):
        # HTTP/etc. have no 'namespace' value set, therefore no lookup
        if self.namespace == '': #http/https/ftp/etc.
            # Open the URL, read 10k (arbitraty) for metadata off media files/etc.
            f = urllib.urlopen(self.uri)
            data = f.read(102400) #100K
            f.close()
            self.mimetype = f.info().gettype()

            if self.mimetype == 'text/html':
                # HTML in data, extract title field with regexp
                s = re.search('<title(.*)>(?P<title>.*)</title>', data)
                self.title = s.group('title')
                # For description we should either try and pull content (by id #content, etc.) or use meta description fields (rarely used)

            # Suggest following are handled with hachoir-metadata (bitbucket)
            elif self.mimetype.startswith('image'):
                pass

            elif self.mimetype.startswith('audio'):
                pass

            elif self.mimetype.startswith('video'):
                pass

        # URN based URIs
        if self.namespace == 'isbn':  
            # Convert to ISBN-13 to prevent duplicates in db
            self.uri=isbn.toI13(self.uri)
            # Get metadata from ISBN database: isbn in self.uri
            # Alternate API available at http://isbndb.com/docs/api/ provides additional information such as page numbers, language etc.
            # however misses description fields etc. A double-request may be optimal here
            f = urllib.urlopen("http://books.google.com/books/feeds/volumes?q=isbn:" + self.uri)
            # Build DOM for requested data
            dom = parse(f)
            f.close()
            # Iterate over available fields and pull them into our model
            for tag,field in {'dc:title':'title','dc:description':'description','dc:creator':'author','dc:publisher':'dc:publisher','dc:date':'published'}.items():
                if dom.getElementsByTagName(tag):
                    self.__setattr__( field, dom.getElementsByTagName(tag)[0].childNodes[0].data )

            # Date format is incorrect, fix before save
            # Google passes either YYYY, YYYY-MM, YYYY-MM-DD formats
            if self.published:
                d = self.published.split('-')
                for n in range(len(d), 3):
                    d.append('1') # 1st January
                self.published = '-'.join(d)

        # URN based URIs
        if self.namespace == 'issn':    
            # Strip dashes to prevent duplicates in DB
            self.uri=self.uri.replace('-','')
            # Get metadata from ISSN service
            # Service only provides a name for the resource, no other information: must do better
            # f = urllib.urlopen("http://tictoclookup.appspot.com/" + self.uri)
            f = urllib.urlopen("http://books.google.com/books/feeds/volumes?q=issn:" + self.uri)
            # Build DOM for requested data
            dom = parse(f)
            f.close()
            # Iterate over available fields and pull them into our model
            for tag,field in {'dc:title':'title'}.items():
                if dom.getElementsByTagName(tag):
                    self.__setattr__( field, dom.getElementsByTagName(tag)[0].childNodes[0].data )

        # WorldCat would probably be 'better' but not seemingly possible
        # http://xissn.worldcat.org/webservices/xid/issn/0036-8075?method=getHistory&format=xml&ai=spenglr&fl=form

    # Process submitted URL/URIs for metadata
    def save(self, force_insert=False, force_update=False):
        # If URL provided pull and get metadata
        # for applicable hosts attempt to generate an URN value for this item
        # Use URN to query databases and build complete metadata entries

        if self.uri:
            if self.uri.find(':'): # split off isbn: > isbn
                uri = self.uri.split(':',1)
                # Other URNspaces would be preferable but require services providing lookup 
                if uri[0] in ('isbn','issn'):
                    self.namespace=uri[0]
                    self.uri = uri[1]
                elif uri[0] in ('http','https','ftp'):
                    # Non-namespaced (includes http://)
                    self.namespace=''

        self.autopopulate()
    
        super(Resource, self).save(force_insert, force_update)

    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    # We need to handle ISBN/etc. input here, use own on-save handler for these
    # URN = isbn,etc. URL = webpage
    # If URN provided use that, otherwise use URL
    # when saving, attempt to generate an URN for any URL (e.g. amazon>ISBN)
    namespace = models.CharField(max_length=5, blank=True)
    uri = models.CharField(max_length=200, unique=True)
    # Content descriptors
    mimetype = models.CharField(editable=False,max_length=50)    
    language = models.CharField(max_length=10, blank=True)
    # Author/publisher 
    author =  models.CharField(max_length=50, blank=True)
    publisher = models.CharField(max_length=50, blank=True) 
    published = models.DateField(max_length=50, blank=True, null=True) 
    # Metadata
    meta = PickledObjectField(editable=False,blank=True, null=True)
    # Positional information of particular bookmarks is stored on use of resource
    # therefore single resource instance for multiple bookmarks (chapters, z-time)
    created = models.DateField(auto_now_add=True)
    # Assignments of the resource to a particular user
    users = models.ManyToManyField(User, through='UserResource')


# User's suggested resources (taken from incorrectly answered questions)
class UserResource(models.Model):
    class Meta:
        unique_together= (('user','resource'),)

    user = models.ForeignKey(User)
    resource = models.ForeignKey(Resource)
