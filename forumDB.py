'''
File: forumDB.py
--------------------------
Created on Dec 6, 2014

@author: Steven
'''

from google.appengine.ext import ndb

class Question(ndb.Model):
    user_ = ndb.UserProperty()
    content_ = ndb.StringProperty(indexed=False)
    date_created_ = ndb.DateTimeProperty(auto_now_add=True)
    date_last_modified_ = ndb.DateTimeProperty(auto_now=True)
    
class Answer(ndb.Model):
    author_ = ndb.UserProperty()
    qid_ = ndb.StringProperty()
    content_ = ndb.StringProperty(indexed=False)
    date_created_ = ndb.DateTimeProperty(auto_now_add=True)
    date_last_modified_ = ndb.DateTimeProperty(auto_now=True)
    
    
class Vote(ndb.Model):
    author_ = ndb.UserProperty()
    qid_ = ndb.StringProperty()
    aid_ = ndb.StringProperty()
    vote_ = ndb.StringProperty( choices=['up', 'down'])
    date_created_ = ndb.DateTimeProperty(auto_now_add=True)
    date_last_modified_ = ndb.DateTimeProperty(auto_now=True)


    
    