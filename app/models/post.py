'''
File: app.model.post.py
-----------------------------------------------
This class is a verbose model class playground, 
whose controller is in app.controllers.posts.py

@author: Jingxin Zhu 
Created on 2015/02/10
-----------------------------------------------
'''

from ferris import BasicModel
from google.appengine.ext import ndb
from google.appengine.api import users


class Post(BasicModel):
    title = ndb.StringProperty(required=True)
    content = ndb.TextProperty()

    # property should be excluded from form of add.html
    views = ndb.IntegerProperty()

# Note:  below are auto inherited from BasicModel
#     created = ndb.DateTimeProperty(auto_now_add=True)
#     created_by = ndb.UserProperty(auto_current_user_add=True)
#     modified = ndb.DateTimeProperty(auto_now=True)
#     modified_by = ndb.UserProperty(auto_current_user=True)

    @classmethod
    def all_posts(cls):
        """
        Queries all posts in the system, regardless of user, ordered by date created descending.
        """
        return cls.query().order(-cls.created)

#   class method similar as class static method,
#   which is Question.all_posts_by_users()
    @classmethod
    def all_posts_by_user(cls, user=None):
        """
        Queries all posts in the system for a particular user, ordered by date created descending.
        If no user is provided, it returns the posts for the current user.
        """
        if not user:
            user = users.get_current_user()
                # automatic find_all_by_[property]
        return cls.find_all_by_created_by(user).order(-cls.created)
    

#   instance method which is associated with class Instance
#   question.foo
    def increase_views(self):
        self.views += 1
        self.put()