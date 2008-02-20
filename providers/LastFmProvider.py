from FeedProvider import *
from Utilities import *

from xml.dom.minidom import parseString
from time import time, gmtime
from urllib import quote

class LastFmAtom( ProviderAtom ):
    def __init__(self, *stuff):
        ProviderAtom.__init__( self, *stuff )

        username = re.search(r'user/([^/]+)', self.url).group(1)
        self.name = "last.fm / %s"%username
        
        self.tracks = []

        recent_url = "http://ws.audioscrobbler.com/1.0/user/%s/recenttracks.xml"%username
        Cache.getContentOfUrlAndCallback( callback = self.gotRecentTracks, url = recent_url, timeout = 60, wantStale = True, failure = self.failed )

    def failed( self, error ):
        self.stale = False
        self.changed()

    def gotRecentTracks(self, xml, stale):
        self.stale = stale
        dom = parseString( xml )
        self.tracks = []
        def gsv(node, val):
            try:
                return node.getElementsByTagName(val)[0].childNodes[0].wholeText
            except IndexError:
                return None
        for track in dom.getElementsByTagName("track")[0:3]:
            track.normalize()
            played = int(track.getElementsByTagName("date")[0].getAttribute('uts'))
            data = {
              'link':gsv(track, "url"),
              'art':"",
              'artist':gsv(track, "artist"),
              'album':gsv(track, "album"),
              'title':gsv(track, "name"),
              'date':played
            }
            self.tracks.append( data )
            if data['album']:
                def updateArtwork(data, stale, trackdata = data):
                    trackdata['art'] = gsv( parseString(data), 'small' )
                    self.changed()
                art_url = "http://ws.audioscrobbler.com/1.0/album/%s/%s/info.xml"%( quote(data['artist'].encode('utf-8'),""), quote(data['album'].encode('utf-8'),"") )
                Cache.getContentOfUrlAndCallback( callback = updateArtwork, url = art_url, timeout = 24 * 3600, wantStale = True )
            
        self.changed()
    
    def body(self):
        html = ""

        for track in self.tracks:
            ago = time_ago_in_words(gmtime(track['date'])) + " ago"
            html += u'<span class="feed-date">%s</span>'%ago

            html += "<a href='%s'><img src='%s' class='flickr-image'></a>"%( track['link'], track['art'] )

            html += '<p class="feed-title"><a href="%s">%s</a></p>'%( track['link'], track['title'] )
            html += u'<p class="feed-content">%s</p>'%( track['artist'] )

            html += '<div style="clear:both"></div>'

        return html


    def timeout(self):
        return 180





    
class LastFmProvider( Provider ):

    def atomClass(self):
        return LastFmAtom

    def provide( self ):
        urls = self.clue.takeUrls(r'last\.fm/user/.')
        self.atoms = [ self.atomClass()( self, url ) for url in urls ]
