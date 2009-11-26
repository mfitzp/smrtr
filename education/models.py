from django.db import models
from django.contrib.auth.models import User
# Externals
from spenglr.network.models import Network,UserNetwork
from spenglr.sq.utils import * 
# External
from countries.models import Country
from datetime import date as _date


# Definitions of courses available and associated modules
# Courses and Modules are both tied to 'home' networks (providers) however they
# are then assembled into combinations - allowing modules to be used on
# multiple courses for example. This hierarchy is managed through Instances
# NOTE: This is not navigable upstream i.e. moduleinstance > course (not courseinstance)
# navigation upstream in this manner is handled through UserCourse/UserModule trees

class Course(models.Model):
    def __unicode__(self):
        return self.name
    def update_sq(self):
        # update
        self.sq = self.modules.aggregate(Avg('sq'))['sq__avg']
        self.save()

    network = models.ForeignKey(Network)
    name = models.CharField(max_length=75)
    description = models.TextField(blank = True)
    start_date = models.DateField('start date')    
    qualification = models.ForeignKey('Qualification', blank = True, null = True) # Standardised qualification level
    modules = models.ManyToManyField('Module', related_name='courses', through='ModuleInstance')
    provided_by = models.ManyToManyField(Network, related_name='courses_provided', through='CourseInstance')
    url = models.URLField(verify_exists = True, blank = True) # External website for additional course information (e.g. provider site)
    sq = models.IntegerField(editable = False, null = True)

# NOTE: This linker model may be unnnecessary
# Course as offered by a specific network
class CourseInstance(models.Model):
    def __unicode__(self):
        return self.course.name
    def memberships(self):
        return self.usercourse_set.all()

    members = models.ManyToManyField(User, through='UserCourse', related_name='courses')
    network = models.ForeignKey(Network)
    course = models.ForeignKey(Course)

class Module(models.Model):
    def __unicode__(self):
        return self.name
    def update_sq(self):
        # update
        self.sq = self.question_set.aggregate(Avg('sq'))['sq__avg']
        self.save()

    network = models.ForeignKey(Network)
    name = models.CharField(max_length=75)
    code = models.CharField(max_length=10,blank = True)
    description = models.TextField(blank = True)
    credits = models.IntegerField(default=10)
    sq = models.IntegerField(editable = False, null = True)

# Module as used by a specific course
class ModuleInstance(models.Model):
    def __unicode__(self):
        return self.module.name
    def memberships(self):
        return UserModule.objects.filter(modulei=self)
    start_week = models.IntegerField(default = 1)
    members = models.ManyToManyField(User, through='UserModule', related_name='modules')
    course = models.ForeignKey(Course)
    module = models.ForeignKey(Module)

# NOTE: The CourseInstance/ModuleInstance models do not allow a through-route from a module to it's hosted network
# as it directs through the generic model, not the instance (moduleinstance->course not moduleinstance->courseinstance)
# because this would require massive duplication of trees. If this traversal is required, it is possible through the
# user tree instead (which is incidentally the only time it would be needed, woop woop)





# Study models store information about user's experience with education
# Models are ManytoMany through Models (ie they are used as the basis for linking
# other models together, while appending additional information

class UserCourse(models.Model):
    def __unicode__(self):
        return self.coursei.course.name
    # Shortcuts through tree
    def network(self):
        return self.coursei.network
    def course(self):
        return self.coursei.course
    # Additional information
    def year_of_study(self):
        return ( ( _date.today() - self.start_date  ).days / 365 )+1
    def is_active(self):
        return ( self.end_date == None ) or ( self.end_date > _date.today() )
    def update_sq(self):
        self.sq = self.usermodule_set.aggregate(Avg('sq'))['sq__avg']
        self.save()

    user = models.ForeignKey(User)
    usernetwork = models.ForeignKey(UserNetwork) # Up tree

    # Course instance
    coursei = models.ForeignKey(CourseInstance)

    start_date = models.DateField(null = True)
    end_date = models.DateField(null = True)

    sq = models.IntegerField(editable = False, null = True)

class UserModule(models.Model):
    def __unicode__(self):
        return self.modulei.module.name
    # Shortcuts through tree
    def network(self):
        return self.usercourse.coursei.network
    def course(self):
        return self.modulei.course
    def module(self):
        return self.modulei.module
    # Additional information
    def week_of_study(self):
        return ( ( _date.today() - self.start_date  ).days / 7 ) + 1
    def is_active(self):
        return ( self.end_date == None ) or ( self.end_date > _date.today() )
    # Update user's SQ value on this module
    def update_sq(self):
        # Get user's attempts on this module's questions 
        # group by x
        # x = qSQ (question's SQ)
        # y = percent_correct
        # Final Max('usq') is just to rename value, not possible to rename on values bit, which sucks
        data = self.modulei.module.question_set.all().filter(userquestionattempt__user=self.user).values('sq').annotate(n=Count('id'),y=Avg('userquestionattempt__percent_correct'),x=Max('sq'))
        self.sq = sq_calculate(data, 'desc') # Descending data set  
        self.save()

    user = models.ForeignKey(User)
    usercourse = models.ForeignKey(UserCourse) # Up tree

    # Module instance
    modulei = models.ForeignKey(ModuleInstance)

    start_date = models.DateField(null = True) 
    end_date = models.DateField(null = True) 

    sq = models.IntegerField(editable = False, null = True)
    focus = models.IntegerField( default = 0,editable = False)




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


class Exam(models.Model):
    def __unicode__(self):
        return parent.name
    module = models.ForeignKey('Module')
    name = models.CharField(max_length=50)
    description = models.TextField(blank = True)
    date = models.DateTimeField('exam date')
    members = models.ManyToManyField(User, through='UserExam', related_name='exams')





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


