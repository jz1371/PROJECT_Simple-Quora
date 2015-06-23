import json
import logging
import wtforms
import webapp2

from ferris import Controller, scaffold, settings, route_with, route, add_authorizations
from ferris.components.flash_messages import FlashMessages
from ferris.core import mail
from google.appengine.api import users
from ferris.components import csrf
from plugins.recaptcha.components import recaptcha
from webapp2_extras.appengine.auth.models import Unique
from webapp2_extras.auth import InvalidAuthIdError, InvalidPasswordError
from webapp2_extras import security
from ..components import custom_auth
from ..lib import facebook
from ..lib import twitter
from ..packages.github import github
from ..packages.linkedin import linkedin
from .. import models
from .. import utils

class ResetPasswordForm(wtforms.Form):
    password = wtforms.fields.TextField('Password',
                    [wtforms.validators.Required()])

class EditEmailForm(wtforms.Form):
    new_email = wtforms.fields.TextField('New Email',
                    [wtforms.validators.Required(),
                     wtforms.validators.Email()])
    password = wtforms.fields.TextField('Password',
                    [wtforms.validators.Required()])

class EditPasswordForm(wtforms.Form):
    old_password = wtforms.fields.TextField('Old Password',
                    [wtforms.validators.Required()])
    new_password = wtforms.fields.TextField('New Password',
                    [wtforms.validators.Required()])

class EditProfileForm(wtforms.Form):
    first_name = wtforms.fields.TextField('First Name',
                    [wtforms.validators.Required()])
    last_name = wtforms.fields.TextField('Last Name',
                    [wtforms.validators.Required()])

class LoginForm(wtforms.Form):
    email = wtforms.fields.TextField('Email',
                    [wtforms.validators.Required(),
                     wtforms.validators.Email()])
    password = wtforms.fields.TextField('Password',
                    [wtforms.validators.Required()])
    remember = wtforms.fields.BooleanField('Remember Me')


class RegisterForm(wtforms.Form):
    first_name = wtforms.fields.TextField('First Name',
                    [wtforms.validators.Required()])
    last_name = wtforms.fields.TextField('Last Name',
                    [wtforms.validators.Required()])
    email = wtforms.fields.TextField('Email',
                    [wtforms.validators.Required(),
                     wtforms.validators.Email()])
    password = wtforms.fields.TextField('Password',
                    [wtforms.validators.Required()])


class User(Controller):
    class Meta:
        components = (custom_auth.CustomAuth, csrf.CSRF, FlashMessages,  scaffold.Scaffolding, recaptcha.Recaptcha)
        authorizations = (csrf.require_csrf,)

    @route_with('/login')
    @add_authorizations(custom_auth.require_not_user)
    def login(self):
        parser = self.parse_request(container=LoginForm)
        parser.container.password.description ='<a href="' + self.uri_for('user:reset_password') + '">Forgot your password?</a>'
        if self.request.method == "POST":

            # validate the form
            if not parser.validate():
                self.context['form'] = parser.container
                return

            # properties
            email = parser.container.email.data.lower()
            remember = parser.container.remember.data

            # Password to SHA512
            password = parser.container.password.data
            password = utils.hashing(password, settings.get('salt'))

            try:

                # Auth id
                auth_id = 'email:%s' % email
                user = models.User.get_by_auth_id(auth_id)

                # Try to login user with password
                # Raises InvalidAuthIdError if user is not found
                # Raises InvalidPasswordError if provided password
                # doesn't match with specified user
                self.auth().get_user_by_password(
                    auth_id, password, remember=remember)

                # if user account is not activated, logout and redirect to home
                if (user.activated == False):
                    # logout
                    self.auth().unset_session()

                    # redirect to home with error message
                    resend_email_uri = self.uri_for('user:resend_activation', user_id=user.get_id(), token=models.User.create_resend_token(user.get_id()))
                    message = 'Your account has not yet been activated. Please check your email to activate it or <a href="' + resend_email_uri + '">click here</a> to resend the email.'
                    self.components.flash_messages.flash(message, 'danger')
                    return self.redirect('/')

                # check twitter association in session
                twitter_helper = twitter.TwitterAuth(self)
                twitter_association_data = twitter_helper.get_association_data()
                if twitter_association_data is not None:
                    if models.SocialUser.check_unique(user.key, 'twitter', str(twitter_association_data['id'])):
                        social_user = models.SocialUser(
                            user=user.key,
                            provider='twitter',
                            uid=str(twitter_association_data['id']),
                            extra_data=twitter_association_data
                        )
                        social_user.put()

                # check facebook association
                fb_data = None
                try:
                    fb_data = json.loads(self.session['facebook'])
                except:
                    pass

                if fb_data is not None:
                    if models.SocialUser.check_unique(user.key, 'facebook', str(fb_data['id'])):
                        social_user = models.SocialUser(
                            user=user.key,
                            provider='facebook',
                            uid=str(fb_data['id']),
                            extra_data=fb_data
                        )
                        social_user.put()

                # check linkedin association
                li_data = None
                try:
                    li_data = json.loads(self.session['linkedin'])
                except:
                    pass

                if li_data is not None:
                    if models.SocialUser.check_unique(user.key, 'linkedin', str(li_data['id'])):
                        social_user = models.SocialUser(
                            user=user.key,
                            provider='linkedin',
                            uid=str(li_data['id']),
                            extra_data=li_data
                        )
                        social_user.put()

                # end linkedin

                # success
                self.components.flash_messages.flash('You were logged in!', 'success')
                return self.redirect('/')

            except (InvalidAuthIdError, InvalidPasswordError), e:
                # Returns error message to self.response.write in
                # the BaseHandler.dispatcher
                message = "Your username or password is incorrect. Please try again (make sure your caps lock is off)"
                self.components.flash_messages.flash(message, 'danger')
                return self.redirect_to('user:login')

        elif self.request.method == "GET":
            self.context['form'] = parser.container
            return

    @route_with('/logout')
    @add_authorizations(custom_auth.require_user)
    def logout(self):
        if self.user():
            message = ("You've signed out successfully. Warning: Please clear all cookies and logout of OpenID providers too if you logged in on a public computer.")
            self.components.flash_messages.flash(message, 'info')

        self.auth().unset_session()

        # User is logged out, let's try redirecting to login page
        try:
            return self.redirect_to('user:login')
        except (AttributeError, KeyError), e:
            logging.error("Error logging out: %s" % e)
            message = ("User is logged out, but there was an error on the redirection.")
            self.components.flash_messages.flash(message, 'danger')
            return self.redirect('/')

    @route_with('/register')
    @add_authorizations(custom_auth.require_not_user)
    def register(self):
        parser = self.parse_request(container=RegisterForm)
        if self.request.method == "POST":

            # Validate the form
            if not parser.validate():
                self.context['form'] = parser.container
                return

            # properties
            email = parser.container.email.data.lower()
            first_name = parser.container.first_name.data.strip()
            last_name = parser.container.last_name.data.strip()

            # Password to SHA512
            password = parser.container.password.data
            password = utils.hashing(password, settings.get('salt'))

            # Auth id
            auth_id = 'email:%s' % email
            unique_properties = ['email']

            # Passing password_raw=password so password will be hashed
            # Returns a tuple, where first value is BOOL.
            # If True ok, If False no new user is created
            success, user = self.auth().store.user_model.create_user(
                auth_id,
                unique_properties=unique_properties,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password_raw=password)

            # If it failed
            if not success:
                error = "That email is already in use. %s" % email if 'email' in user else "Something has gone horrible wrong."
                self.components.flash_messages.flash(error, 'danger')
                return self.redirect_to('user:register')

            # Send the activation email
            if not user.activated:

                # send email
                subject = "%s Account Verification" % settings.get('app_name')
                confirmation_url = self.uri_for("user:activate",
                                                user_id=user.get_id(),
                                                token=models.User.create_auth_token(user.get_id()),
                                                _full=True)

                mail.send_template(
                    recipient=str(email),
                    subject=subject,
                    template_name='account_activation',
                    context={
                        "app_name": settings.get('app_name'),
                        "full_name": user.full_name,
                        "confirmation_url": confirmation_url,
                        "support_url": "#" #self.uri_for("contact", _full=True)
                    }
                )

                logging.info('confirmation_url: %s' % confirmation_url)

                self.components.flash_messages.flash('You were successfully registered. Please check your email to activate your account.', 'success')
                return self.redirect('/')

            self.components.flash_messages.flash('The user was successfully added', 'success')
            return self.redirect('/')
        else:
            self.context['form'] = parser.container
            return


    @route_with('/activation/<user_id>/<token>')
    def activate(self, user_id, token):
        try:
            if not models.User.validate_auth_token(user_id, token):
                message = 'The link is invalid.'
                self.components.flash_messages.flash(message, 'danger')
                return self.redirect('/')

            # activate the user's account
            user = models.User.get_by_id(long(user_id))
            user.activated = True
            user.put()

            # Login User
            self.auth().get_user_by_token(int(user_id), token)

            # Delete token
            models.User.delete_auth_token(user_id, token)

            message = 'Congratulations, Your account has been successfully activated.'
            self.components.flash_messages.flash(message, 'success')
            return self.redirect('/')

        except (AttributeError, KeyError, InvalidAuthIdError, NameError), e:
            logging.error("Error activating an account: %s" % e)
            message = 'Sorry, Some error occurred.'
            self.components.flash_messages.flash(message, 'danger')
            return self.redirect('/')

    @route_with('/resend/<user_id>/<token>')
    def resend_activation(self, user_id, token):
        logging.info('YO')
        try:
            if not models.User.validate_resend_token(user_id, token):
                message = 'The link is invalid.'
                self.components.flash_messages.flash(message, 'danger')
                return self.redirect('/')

            user = models.User.get_by_id(long(user_id))
            email = user.email

            if (user.activated == False):
                # send email
                subject = "%s Account Verification" % settings.get('app_name')
                confirmation_url = self.uri("user:activate",
                                                user_id=user.get_id(),
                                                token=models.User.create_auth_token(user.get_id()),
                                                _full=True)

                mail.send_template(
                    recipient=str(email),
                    subject=subject,
                    template_name='account_activation',
                    context={
                        "app_name": settings.get('app_name'),
                        "full_name": user.full_name,
                        "confirmation_url": confirmation_url,
                        "support_url": "#" #self.uri_for("contact", _full=True)
                    }
                )

                logging.info('confirmation_url: %s' % confirmation_url)

                models.User.delete_resend_token(user_id, token)

                message = 'The verification email has been resent to %s. Please check your email to activate your account.' % email
                self.components.flash_messages.flash(message, 'success')
                return self.redirect('/')
            else:
                message = 'Your account has been activated. Please <a href="%s">sign in</a> to your account.' % self.uri('user:login')
                self.components.flash_messages.flash(message, 'warning')
                return self.redirect('/')

        except (KeyError, AttributeError), e:
            logging.error("Error resending activation email: %s" % e)
            message = 'Sorry, Some error occurred.'
            self.components.flash_messages.flash(message, 'danger')
            return self.redirect('/')


    @route_with('/social-login/<provider_name>')
    def social_login(self, provider_name):
        """
        Handler for Social authentication
        """
        provider = settings.get('social_providers').get(provider_name)

        if not settings.get('enable_federated_login'):
            message = 'Federated login is disabled.'
            self.components.flash_messages.flash(message, 'warning')
            return self.redirect_to('user:login')
        callback_url = self.uri('user:social_login_complete', provider_name=provider_name, _full=True)

        if provider_name == 'twitter':
            twitter_helper = twitter.TwitterAuth(self, redirect_uri=callback_url)
            return self.redirect(twitter_helper.auth_url())

        elif provider_name == 'facebook':
            self.session['linkedin'] = None
            perms = ['email', 'publish_stream']
            return self.redirect(facebook.auth_url(settings.get('fb_api_key'), callback_url, perms))

        elif provider_name == 'linkedin':
            self.session['facebook'] = None
            authentication = linkedin.LinkedInAuthentication(
                settings.get('linkedin_api'),
                settings.get('linkedin_secret'),
                callback_url,
                [linkedin.PERMISSIONS.BASIC_PROFILE, linkedin.PERMISSIONS.EMAIL_ADDRESS])
            return self.redirect(authentication.authorization_url)

        elif provider_name == 'github':
            scope = 'gist'
            github_helper = github.GithubAuth(settings.get('github_server'),
                                              settings.get('github_client_id'), \
                                              settings.get('github_client_secret'),
                                              settings.get('github_redirect_uri'), scope)
            return self.redirect(github_helper.get_authorize_url())

        elif provider_name in settings.get('social_providers'):
            continue_url = self.request.get('continue_url')
            if continue_url:
                dest_url = self.uri_for('user:social_login_complete', provider_name=provider_name, continue_url=continue_url)
            else:
                dest_url = self.uri_for('user:social_login_complete', provider_name=provider_name)
            try:
                login_url = users.create_login_url(federated_identity=provider['uri'], dest_url=dest_url)
                return self.redirect(login_url)
            except users.NotAllowedError:
                message = 'You must enable Federated Login Before for this application.<br> <a href="http://appengine.google.com" target="_blank">Google App Engine Control Panel</a> -> Administration -> Application Settings -> Authentication Options'
                self.components.flash_messages.flash(message, 'danger')
                return self.redirect_to('user:login')

        else:
            message = '%s authentication is not yet implemented.' % provider.get('label')
            self.components.flash_messages.flash(message, 'warning')
            return self.redirect_to('user:login')


    @route_with('/social-login/<provider_name>/complete')
    def social_login_complete(self, provider_name):
        """
        Callback (Save Information) for Social Authentication
        """
        if not settings.get('enable_federated_login'):
            message = 'Federated login is disabled.'
            self.components.flash_messages.flash(message, 'warning')
            return self.redirect_to('user:login')
        continue_url = self.request.get('continue_url')
        if provider_name == "twitter":
            oauth_token = self.request.get('oauth_token')
            oauth_verifier = self.request.get('oauth_verifier')
            twitter_helper = twitter.TwitterAuth(self)
            user_data = twitter_helper.auth_complete(oauth_token,
                                                     oauth_verifier)
            logging.info('twitter user_data: ' + str(user_data))
            if self.user():
                # new association with twitter
                user_info = models.User.get_by_id(long(self.user_id()))
                if models.SocialUser.check_unique(user_info.key, 'twitter', str(user_data['user_id'])):
                    social_user = models.SocialUser(
                        user=user_info.key,
                        provider='twitter',
                        uid=str(user_data['user_id']),
                        extra_data=user_data
                    )
                    social_user.put()

                    message = 'Twitter association added.'
                    self.components.flash_messages.flash(message, 'success')
                else:
                    message = 'This Twitter account is already in use.'
                    self.components.flash_messages.flash(message, 'danger')
                if continue_url:
                    return self.redirect(continue_url)
                else:
                    return self.redirect_to('user:edit')
            else:
                # login with twitter
                social_user = models.SocialUser.get_by_provider_and_uid('twitter', str(user_data['user_id']))
                if social_user:
                    # Social user exists. Need authenticate related site account
                    user = social_user.user.get()
                    self.auth().set_session(self.auth().store.user_to_dict(user), remember=True)
                    if settings.get('log_visit'):
                        try:
                            logVisit = models.LogVisit(
                                user=user.key,
                                uastring=self.request.user_agent,
                                ip=self.request.remote_addr,
                                timestamp=utils.get_date_time()
                            )
                            logVisit.put()
                        except (apiproxy_errors.OverQuotaError, BadValueError):
                            logging.error('Error saving Visit Log in datastore')
                    if continue_url:
                        return self.redirect(continue_url)
                    else:
                        return self.redirect('/')
                else:
                    uid = str(user_data['user_id'])
                    email = str(user_data.get('email'))
                    return self.create_account_from_social_provider(provider_name, uid, email, continue_url, user_data)

        # github association
        elif provider_name == "github":
            # get our request code back from the social login handler above
            code = self.request.get('code')

            # create our github auth object
            scope = 'gist'
            github_helper = github.GithubAuth(settings.get('github_server'),
                                              settings.get('github_client_id'), \
                                              settings.get('github_client_secret'),
                                              settings.get('github_redirect_uri'), scope)

            # retrieve the access token using the code and auth object
            access_token = github_helper.get_access_token(code)
            user_data = github_helper.get_user_info(access_token)
            logging.info('github user_data: ' + str(user_data))
            if self.user():
                # user is already logged in so we set a new association with twitter
                user_info = models.User.get_by_id(long(self.user_id()))
                if models.SocialUser.check_unique(user_info.key, 'github', str(user_data['login'])):
                    social_user = models.SocialUser(
                        user=user_info.key,
                        provider='github',
                        uid=str(user_data['login']),
                        extra_data=user_data
                    )
                    social_user.put()

                    message = 'Github association added.'
                    self.components.flash_messages.flash(message, 'success')
                else:
                    message = 'This Github account is already in use.'
                    self.components.flash_messages.flash(message, 'danger')
                return self.redirect_to('user:edit')
            else:
                # user is not logged in, but is trying to log in via github
                social_user = models.SocialUser.get_by_provider_and_uid('github', str(user_data['login']))
                if social_user:
                    # Social user exists. Need authenticate related site account
                    user = social_user.user.get()
                    self.auth().set_session(self.auth().store.user_to_dict(user), remember=True)
                    if settings.get('log_visit'):
                        try:
                            logVisit = models.LogVisit(
                                user=user.key,
                                uastring=self.request.user_agent,
                                ip=self.request.remote_addr,
                                timestamp=utils.get_date_time()
                            )
                            logVisit.put()
                        except (apiproxy_errors.OverQuotaError, BadValueError):
                            logging.error("Error saving Visit Log in datastore")
                    return self.redirect('/')
                else:
                    uid = str(user_data['id'])
                    email = str(user_data.get('email'))
                    return self.create_account_from_social_provider(provider_name, uid, email, continue_url, user_data)
        #end github

        # facebook association
        elif provider_name == "facebook":
            code = self.request.get('code')
            callback_url = self.uri('user:social_login_complete', provider_name=provider_name, _full=True)
            token = facebook.get_access_token_from_code(code, callback_url, settings.get('fb_api_key'), settings.get('fb_secret'))
            access_token = token['access_token']
            fb = facebook.GraphAPI(access_token)
            user_data = fb.get_object('me')
            logging.info('facebook user_data: ' + str(user_data))
            if self.user():
                # new association with facebook
                user_info = models.User.get_by_id(long(self.user_id()))
                if models.SocialUser.check_unique(user_info.key, 'facebook', str(user_data['id'])):
                    social_user = models.SocialUser(
                        user=user_info.key,
                        provider='facebook',
                        uid=str(user_data['id']),
                        extra_data=user_data
                    )
                    social_user.put()

                    message = 'Facebook association added!'
                    self.components.flash_messages.flash(message, 'success')
                else:
                    message = 'This Facebook account is already in use!'
                    self.components.flash_messages.flash(message, 'danger')
                if continue_url:
                    return self.redirect(continue_url)
                else:
                    return self.redirect_to('user:edit')
            else:
                # login with Facebook
                social_user = models.SocialUser.get_by_provider_and_uid('facebook', str(user_data['id']))
                if social_user:
                    # Social user exists. Need authenticate related site account
                    user = social_user.user.get()
                    self.auth().set_session(self.auth().store.user_to_dict(user), remember=True)
                    if settings.get('log_visit'):
                        try:
                            logVisit = models.LogVisit(
                                user=user.key,
                                uastring=self.request.user_agent,
                                ip=self.request.remote_addr,
                                timestamp=utils.get_date_time()
                            )
                            logVisit.put()
                        except (apiproxy_errors.OverQuotaError, BadValueError):
                            logging.error("Error saving Visit Log in datastore")
                    if continue_url:
                        return self.redirect(continue_url)
                    else:
                        return self.redirect('/')
                else:
                    uid = str(user_data['id'])
                    email = str(user_data.get('email'))
                    return self.create_account_from_social_provider(provider_name, uid, email, continue_url, user_data)

                    # end facebook
        # association with linkedin
        elif provider_name == "linkedin":
            callback_url = self.uri('user:social_login_complete', provider_name=provider_name, _full=True)
            authentication = linkedin.LinkedInAuthentication(
                settings.get('linkedin_api'),
                settings.get('linkedin_secret'),
                callback_url,
                [linkedin.PERMISSIONS.BASIC_PROFILE, linkedin.PERMISSIONS.EMAIL_ADDRESS])
            authentication.authorization_code = self.request.get('code')
            access_token = authentication.get_access_token()
            link = linkedin.LinkedInApplication(authentication)
            u_data = link.get_profile(selectors=['id', 'first-name', 'last-name', 'email-address'])
            user_data = {
                'first_name': u_data.get('firstName'),
                'last_name': u_data.get('lastName'),
                'id': u_data.get('id'),
                'email': u_data.get('emailAddress')}
            self.session['linkedin'] = json.dumps(user_data)
            logging.info('linkedin user_data: ' + str(user_data))

            if self.user():
                # new association with linkedin
                user_info = models.User.get_by_id(long(self.user_id()))
                if models.SocialUser.check_unique(user_info.key, 'linkedin', str(user_data['id'])):
                    social_user = models.SocialUser(
                        user=user_info.key,
                        provider='linkedin',
                        uid=str(user_data['id']),
                        extra_data=user_data
                    )
                    social_user.put()

                    message = 'Linkedin association added!'
                    self.components.flash_messages.flash(message, 'success')
                else:
                    message = 'This Linkedin account is already in use!'
                    self.components.flash_messages.flash(message, 'danger')
                if continue_url:
                    return self.redirect(continue_url)
                else:
                    return self.redirect_to('user:edit')
            else:
                # login with Linkedin
                social_user = models.SocialUser.get_by_provider_and_uid('linkedin', str(user_data['id']))
                if social_user:
                    # Social user exists. Need authenticate related site account
                    user = social_user.user.get()
                    self.auth().set_session(self.auth().store.user_to_dict(user), remember=True)
                    if settings.get('log_visit'):
                        try:
                            logVisit = models.LogVisit(
                                user=user.key,
                                uastring=self.request.user_agent,
                                ip=self.request.remote_addr,
                                timestamp=utils.get_date_time()
                            )
                            logVisit.put()
                        except (apiproxy_errors.OverQuotaError, BadValueError):
                            logging.error("Error saving Visit Log in datastore")
                    if continue_url:
                        return self.redirect(continue_url)
                    else:
                        return self.redirect('/')
                else:
                    uid = str(user_data['id'])
                    email = str(user_data.get('email'))
                    return self.create_account_from_social_provider(provider_name, uid, email, continue_url, user_data)

                    #end linkedin

        # google, myopenid, yahoo OpenID Providers
        elif provider_name in settings.get('social_providers'):
            provider_display_name = settings.get('social_providers').get(provider_name).get('label')
            # get info passed from OpenID Provider
            from google.appengine.api import users

            current_user = users.get_current_user()
            if current_user:
                if current_user.federated_identity():
                    uid = current_user.federated_identity()
                else:
                    uid = current_user.user_id()
                email = current_user.email()
            else:
                message = 'No user authentication information received from %s. Please ensure you are logging in from an authorized OpenID Provider (OP).' % provider_display_name
                self.components.flash_messages.flash(message, 'danger')
                return self.redirect_to('user:login', continue_url=continue_url) if continue_url else self.redirect_to(
                    'user:login')
            if self.user():
                # add social account to user
                user_info = models.User.get_by_id(long(self.user_id()))
                if models.SocialUser.check_unique(user_info.key, provider_name, uid):
                    social_user = models.SocialUser(
                        user=user_info.key,
                        provider=provider_name,
                        uid=uid
                    )
                    social_user.put()

                    message = '%s association successfully added.' % provider_display_name
                    self.components.flash_messages.flash(message, 'success')
                else:
                    message = 'This %s account is already in use.' % provider_display_name
                    self.components.flash_messages.flash(message, 'danger')
                if continue_url:
                    return self.redirect(continue_url)
                else:
                    return self.redirect_to('user:edit')
            else:
                # login with OpenID Provider
                social_user = models.SocialUser.get_by_provider_and_uid(provider_name, uid)
                if social_user:
                    # Social user found. Authenticate the user
                    user = social_user.user.get()
                    self.auth().set_session(self.auth().store.user_to_dict(user), remember=True)
                    if settings.get('log_visit'):
                        try:
                            logVisit = models.LogVisit(
                                user=user.key,
                                uastring=self.request.user_agent,
                                ip=self.request.remote_addr,
                                timestamp=utils.get_date_time()
                            )
                            logVisit.put()
                        except (apiproxy_errors.OverQuotaError, BadValueError):
                            logging.error("Error saving Visit Log in datastore")
                    if continue_url:
                        return self.redirect(continue_url)
                    else:
                        return self.redirect('/')
                else:
                    return self.create_account_from_social_provider(provider_name, uid, email, continue_url)
        else:
            message = 'This authentication method is not yet implemented.'
            self.components.flash_messages.flash(message, 'warning')
            return self.redirect_to('user:login', continue_url=continue_url) if continue_url else self.redirect_to('user:login')


    def create_account_from_social_provider(self, provider_name, uid, email=None, continue_url=None, user_data=None):
        """Social user does not exist yet so create it with the federated identity provided (uid)
        and create prerequisite user and log the user account in
        """
        provider_display_name = settings.get('social_providers').get(provider_name).get('label')
        if models.SocialUser.check_unique_uid(provider_name, uid):
            # create user
            # Returns a tuple, where first value is BOOL.
            # If True ok, If False no new user is created
            # Assume provider has already verified email address
            # if email is provided so set activated to True
            auth_id = "%s:%s" % (provider_name, uid)

            # Extract any user data
            kwargs = {}
            kwargs['activated'] = True
            if email:
                kwargs['email'] = email
                kwargs['unique_properties'] = ['email']
            if user_data:
                if 'first_name' in user_data:
                    kwargs['first_name'] = user_data['first_name']
                if 'last_name' in user_data:
                    kwargs['last_name'] = user_data['last_name']

            # Create the user
            user_info = self.auth().store.user_model.create_user(
                    auth_id, **kwargs
                )

            if not user_info[0]: #user is a tuple
                message = 'The account %s is already in use.' % provider_display_name
                self.components.flash_messages.flash(message, 'danger')
                return self.redirect_to('user:register')

            user = user_info[1]

            # create social user and associate with user
            social_user = models.SocialUser(
                user=user.key,
                provider=provider_name,
                uid=uid,
            )
            if user_data:
                social_user.extra_data = user_data
                self.session[provider_name] = json.dumps(user_data) # TODO is this needed?
            social_user.put()
            # authenticate user
            self.auth().set_session(self.auth().store.user_to_dict(user), remember=True)
            if settings.get('log_visit'):
                try:
                    logVisit = models.LogVisit(
                        user=user.key,
                        uastring=self.request.user_agent,
                        ip=self.request.remote_addr,
                        timestamp=utils.get_date_time()
                    )
                    logVisit.put()
                except (apiproxy_errors.OverQuotaError, BadValueError):
                    logging.error("Error saving Visit Log in datastore")

            message = 'Welcome!  You have been registered as a new user and logged in through {}.'.format(provider_display_name)
            self.components.flash_messages.flash(message, 'success')
        else:
            message = 'This %s account is already in use.' % provider_display_name
            self.components.flash_messages.flash(message, 'danger')
        if continue_url:
            return self.redirect(continue_url)
        else:
            return self.redirect_to('user:edit')

    @route
    @add_authorizations(custom_auth.require_user)
    def edit(self):
        user = self.user()
        parser = self.parse_request(container=EditProfileForm, fallback=user)
        providers_info = user.get_social_providers_info()
        self.context['used_providers'] = providers_info['used']
        self.context['unused_providers'] = providers_info['unused']
        self.context['user'] = user
        self.context['form'] = parser.container
        self.context['local_account'] = user.password != None
        if self.request.method == "POST":

            # validate the form
            if not parser.validate():
                return

            parser.update(self.user())
            self.user().put()

            self.components.flash_messages.flash('Thanks, your profile has been saved!', 'success')
            return

        elif self.request.method == "GET":
            return


    @route
    @add_authorizations(custom_auth.require_user)
    def edit_password(self):
        parser = self.parse_request(container=EditPasswordForm)
        if self.request.method == "POST":

            # validate the form
            if not parser.validate():
                self.context['form'] = parser.container
                return

            old_password = parser.container.old_password.data.strip()
            new_password = parser.container.new_password.data.strip()

            try:
                user_info = self.user()
                auth_id = "email:%s" % user_info.email

                # Password to SHA512
                old_password = utils.hashing(old_password, settings.get('salt'))

                try:
                    user = models.User.get_by_auth_password(auth_id, old_password)
                    # Password to SHA512
                    new_password = utils.hashing(new_password, settings.get('salt'))
                    user.password = security.generate_password_hash(new_password, length=12)
                    user.put()

                    # send email
                    subject = settings.get('app_name') + " Account Password Changed"

                    mail.send_template(
                        recipient=user.email,
                        subject=subject,
                        template_name='password_changed',
                        context={
                            "app_name": settings.get('app_name'),
                            "full_name": user.full_name,
                            "email": user.email,
                            "reset_password_url": self.uri_for("user:reset_password", _full=True),
                        }
                    )

                    #Login User
                    self.auth().get_user_by_password(user.auth_ids[0], new_password)
                    self.components.flash_messages.flash('Password changed successfully.', 'success')
                    return self.redirect_to('user:edit')
                except (InvalidAuthIdError, InvalidPasswordError), e:
                    # Returns error message to self.response.write in
                    # the BaseHandler.dispatcher
                    message = "Incorrect password! Please enter your current password to change your account settings."
                    self.components.flash_messages.flash(message, 'danger')
                    return self.redirect_to('user:edit_password')
            except (AttributeError, TypeError), e:
                login_error_message = 'Your session has expired.'
                self.components.flash_messages.flash(login_error_message, 'danger')
                return self.redirect_to('user:login')

        elif self.request.method == "GET":
            self.context['form'] = parser.container
            return


    @route
    @add_authorizations(custom_auth.require_user)
    def edit_email(self):
        parser = self.parse_request(container=EditEmailForm)
        if self.request.method == "POST":

            # validate the form
            if not parser.validate():
                self.context['form'] = parser.container
                self.context['user'] = self.user()
                return

            new_email = parser.container.new_email.data.strip()
            password = parser.container.password.data.strip()

            try:
                user_info = models.User.get_by_id(long(self.user_id()))
                auth_id = "email:%s" % user_info.email
                # Password to SHA512
                password = utils.hashing(password, settings.get('salt'))

                try:
                    # authenticate user by its password
                    user = models.User.get_by_auth_password(auth_id, password)

                    # if the user change his/her email address
                    if new_email != user.email:

                        # check whether the new email has been used by another user
                        aUser = models.User.get_by_email(new_email)
                        if aUser is not None:
                            message = "The email %s is already registered." % new_email
                            self.components.flash_messages.flash(message, 'danger')
                            return self.redirect_to("user:edit_email")

                        # send email
                        subject = "%s Email Changed Notification" % settings.get('app_name')
                        user_token = models.User.create_auth_token(self.user_id())
                        confirmation_url = self.uri_for(
                            "user:change_email_complete",
                            user_id=user_info.get_id(),
                            encoded_email=utils.encode(new_email),
                            token=user_token,
                            _full=True)

                        context = {
                            "app_name": settings.get('app_name'),
                            "full_name": user.full_name,
                            "email": user.email,
                            "new_email": new_email,
                            "confirmation_url": confirmation_url,
                            "support_url": "#" #self.uri_for("contact", _full=True)
                        }

                        mail.send_template(
                            recipient=user.email,
                            subject=subject,
                            template_name='email_changed_notification_old',
                            context=context
                        )

                        mail.send_template(
                            recipient=new_email,
                            subject=subject,
                            template_name='email_changed_notification_new',
                            context=context
                        )

                        logging.info('confirmation_url: %s' % confirmation_url)

                        # display successful message
                        msg = "Please check your new email for confirmation. Your email will be updated after confirmation."
                        self.components.flash_messages.flash(msg, 'success')
                        return self.redirect_to('user:edit')

                    else:
                        self.components.flash_messages.flash('You didn''t change your email', 'warning')
                        return self.redirect_to("user:edit_email")

                except (InvalidAuthIdError, InvalidPasswordError), e:
                    # Returns error message to self.response.write in
                    # the BaseHandler.dispatcher
                    message = "Incorrect password! Please enter your current password to change your account settings."
                    self.components.flash_messages.flash(message, 'danger')
                    return self.redirect_to('user:edit_email')

            except (AttributeError, TypeError), e:
                login_error_message = 'Your session has expired.'
                self.components.flash_messages.flash(login_error_message, 'danger')
                return self.redirect_to('user:login')

        elif self.request.method == "GET":
            self.context['form'] = parser.container
            self.context['user'] = self.user()
            return

    @route
    def change_email_complete(self, user_id, encoded_email, token):
        """
        Handler for completed email change
        Will be called when the user click confirmation link from email
        """
        verify = models.User.get_by_auth_token(int(user_id), token)
        email = utils.decode(encoded_email)
        if verify[0] is None:
            message = 'The URL you tried to use is either incorrect or no longer valid.'
            self.components.flash_messages.flash(message, 'warning')
            return self.redirect('/')

        else:
            # save new email
            user = verify[0]

            # update username if it has changed and it isn't already taken
            uniques = [
                'User.auth_id:email:%s' % email,
                'User.email:%s' % email,
            ]

            # Create the unique username and auth_id.
            success, existing = Unique.create_multi(uniques)
            if success:
                # free old uniques
                Unique.delete_multi(
                  ['User.auth_id:email:%s' % user.email,
                   'User.email:%s' % user.email])
                # The unique values were created, so we can save the user.
            else:
                message = 'The email <strong>{}</strong> is already taken. Please choose another.'.format(email)
                # At least one of the values is not unique.
                self.components.flash_messages.flash(message, 'danger')
                return self.redirect('/')

            # save new email
            user.email = email
            user.auth_ids[0] = "email:%s" % email
            user.put()

            # delete token
            models.User.delete_auth_token(int(user_id), token)

            # add successful message and redirect
            message = 'Your email has been successfully updated.'
            self.components.flash_messages.flash(message, 'success')
            return self.redirect_to('user:edit')


    @route
    @add_authorizations(recaptcha.require_captcha_for_post)
    def reset_password(self):

        if self.request.method == 'POST':

            #check if we got an email or username
            email = str(self.request.POST.get('email')).lower().strip()
            if utils.is_email_valid(email):
                user = models.User.get_by_email(email)
                message = "If the email address you entered" + " (<strong>%s</strong>) " % email
            else:
                auth_id = "own:%s" % email
                user = models.User.get_by_auth_id(auth_id)
                message = "If the username you entered" + " (<strong>%s</strong>) " % email

            contact_uri = "#"
            message = message + 'is associated with an account in our records, you will receive an email from us with instructions for resetting your password. <br>If you don''t receive instructions within a minute or two, check your email''s spam and junk filters, or <a href="' + contact_uri + '">' + 'contact us' + '</a> ' + 'for further assistance.'

            if user is not None:
                user_id = user.get_id()
                token = models.User.create_auth_token(user_id)

                reset_url = self.uri_for('user:reset_password_complete', user_id=user_id, token=token, _full=True)
                subject = "%s Password Assistance" % settings.get('app_name')

                mail.send_template(
                    recipient=user.email,
                    subject=subject,
                    template_name='reset_password',
                    context={
                        'full_name': user.full_name,
                        'email': user.email,
                        'reset_password_url': reset_url,
                        'support_url': contact_uri,
                        'app_name': settings.get('app_name')
                    }
                )

                logging.info('reset_password_url: %s' % reset_url)

            self.components.flash_messages.flash(message, 'warning')
            return self.redirect_to('user:login')

        elif self.request.method == 'GET':
            return


    @route
    def reset_password_complete(self, user_id, token):
        parser = self.parse_request(container=ResetPasswordForm)
        self.context['form'] = parser.container
        if self.request.method == 'POST':
            verify = models.User.get_by_auth_token(int(user_id), token)
            user = verify[0]
            password = parser.container.password.data.strip()
            if user and parser.validate():
                # Password to SHA512
                password = utils.hashing(password, settings.get('salt'))

                user.password = security.generate_password_hash(password, length=12)
                user.put()
                # Delete token
                models.User.delete_auth_token(int(user_id), token)
                # Login User
                self.auth().get_user_by_password(user.auth_ids[0], password)
                self.components.flash_messages.flash('Password changed successfully.', 'success')
                return self.redirect('/')

            else:
                self.components.flash_messages.flash('The two passwords must match.', 'danger')
                return
            return
        elif self.request.method == 'GET':

            verify = models.User.get_by_auth_token(int(user_id), token)
            params = {}
            if verify[0] is None:
                message = 'The URL you tried to use is either incorrect or no longer valid. Enter your details again below to get a new one.'
                self.components.flash_messages.flash(message, 'warning')
                return self.redirect_to('user:reset_password')

            else:
                return


    @route
    @add_authorizations(custom_auth.require_user)
    def remove_social_login(self, provider_name):
        user = self.user()
        if len(user.get_social_providers_info()['used']) > 1:
            social_user = models.SocialUser.get_by_user_and_provider(user.key, provider_name)
            if social_user:
                social_user.key.delete()
                message = '%s successfully disassociated.' % provider_name
                self.components.flash_messages.flash(message, 'success')
            else:
                message = 'Social account on %s not found for this user.' % provider_name
                self.components.flash_messages.flash(message, 'danger')
        else:
            message = 'Social account on %s cannot be deleted for user. Please create a username and password to delete social account.' % provider_name
            self.components.flash_messages.flash(message, 'danger')
        return self.redirect_to('user:edit')
