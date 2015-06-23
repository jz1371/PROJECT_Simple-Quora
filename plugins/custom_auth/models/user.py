import time

from ferris import BasicModel, settings
from google.appengine.ext import ndb
import webapp2_extras.appengine.auth.models as auth_models
from webapp2_extras import security


class User(auth_models.User):
    """
    Universal user model. Can be used with App Engine's default users API,
    own auth or third party authentication methods (OpenID, OAuth etc).
    based on https://gist.github.com/kylefinley
    """
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    full_name = ndb.ComputedProperty(lambda self: (self.first_name if self.first_name else '') + ' ' + (self.last_name if self.last_name else ''))
    email = ndb.StringProperty()
    activated = ndb.BooleanProperty(default=False)

    @classmethod
    def get_by_email(cls, email):
        """Returns a user object based on an email.

        :param email:
            String representing the user email. Examples:

        :returns:
            A user object.
        """
        return cls.query(cls.email == email).get()

    @classmethod
    def create_resend_token(cls, user_id):
        entity = cls.token_model.create(user_id, 'resend-activation-mail')
        return entity.token

    @classmethod
    def validate_resend_token(cls, user_id, token):
        return cls.validate_token(user_id, 'resend-activation-mail', token)

    @classmethod
    def delete_resend_token(cls, user_id, token):
        cls.token_model.get_key(user_id, 'resend-activation-mail', token).delete()

    def get_social_providers_names(self):
        from social_user import SocialUser
        social_users = SocialUser.get_by_user(self.key)
        result = []
        for social_user in social_users:
            result.append(social_user.provider)
        return result

    def get_social_providers_info(self):
        providers = self.get_social_providers_names()
        result = {'used': [], 'unused': []}
        for k,v in settings.get('social_providers').items():
            if k in providers:
                result['used'].append(v)
            else:
                result['unused'].append(v)
        return result
