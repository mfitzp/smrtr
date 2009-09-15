from django.db import models
from django.contrib.auth.models import User
# Externals
from countries.models import Country
from forum.models import Forum

# Education models contain educational structure from institution to module exam
class Institution(models.Model):
    def __unicode__(self):
        return self.name
    name = models.CharField(max_length=50)
    city = models.CharField('City', max_length = 100, blank = True)
    country = models.ForeignKey(Country)
    STAGE_CHOICES = (
        (0, 'Preschool'),
        (1, 'Primary'),
        (2, 'Secondary'),
        (3, 'Tertiary'),
        (4, 'Vocational'),
        (5, 'Other'),
    )
    stage = models.PositiveSmallIntegerField(choices=STAGE_CHOICES)
    #members = models.ManyToManyField(User, through='study.UserInstitution')

# Qualification types available, level is arbitrary comparison
# Use standardised tables to build this e.g.
# http://en.wikipedia.org/wiki/Scottish_Credit_and_Qualifications_Framework
# http://en.wikipedia.org/wiki/UCAS_Tariff
# A seperate sub-table giving relationships at grade level may be neccessary
class Qualification(models.Model):
    def __unicode__(self):
        return self.name
    name = models.CharField(max_length=50)
    level = models.IntegerField(blank = True)
    country = models.ForeignKey(Country, blank = True, null = True)
    #members = models.ManyToManyField(User, through='study.UserQualification')

class Course(models.Model):
    def __unicode__(self):
        return self.name
    institution = models.ForeignKey(Institution)
    name = models.CharField(max_length=50)
    start_date = models.DateField('start date')    
    qualification = models.ForeignKey(Qualification) # Standardised qualification level
    #members = models.ManyToManyField(User, through='study.UserCourse')

class Module(models.Model):
    def __unicode__(self):
        return self.name
    course = models.ForeignKey(Course)
    name = models.CharField(max_length=50)
    start_date = models.DateField('start date offset')
    credits = models.IntegerField(default=10)
    forum = models.OneToOneField(Forum)

    #members = models.ManyToManyField(User, through='study.UserModule')

class Exam(models.Model):
    def __unicode__(self):
        return parent.name
    module = models.ForeignKey(Module)
    date = models.DateTimeField('exam date')
    #members = models.ManyToManyField(User, through='study.UserExam')




