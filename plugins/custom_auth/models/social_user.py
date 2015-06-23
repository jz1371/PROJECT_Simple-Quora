import time
from user import User

from ferris import BasicModel, settings
from google.appengine.ext import ndb
import webapp2_extras.appengine.auth.models as auth_models
from webapp2_extras import security


class SocialUser(BasicModel):

    user = ndb.KeyProperty(kind=User)
    provider = ndb.StringProperty()
    uid = ndb.StringProperty()
    extra_data = ndb.JsonProperty()

    @classmethod
    def get_by_user(cls, user):
        return cls.query(cls.user == user).fetch()

    @classmethod
    def get_by_user_and_provider(cls, user, provider):
        return cls.query(cls.user == user, cls.provider == provider).get()

    @classmethod
    def get_by_provider_and_uid(cls, provider, uid):
        return cls.query(cls.provider == provider, cls.uid == uid).get()

    @classmethod
    def check_unique_uid(cls, provider, uid):
        # pair (provider, uid) should be unique
        test_unique_provider = cls.get_by_provider_and_uid(provider, uid)
        if test_unique_provider is not None:
            return False
        else:
            return True
    
    @classmethod
    def check_unique_user(cls, provider, user):
        # pair (user, provider) should be unique
        test_unique_user = cls.get_by_user_and_provider(user, provider)
        if test_unique_user is not None:
            return False
        else:
            return True

    @classmethod
    def check_unique(cls, user, provider, uid):
        # pair (provider, uid) should be unique and pair (user, provider) should be unique
        return cls.check_unique_uid(provider, uid) and cls.check_unique_user(provider, user)
    
    @staticmethod
    def open_id_providers():
        return [k for k,v in ferris.settings.get['social_providers'].items() if v['uri']]