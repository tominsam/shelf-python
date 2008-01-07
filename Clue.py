import objc
from AddressBook import *

class Clue(object):
    
    def __init__(self, person):
        self.person = person
        self.nsimage = None
    
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
