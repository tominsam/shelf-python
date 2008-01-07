from Provider import *
from urllib import quote


class BasicProvider( Provider ):

    def provide( self ):
        self.atoms = []
        
        emails = ["<a href='mailto:%s'>%s</a>"%( email, email ) for email in self.person.emails()]
        if emails:
            self.atoms.append("<p>" + ", ".join(emails) + "</p>" )

        addresses = self.person.addresses()
        if len(addresses) > 0:
           address = addresses[0]
           bits = [ address[atom] for atom in filter(lambda a: a in address, ['Street', 'City', 'Zip']) ]
           joined = ", ".join(bits)
           if bits:
               self.atoms.append('<p><a href="http://maps.google.com/maps?q=%s">%s</a></p>'%( quote(joined), joined ) )

        if self.person.urls():
            self.atoms.append("<p>" + "<br>".join(map(lambda url: "<a href='%s'>%s</a>"%(url, url), self.person.urls())) + "</p>")
        
        self.changed()
    