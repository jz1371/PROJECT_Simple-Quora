'''
File: app.models.question.py

@author: Jingxin Zhu 
'''

from ferris.core.ndb.model import BasicModel
from google.appengine.ext import ndb
from google.appengine.api import users

class Question(BasicModel):
    '''
    Question model that describes a question posted by user.
    '''

    title   = ndb.StringProperty(required=True)
    content = ndb.TextProperty(indexed=False)
    image   = ndb.BlobProperty()
    votes   = ndb.IntegerProperty(indexed=True)
    views   = ndb.IntegerProperty()
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
    
    
    def modify_views(self):
        self.views += 1
        self.put()
        
        
        