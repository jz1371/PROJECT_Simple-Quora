'''
File: app/models/vote.py
-------------------------------------------
@author: Jingxin Zhu 
@date  : 2015.03.11
-------------------------------------------
'''

from google.appengine.ext import ndb
from google.appengine.api import users
from ferris.core.ndb.model import BasicModel
from ferris.core.ndb import encode_key, decode_key
from ferris.behaviors.searchable import Searchable
from app.models.question import Question
from app.models.answer import Answer
from jinja2.runtime import to_string
from ferris.core.uri import Uri

class Vote(BasicModel):
    
    class Meta:
        '''
        global configuration for model.
        '''
        # allow this model for user searching
        behaviors = (Searchable, )
        
    type = ndb.StringProperty(choices=['up', 'down'])    
    vote = ndb.ComputedProperty(lambda self: 1 if (self.type == 'up') else -1)
    
    @classmethod
    def vote_up(cls, parentKey):
        parent = decode_key(parentKey).get()
        vote_qry = cls.query(ancestor=ndb.Key('Parent', parentKey)).filter(cls.created_by == users.get_current_user())
        if parent: 
            if vote_qry.count() != 0:
                # update existing vote
                vote = vote_qry.get()
                if (vote.type == 'down'):
                    parent.votes += 2
                    vote.type = 'up'
                    vote.put()
                    parent.put()
            else:
                vote = cls(parent=ndb.Key('Parent', parentKey), type='up');
                parent.votes += 1
                vote.put()
                parent.put()
        
    @classmethod
    def vote_down(cls, parentKey):
        parent = decode_key(parentKey).get()
        vote_qry = cls.query(ancestor=ndb.Key('Parent', parentKey)).filter(cls.created_by == users.get_current_user())
        if parent: 
            if vote_qry.count() != 0:
                # update existing vote
                vote = vote_qry.get()
                if (vote.type == 'up'):
                    parent.votes -= 2
                    vote.type = 'down'
                    vote.put()
                    parent.put()
            else:
                vote = cls(parent=ndb.Key('Parent', parentKey), type='up');
                parent.votes -= 1
                vote.put()
                parent.put()
        
        
    
    @classmethod
    def all_votes(cls):
        """
        Queries all answers the system, regardless of user, ordered by date created descending.
        """
        return cls.query().order(-cls.created) 
    
        