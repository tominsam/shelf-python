from Provider import *
from urllib import quote


class BasicProvider( Provider ):

    def about( self, person ):
        data = []
    
        emails = ["<a href='mailto:%s'>%s</a>"%( email, email ) for email in person.emails()]
        data.append("<p>" + ", ".join(emails) + "</p>" )

        addresses = person.addresses()
        if len(addresses) > 0:
           a = addresses[0]
           joined = ", ".join([ a['Street'], a['City'], a['ZIP'] ])
           data.append('<p><a href="http://maps.google.com/maps?q=%s">%s</a></p>'%( quote(joined), joined ) )
    
        return data
            


Provider.PROVIDERS.append( BasicProvider() )