from ferris.core import routing, plugins

# Routes all App handlers
routing.auto_route()

# Default root route
# routing.default_root()
routing.redirect('/', to='/questions')


# Plugins
#plugins.enable('settings')
#plugins.enable('oauth_manager')