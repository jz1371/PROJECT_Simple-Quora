'''
File: app.controllers.posts.py
----------------------------------------------------
This class is a verbose controller class playground,
whose model is in app.model.post.py

@author: Jingxin Zhu 
Created on 2015/02/11
----------------------------------------------------
'''

from ferris import Controller, scaffold
from wtforms.ext.appengine.ndb import model_form 

class Posts(Controller):
    """
    Except explicitly import and specify, the model is communicated with Post,
    which is referred to in this controller as 'self.meta.Model'
    """
    
    # configuration for meta
    class Meta:
        prefixes = ('admin',)
        components = (scaffold.Scaffolding,)
        
    # configuration for scaffolding
    class Scaffold:
        display_properties = ("title", "content")


    # ------ admin user rights ------

    admin_list = scaffold.list        #lists all posts
    admin_view = scaffold.view        #view a post
    admin_add = scaffold.add          #add a new post
    admin_edit = scaffold.edit        #edit a post
    admin_delete = scaffold.delete    #delete a post


    # ----- non-admin user rights -----
    
    def add(self):
#       a custom form exclude "views" property
        PostForm = model_form(self.meta.Model, exclude=('views',))
#       override model form of BasicModel
        self.scaffold.ModelForm = PostForm
        return scaffold.add(self)

    def list(self):
        """
        Non-admin user can only edit posts created by himself/herself.
        """
        if 'mine' in self.request.params:

#           populate table with query result from model
            self.context['posts'] = self.meta.Model.all_posts_by_user()

        else:
            self.context['posts'] = self.meta.Model.all_posts()
            
    def edit(self, key):
        """
        Non-admin user can only edit posts created by himself/herself.
        """
#       get the instance from Model
        post = self.util.decode_key(key).get()

        if post.created_by != self.user:
            return 403

        return scaffold.edit(self, key)


#   delegate scaffold.views
    def view(self, key):
    
#       modify model fields
        post = self.util.decode_key(key).get()
        post.views += 1
        post.put()
        return scaffold.view(self, key)
