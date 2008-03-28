# slightly based on http://phildawes.net/microformats/microformatparser.html

from sgmllib import SGMLParser, SGMLParseError
import urlparse

class RelMeProcessor(SGMLParser):
    
    def __init__(self, *stuff, **other):
        SGMLParser.__init__(self, *stuff, **other)
        self.rels = []

    def _getattr(self,name,attrs):
        for attr in attrs:
            if name == attr[0]: return attr[1]    
        
    def start_a(self, attrs):
        if self._getattr('rel',attrs) == 'me':
            self.rels.append( self._getattr('href',attrs) )

def parse(inp, base = "http://dummy/url"):
    m = RelMeProcessor(base)
    try:
        str = inp.read()
    except AttributeError:
        str = inp
    if not str:
        return []
    try:
        m.feed(str)
        m.close()
        return map( lambda u: urlparse.urljoin( base, u ), m.rels )
    except SGMLParseError:
        return []

if __name__ == "__main__":
    import urllib, sys
    if len(sys.argv) == 1:
        print "Usage:",sys.argv[0],"<url>"
        sys.exit(0)
    else:
        for url in sys.argv[1:]:
            print(repr(parse(urllib.urlopen(url),url)))
