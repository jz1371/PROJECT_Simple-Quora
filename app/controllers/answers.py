'''
File: app/controllers/answers.py
-------------------------------------------
@author: Jingxin Zhu
@date  : 2015.02.28
-------------------------------------------
'''

from ferris import Controller, scaffold
from ferris import model_form
from ferris.components.search import Search
from ferris.components.pagination import Pagination
from ferris.core.controller import route    # for @route
from app.models.answer import Answer
from google.appengine.ext import ndb
import time

class Answers(Controller):
    '''
    TODO: class doc
    '''
    class Meta:
        """ global configuration """
        prefixes = ('admin',)
        # allow utilities of 'search', 'pagination', and take advantage of 'scaffolding'
        components = (scaffold.Scaffolding, Pagination, Search)
       
    class Scaffold:
        """ global configuration """
        # properties of model to show to user when controlling model
        # [!] if only property to show, add comma at the end. e.g.: =("title",)
        display_properties = ("content", "created_by", "votes")
        ModelForm = model_form(Answer, only=("content",))

    # ==== Administration user's controller ==== #
    admin_list = scaffold.list        #lists all 
    admin_view = scaffold.view        #view one instance 
    admin_add = scaffold.add          #add a new instance 
    admin_edit = scaffold.edit        #edit an instance 
    admin_delete = scaffold.delete    #delete an instance 
 

    # ==== Non-administration user's controller ==== #

    @route
    def answer(self, questionKey):
        def ancestored_create_factory(controller):
            return controller.meta.Model(parent=ndb.Key("Question", questionKey))
        self.scaffold.create_factory = ancestored_create_factory
        def set_redirect(controller, container, item):
            controller.scaffold.redirect = controller.uri(controller='questions', action='view', key=questionKey)
        self.events.scaffold_after_save += set_redirect
        returnKey = scaffold.add(self)
        time.sleep(0.1)     # in order to let item can be queried immediately after adding
        return returnKey

    def add(self):
        AnswerForm = model_form(self.meta.Model, exclude=("votes",))
        self.scaffold.ModelForm = AnswerForm 
        returnKey = scaffold.add(self)
        time.sleep(0.1)     # in order to let item can be queried immediately after adding
        return returnKey

    def list(self):
        # properties to show when listing items
        self.scaffold.display_properties = ("content","created_by","views")

        if 'query' in self.request.params:
            # list for user's searching request
            self.context['answers'] = self.components.search()
        elif 'mine' in self.request.params:
            # list for user's created items
            self.context['answers'] = self.meta.Model.all_answers_by_user()
        else:
            # list all model items 
            self.context['answers'] = self.meta.Model.all_answers()
    
    def edit(self, key):
        """
        Non-admin user can only edit questions created by himself/herself.
        """
        # properties to show when listing items
        self.scaffold.display_properties = ("content",)

        answer = self.util.decode_key(key).get()

        if answer.created_by != self.user:
            return 403

        return scaffold.edit(self, key) 
    
    def delete(self, key):
        answer = self.util.decode_key(key).get()

        if answer.created_by != self.user:
            return 403

        return scaffold.delete(self, key)

    def view(self, key):
        self.scaffold.display_properties = ("content",)
        return scaffold.view(self, key)
