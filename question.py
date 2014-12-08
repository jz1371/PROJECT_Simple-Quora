'''
Created on Dec 6, 2014

@author: Steven
'''

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


# skip first 20 results, and only fetch entities' keys
DB.Question.query().fetch(limit=None, keys_only=True, offset=10)

"""

# create a new question
def create_question(user, content):
    question = DB.Question(user_ = user, content_ = content)
    q_key = question.put()
    return q_key

def create_answer(author, question_id, content):
    ans = DB.Answer(author_ = author, qid_ = question_id, content_ = content)
    a_key = ans.put()
    return a_key

def create_vote(author, qid, vote, aid=None):
    v = DB.Vote(author_ = author, qid_ = qid, aid_ = aid, vote_ = vote)
    v_key = v.put()
    return v_key

def view(question_id):
    # get question from data store
    question = DB.Question.get_by_id(long(question_id)) # return entity
    q_v_up = DB.Vote.query(DB.Vote.qid_ == question_id, DB.Vote.aid_ == None, DB.Vote.vote_ == 'up').count()
    print q_v_up
    q_v_down = DB.Vote.query(DB.Vote.qid_ == question_id, DB.Vote.aid_ == None, DB.Vote.vote_ == 'down').count()
    questions = (question.content_, q_v_up - q_v_down, question.user_)
    
    # need get() or fetch() to get the entity from query
    answer = DB.Answer.query(DB.Answer.qid_ == question_id).fetch()
    answers = []
    for a_key in answer:
        aid = str(a_key.key.id())
        vote = DB.Vote.query(DB.Vote.qid_ == question_id, DB.Vote.aid_ == aid)
        a_v_up = vote.filter(DB.Vote.vote_ == 'up').count()
        a_v_down = vote.filter(DB.Vote.vote_ == 'down').count()
        a_vote = a_v_up - a_v_down
        answers.append((a_vote, a_key))
        
        
    answers.sort(key=operator.itemgetter(0), reverse=True)
    profile = {'question' : questions, 'answer' : answers}
    return profile

def list_all():
    # !! How to fetch all instances or fetch all keys
    questions = DB.Question.query().fetch(limit=None, keys_only=True)
    '''
    for q_key in questions:
        print q_key.id()
        print q_key.get().content_
    '''
#     questions = ndb.gql("SELECT user_ FROM Question").fetch(10)
    return questions 
