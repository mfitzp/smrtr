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
from tagging.fields import TagField
from tagging.models import Tag

# Handler to extract text from a DOM nodelist
def getText(nodelist):
    rc = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
    return rc




# Question and resource models store information for testing/studying purposes
class Resource(models.Model):
    def __unicode__(self):
        return self.title

    class Meta:
        unique_together= (('namespace','uri'),)

    # Generate an URL for this resource object - these are standard resource
    # urls (not amazon/etc. which are handled by the template)
    # Preference is given to doi, then urn, then direct links
    def url(self):
        if self.namespace == 'doi':
            return "http://dx.doi.org/" + self.uri

        elif self.namespace == 'isbn':
            return "http://books.google.com/books?as_isbn=%s" % self.uri

        elif self.url:
            return self.uri


    # Autopopulate fields from the url/uri via webservices or direct request
    def autopopulate(self):

        # DOI is available for this resource (preferable)
        if self.namespace == 'doi':

            # Use the following lookup URL to return XML describing the entity in question
            f = urllib.urlopen("http://www.crossref.org/openurl?pid=egon@spenglr.com&noredirect=true&id=" + self.uri)
            # Build DOM for requested data
            dom = parse(f)
            f.close()

            if dom:
                # Iterate over available fields and pull them into our model
                for tag,field in {'article_title':'title','journal_title':'publisher','contributor':'author'}.items():
                    if dom.getElementsByTagName(tag):
                        self.__setattr__( field, dom.getElementsByTagName(tag)[0].childNodes[0].data )

                # Extract data information (only year is available, must process before assigning)
                if dom.getElementsByTagName('year'):
                    self.published = dom.getElementsByTagName('year')[0].childNodes[0].data + '-1-1'

                # Multiple contributor/author fields so handle by transforming into comma separated text field
                if dom.getElementsByTagName('contributor'):
                    authors = []
                    for contributor in dom.getElementsByTagName('contributor'):
                        # Hacky: It pulls in the first and surname of the contributor - but if the positions in the dom tree change it will bork
                        # Can't see obvious solution using the minidom
                        authors.append( contributor.childNodes[1].childNodes[0].data + ' ' + contributor.childNodes[3].childNodes[0].data )

                    # Should end up with "Martin Fitzpatrick, Cael Kay-Jackson" style listing of the authors pulled down
                    self.author = ', '.join(authors)

                # Iterate over available fields and pull them into our META
                for tag,field in {'volume':'volume','issue':'issue','first_page':'first_page','last_page':'last_page'}.items():
                    if dom.getElementsByTagName(tag):
                        self.meta[field]=dom.getElementsByTagName(tag)[0].childNodes[0].data

                if 'first_page' in self.meta and 'last_page' in self.meta:
                    self.meta['pages'] = int(self.meta['last_page']) - int(self.meta['first_page'])

        # No doi available, attempt lookup of information via ISBN if provided
        elif self.namespace == 'isbn':
            # Convert to ISBN-13 to prevent duplicates in db
            # Removed as changing this breaks some services - keep in format as shown on book itself
            # self.uri=isbn.toI13(self.uri)
            self.uri = isbn.isbn_strip(self.uri)
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
    
            # WorldCat would probably be 'better' but not seemingly possible
            # http://xissn.worldcat.org/webservices/xid/issn/0036-8075?method=getHistory&format=xml&ai=spenglr&fl=form

        # URN value is not set therefore attempt lookup via http directly (html, image, media files)
        else: #No namespace (a standard URL we hope) http/https/ftp/etc.
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


    # Process submitted URL/URIs for metadata
    def save(self, force_insert=False, force_update=False):
        # If URL provided pull and get metadata
        # for applicable hosts attempt to generate an URN value for this item
        # Use URN to query databases and build complete metadata entries
        self.autopopulate()
    
        super(Resource, self).save(force_insert, force_update)

    def mimemajor(self):
        if self.mimetype.find('/'):
            return self.mimetype.split('/')[0]
        else:
            return False

    def set_tags(self, tags):
        Tag.objects.update_tags(self, tags)
    def get_tags(self):
        return Tag.objects.get_for_object(self)    

    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    # We need to handle ISBN/etc. input here, use own on-save handler for these
    NAMESPACE_CHOICES = (
        ('isbn', 'ISBN: International Standard Book Number'),
        ('doi', 'DOI: Digital Object Identifier'),
    )
    namespace = models.CharField(max_length=4,choices=NAMESPACE_CHOICES, null = True, blank = True)
    uri = models.CharField(max_length=200, unique=True)
    # Content descriptors
    mimetype = models.CharField(editable=False,max_length=50)    
    language = models.CharField(max_length=10, blank=True)
    # Author/publisher 
    author =  models.CharField(max_length=50, blank=True)
    publisher = models.CharField(max_length=50, blank=True) 
    published = models.DateField(max_length=50, blank=True, null=True) 
    # Metadata
    meta = PickledObjectField(editable=False,blank=True,default=dict())
    # Positional information of particular bookmarks is stored on use of resource
    # therefore single resource instance for multiple bookmarks (chapters, z-time)
    created = models.DateField(auto_now_add=True)
    # Assignments of the resource to a particular user
    users = models.ManyToManyField(User, through='UserResource')
    # Resource tagging to aid searching
    tags = TagField()



# User's suggested resources (taken from incorrectly answered questions)
class UserResource(models.Model):
    class Meta:
        unique_together= (('user','resource'),)

    user = models.ForeignKey(User)
    resource = models.ForeignKey(Resource)
