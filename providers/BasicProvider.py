from Provider import *
from urllib import quote
from Utilities import *

import time

class BasicProvider( Provider ):

    def content( self ):
        content = ""
        
        if self.clue.emails():
            content += "<p>"
            for email in self.clue.emails():
                content += "<a href='mailto:%s'>%s</a> "%( email, email )
            content += "</p>"

        if self.clue.birthday():
            content += "<p>Born %s</p>"%time.strftime("%B %d, %Y", self.clue.birthday())

        addresses = self.clue.addresses()
        if len(addresses) > 0:
           address = addresses[0]
           bits = [ address[atom] for atom in filter(lambda a: a in address, ['Street', 'City', 'Zip']) ]
           joined = ", ".join(bits)
           if bits:
               content += '<p><a href="http://maps.google.com/maps?q=%s">%s</a></p>'%( quote(joined.encode("utf-8")), joined )

        if self.clue.ab_urls():
            content += "<p>" + "<br>".join(map(lambda url: "<a href='%s'>%s</a>"%(url, url), self.clue.ab_urls())) + "</p>"
        
        if not content:
            content = "<p>No address book information for %s</p>"%self.clue.forename()
        
        return content
    
