import objc
from AddressBook import *

# this _could_ be described as.. evil. Yes, it could. We're stuffing our
# own methods into the ABPerson class because I'm lazy. I loooove Objective C.
def swizzleAB( name ):
    return lambda method: objc.classAddMethod( ABPerson, name, method )



@swizzleAB("forename")
def forename(self):
    return self.valueForProperty_(kABFirstNameProperty)


@swizzleAB("surname")
def surname(self):
    return self.valueForProperty_(kABLastNameProperty)


@swizzleAB( 'displayName' )
def displayName(self):
    f = self.forename()
    s = self.surname()
    if s and f: return f + " " + s
    if s: return s
    if f: return f
    return ""


@swizzleAB( 'companyName' )
def companyName(self):
    c = self.valueForProperty_(kABOrganizationProperty)
    if c: return c
    return ""

def multi_to_list( multi ):
    if not multi: return []
    output = []
    for i in range(0, multi.count() ):
        output.append( multi.valueAtIndex_( i ) )
    return output


@swizzleAB("addresses")
def emails(self):
    return multi_to_list( self.valueForProperty_(kABAddressProperty) )

@swizzleAB("emails")
def emails(self):
    return multi_to_list( self.valueForProperty_(kABEmailProperty) )

@swizzleAB('email')
def email(self): 
    return self.emails()[0]

@swizzleAB("urls")
def emails(self):
    return multi_to_list( self.valueForProperty_(kABURLsProperty) )

