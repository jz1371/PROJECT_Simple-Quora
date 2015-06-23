"""
Copy the contents of this file into the bottom of `app/settings.py`

Modify the settings as needed
"""
from ferris import ndb
from plugins.settings import SettingsModel

class SocialLogin(SettingsModel):
    _name = 'SocialLogin'
    _settings_key = 'oauth2'
    _description = """
    Control use of social login
    """
    enable_login = ndb.BooleanProperty(indexed=False, default=True)
    fb_api_key = ndb.StringProperty(indexed=False)
    fb_secret = ndb.StringProperty(indexed=False)


# # This gets used in emails
# settings['app_name'] = {'APP_NAME'}
# 
# settings['app_config'] = {
#     'webapp2_extras.sessions': {
#         # WebApp2 encrypted cookie key
#         # You can use a UUID generator like http://www.famkruithof.net/uuid/uuidgen
#         'secret_key': '_PUT_KEY_HERE_YOUR_SECRET_KEY_',
#     },
#     'webapp2_extras.auth': {
#         'user_model': 'plugins.custom_auth.models.user.User',
#         'user_attributes': ['email'],
#     }
# }
# 
# # Password AES Encryption Parameters
# # aes_key must be only 16 (*AES-128*), 24 (*AES-192*), or 32 (*AES-256*) bytes (characters) long.
# settings['aes_key'] = "12_24_32_BYTES_KEY_FOR_PASSWORDS"
# settings['salt'] = "_PUT_SALT_HERE_TO_SHA512_PASSWORDS_"
# 
# # get your own consumer key and consumer secret by registering at https://dev.twitter.com/apps
# # callback url must be: http://[YOUR DOMAIN]/login/twitter/complete
# settings['twitter_consumer_key'] = 'TWITTER_CONSUMER_KEY'
# settings['twitter_consumer_secret'] = 'TWITTER_CONSUMER_SECRET'
# 
# #Facebook Login
# # get your own consumer key and consumer secret by registering at https://developers.facebook.com/apps
# #Very Important: set the site_url= your domain in the application settings in the facebook app settings page
# # callback url must be: http://[YOUR DOMAIN]/login/facebook/complete
# settings['fb_api_key'] = 'FACEBOOK_API_KEY'
# settings['fb_secret'] = 'FACEBOOK_SECRET'
# 
# #Linkedin Login
# #Get you own api key and secret from https://www.linkedin.com/secure/developer
# settings['linkedin_api'] = 'LINKEDIN_API'
# settings['linkedin_secret'] = 'LINKEDIN_SECRET'
# 
# # Github login
# # Register apps here: https://github.com/settings/applications/new
# settings['github_server'] = 'github.com'
# settings['github_redirect_uri'] = 'http://www.example.com/social_login/github/complete',
# settings['github_client_id'] = 'GITHUB_CLIENT_ID'
# settings['github_client_secret'] = 'GITHUB_CLIENT_SECRET'
# 
# # Enable Federated login (OpenID and OAuth)
# # Google App Engine Settings must be set to Authentication Options: Federated Login
# settings['enable_federated_login'] = True
# 
# # List of social login providers
# # uri is for OpenID only (not OAuth)
# settings['social_providers'] = { 
#         'google': {'name': 'google', 'label': 'Google', 'uri': 'gmail.com'},
#         'github': {'name': 'github', 'label': 'Github', 'uri': ''},
#         'facebook': {'name': 'facebook', 'label': 'Facebook', 'uri': ''},
#         'linkedin': {'name': 'linkedin', 'label': 'LinkedIn', 'uri': ''},
#         #'myopenid': {'name': 'myopenid', 'label': 'MyOpenid', 'uri': 'myopenid.com'},
#         'twitter': {'name': 'twitter', 'label': 'Twitter', 'uri': ''},
#         'yahoo': {'name': 'yahoo', 'label': 'Yahoo!', 'uri': 'yahoo.com'},
#     }
# 
# # If true, it will write in datastore a log of every email sent
# settings['log_email'] = False
# 
# # If true, it will write in datastore a log of every visit
# settings['log_visit'] = False