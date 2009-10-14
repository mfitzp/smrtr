from django.db import models
from django.contrib.auth.models import User
# Externals
from countries.models import Country
from forum.models import Forum
from datetime import date as _date
# Spenglr
from spenglr.network.models import Network

# Qualification types available, level is arbitrary comparison
# Use standardised tables to build this e.g.
# http://en.wikipedia.org/wiki/Scottish_Credit_and_Qualifications_Framework
# http://en.wikipedia.org/wiki/UCAS_Tariff
# A seperate sub-table giving relationships at grade level may be neccessary
class Qualification(models.Model):
    def __unicode__(self):
        return self.name
    name = models.CharField(max_length=50)
    description = models.TextField(blank = True)
    level = models.IntegerField(blank = True)
    country = models.ForeignKey(Country, blank = True, null = True)
    members = models.ManyToManyField(User, through='UserQualification', related_name='qualifications')

class Course(models.Model):
    def __unicode__(self):
        return self.name
    network = models.ForeignKey(Network)
    name = models.CharField(max_length=50)
    description = models.TextField(blank = True)
    start_date = models.DateField('start date')    
    qualification = models.ForeignKey(Qualification, blank = True, null = True) # Standardised qualification level
    modules = models.ManyToManyField('Module', related_name='courses')
    members = models.ManyToManyField(User, through='UserCourse', related_name='courses')
    offered_by = models.ManyToManyField(Network, related_name='courses_offered')

class Module(models.Model):
    def __unicode__(self):
        return self.name
    network = models.ForeignKey(Network)
    name = models.CharField(max_length=50)
    description = models.TextField(blank = True)
    start_date = models.DateField('start date offset')
    credits = models.IntegerField(default=10)
    forum = models.OneToOneField(Forum)
    members = models.ManyToManyField(User, through='UserModule', related_name='modules')
    momd = models.BooleanField(default = False)

class Exam(models.Model):
    def __unicode__(self):
        return parent.name
    module = models.ForeignKey(Module)
    name = models.CharField(max_length=50)
    description = models.TextField(blank = True)
    date = models.DateTimeField('exam date')
    members = models.ManyToManyField(User, through='UserExam', related_name='exams')




# Study models store information about user's experience with education
# Models are ManytoMany through Models (ie they are used as the basis for linking
# other models together, while appending additional information

class UserCourse(models.Model):
    def __unicode__(self):
        return self.course.name
    def year_of_study(self):
        return ( _date.today().year - self.start_date.year ) + 1

    user = models.ForeignKey(User)
    course = models.ForeignKey(Course, related_name='memberships')
    start_date = models.DateField(null = True)
    end_date = models.DateField(null = True)
    sq = models.FloatField(editable = False, null = True)

class UserQualification(models.Model):
    def __unicode__(self):
        return self.qualification.name
    user = models.ForeignKey(User)
    qualification = models.ForeignKey(Qualification, related_name='memberships')
    date = models.DateField()
    result = models.FloatField() # Store as grade value and provide alternative conversion patterns (70>A, etc.)
    # course = models.ForeignKey(UserCourse) # Qualifications always assigned to specific courses (access via qualification>course)

class UserModule(models.Model):
    def __unicode__(self):
        return self.module.name
    def week_of_study(self):
        return ( ( _date.today() - self.start_date  ).days / 7 ) + 1

    user = models.ForeignKey(User)
    module = models.ForeignKey(Module, related_name='memberships')
    usercourse = models.ForeignKey(UserCourse) # For easy group listings
    start_date = models.DateField(null = True) 
    end_date = models.DateField(null = True) 
    sq = models.FloatField(editable = False, null = True)
    focus = models.IntegerField( default = 0,editable = False)

class UserExam(models.Model):
    def __unicode__(self):
        return self.exam.name
    user = models.ForeignKey(User)
    exam = models.ForeignKey(Exam, related_name='memberships')
    # course acess via exam.course
    result = models.IntegerField(blank = True, null = True)
