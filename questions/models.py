from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg, Max, Min, Count
# Spenglr
from resources.models import Resource
from education.models import Module
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
    def answers_shuffled(self):
        return self.answer_set.order_by('?')

    def set_tags(self, tags):
        Tag.objects.update_tags(self, tags)
    def get_tags(self):
        return Tag.objects.get_for_object(self)     

    def update_sq(self):
        # Get all user's attempts at this question
        # Final Max('usq') is just to rename value, not possible to rename on values bit, which sucks
        data = self.userquestionattempt_set.values('usq').annotate(n=Count('id'),y=Avg('percent_correct'),x=Max('usq'))
        self.sq = sq_calculate(data, 'asc') # Ascending data set
        self.save()

    content = models.TextField()
    resource = models.ManyToManyField(Resource, blank=True) # Multiple resource records for this Question, resources assigned to >1 question
    modules = models.ManyToManyField(Module, blank=True)
    created = models.DateTimeField(auto_now_add = True)
    last_updated = models.DateTimeField(auto_now = True)
    tags = TagField()
    author = models.ForeignKey(User)
    sq = models.IntegerField(blank = True, null = True, editable = False) 

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
    usq = models.IntegerField() # User's SQ at time of answering
    created = models.DateTimeField(auto_now_add = True)

# Question Queue stores questions that have been presented, and is added to to make sure user always has n available
# this prevents the user skipping a question. Cross-site locking may also be implemented on this (if we can be bothered)
# User's queued questions for locking/skip preventing
# class UserQuestionQueue











