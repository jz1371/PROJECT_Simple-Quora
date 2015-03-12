'''
File: app/models/answer.py
-------------------------------------------
@author: Jingxin Zhu 
@date  : 2015.02.28
-------------------------------------------
'''

from google.appengine.ext import ndb
from google.appengine.api import users
from ferris.core.ndb.model import BasicModel
from ferris.behaviors.searchable import Searchable

class Answer(BasicModel):
    '''
    TODO: class doc
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
    content = ndb.TextProperty(required=True)
    image   = ndb.BlobProperty()
    votes   = ndb.IntegerProperty(default=0, indexed=True)
    
    @classmethod
    def all_answers(cls):
        """
        Queries all answers the system, regardless of user, ordered by date created descending.
        """
        return cls.query().order(-cls.created) 
    
    @classmethod
    def all_answers_by_user(cls, user=None):
        """
        Queries all answers in the system for a particular user, ordered by date created descending.
        If no user is provided, it returns the posts for the current user.
        """
        if not user:
            user = users.get_current_user()
        return cls.find_all_by_created_by(user).order(-cls.created)
    
    @classmethod
    def create_answer_by_parent(cls, questionKey):
        return cls(parent=ndb.Key("Question", questionKey))
        
    @classmethod
    def all_answers_by_question(cls, key):
        questionKey = ndb.Key("Question", key)
        return cls.query(ancestor=questionKey).order(-cls.created).fetch()
        