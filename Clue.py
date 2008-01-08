import objc
from AddressBook import *
import re

class Clue(object):
    
    def __init__(self, person):
        self.person = person
        self.nsimage = None
        self.boring_urls = self.urls()
        self.cache = {}
    
    def takeUrls(self,pattern):
        interesting = []
        for u in self.urls():
            if re.search(pattern, u):
                interesting.append(u)
        for u in interesting:
            if u in self.boring_urls:
                self.boring_urls.remove(u)
        return interesting
    
    def uniqueId(self):
        return self.person.uniqueId()
        
    def image(self):
        if not self.nsimage:
            self.nsimage = NSImage.alloc().initWithData_( self.person.imageData() )
        return self.nsimage

    def forename(self):
        return self.person.valueForProperty_(kABFirstNameProperty)

    def surname(self):
        return self.person.valueForProperty_(kABLastNameProperty)

    def displayName(self):
        f = self.forename()
        s = self.surname()
        if s and f: return f + " " + s
        if s: return s
        if f: return f
        return ""

    def companyName(self):
        c = self.person.valueForProperty_(kABOrganizationProperty)
        if c: return c
        return ""

    def addresses(self):
        return self._multi_to_list( self.person.valueForProperty_(kABAddressProperty) )

    def emails(self):
        return self._multi_to_list( self.person.valueForProperty_(kABEmailProperty) )

    def urls(self):
        return self._multi_to_list( self.person.valueForProperty_(kABURLsProperty) )

    def email(self): 
        return self.emails()[0]

        


    def _multi_to_list(self, multi):
        if not multi: return []
        output = []
        for i in range(0, multi.count() ):
            output.append( multi.valueAtIndex_( i ) )
        return output
