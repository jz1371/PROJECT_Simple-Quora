'''
File: app.controllers.questions.py
----------------------------------------------


@author: Jingxin Zhu
Created on 2015/02/10
----------------------------------------------
'''

from ferris import Controller, scaffold
from wtforms.ext.appengine.ndb import model_form 

class Questions(Controller):
    '''
    TODO: classdocs
    '''
    class Meta:
        prefixes = ('admin',)
        components = (scaffold.Scaffolding,)
        
#     class Scaffold:
#         display_properties = ("vote", )

    admin_list = scaffold.list        #lists all 
    admin_view = scaffold.view        #view one instance 
    admin_add = scaffold.add          #add a new instance 
    admin_edit = scaffold.edit        #edit an instance 
    admin_delete = scaffold.delete    #delete an instance 
   
    
    # delegate scaffold.add 
    def add(self):
        QuestionForm = model_form(self.meta.Model, exclude=("votes", "views", ))
        self.scaffold.ModelForm = QuestionForm 
        return scaffold.add(self)

    def list(self):
        if 'mine' in self.request.params:
            self.context['questions'] = self.meta.Model.all_questions_by_user()
        else:
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