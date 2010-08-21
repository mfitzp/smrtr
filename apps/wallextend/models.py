import os.path
# Django
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.template import Context
from django.template.loader import render_to_string

# Externals
from wall.models import WallItem


class WallItemExtend(models.Model):

    class Meta:
        db_table = 'wall_wallitem_extend'

    def __unicode__(self):
        return self.wall
    
    wallitem = models.OneToOneField(WallItem, primary_key=True, related_name='extend')
    
    # Flag the parent WallItem as safe (i.e. output html as is, overriding the Wall setting)
    is_safe = models.BooleanField(default=False)
            
    #TODO: Think up some other uses for this table ;)
    

# Add an extended wallitem to specified Wall, using defined template and supplied extra_context
def add_extended_wallitem( wall, author, template_name='default.html',extra_context={}):


        # Default context variables for the wallitem
        context = Context({
            "wall": wall,
            "author": author,
        })
        
        context.update(extra_context)

        body = render_to_string('wallextend/%s' % template_name, context) 
        
        try:
            # Create the standard WallItem
            wi = WallItem(wall=wall,body=body, author=author)
            wi.save()
        except:
            pass
        else:
            #Success now create the extended item
            WallItemExtend(wallitem=wi,is_safe=True).save()
 
            
            
