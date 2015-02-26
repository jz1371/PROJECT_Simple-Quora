'''
Created on Feb 11, 2015

@author: Jingxin Zhu 
'''

# from ferris.tests.lib import WithTestBed
from app.models.post import Post
from ferrisnose import AppEngineTest


class CatTest(AppEngineTest):
    def test_herding(self):
        Post(title="Pickles").put()
        Post(title="Mr. Sparkles").put()

        assert Post.query().count() == 2
        
