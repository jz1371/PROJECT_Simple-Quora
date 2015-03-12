'''
File: app/controllers/votes.py
-------------------------------------------
@author: Jingxin Zhu
@date  : 2015.03.11
-------------------------------------------
'''
from ferris import Controller, scaffold
from ferris.components.search import Search
from ferris.components.pagination import Pagination
from ferris.core.controller import route
from jinja2.runtime import to_string
from ferris.core.ndb import decode_key

from app.models.answer import Answer

class Votes(Controller):
    class Meta:
        """ global configuration """
        prefixes = ('admin',)
        # allow utilities of 'search', 'pagination', and take advantage of 'scaffolding'
        components = (scaffold.Scaffolding, Pagination, Search)
        
            
    @route       
    def up(self, target, key):
        self.meta.Model.vote_up(key)
        if (target == 'answer'):
            key = decode_key(key).parent().id()
        return self.redirect(self.uri(controller='questions', action='view', key=key))

    @route       
    def down(self, target, key):
        self.meta.Model.vote_down(key)
        if (target == 'answer'):
            key = decode_key(key).parent().id()
        return self.redirect(self.uri(controller='questions', action='view', key=key))    
