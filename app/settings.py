"""
This file is used to configure application settings.

Do not import this file directly.

You can use the settings API via:

    from ferris import settings

    mysettings = settings.get("mysettings")

The settings API will load the "settings" dictionary from this file. Anything else
will be ignored.

Optionally, you may enable the dynamic settings plugin at the bottom of this file.
"""

settings = {}

settings['timezone'] = {
    'local': 'US/Eastern'
}

settings['email'] = {
    # Configures what address is in the sender field by default.
#     'sender': 'jz1371@nyu.edu' 
    'sender': "service@quora-jz1371.appspotmail.com"
}

settings['app_config'] = {
    'webapp2_extras.sessions': {
        # WebApp2 encrypted cookie key
        # You can use a UUID generator like http://www.famkruithof.net/uuid/uuidgen
        'secret_key': '9a788030-837b-11e1-b0c4-0800200c9a66',
    }
}

settings['oauth2'] = {
    # OAuth2 Configuration should be generated from
    # the google cloud console (Credentials for Web Application)
    'client_id': '789864515729-pm3k5eva2qad6o6g9up34phc7smlr5o3.apps.googleusercontent.com',  # XXXXXXXXXXXXXXX.apps.googleusercontent.com',
    'client_secret': 'Eym5SX-9ZxrGHlCgjix6ZT--',
    'developer_key': None  # Optional
}

settings['oauth2_service_account'] = {
    # OAuth2 service account configuration should be generated
    # from the google cloud console (Service Account Credentials)
    'client_email': None,  # XXX@developer.gserviceaccount.com
    'private_key': None,  # Must be in PEM format
    'developer_key': None  # Optional
}

settings['upload'] = {
    # Whether to use Cloud Storage (default) or the blobstore to store uploaded files.
    'use_cloud_storage': True,
    # The Cloud Storage bucket to use. Leave as "None" to use the default GCS bucket.
    # See here for info: https://developers.google.com/appengine/docs/python/googlecloudstorageclient/activate#Using_the_Default_GCS_Bucket
    'bucket': None
}

# Enables or disables app stats.
# Note that appstats must also be enabled in app.yaml.
settings['appstats'] = {
    'enabled': False,
    'enabled_live': False
}


settings['captcha_public_key'] = "6LdhoAgTAAAAAOhR7RzSxNgQOeOPXWk7kx8I0cc5"
settings['captcha_private_key'] = "6LdhoAgTAAAAAKfVHoFjCJMOU3qyH_97oaYLVyJy"

# This gets used in emails
settings['app_name'] = 'Simple Quora'

settings['app_config'] = {
    'webapp2_extras.sessions': {
        # WebApp2 encrypted cookie key
        # You can use a UUID generator like http://www.famkruithof.net/uuid/uuidgen
        'secret_key': '_PUT_KEY_HERE_YOUR_SECRET_KEY_',
    },
    'webapp2_extras.auth': {
        'user_model': 'plugins.custom_auth.models.user.User',
        'user_attributes': ['email'],
    }
}

# Password AES Encryption Parameters
# aes_key must be only 16 (*AES-128*), 24 (*AES-192*), or 32 (*AES-256*) bytes (characters) long.
settings['aes_key'] = "12_24_32_BYTES_KEY_FOR_PASSWORDS"
settings['salt'] = "_PUT_SALT_HERE_TO_SHA512_PASSWORDS_"

# get your own consumer key and consumer secret by registering at https://dev.twitter.com/apps
# callback url must be: http://[YOUR DOMAIN]/login/twitter/complete
settings['twitter_consumer_key'] = 'TWITTER_CONSUMER_KEY'
settings['twitter_consumer_secret'] = 'TWITTER_CONSUMER_SECRET'

#Facebook Login
# get your own consumer key and consumer secret by registering at https://developers.facebook.com/apps
#Very Important: set the site_url= your domain in the application settings in the facebook app settings page
# callback url must be: http://[YOUR DOMAIN]/login/facebook/complete
settings['fb_api_key'] = '1592189004350323'
settings['fb_secret'] = '8e116b89a9c707068a777c3ab25d8ead'

#Linkedin Login
#Get you own api key and secret from https://www.linkedin.com/secure/developer
settings['linkedin_api'] = 'LINKEDIN_API'
settings['linkedin_secret'] = 'LINKEDIN_SECRET'

# Github login
# Register apps here: https://github.com/settings/applications/new
settings['github_server'] = 'github.com'
settings['github_redirect_uri'] = 'http://www.example.com/social_login/github/complete',
settings['github_client_id'] = 'GITHUB_CLIENT_ID'
settings['github_client_secret'] = 'GITHUB_CLIENT_SECRET'

# Enable Federated login (OpenID and OAuth)
# Google App Engine Settings must be set to Authentication Options: Federated Login
settings['enable_federated_login'] = True

# List of social login providers
# uri is for OpenID only (not OAuth)
settings['social_providers'] = { 
        'google': {'name': 'google', 'label': 'Google', 'uri': 'gmail.com'},
        'github': {'name': 'github', 'label': 'Github', 'uri': ''},
        'facebook': {'name': 'facebook', 'label': 'Facebook', 'uri': ''},
        'linkedin': {'name': 'linkedin', 'label': 'LinkedIn', 'uri': ''},
        #'myopenid': {'name': 'myopenid', 'label': 'MyOpenid', 'uri': 'myopenid.com'},
        'twitter': {'name': 'twitter', 'label': 'Twitter', 'uri': ''},
        'yahoo': {'name': 'yahoo', 'label': 'Yahoo!', 'uri': 'yahoo.com'},
    }

# If true, it will write in datastore a log of every email sent
settings['log_email'] = False

# If true, it will write in datastore a log of every visit
settings['log_visit'] = False 

# Optionally, you may use the settings plugin to dynamically
# configure your settings via the admin interface. Be sure to
# also enable the plugin via app/routes.py.

import plugins.settings

# import any additional dynamic settings classes here.
# import plugins.recaptcha.settings
import plugins.custom_auth.settings

# Un-comment to enable dynamic settings, (i.e.) able to edit from admin console
plugins.settings.activate(settings)
