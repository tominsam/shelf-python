from Provider import *
from urllib import quote
from Utilities import *

import time

class BasicAtom( ProviderAtom ):

    def sortOrder(self):
        return MAX_SORT_ORDER
        
    def content(self):
        clue = self.provider.clue
        content = ""

        if clue.emails():
            content += "<p>"
            for email in clue.emails():
                content += "<a href='mailto:%s'>%s</a> "%( email, email )
            content += "</p>"

        if clue.birthday():
            content += "<p>Born %s</p>"%time.strftime("%B %d, %Y", clue.birthday())

        addresses = clue.addresses()
        if len(addresses) > 0:
           address = addresses[0]
           bits = [ address[atom] for atom in filter(lambda a: a in address, ['Street', 'City', 'Zip']) ]
           joined = ", ".join(bits)
           if bits:
               content += '<p><a href="http://maps.google.com/maps?q=%s">%s</a></p>'%( quote(joined.encode("utf-8")), joined )

        if clue.ab_urls():
            content += "<p>" + "<br>".join(map(lambda url: "<a href='%s'>%s</a>"%(url, url), clue.ab_urls())) + "</p>"
        
        if not content:
            content = "<p>No address book information for %s</p>"%clue.forename()
        
        return content

class BasicProvider( Provider ):

    def atomClass(self):
        return BasicAtom

    def provide( self ):
        self.atoms = [ BasicAtom(self, "") ]
