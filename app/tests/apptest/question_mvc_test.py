'''
File: app/tests/controllers_test/questions_test.py
----------------------------------------------------

@author: Jingxin Zhu 
Created on Feb 26, 2015
----------------------------------------------------
'''

from app.models.question import Question
from ferrisnose.utilities import FerrisAppTest

class QuestionsTest(FerrisAppTest):
        
    def testQueries(self):
        # log in user one
        self.loginUser('user1@example.com')

        # create two Questions
        Question1 = Question(title="Question 1")
        Question1.put()
        Question2 = Question(title="Question 2")
        Question2.put()

        # log in user two
        self.loginUser('user2@example.com')

        # create two more Questions
        Question3 = Question(title="Question 3")
        Question3.put()
        Question4 = Question(title="Question 4")
        Question4.put()

        # Get all Questions
        all_Questions = list(Question.all_questions())

        # Make sure there are 4 Questions in total
        assert len(all_Questions) == 4 

        # Make sure they're in the right order
        assert all_Questions == [Question4, Question3, Question2, Question1]

        # Make sure we only get two for user2, and that they're the right Questions
        user2_Questions = list(Question.all_questions_by_user())

        assert len(user2_Questions) == 2
        assert user2_Questions == [Question4, Question3]

        # Test all Questions shown up
        resp = self.testapp.get('/questions')
        assert 'Question 1' in resp.body
        assert 'Question 2' in resp.body
        assert 'Question 3' in resp.body
        assert 'Question 4' in resp.body
         
        # Test Questions_created_by_user
        resp = self.testapp.get('/questions?=mine')
#         assert 'Question 1' not in resp.body
#         assert 'Question 2' not in resp.body
#         assert 'Question 3' in resp.body
#         assert 'Question 4' in resp.body
         
        # Test 'edit' link exists
        assert 'Edit' in resp.body
         
    def testAdd(self):
        self.loginUser("user1@example.com")
        resp = self.testapp.get('/questions/add')
         
        # Test not filling requried will cause validation error
        form = resp.form
        error_resp = form.submit()
        assert 'This field is required' in error_resp.body
         
        # Test add successfully
        form['title'] = 'Test Question'
        good_resp = form.submit()
        assert good_resp.status_int == 302  # Success redirects us to list
         
        # Load new page and verify Question
        final_resp = good_resp.follow()
        assert 'Test Question' in final_resp
