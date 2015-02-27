'''
File: app.controllers.questions.py
----------------------------------------------

@author: Jingxin Zhu
Created on 2015/02/10
----------------------------------------------
'''

from ferris import Controller, scaffold
from ferris.components.search import Search
from ferris.components.pagination import Pagination
from wtforms.ext.appengine.ndb import model_form 

class Questions(Controller):
    '''
    TODO: classdocs
    '''
    class Meta:
        """ global configuration """
        prefixes = ('admin',)
        components = (scaffold.Scaffolding, Pagination, Search)

        # allow utilities of 'search', 'pagination', and take advantage of 'scaffolding'
        
    class Scaffold:
        """ global configuration """
        # properties of model to show to user when controlling model
        # [!] if only property to show, add comma at the end. e.g.: =("title",)
        display_properties = ("title", "content", "created_by", "votes", "views")


    # ==== Administration user's controller ==== #
    admin_list = scaffold.list        #lists all 
    admin_view = scaffold.view        #view one instance 
    admin_add = scaffold.add          #add a new instance 
    admin_edit = scaffold.edit        #edit an instance 
    admin_delete = scaffold.delete    #delete an instance 
   
    
    # ==== Non-administration user's controller ==== #

    # delegate scaffold.add 
    def add(self):
        QuestionForm = model_form(self.meta.Model, exclude=("votes", "views", ))
        self.scaffold.ModelForm = QuestionForm 
        return scaffold.add(self)

    def list(self):
        if 'query' in self.request.params:
            # list for user's searching request
            self.context['questions'] = self.components.search()
        elif 'mine' in self.request.params:
            # list for user's created items
            self.context['questions'] = self.meta.Model.all_questions_by_user()
        else:
            # list all model items 
            self.context['questions'] = self.meta.Model.all_questions()
    
    def edit(self, key):
        """
        Non-admin user can only edit questions created by himself/herself.
        """
        question = self.util.decode_key(key).get()

        if question.created_by != self.user:
            return 403

        return scaffold.edit(self, key) 
    
    def delete(self, key):
        question = self.util.decode_key(key).get()

        if question.created_by != self.user:
            return 403

        return scaffold.delete(self, key)

    def view(self, key):
        question = self.util.decode_key(key).get()
        question.increase_views()
        return scaffold.view(self, key)