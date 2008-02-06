from Provider import *
from urllib import quote
from Utilities import *

import time

class BasicProvider( Provider ):

    def provide( self ):
        self.atoms = []
        
        emails = ["<a href='mailto:%s'>%s</a>"%( email, email ) for email in self.person.emails()]
        if emails:
            self.atoms.append("<p>" + ", ".join(emails) + "</p>" )

        if self.person.birthday():
            self.atoms.append("<p>Born %s</p>"%time.strftime("%B %d", self.person.birthday()))

        addresses = self.person.addresses()
        if len(addresses) > 0:
           address = addresses[0]
           bits = [ address[atom] for atom in filter(lambda a: a in address, ['Street', 'City', 'Zip']) ]
           joined = ", ".join(bits)
           if bits:
               self.atoms.append('<p><a href="http://maps.google.com/maps?q=%s">%s</a></p>'%( quote(joined.encode("utf-8")), joined ) )

        if self.person.ab_urls():
            self.atoms.append("<p>" + "<br>".join(map(lambda url: "<a href='%s'>%s</a>"%(url, url), self.person.ab_urls())) + "</p>")
        
        if not self.atoms:
            self.atoms.append("<p>No address book information for %s</p>"%self.person.forename())
        
        self.changed()
