import objc
from AddressBook import *
import re
from time import time, gmtime

from Utilities import *
from Provider import *
from urllib import quote
import simplejson

class Clue(object):
    
    def __init__(self, person):
        self.person = person
        self.nsimage = None
        self.extra_urls = []
        self.cache = {}
        self.providers = []

    def setDelegate_(self, delegate):
        self.delegate = delegate
    
    def getInfo(self):
        for current in self.providers:
            current.stop()

        self.boring_urls = self.urls()
        self.providers = []
        for cls in Provider.providers():
            try:
                self.providers.append( cls( self ) )
            except:
                print("Failed to create provider %s for clue:"%cls)
                print(traceback.format_exc())

        # just in case any providers (basicprovider, I'm looking at you)
        # are done already
        self.delegate.setWebContent( self.content() )

    def getMoreUrls( self ):
        if not self.ab_urls(): return # no point
        api = "http://socialgraph.apis.google.com/lookup?pretty=1&fme=1"
        api += "&q=" + ",".join([ quote(url) for url in self.ab_urls() ])
        print_info("Social graph API call to " + api )
        Cache.getContentOfUrlAndCallback( self.gotSocialGraphData, api, timeout = 3600 * 12 ) # huge timeout here

    def gotSocialGraphData( self, raw, isStale ):
        data = simplejson.loads( raw )
        urls = data['nodes'].keys()
        all_extra_urls = self.extra_urls + urls
        dedupe = {}
        for url in all_extra_urls:
            dedupe[ normalize_url( url ) ] = url
        self.extra_urls = dedupe.values()
        
        # remove all the urls we already know about
        known_urls = [ normalize_url( url ) for url in self.ab_urls() ]
        for url in [ u for u in self.extra_urls ]: # cheap copy, as we're mutating the array
            if normalize_url( url ) in known_urls:
                self.extra_urls.remove(url)
        
        print_info("I have the AB urls '%s'"%(", ".join(self.ab_urls())))
        print_info("Google gave me the urls '%s'"%(", ".join(self.extra_urls)))

        self.getInfo() # TODO - this is a little too heavy for my liking.

    def providerUpdated_(self, provider):
        print_info("Update for %s from %s"%( self, provider ))
        if provider in self.providers:
            self.delegate.setWebContent( self.content() )
    
    def content(self):
        content = ""
        for provider in self.providers:
            content += provider.content()
        if not content:
            return "<p>thinking..</p>"
        return content
    
    def stop(self):
        for current in self.providers:
            current.stop()

    def __eq__(self, other):
        return self.uniqueId() == other.uniqueId()
    
    def __str__(self):
        return "<Clue: '%s'>"%self.displayName()
    
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
            if not self.nsimage:
                if self.isCompany():
                    self.nsimage = NSImage.imageNamed_("NSUserGroup")
                else:
                    self.nsimage = NSImage.imageNamed_("NSUser")
        return self.nsimage

    def forename(self):
        return self.person.valueForProperty_(kABFirstNameProperty)

    def surname(self):
        return self.person.valueForProperty_(kABLastNameProperty)

    def isCompany(self):
        return ( self.person.valueForProperty_(kABPersonFlags) or 0 ) & kABShowAsCompany
        
    def displayName(self):
        if self.isCompany():
            return self.person.valueForProperty_(kABOrganizationProperty)
        f = self.forename()
        s = self.surname()
        if s and f: return f + " " + s
        if s: return s
        if f: return f
        return ""

    def companyName(self):
        if self.isCompany(): return ""
        c = self.person.valueForProperty_(kABOrganizationProperty)
        if c: return c
        return ""

    def addresses(self):
        return self._multi_to_list( self.person.valueForProperty_(kABAddressProperty) )

    def emails(self):
        return self._multi_to_list( self.person.valueForProperty_(kABEmailProperty) )

    def ab_urls(self):
        return self._multi_to_list( self.person.valueForProperty_(kABURLsProperty) )
    
    def urls(self):
        return self.ab_urls() + self.extra_urls

    def email(self): 
        return self.emails()[0]
        
    def birthday(self):
        if self.person.valueForProperty_( kABBirthdayProperty ):
            return gmtime( self.person.valueForProperty_( kABBirthdayProperty ).timeIntervalSince1970() )
        return None


    def _multi_to_list(self, multi):
        if not multi: return []
        output = []
        for i in range(0, multi.count() ):
            output.append( multi.valueAtIndex_( i ) )
        return output
