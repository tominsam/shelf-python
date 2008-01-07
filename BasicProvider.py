from Provider import *
from urllib import quote


class BasicProvider( Provider ):

    def about( self, person ):
        data = []
    
        emails = ["<a href='mailto:%s'>%s</a>"%( email, email ) for email in person.emails()]
        data.append("<p>" + ", ".join(emails) + "</p>" )

        addresses = person.addresses()
        if len(addresses) > 0:
           address = addresses[0]
           bits = [ address[atom] for atom in filter(lambda a: a in address, ['Street', 'City', 'Zip']) ]
           joined = ", ".join(bits)
           data.append('<p><a href="http://maps.google.com/maps?q=%s">%s</a></p>'%( quote(joined), joined ) )
    
        return data
            


Provider.PROVIDERS.append( BasicProvider() )