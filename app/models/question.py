'''
File: app/models/question.py
--------------------------------------------

@author: Jingxin Zhu 
@date  : 2015.02.10
--------------------------------------------
'''

from google.appengine.ext import ndb
from google.appengine.api import users
from ferris.core.ndb.model import BasicModel
from ferris.behaviors.searchable import Searchable

class Question(BasicModel):
    '''
    'Question' model that describes a question posted by user.

    '''
    
    class Meta:
        '''
        global configuration for model.
        '''
        # allow this model for user searching
        behaviors = (Searchable, )

    # === Model's properties ===#
    # 'created_by', 'modified_by', 'created', 'modified' are automatically 
    # added to model due to BasicModel
    title   = ndb.StringProperty(required=True)
    content = ndb.TextProperty()
    image   = ndb.BlobProperty()
    votes   = ndb.IntegerProperty(indexed=True)
    views   = ndb.IntegerProperty(default=0)
    tags    = ndb.StringProperty(repeated=True)
    
    @classmethod
    def all_questions(cls):
        """
        Queries all questions the system, regardless of user, ordered by date created descending.
        """
        return cls.query().order(-cls.created) 
    
    @classmethod
    def all_questions_by_user(cls, user=None):
        """
        Queries all questions in the system for a particular user, ordered by date created descending.
        If no user is provided, it returns the posts for the current user.
        """
        if not user:
            user = users.get_current_user()
        return cls.find_all_by_created_by(user).order(-cls.created)
    
    
    def increase_views(self):
        """
        Increases views of question by 1 each time question is viewed.
        """
        if self.views == None:
            self.views = 1 
        else:
            self.views += 1
        self.put()
        