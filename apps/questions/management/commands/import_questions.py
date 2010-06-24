from optparse import make_option
import sys
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    args = "<filename>"
    help = "Import questions, answers and tags from CSV"
    
    def handle(self, *args, **options):
        """Imports questions from CSV."""
        # Cause the default site to load.
        import csv, os
                
        for filename in args:
            
            print "Importing from " + filename
            
            csvReader = csv.DictReader(open(filename), dialect='excel')
            for row in csvReader:
                data = dict()
                # Import from own standard CSV listing
                if 'question' in row:
                    pass
                # Import from mturk format
                else:
                    if 'HITId' in row:
                        # Translate to standard format (as above)
                        data['question'] = row['Answer.question']
                        data['correct'] = row['Answer.correct']
                        data['incorrect'] = [
                            row['Answer.incorrect1'],
                            row['Answer.incorrect2'],
                            row['Answer.incorrect3'],
                            row['Answer.incorrect4'],
                            ]
                        data['tags'] = row['Answer.tags']

                        self.doimport(data)                        

            print "Done."
            
    # Handle actual import from standard format file            
    def doimport(self,data):

        from django.contrib.auth.models import User
        from questions.models import Question, Answer
        from tagging.models import Tag

        question = Question()
        question.content = data['question']
        question.tags = data['tags']
        question.author = User.objects.get(pk=0) #FIXME: System smrtr user: use constant?
        question.save() # Save to allow m2m

        # Create correct answer
        c = Answer()
        c.content = data['correct']
        c.is_correct = True
        c.question = question
        c.save()
        
        # Save incorrect answers
        data['incorrect'] = filter(lambda x: len(x)>0, data['incorrect']) # Remove empty items
        for incorrect in data['incorrect']:
            ic = Answer()
            ic.content = incorrect
            ic.is_correct = False
            ic.question = question
            ic.save()
            
