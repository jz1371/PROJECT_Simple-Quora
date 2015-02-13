'''
Created on Feb 11, 2015

@author: Jingxin Zhu 
'''

# import route from ferris to route to custom action 
from ferris import Controller, route


class Hello(Controller):

#     def list(self):
#         return "Hello, is it me you're looking for?"

    def list(self):
        self.context['who'] = self.request.params['name']

    # respondint to page controller/action, i.e.
    #@route
    # ~/hello/custom
#     def custom(self):
#         return "Something, indeed."

    # route for hello/custom/text
    @route
    def custom(self, text):
        return "%s, indeed." % text
    
    # route for hello/custom/text/persion
#    @route
#     def custom(self, text, person):
#         return "%s, %s, indeed." % (text, person)