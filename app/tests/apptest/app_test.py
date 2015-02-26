'''
Created on Feb 26, 2015

@author: Steven
'''

from app.controllers.questions import Questions
from app.models.question import Question
from ferrisnose import FerrisAppTest

class CatsTest(FerrisAppTest):
    def test_herding(self):
        Question(title="Pickles").put()
        Question(title="Mr. Sparkles").put()

        r = self.testapp.get('/questions')

        assert "Pickles" in r
        assert "Mr. Sparkles" in r
