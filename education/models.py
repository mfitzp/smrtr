from django.db import models
from django.contrib.auth.models import User
# Externals
from countries.models import Country
from datetime import date as _date


# Education models contain educational structure from institution to module exam
# INSERT INTO education_institution (name,address_1,address_2,city,state,country_id,postcode,telno,stage) SELECT SCHOOL_NAME as name,STREET as address_1, LOCALITY as address_2, TOWN as city, COUNTY as state, 'GB' as country_id, POSTCODE as postcode, CONCAT(0,TEL_STD,' ',TEL_NO) as telno,stage as stage FROM `school_list` WHERE 1
class Network(models.Model):
    def __unicode__(self):
        return self.name
    def memberships(self):
        return UserNetwork.objects.filter(network=self)

    name = models.CharField(max_length=200)
    description = models.TextField(blank = True)
    address_1 = models.CharField('Address Line 1', max_length=50, blank = True)
    address_2 = models.CharField('Address Line 1', max_length=50, blank = True)
    city = models.CharField('City', max_length = 50, blank = True)
    state = models.CharField('State/Province/Region', max_length = 50, blank = True)
    postcode = models.CharField('ZIP/Postal Code', max_length = 15, blank = True)
    country = models.ForeignKey(Country, null = True, blank = True)
    telno = models.CharField('Telephone', max_length=50, blank = True)
    TYPE_CHOICES = (
        (0, 'Other'),
        (1, 'Educational Institution'),
        (2, 'Examination Board'),
        (3, 'Organisation'),
        (4, 'Community'),
    )
    type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES, null = True, blank = True)
    STAGE_CHOICES = (
        (0, 'Other'),
        (1, 'Preschool'),
        (2, 'Primary'),
        (3, 'Middle'),
        (4, 'Secondary'),
        (5, 'Tertiary'),
        (6, 'Vocational'),
    )
    stage = models.PositiveSmallIntegerField(choices=STAGE_CHOICES, null = True, blank = True)
    members = models.ManyToManyField(User, through='UserNetwork', related_name='networks')


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
    def memberships(self):
        return UserCourse.objects.filter(course=self)
    def memberships_context(self,network):
        return UserCourse.objects.filter(network=network,course=self)

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
    def memberships(self):
        return UserModule.objects.filter(module=self)
    def memberships_context(self,network,course):
        return UserModule.objects.filter(network=network,course=course,module=self)

    network = models.ForeignKey(Network)
    name = models.CharField(max_length=50)
    description = models.TextField(blank = True)
    start_date = models.DateField('start date offset')
    credits = models.IntegerField(default=10)
    members = models.ManyToManyField(User, through='UserModule', related_name='modules')

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


class UserNetwork(models.Model):
    def __unicode__(self):
        return self.network.name
    user = models.ForeignKey(User)
    network = models.ForeignKey(Network)
    start_date = models.DateField(editable = False, auto_now_add = True) # Join date for the network

class UserCourse(models.Model):
    def __unicode__(self):
        return self.course.name

    usernetwork = models.ForeignKey(UserNetwork)

    user = models.ForeignKey(User)

    network = models.ForeignKey(Network)
    course = models.ForeignKey(Course)

    start_date = models.DateField(null = True)
    end_date = models.DateField(null = True)
    sq = models.FloatField(editable = False, null = True)

class UserModule(models.Model):
    def __unicode__(self):
        return self.module.name
    def week_of_study(self):
        return ( ( _date.today() - self.start_date  ).days / 7 ) + 1

    usercourse = models.ForeignKey(UserCourse) # For easy group listings

    user = models.ForeignKey(User)

    network = models.ForeignKey(Network)
    course = models.ForeignKey(Course)
    module = models.ForeignKey(Module)

    start_date = models.DateField(null = True) 
    end_date = models.DateField(null = True) 
    sq = models.FloatField(editable = False, null = True)
    focus = models.IntegerField( default = 0,editable = False)


class UserQualification(models.Model):
    def __unicode__(self):
        return self.qualification.name
    user = models.ForeignKey(User)
    qualification = models.ForeignKey(Qualification, related_name='memberships')
    date = models.DateField()
    result = models.FloatField() # Store as grade value and provide alternative conversion patterns (70>A, etc.)
    # course = models.ForeignKey(UserCourse) # Qualifications always assigned to specific courses (access via qualification>course)

class UserExam(models.Model):
    def __unicode__(self):
        return self.exam.name
    user = models.ForeignKey(User)
    exam = models.ForeignKey(Exam, related_name='memberships')
    # course acess via exam.course
    result = models.IntegerField(blank = True, null = True)
