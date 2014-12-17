'''
Created on Dec 6, 2014

@author: Steven
'''

from google.appengine.ext import ndb
import forumDB as DB
import operator

"""
# 1. access entity's properties set up by database system,
# namely, the entity's Key and entity's ID 
    q_key = quesetion.put() has two attributes: 
    q_key.kind()
    q_key.id()
# Or, through entity
    entity = Question.get_by_id(qid) 
    print entity.key.kind()  
    print entity.key.id()  

# 1.2. access entity's custom property
# Entity:

    entity = Question.get_by_id(qid) 
    print entity.content_

# 1.3. fetch()

    keys = Question.query(...).fetch()
    # keys would contain keys' list
    key = Question.query(...).get()
    # This return one single key
    key.content_ = ...
    

# skip first 20 results, and only fetch entities' keys

    DB.Question.query().fetch(limit=None, keys_only=True, offset=10)

"""

# create a new question
def create_question(qid, user, content):
    if qid:
        # update existing one
        key = ndb.Key('Question', long(qid))
        q_key = key.get()
        q_key.content_ = content
        q_key = q_key.put()
    else:
        # create a new one
        question = DB.Question(user_ = user, content_ = content)
        q_key = question.put()
    return q_key

def create_answer(author, question_id, content):
    ans = DB.Answer(author_ = author, qid_ = question_id, content_ = content)
    a_key = ans.put()
    return a_key

# if vote exists, then update, otherwise, create new vote
def create_vote(author, qid, vote, aid=None):
    vote_qry = DB.Vote.query(DB.Vote.author_ == author, DB.Vote.qid_ == qid, DB.Vote.aid_ == aid)
    if vote_qry.count() == 0:
        print "No vote"
        # create your one
        v = DB.Vote(author_ = author, qid_ = qid, aid_ = aid, vote_ = vote)
        v_key = v.put()
    else:
        # edit existing one
        v_key = vote_qry.get()
        v_key.vote_ = vote
        v_key.put()
        
    return v_key

def view(question_id):
    # get question from data store
    question = DB.Question.get_by_id(long(question_id)) # return entity
    q_v_up = DB.Vote.query(DB.Vote.qid_ == question_id, DB.Vote.aid_ == None, DB.Vote.vote_ == 'up').count()
    q_v_down = DB.Vote.query(DB.Vote.qid_ == question_id, DB.Vote.aid_ == None, DB.Vote.vote_ == 'down').count()
    questions = {
        'content': question.content_ , 
        'votes':  q_v_up - q_v_down,
        'author': question.user_
        }
    
    # need get() or fetch() to get the entity from query
    answer = DB.Answer.query(DB.Answer.qid_ == question_id).fetch()
    answers = []
    for a_key in answer:
        aid = str(a_key.key.id())
        vote = DB.Vote.query(DB.Vote.qid_ == question_id, DB.Vote.aid_ == aid)
        a_v_up = vote.filter(DB.Vote.vote_ == 'up').count()
        a_v_down = vote.filter(DB.Vote.vote_ == 'down').count()
        a_vote = a_v_up - a_v_down
        
        answers.append({"votes": a_vote, "key": a_key})
       
    tags = []
    tag_qry = DB.Tag.query(DB.Tag.qid_ == question_id).fetch(keys_only=True)
    for t_key in tag_qry:
        tags.append(t_key.get().tag_)
    tag = " ; ".join(tags)
        
    answers.sort(key=operator.itemgetter('votes'), reverse=True)
    profile = {'question' : questions, 'answer' : answers, 'tag': tag}
    return profile

def list_all(tag):
    
    if tag:
        # filter question by tag
        # get all qids
        questions = []
        q_qry = DB.Tag.query(DB.Tag.tag_ == tag).fetch(keys_only=True)
        for q_key in q_qry:
            key = ndb.Key('Question', long(q_key.get().qid_))
            q_key = key.get()
            questions.append(q_key.key)
        
    else:
        # !! How to fetch all instances or fetch all keys
        questions = DB.Question.query().order(-DB.Question.date_last_modified_).fetch(limit=None, keys_only=True)
    '''
    for q_key in questions:
        print q_key.id()
        print q_key.get().content_
    '''
    tags = set()
    tag_qry = DB.Tag.query().fetch(limit=None, keys_only=True)
    for t_key in tag_qry:
        tags.add(t_key.get().tag_)
    
#     questions = ndb.gql("SELECT user_ FROM Question").fetch(10)
    return questions, tags

def add_tag(qid, tags):
    tags = [t.strip() for t in tags.split(';')]
    tags = set(tags)
    for tag in tags:
        if tag != "":
            t = DB.Tag(qid_ = str(qid), tag_ = tag.strip())
            t.put()