"""
File:  main.py
-------------------------
Last Update: 12/12/14
"""
import os
import urllib
import re

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.datastore.datastore_query import Cursor
from google.appengine.api import mail

import jinja2
import webapp2
import datetime
import time

# -------------------------------
"""
Return entity:   

    1. Model.query().fetch()

    2. use parent key to query
    qry = Question.query(ancestor=ndb.Key('qid', qid)).fetch()

Return key:

    1. Model.query().fetch(keys_only=True)

    2.  q_url = self.request.get('q')
        q_key = ndb.Key(urlsafe=q_url)
        question = q_key.get()
        
"""
# ===== [ START : DATABASE CLASS ] =====

# 'uid': user.user_id() as parent
class Question(ndb.Model):
    author_ = ndb.UserProperty()
    content_ = ndb.StringProperty(indexed=False)
    image_ = ndb.BlobProperty()
    votes_ = ndb.IntegerProperty(indexed=True)
    views_ = ndb.FloatProperty(indexed=True)
    date_created_ = ndb.DateTimeProperty(auto_now_add=True)
    date_last_modified_ = ndb.DateTimeProperty()
    tags_ = ndb.StringProperty(repeated=True)
    
# each answer is associated with a question
# i.e. Answer has Question as parent
class Answer(ndb.Model):
    author_ = ndb.UserProperty()
    content_ = ndb.StringProperty(indexed=False)
    image_ = ndb.BlobProperty()
    votes_ = ndb.IntegerProperty(indexed=True)
    date_created_ = ndb.DateTimeProperty(auto_now_add=True)
    date_last_modified_ = ndb.DateTimeProperty()
    
class Vote(ndb.Model):
    author_ = ndb.UserProperty()
    type_ = ndb.StringProperty(choices=['question', 'answer'])
    vote_ = ndb.StringProperty(choices=['up', 'down'])
    date_created_ = ndb.DateTimeProperty(auto_now_add=True)
    date_last_modified_ = ndb.DateTimeProperty(auto_now=True)

class Tag(ndb.Model):
    tag_ = ndb.StringProperty()
    count_ = ndb.IntegerProperty()
    date_created_ = ndb.DateTimeProperty(auto_now_add=True)
    
class Image(ndb.Model):
    author_ = ndb.UserProperty()
    image_ = ndb.BlobProperty()
    link_ = ndb.StringProperty()
#[ END : DATABASE CLASS ]


def post_vote(author, question, vote, answer=None):
    
    if answer == None:
        # voting for question
        vote_qry = Vote.query(ancestor=question.key)
        votes = vote_qry.filter(Vote.author_ == author, Vote.type_ == 'question')
        if votes.count() == 0:
            # create new vote
            v = Vote(parent=question.key, author_ = author, type_ = 'question',
                vote_ = vote)
            v_key = v.put()
        else:
            # editing existing vote
            v = votes.get()
            v.vote_ = vote
            v.put()
        # update question vote count for question
        q_vote_qry = Vote.query(ancestor=question.key).filter(Vote.type_ == 'question')
        q_v_up = q_vote_qry.filter(Vote.vote_ == 'up').count()
        q_v_down = q_vote_qry.filter(Vote.vote_ == 'down').count()
        question.votes_ = q_v_up - q_v_down
#         question.date_last_modified_ = datetime.datetime.now()
        question.put()
        
    else:
        # voting for answer 
        vote_qry = Vote.query(ancestor=answer.key).filter(Vote.type_ == 'answer')
        votes = vote_qry.filter(Vote.author_ == author)
        if votes.count() == 0:
            v = Vote(parent=answer.key)
            v.populate(author_ = author, type_ = 'answer', vote_ = vote)
            v_key = v.put()
        else:
            v = votes.get()
            v.vote_ = vote
            v.put()
        a_vote_qry = Vote.query(ancestor = answer.key).filter(Vote.type_ == 'answer')
        a_v_up = a_vote_qry.filter(Vote.vote_ == 'up').count()
        a_v_down = a_vote_qry.filter(Vote.vote_ == 'down').count()
        answer.votes_ = a_v_up - a_v_down
#         answer.date_last_modified_ = datetime.datetime.now()
        answer.put()
            

# [ WEB ENVIRONMENT ]
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader( \
        os.path.join(os.path.dirname(__file__), 'templates')),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

def make_page(handler, template_file, substitutes):
    template = JINJA_ENVIRONMENT.get_template(template_file)
    handler.response.write(template.render(substitutes))

DEFAULT_QUESTION_TAG = 'default_tag'
# =============================================================

def send_email(q_author, content):
    if mail.is_email_valid(q_author.email()):
        message = mail.EmailMessage(sender="Admin <jz1371@nyu.edu>",
                            subject="Your question receives a new answer")

        message.to = "%s <%s>" % (q_author.nickname(), q_author.email())
        message.body = """
        Dear %s:

        Your question has received a new answer:

        %s
        
        Please let us know if you have any questions.

        The Simple Quora Team
        """ % (q_author.nickname(), content)
        message.send()
# http://www.google.com is here

def detect_link(content):
    def replink(m):
        if m.group().endswith('.jpg') or m.group().endswith('.png') or m.group().endswith('.gif'):
            return  '<img src="'  + m.group() + '">'
        elif m.group().startswith('http://quora-jz1371.appspot.com/dyimg_serve?img_id') :
            return '<img src="' + m.group() + '">'
        else:
            return '<a href="' + m.group(1) + '">' + m.group(2) + '</a >'
    return re.sub(r'(https?://([^ ,;\n]*))', replink, content)


# [ START : Request Handler ]
class MainPage(webapp2.RequestHandler):
    
    def get(self):
        cursor = self.request.get('cursor')
        if cursor:
            print "here" 
        tag_name = urllib.unquote(self.request.get('tag'))
        print tag_name
        curs = Cursor(urlsafe=self.request.get('cursor'))
        if tag_name:
            question_qry = Question.query(Question.tags_ == tag_name).order( -Question.date_last_modified_)
        else:
            question_qry = Question.query().order(-Question.date_last_modified_)
        questions, next_curs, more = question_qry.fetch_page(
            10, start_cursor=curs)
        if more and next_curs:
            self.response.out.write('<a href="/?cursor=%s"> >> More Questions >> </a>' %
                              next_curs.urlsafe()) 
        tags = Tag.query().order(-Tag.count_).fetch()
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
            
        substitutes = {
            'questions' : questions, 
            'tags': (tags),
            'cur_user': users.get_current_user(),
            'url' : url,
            'url_linktext' : url_linktext,
        }
        make_page(self, 'home.html', substitutes)

class AskQuestionHandler(webapp2.RequestHandler):
    def get(self):
        if users.get_current_user():
            substitutes = {
                   'upload_url' :"", 
                   'cur_user': users.get_current_user(),
                   }
            make_page(self, 'create_question.html', substitutes)
        else:
            self.redirect(users.create_login_url(self.request.uri))
        
    
class PostQuestionHandler(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        q_url = self.request.get('q')
        # update existing one
        if q_url:
            q_key = ndb.Key(urlsafe=q_url)
            question = q_key.get()
        else:
            # create new question
            question = Question(parent=ndb.Key('uid', user.user_id()))
            question.author_ = user
            question.votes_ = 0
            question.views_ = -0.5 
#             file_upload = self.request.POST.get("img", None)
            if self.request.get('img'):
                file_upload = self.request.POST.get('img', None)
                if file_upload != None: 
                    question.image_ = file_upload.file.read()

            tags_str = self.request.get('tags')
            # parse tags
            tag_set = set(tag.strip() for tag in tags_str.split(';') if tag != '')
            question.tags_ = [tag for tag in tag_set]
            # update Tag class
            for tag in tag_set:
                qry = Tag.query(Tag.tag_==tag)
                count = qry.count()
                if count == 0:
                    tag = Tag(tag_ = tag, count_=1)
                    tag.put()
                else:
                    tag = qry.get()
                    tag.count_ += 1
                    tag.put()
        question.content_ = detect_link(self.request.get('content'))
        question.date_last_modified_ = datetime.datetime.now()
        q_key = question.put()
        self.redirect('/view?q=' + q_key.urlsafe())

    



class PostAnswerHandler(webapp2.RequestHandler):
    
    def post(self):
        user = users.get_current_user()
        if user:
            q_url = self.request.get('q')
            a_url = self.request.get('a')
            if not a_url: 
                # if is creating new answer
                q_key = ndb.Key(urlsafe=q_url)
                question = q_key.get()
                answer = Answer(parent=q_key)
                #             answer = Answer(parent=ndb.Key('qid', question.key.id()))
                answer.author_ = user
                answer.votes_ = 0
                answer.content_ = detect_link(self.request.get('content'))
                answer.date_last_modified_ = datetime.datetime.now()

                if self.request.get('img'):
                    file_upload = self.request.POST.get('img', None)
                    if file_upload != None and file_upload.file != None:
#                     print file_upload
                        answer.image_ = file_upload.file.read() 
                answer.put()
                send_email(question.author_, answer.content_)
            else:
                # editing existing answer 
                # get this answer 
                a_key = ndb.Key(urlsafe=a_url)
                answer = a_key.get()
                # in case answer not exist
                if answer == None:
                    self.response.write("no such answer")
                else:
                    # update answer
                    answer.content_ = detect_link(self.request.get('content'))
                    answer.date_last_modified_ = datetime.datetime.now()
                    answer.put()
        else:
            self.redirect(users.create_login_url(self.request.uri))
         
#         time.sleep(0.1)
        self.redirect('/view?q=' + q_url)
#         self.redirect('/view?q=' + q_key.urlsafe())

class ViewHandler(webapp2.RequestHandler):
    def get(self):
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        q_url = self.request.get('q')
        q_key = ndb.Key(urlsafe=q_url)
        question = q_key.get()
        # get all answers based on parent qid
        qid = question.key.id()
#         ans_qry = Answer.query(ancestor=ndb.Key('qid', qid))
        ans_qry = Answer.query(ancestor=q_key).order(-Answer.votes_)
        answers = ans_qry.fetch()
        question.views_ = question.views_ + 0.5 
        question.put()
#         self.response.write(answers)
        substitutes = {
            'cur_user': users.get_current_user(),
            'admin': users.is_current_user_admin(),
            'question' : question, 
            'answers': answers,
            'url' : url,
            'url_linktext' : url_linktext,
        }
        make_page(self, 'view.html', substitutes)
#         question.put()
# [ END : Request Handler ]

class VoteHandler(webapp2.RedirectHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            vote = self.request.get('v')
            q_url = self.request.get('q')
            q_key = ndb.Key(urlsafe=q_url)
            question = q_key.get()

            a_url= self.request.get('a')
            if a_url == "":
                post_vote(user, question, vote)
            else:
                a_key = ndb.Key(urlsafe=a_url)
                answer = a_key.get()
                post_vote(user, question, vote, answer)
    
#             qid = self.request.get('qid')
#             aid = self.request.get('aid')

            q_key = Question.query(ancestor=ndb.Key('uid', user.user_id())).get()
            self.redirect('/view?q=' + question.key.urlsafe())
#                 create_vote(user, qid, vote, aid)
#             self.response.write(qid)
#             q = Question.get_by_id(long(qid), ndb.Key('uid', user.user_id()))
#             self.response.write(q)
#             self.redirect('view?q=')
        else:
            self.redirect(users.create_login_url(self.request.uri))

class UploadHandler(webapp2.RequestHandler):
    def post(self):
        if self.request.get('img'):
            file_upload = self.request.POST.get('img', None)
            if file_upload != None and file_upload.file != None:
                img = Image(parent=ndb.Key('uid', users.get_current_user().user_id()))
                img.image_ = file_upload.file.read()
                img.author_ = users.get_current_user()
                img_key = img.put()
                self.redirect("/")
                
        
#         self.response.write(q_key.get().image_)

class DynamicImageServe(webapp2.RequestHandler):
    def get(self):
        url = self.request.get('img_id')
        key = ndb.Key(urlsafe=url)
        entity = key.get()
        if entity.image_:
            self.response.headers['Content-Type'] = 'image/jpeg'
            self.response.out.write(entity.image_)
#         if greeting.avatar:
#             self.response.headers['Content-Type'] = 'image/png'
#             self.response.out.write(greeting.avatar)
#         oldUser = MyUser.get_by_id(email_id)
#         if oldUser != None and oldUser.blob != None:
#             ##            self.response.headers['Content-Type'] = 'image/png'
#             self.response.headers[b'Content-Type'] = mimetypes.guess_type(oldUser.file_name)[0]
#             self.response.write(oldUser.blob)
#         else:
#             self.response.write('Error while fetching image data')
 
class RssFeedHandler(webapp2.RequestHandler):
    def get(self):
        q_url = self.request.get('q')
        q_key = ndb.Key(urlsafe=q_url)
        question = q_key.get()
        if question:
            answers = Answer.query(ancestor=q_key).order(-Answer.votes_).fetch()
            
            substitutes = {
                           'question' : question,
                           'answers' : answers,
                           }

            self.response.headers['Content-Type'] = 'text/xml'
            make_page(self, 'feed.xml', substitutes)

class DeleteHandler(webapp2.RequestHandler):
    def get(self):
        url = self.request.get('p')
        key = ndb.Key(urlsafe=url)
        key.delete()
        time.sleep(0.1)
        self.redirect('/')

    
class ShowImageHandler(webapp2.RequestHandler):
    def get(self):
        images = Image.query().fetch(limit=None)
        substitutes = {"images": images}
        make_page(self, 'image.html', substitutes)
        
class ImageRedirectHandler(webapp2.RequestHandler):
    def get(self):
        url_long = self.request.get('img_id')
        url = url_long[:-4]
        self.redirect('/dyimg_serve?img_id=%s' % url)
        
class UploadPageHandler(webapp2.RequestHandler):
    def get(self):
        images = Image.query().fetch(limit=None)
        substitutes = {"images": images}
        make_page(self, 'image.html', substitutes)
        
# ======== Main ==============
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/ask', AskQuestionHandler),
    ('/post-question', PostQuestionHandler),
    ('/post-answer', PostAnswerHandler),
    ('/view', ViewHandler),
    ('/vote', VoteHandler),
    ('/upload', UploadHandler),
    ('/uploadpage', UploadPageHandler),
    ('/dyimg_serve',DynamicImageServe),
    ('/rss', RssFeedHandler),
    ('/delete', DeleteHandler),
    ('/images', ImageRedirectHandler),
    ('/showimage', ShowImageHandler),
], debug=True)