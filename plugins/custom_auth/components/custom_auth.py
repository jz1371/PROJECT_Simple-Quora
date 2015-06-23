import webapp2
import logging

from .. import models

from webapp2_extras import sessions, auth # we'll use auth later on

def require_user(controller):
    """
    Requires that a user is logged in
    """
    if controller.components.custom_auth.current_user:
        return True
    return controller.redirect_to('user:login')

def require_not_user(controller):
    """
    Requires that there is no logged in user
    """
    if not controller.components.custom_auth.current_user:
        return True
    return controller.redirect('/')


class CustomAuth(object):
    def __init__(self, controller):
        self.controller = controller
        self.controller.events.before_render += self._on_before_render
        setattr(controller, 'user', self.get_user)
        setattr(controller, 'auth', self.get_auth)
        setattr(controller, 'user_id', self.get_user_id)
        self.controller = controller

    def get_user(self):
        return self.current_user

    def get_auth(self):
        return self.auth

    def get_user_id(self):
        return self.user_id

    @webapp2.cached_property
    def auth(self):
        return auth.get_auth()

    @webapp2.cached_property
    def user(self):
        return self.auth.get_user_by_session()

    @webapp2.cached_property
    def current_user(self):
        user = self.user
        if user:
            try:
                user_info = models.User.get_by_id(user['user_id'])
                if not user_info.activated:
                    self.auth.unset_session()
                    self.redirect('/')
                return user_info
            except AttributeError, e:
                # avoid AttributeError when the session was deleted from the server
                logging.error(e)
                self.auth.unset_session()
                self.controller.redirect('/')
        return None

    @webapp2.cached_property
    def user_id(self):
        return str(self.user['user_id']) if self.user else None

    @webapp2.cached_property
    def user_key(self):
        if self.user:
            user_info = models.User.get_by_id(long(self.user_id))
            return user_info.key
        return None

    def _on_before_render(self, controller, *args, **kwargs):
        controller.context.set_dotted('this.user', self.current_user)