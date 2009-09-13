from django.db import models
from django.contrib.auth.models import User
# Externals
from spenglr.countries.models import Country
from spenglr.education.models import *
from spenglr.questions.models import *


# Study models store information about user's experience with education
# Models are ManytoMany through Models (ie they are used as the basis for linking
# other models together, while appending additional information
class UserInstitution(models.Model):
    def __unicode__(self):
        return self.institution.name
    user = models.ForeignKey(User)
    institution = models.ForeignKey(Institution)
    start_date = models.DateField(editable = False, null = True) # Auto calculate from first course start date
    end_date = models.DateField(editable = False, null = True) # Auto calculate from last course end date
    year_of_study = models.IntegerField(editable = False, null = True)

class UserCourse(models.Model):
    def __unicode__(self):
        return self.course.name
    user = models.ForeignKey(User)
    course = models.ForeignKey(Course)
    institution = models.ForeignKey(UserInstitution) # User's institution: As courses can be both offered and owned by institutions this may not match
    start_date = models.DateField()
    end_date = models.DateField()
    year_of_study = models.IntegerField( default = 1)
    sq = models.FloatField(editable = False, null = True)

class UserQualification(models.Model):
    def __unicode__(self):
        return self.qualification.name
    user = models.ForeignKey(User)
    qualification = models.ForeignKey(Qualification)
    date = models.DateField()
    result = models.FloatField() # Store as grade value and provide alternative conversion patterns (70>A, etc.)
    # course = models.ForeignKey(UserCourse) # Qualifications always assigned to specific courses (access via qualification>course)

class UserModule(models.Model):
    def __unicode__(self):
        return self.module.name
    user = models.ForeignKey(User)
    module = models.ForeignKey(Module)
    course = models.ForeignKey(UserCourse) # User's course: May differ from 'normal' location in MOMDs
    sq = models.FloatField(editable = False, null = True)
    focus = models.IntegerField( default = 0,editable = False)

class UserExam(models.Model):
    def __unicode__(self):
        return self.exam.name
    user = models.ForeignKey(User)
    exam = models.ForeignKey(Exam)
    result = models.IntegerField(blank = True, null = True)
    # course = models.ForeignKey(UserCourse) # Exams always assigned to specific courses (access via exam>course)


# Following models store user relationships with questions and resources
# Question Queue stores questions that have been presented, and is added to to make sure user always has n available
# this prevents the user skipping a question. Cross-site locking may also be implemented on this (if we can be bothered)

# User's attempts at questions
# class UserQuestionAttempt


# User's queued questions for locking/skip preventing
# class UserQuestionQueue

# User's suggested resources (taken from incorrectly answered questions)
# class UserResource


