import objc
from AddressBook import *

import re
from time import time, gmtime
from urllib import quote
import json

from Utilities import *

from Provider import *

Provider.addProvider( "BasicProvider" )
Provider.addProvider( "SpotlightProvider" )
Provider.addProvider( "TwitterProvider" )
Provider.addProvider( "DopplrProvider" )
Provider.addProvider( "LastFmProvider" )
Provider.addProvider( "FlickrProvider" )
# Order is important - FeedProvider must be _last_, because it uses all
# urls in the address book card not claimed by another provider
Provider.addProvider( "FeedProvider" )


class Clue(object):
    
    # Make Clue objects singletons - one Person in the address book, one Clue.
    # This way clues can retain their local providers and content, so a clue
    # you've seen before will display more quickly.
    CACHE = {}
    @classmethod
    def forPerson( cls, person ):
        if person.uniqueId() in Clue.CACHE:
            print_info("person is cached")
            return Clue.CACHE[ person.uniqueId() ]
        print_info("creating new person")
        Clue.CACHE[ person.uniqueId() ] = Clue( person )
        return Clue.CACHE[ person.uniqueId() ]
    
    # sometimes, google will suggest a page for a person because I have
    # page A, that lnks to page B, that links to page C. Shelf suggests
    # page C as a page for this person. When I visit page C, Google will only
    # tell me about page B, and I won't be able to tie it back to that person.
    # To work around this, I'll just remember every url I get for a person.
    @classmethod
    def forUrl( cls, url ):
        for clue in Clue.CACHE.values():
            if normalize_url( url) in [ normalize_url(u) for u in clue.urls() ]:
                return clue

    def __init__(self, person):
        # for now, clues are tied to AddressBook person objects.
        # But nothing outside the Clue object knows this - names, etc are
        # all extractd from the Clue object using methods on the Clue, not
        # on the ABPerson.
        # Clues are constructed using Clue.forPerson() from everywhere. Eventually
        # I'd like clues to be a little more flexible.
        self.person = person
        self.delegate = None
        self.extra_urls = [] # Urls from google social

        # on the first inflate of this person, ask google for more urls.
        if NSUserDefaults.standardUserDefaults().boolForKey_("googleSocialContext"):
            self.getMoreUrls()

        # create providers
        self.providers = [ cls(self) for cls in Provider.providers() ]


    def setDelegate_(self, delegate):
        self.delegate = delegate
    
    # Kick off all the providers to start getting information on the person.
    # providers call back to this object when they have something.
    def start(self):

        # the 'interesting' providers - flickr, twitter, etc - extract urls
        # from the boring_urls list based on regular expressions. The FeedProvider
        # wakes up right at the end, and turns everything left over into feeds.
        self.boring_urls = self.urls()

        # tell every provider to look for clues.
        # TODO - we really don't need to do this _incredibly_ often. a 30 second
        # timeout would make Shelf a lot less twitchy in terms of looking for feeds
        for provider in self.providers:
            provider.provide()
        
        self.changed()

    # use Google Social - ask it to tell us which urls are linked to using
    # rel="me" links from any of the urls that we already have for this person.
    def getMoreUrls( self ):
        if not self.ab_urls(): return # no point
        api = "http://socialgraph.apis.google.com/lookup?pretty=1&fme=1&q=" + ",".join([ quote(url) for url in self.ab_urls() ])
        print_info("Social graph API call to " + api )
        Cache.getContentOfUrlAndCallback( callback = self.gotSocialGraphData, url = api, timeout = 3600 * 48, wantStale = False, delay = 2 ) # huge timeout here

    # callback from Google Social call
    def gotSocialGraphData( self, raw, isStale ):
        try:
            data = json.loads( raw )
        except ValueError:
            return # meh
        urls = data['nodes'].keys()
        self.addExtraUrls( urls )
        self.start() # TODO - this kicks everything off again. Too heavy?
    
    def addExtraUrls( self, urls ):
        if not urls: return
        
        # build hash to dedupe - keys are the normalized url form,
        # values are the URLs as they came in.
        dedupe = {}
        for url in self.extra_urls + urls:
            if re.match(r'http', url): # HTTP only
                # respect existing normalizartion forms
                if not normalize_url( url ) in dedupe:
                    dedupe[ normalize_url( url ) ] = url
        self.extra_urls = dedupe.values()

        # remove all the urls we already know about from the Address Book
        known_urls = [ normalize_url( url ) for url in self.ab_urls() ]
        for url in [ u for u in self.extra_urls ]: # cheap copy, as we're mutating the array and python doesn't like looping over an array you're changing in place
            if normalize_url( url ) in known_urls:
                self.extra_urls.remove(url)
        
        print_info("I have the Address Book urls '%s'"%(", ".join(self.ab_urls())))
        print_info("Google gave me the extra urls '%s'"%(", ".join(self.extra_urls)))


    # the providers callback to this function when they have something new to say.
    # We just pass the message upwards
    def changed(self):
        if self.delegate:
            self.delegate.updateWebContent_fromClue_( self.content(), self )
    
    # this method returns the HTML content that should be in the webview for this clue.
    def content(self):
        # jut cat together the content of our providers.
        # TODO - long term, I'd like providers to return smarter objects, with
        # contents and date and headings, so the front-end can group them by
        # source, or URL, or date, and get a date-sorted list of everything a
        # person has done.
        atoms = []
        for p in self.providers:
            atoms += p.atoms
        
        atoms.sort(lambda a,b: cmp(b.sortOrder(), a.sortOrder()))
        content = "".join([ atom.content() for atom in atoms ])
        if content: return content
        
        return "<p>thinking..</p>"
        
    # stop this clue from thinking soon. Tell all the providers to stop.
    def stop(self):
        NSObject.cancelPreviousPerformRequestsWithTarget_( self )
        for current in self.providers:
            current.stop()


    # strip urls matching the passed regexp from the boring_urls list, and
    # return them. This lets providers 'take posession of' urls so the FeedProvider
    # doesn't see them
    def takeUrls(self,pattern):
        interesting = []
        for u in self.urls():
            if re.search(pattern, u):
                interesting.append(u)
        for u in interesting:
            if u in self.boring_urls:
                self.boring_urls.remove(u)
        return interesting
    
    
    ######################################
    # These methods represent the properties of the underlying person

    # Used for == comparison
    def __eq__(self, other):
        if not other: return False
        return self.uniqueId() == other.uniqueId()
    
    # Stringify to something readable
    def __str__(self):
        return "<Clue: '%s'>"%self.displayName()
    
    # must be globally unique
    def uniqueId(self):
        return self.person.uniqueId()
    
    # returns an NSImage for this person. Falls back to a nice default if there's
    # nothing in the Address Book
    def image(self):
        if self.person.imageData():
            return NSImage.alloc().initWithData_( self.person.imageData() )
        if self.isCompany():
            return NSImage.imageNamed_("NSUserGroup")
        else:
            return NSImage.imageNamed_("NSUser")

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

    # Address Book urls. Rather than urls we have from all sources.
    def ab_urls(self):
        return self._multi_to_list( self.person.valueForProperty_(kABURLsProperty) )
    
    def urls(self):
        return self.ab_urls() + self.extra_urls

    def email(self): 
        return self.emails()[0]
        
    def birthday(self):
        try:
            if self.person.valueForProperty_( kABBirthdayProperty ):
                return gmtime( self.person.valueForProperty_( kABBirthdayProperty ).timeIntervalSince1970() )
        except ValueError: # too old.. TODO - Um, I know people born <1970. Must fix.
            pass
        return None

    # utility method for dealing with the Cocoa Address Book interface.
    def _multi_to_list(self, multi):
        if not multi: return []
        output = []
        for i in range(0, multi.count() ):
            output.append( multi.valueAtIndex_( i ) )
        return output
