from Provider import *
from urllib import quote
from Utilities import *

import time

class BasicProvider( Provider ):

    def content( self ):
        atoms = []
        
        emails = ["<a href='mailto:%s'>%s</a>"%( email, email ) for email in self.clue.emails()]
        if emails:
            atoms.append("<p>" + ", ".join(emails) + "</p>" )

        if self.clue.birthday():
            atoms.append("<p>Born %s</p>"%time.strftime("%B %d, %Y", self.clue.birthday()))

        addresses = self.clue.addresses()
        if len(addresses) > 0:
           address = addresses[0]
           bits = [ address[atom] for atom in filter(lambda a: a in address, ['Street', 'City', 'Zip']) ]
           joined = ", ".join(bits)
           if bits:
               atoms.append('<p><a href="http://maps.google.com/maps?q=%s">%s</a></p>'%( quote(joined.encode("utf-8")), joined ) )

        if self.clue.ab_urls():
            atoms.append("<p>" + "<br>".join(map(lambda url: "<a href='%s'>%s</a>"%(url, url), self.clue.ab_urls())) + "</p>")
        
        if not atoms:
            atoms.append("<p>No address book information for %s</p>"%self.clue.forename())
        
        return "".join(atoms)
    
