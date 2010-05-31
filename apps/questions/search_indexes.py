import datetime
from haystack.indexes import *
from haystack import site
from questions.models import Question


class QuestionIndex(SearchIndex):
    text = CharField(document=True, use_template=True) #name, description 
   
    def get_queryset(self):
        """Used when the entire index for model is updated."""
        return Question.objects.all()


site.register(Question, QuestionIndex)
