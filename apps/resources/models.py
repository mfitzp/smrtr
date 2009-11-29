from django.db import models
from django.contrib.auth.models import User

# Question and resource models store information for testing/studying purposes
class Resource(models.Model):
    def __unicode__(self):
        return self.name
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # How to handle ISBN references and URIs? May need own handler e.g. URIField
    link = models.URLField(verify_exists=True)


# User's suggested resources (taken from incorrectly answered questions)
# class UserResource




