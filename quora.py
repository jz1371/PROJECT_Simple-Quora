"""
File: quora.py
--------------------
"""
import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import forumDB as DB

import jinja2
import webapp2

import question
import time

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader( \
        os.path.join(os.path.dirname(__file__), 'templates')),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


def make_page(handler, template, substitutes = {}):

    template = JINJA_ENVIRONMENT.get_template(template)
    handler.response.write(template.render(substitutes))


class HomePage(webapp2.RequestHandler):
    def get(self):
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login use Google account'
        
        tag =  self.request.get('tag') 
        question_keys, tags = question.list_all(tag)

        template_values = {
            'version:': 'v1.0',
            'url': url,
            'url_linktext': url_linktext,
            'question_keys': question_keys,
            'tags': tags,
        }
        template = JINJA_ENVIRONMENT.get_template('home.html')
#         self.response.write(template.render(template_values))
        self.response.write(question_keys[0].urlsafe())
# [END home_page]

class CreateQuestionPage(webapp2.RedirectHandler):
    def get(self):
        if users.get_current_user():
            self.response.write(users.get_current_user().nickname() + " is writing question")
            template = JINJA_ENVIRONMENT.get_template('create_question.html')
            self.response.write(template.render())
        else:
            self.redirect(users.create_login_url(self.request.uri))

class CreateQuestion(webapp2.RedirectHandler):
    # process /question with a post form
    def post(self):
        user = users.get_current_user()
        content = self.request.get('question')
        qid = self.request.get("qid")
        tags = self.request.get('tags')

        q = question.create_question(qid,  user, content)
        question.add_tag(q.id(), tags)
        
        query_params =  {'qid': q.id()}
        time.sleep(0.1) 
        self.redirect('/view?' + urllib.urlencode(query_params))
        

class QuestionProfilePage(webapp2.RedirectHandler):

    def get(self):
        qid = urllib.unquote(self.request.get('qid'))
        profile = question.view(qid)
        user = users.get_current_user()
        is_author = (user and user == profile['question']['author'])
        template_values = {
            'is_author': is_author,
            'cur_user': user,
            'qid': qid,
            'q_content': profile['question']['content'],
            'q_vote': profile['question']['votes'],
            'q_tag': profile['tag'],
            'answers': profile['answer'],
        }
        template = JINJA_ENVIRONMENT.get_template('view_question.html')
        self.response.write(template.render(template_values))

class CreateAnswerPage(webapp2.RedirectHandler):
    def get(self):
        if users.get_current_user():
            self.response.write(users.get_current_user().nickname() + " is answering a question")
            template = JINJA_ENVIRONMENT.get_template('create_answer.html')
            template_values = {'qid': self.request.get('qid')}
            self.response.write(template.render(template_values))
        else:
            self.redirect(users.create_login_url(self.request.uri))

class CreateAnswer(webapp2.RedirectHandler):
    # process /question with a post form
    def post(self):

        qid = self.request.get('qid')
        
        user = users.get_current_user()
        
        if user:
            aid = self.request.get('aid')
            # if user is editing existing answer
            if aid:
                key = ndb.Key('Answer', long(aid))
                a = key.get()
                a.content_ = self.request.get('answer')
                a.put()
            else:
                answer = DB.Answer()
                answer.author_ = user
                answer.qid_ = qid
                answer.content_ = self.request.get('answer')
                answer.put()
            query_params = {'qid': qid }
                # because google use strong-consistence, newly posted data will not be shown immediately

            time.sleep(0.1) 
            self.redirect('/view?' + urllib.urlencode(query_params))
        #         query_params = {'qid': qid, 'oper': 'answer'}
        else:
            self.redirect(users.create_login_url(self.request.uri))
            
#         self.redirect('/prompt?' + urllib.urlencode(query_params))
        

class Vote(webapp2.RedirectHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            vote = self.request.get('v')
            qid = self.request.get('qid')
            aid = self.request.get('aid')
            
            if aid=='':
                question.create_vote(user, qid, vote)
            else:
                question.create_vote(user, qid, vote, aid)
            query_params = {'qid': qid, 'oper': 'vote'}
            self.redirect('/prompt?' + urllib.urlencode(query_params))
        else:
            self.redirect(users.create_login_url(self.request.uri))

class Prompt(webapp2.RedirectHandler):
    def get(self):
        qid = self.request.get('qid')
        oper = self.request.get('oper')
        template_values = {'operation': oper, 'qid' : qid}
        template = JINJA_ENVIRONMENT.get_template('prompt_result.html')
        self.response.write(template.render(template_values))

class Test(webapp2.RedirectHandler):
    def get(self):
        template_values = {}
        template = JINJA_ENVIRONMENT.get_template('test.html')
        self.response.write(template.render(template_values))

class Tag(webapp2.RedirectHandler):
    def get(self):
        return 
        
        
# ==== Main =====
app = webapp2.WSGIApplication([
#    ('/', MainPage),
    ('/', HomePage),
    ('/ask', CreateQuestionPage),  # page that user can create a new question
    ('/create-question', CreateQuestion), 
    ('/answer', CreateAnswerPage),
    ('/create-answer', CreateAnswer),
    ('/view', QuestionProfilePage),
    ('/vote', Vote),
    ('/prompt', Prompt),
    ('/test', Test),
    ('tag', Tag),
], debug=True)