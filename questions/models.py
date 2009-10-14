from django.db import models
from django.contrib.auth.models import User
from spenglr.education.models import Module
from spenglr.resources.models import Resource

class Question(models.Model):
    def __unicode__(self):
        return self.content
    def answers_shuffled(self):
        return self.answer_set.order_by('?')
    content = models.TextField()
    resource = models.ManyToManyField(Resource, blank=True) # Multiple resource records for this Question, resources assigned to >1 question
    modules = models.ManyToManyField(Module, blank=True)
    created = models.DateTimeField(auto_now_add = True)
    last_updated = models.DateTimeField(auto_now = True)

class Answer(models.Model):
    question = models.ForeignKey(Question)
    content = models.CharField(max_length=200)
    is_correct = models.BooleanField()

    
# Following models store user relationships with questions and resources
# Question Queue stores questions that have been presented, and is added to to make sure user always has n available
# this prevents the user skipping a question. Cross-site locking may also be implemented on this (if we can be bothered)

# User's attempts at questions
# class UserQuestionAttempt

# User's queued questions for locking/skip preventing
# class UserQuestionQueue











