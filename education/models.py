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
    #members = models.ManyToManyField(User, through='UserQualification')

class Course(models.Model):
    def __unicode__(self):
        return self.name
    institution = models.ForeignKey(Institution)
    name = models.CharField(max_length=50)
    start_date = models.DateField('start date')    
    qualification = models.ForeignKey(Qualification) # Standardised qualification level
    #members = models.ManyToManyField(User, through='UserCourse')

class Module(models.Model):
    def __unicode__(self):
        return self.name
    course = models.ForeignKey(Course)
    name = models.CharField(max_length=50)
    start_date = models.DateField('start date offset')
    credits = models.IntegerField(default=10)
    forum = models.OneToOneField(Forum)
    #members = models.ManyToManyField(User, through='UserModule')

class Exam(models.Model):
    def __unicode__(self):
        return parent.name
    module = models.ForeignKey(Module)
    date = models.DateTimeField('exam date')
    #members = models.ManyToManyField(User, through='UserExam')



# Study models store information about user's experience with education
# Models are ManytoMany through Models (ie they are used as the basis for linking
# other models together, while appending additional information
class UserInstitution(models.Model):
    def __unicode__(self):
        return self.institution.name
    user = models.ForeignKey(User)
    institution = models.ForeignKey(Institution, related_name = 'members')
    start_date = models.DateField(editable = False, null = True) # Auto calculate from first course start date
    end_date = models.DateField(editable = False, null = True) # Auto calculate from last course end date
    year_of_study = models.IntegerField(editable = False, null = True)

class UserCourse(models.Model):
    def __unicode__(self):
        return self.course.name
    user = models.ForeignKey(User)
    course = models.ForeignKey(Course, related_name = 'members')
    institution = models.ForeignKey(UserInstitution) # User's institution: As courses can be both offered and owned by institutions this may not match
    start_date = models.DateField()
    end_date = models.DateField()
    year_of_study = models.IntegerField( default = 1)
    sq = models.FloatField(editable = False, null = True)

class UserQualification(models.Model):
    def __unicode__(self):
        return self.qualification.name
    user = models.ForeignKey(User)
    qualification = models.ForeignKey(Qualification, related_name = 'members')
    date = models.DateField()
    result = models.FloatField() # Store as grade value and provide alternative conversion patterns (70>A, etc.)
    # course = models.ForeignKey(UserCourse) # Qualifications always assigned to specific courses (access via qualification>course)

class UserModule(models.Model):
    def __unicode__(self):
        return self.module.name
    user = models.ForeignKey(User)
    module = models.ForeignKey(Module, related_name = 'members')
    user_course = models.ForeignKey(UserCourse) # User's course: May differ from 'normal' location in MOMDs
    sq = models.FloatField(editable = False, null = True)
    focus = models.IntegerField( default = 0,editable = False)

class UserExam(models.Model):
    def __unicode__(self):
        return self.exam.name
    user = models.ForeignKey(User)
    exam = models.ForeignKey(Exam, related_name = 'members')
    result = models.IntegerField(blank = True, null = True)
    # course = models.ForeignKey(UserCourse) # Exams always assigned to specific courses (access via exam>course)
