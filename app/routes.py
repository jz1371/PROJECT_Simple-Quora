from ferris.core import routing
from ferris.core import plugins

# Routes all App handlers
routing.auto_route()

# Default root route
# routing.default_root()
routing.redirect('/', to='/questions')
# routing.redirect('/', to='/index')


# Plugins
plugins.enable('settings')
plugins.enable('oauth_manager')
plugins.enable('custom_auth')
plugins.enable('recaptcha')
