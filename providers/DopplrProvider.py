from Provider import *
import urllib
import re
import json
from datetime import datetime
from time import time, strftime, gmtime
import feedparser # can parse iso8601 dates

from Utilities import *
import Cache

class DopplrAtom( ProviderAtom ):
    def __init__(self, provider, url):
        ProviderAtom.__init__( self, provider, url )
        self.username = re.search(r'/traveller/([^/]+)', self.url).group(1)
        self.name = "Dopplr / %s"%self.username
        self.response = None
        self.fail = None
        
        self.token = NSUserDefaults.standardUserDefaults().stringForKey_("dopplrToken")
        if not self.token: return

        url = "https://www.dopplr.com/api/traveller_info.js?token=%s&traveller=%s"%( self.token, self.username )
        Cache.getContentOfUrlAndCallback( callback = self.gotDopplrData, url = url, timeout = 3600, wantStale = True, failure = self.failed )

    def failed(self, error):
        NSLog("dopplr client fail: %@", error)
        self.fail = error
        self.changed()
    
    def gotDopplrData(self, data, stale):
        self.stale = stale
        try:
            doc = json.loads( data )
            self.response = doc['traveller']
        except ValueError, e:
            print(e)
            self.dead = True
        except KeyError, e:
            print(e)
            self.dead = True
        
        self.changed()
        
    def body(self):
        if not self.token:
            return """<p>No Dopplr API token defined. <a href="https://www.dopplr.com/api/AuthSubRequest?scope=http://www.dopplr.com&next=shelf://shelf/&session=1">click here</a> to get one.</a></p>"""
        
        if self.fail:
           return """<p>Problem talking to Dopplr - maybe the token is invalid? Try <a href="https://www.dopplr.com/api/AuthSubRequest?scope=http://www.dopplr.com&next=shelf://shelf/&session=1">re-authorizing</a>.</a>.</p>"""
        
        if not self.response: return None

        # dopplr api coveniently provides offset from UTC :-)
        offset = int(str(self.response['current_city']['utcoffset']))
        readable_time = strftime("%l:%M&nbsp;%p&nbsp;on&nbsp;%A", gmtime( time() + offset ))

        if 'current_trip' in self.response:
            start = feedparser._parse_date_iso8601( self.response['current_trip']['start'] )
            finish = feedparser._parse_date_iso8601( self.response['current_trip']['finish'] )

            body = "<p>%s is in %s (from %s&nbsp;to %s). Local time is %s.</p>"%(
                self.provider.clue.displayName(),
                self.response['current_trip']['city']['name'],
                strftime("%B&nbsp;%d", start ),
                strftime("%B&nbsp;%d", finish ),
                readable_time
            )
        else:
            body = "<p>%s is at home in %s (where it is %s).</p>"%(
                self.provider.clue.displayName(),
                self.response['current_city']['name'],
                readable_time
            )

        return body

    def sortOrder(self):
        return MAX_SORT_ORDER - 1


class DopplrProvider( Provider ):

    def atomClass(self):
        return DopplrAtom

    def provide( self ):
        dopplrs = self.clue.takeUrls(r'dopplr\.com/traveller')
        
        self.atoms = []
        for url in dopplrs:
            self.atoms.append( DopplrAtom( self, url ) )
