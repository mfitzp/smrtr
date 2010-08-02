from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg, Max, Min, Count
from django.core.urlresolvers import reverse
import datetime
# Smrtr
from settings import QUESTION_TTC_MINIMUM
from resources.models import Resource
from education.models import Concept
from sq.utils import * 
# Externals
from tagging.fields import TagField
from tagging.models import Tag

"""
Update tags on question models from tagging_taggeditem table
UPDATE questions_question AS q, (SELECT xti.object_id as id, GROUP_CONCAT(name ) AS tags FROM `tagging_tag` AS xt INNER JOIN `tagging_taggeditem` AS xti ON xt.id=xti.tag_id GROUP BY xti.object_id) AS qt SET q.tags = qt.tags WHERE q.id = qt.id
"""

class Question(models.Model):
    def __unicode__(self):
        return self.content
        
    def get_absolute_url(self):
        return reverse('question-detail', kwargs={ 'question_id':str(self.id) } )        

    def answers_shuffled(self):
        return self.answer_set.order_by('?')

    def set_tags(self, tags):
        Tag.objects.update_tags(self, tags)
    def get_tags(self):
        return Tag.objects.get_for_object(self)     

    def update_sq(self):
        # Get all user's attempts at this question
        # Final Max('usq') is just to rename value, not possible to rename on values bit, which sucks
        data = self.userquestionattempt_set.values('user_sq').annotate(n=Count('id'),y=Avg('percent_correct'),x=Max('user_sq'))
        self.sq = sq_calculate(data, 'asc') # Ascending data set
        self.save()
        
    def update_ttc(self):
        ttc = self.userquestionattempt_set.aggregate(Avg('time_to_complete'))
        if ttc:
            self.time_to_complete = min( ttc['time_to_complete__avg'], QUESTION_TTC_MINIMUM) # Minimum 5 seconds per question
            self.save()
            
    content = models.TextField()
    concepts = models.ManyToManyField(Concept, blank=True) #, related_name='questions'
    
    created = models.DateTimeField(auto_now_add = True)
    last_updated = models.DateTimeField(auto_now = True)
    tags = TagField()
    author = models.ForeignKey(User)
    sq = models.IntegerField(blank = True, null = True, editable = False) 
    
    # Auto-populated from averages of all user attempts (total seconds taken)
    time_to_complete = models.IntegerField(default = 15 )#, editable = False )

class Answer(models.Model):
    question = models.ForeignKey(Question)
    content = models.CharField(max_length=200)
    is_correct = models.BooleanField()


# Following models store user relationships with questions and resources
# User's attempts at questions
class UserQuestionAttempt(models.Model):
    question = models.ForeignKey('Question')
    user = models.ForeignKey(User)
    percent_correct = models.IntegerField() # Percent correct (will be 0 or 100 until implement multi-part answers)
    user_sq = models.IntegerField() # User's SQ at time of answering
    created = models.DateTimeField(auto_now_add = True)

    # Time taken by the user to answer the question (seconds), calculated from no_of_questions/total_time
    time_to_complete = models.IntegerField(editable = False )










