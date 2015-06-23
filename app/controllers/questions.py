'''
File: app/controllers/questions.py
----------------------------------------------
@author: Jingxin Zhu
@date  : 2015/02/10
----------------------------------------------
'''

from ferris import Controller, scaffold
from ferris.core.forms import model_form
from ferris.components.search import Search
from ferris.components.pagination import Pagination
from ferris.components import oauth
from app.models.answer import Answer
from app.models.question import Question
from google.appengine.api import users
from apiclient.discovery import build

import time

class Questions(Controller):
    '''
    TODO: classdocs
    '''
    class Meta:
        """ global configuration """
        prefixes = ('admin',)
        # allow utilities of 'search', 'pagination', and take advantage of 'scaffolding'
        components = (scaffold.Scaffolding, Pagination, Search, oauth.OAuth)
        oauth_scopes = ['https://www.googleapis.com/auth/userinfo.profile', ]
        pagination_limit = 10

        
    class Scaffold:
        """ global configuration """
        # properties of model to show to user when controlling model
        # [!] if only property to show, add comma at the end. e.g.: =("title",)
        display_properties = ("title", "content", "created_by", "votes", "views")
        ModelForm = model_form(Question, exclude=("votes", "views"))


    # ==== Administration user's controller ==== #
    admin_list = scaffold.list        #lists all 
    admin_view = scaffold.view        #view one instance 
    admin_add = scaffold.add          #add a new instance 
    admin_edit = scaffold.edit        #edit an instance 
    admin_delete = scaffold.delete    #delete an instance 
   
    
    # ==== Non-administration user's controller ==== #

    # delegate scaffold.add 
#     @oauth.require_credentials
    def add(self):
#         http = self.oauth.http()
#         service = build('oauth2', 'v2', http=http)
#         user_info = service.userinfo().get().execute()
        # more fields see here {@link https://developers.google.com/apis-explorer/#p/oauth2/v2/oauth2.userinfo.v2.me.get }
#         return "Hello, you are %s" % user_info['name']
        user = users.get_current_user()
        returnKey = scaffold.add(self)
        time.sleep(0.1)     # in order to let item can be queried immediately after adding
        print user 
        return returnKey

    def list(self):
        # properties to show when listing items
        self.scaffold.display_properties = ("title", "votes", "views")

        if 'query' in self.request.params:
            # list for user's searching request
            self.context['questions'] = self.components.search()
        elif 'mine' in self.request.params:
            # list for user's created items
            self.context['questions'] = self.meta.Model.all_questions_by_user()
        else:
            # list all model items 
            self.context['questions'] = self.meta.Model.all_questions()

        time.sleep(0.1)
        return
    

    def edit(self, key):
        """
        Non-admin user can only edit questions created by himself/herself.
        """
        question = self.util.decode_key(key).get()

        if question.created_by != self.user:
            return 403

        QuestionForm = model_form(self.meta.Model, exclude=("votes", "views", ))
        self.scaffold.ModelForm = QuestionForm 
        return scaffold.edit(self, key) 
    
    def delete(self, key):
        question = self.util.decode_key(key).get()

        if question.created_by != self.user:
            return 403

        return scaffold.delete(self, key)

    def view(self, key):
        self.scaffold.display_properties = ("title", "content", "tags")
#         self.context['answers'] = Answer.all_answers_by_question(key)
        self.context['answers'] = Answer.all_answers_by_question(key)
        self.context['display_properties'] = ("content",)
        question = self.util.decode_key(key).get()
        question.increase_views()
        return scaffold.view(self, key)
    
    ###### Helper Functions #######
    def getQuestion(self, key):
        return self.util.decode_key(key)