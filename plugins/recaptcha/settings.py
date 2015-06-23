"""
Copy these settings to the bottom of app/settings.py
"""
from ferris import ndb
from plugins.settings import SettingsModel

# get your own recaptcha keys by registering at http://www.google.com/recaptcha/
settings['captcha_public_key'] = {"6LdhoAgTAAAAAOhR7RzSxNgQOeOPXWk7kx8I0cc5"}
settings['captcha_private_key'] = {"6LdhoAgTAAAAAKfVHoFjCJMOU3qyH_97oaYLVyJy"}