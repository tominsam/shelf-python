"""Find RSS feed from site's LINK tag"""

__author__ = "Mark Pilgrim (f8dy@diveintomark.org)"
__copyright__ = "Copyright 2002, Mark Pilgrim"
__license__ = "Python"

# messed around with by Tom to do Atom as well.

import urllib, urlparse
from sgmllib import SGMLParser

BUFFERSIZE = 1024

class LinkParser(SGMLParser):
    def reset(self):
        SGMLParser.reset(self)
        self.href = ''
        
    def do_link(self, attrs):
        if not ('rel', 'alternate') in attrs: return
        typelist = [e[1] for e in attrs if e[0]=='type']
        if len(typelist) == 0: return
        if typelist[0] !='application/rss+xml' and typelist[0] != 'application/atom+xml': return
        hreflist = [e[1] for e in attrs if e[0]=='href']
        if not hreflist: return
        self.href = hreflist[0]
        self.setnomoretags()
    
    def end_head(self, attrs):
        self.setnomoretags()
    start_body = end_head

def getRSSLinkFromHTMLSource(htmlSource):
    try:
        parser = LinkParser()
        parser.feed(htmlSource)
        return parser.href
    except:
        return ''
    
def getRSSLink(url):
    try:
        usock = urllib.urlopen(url)
        parser = LinkParser()
        while 1:
            buffer = usock.read(BUFFERSIZE)
            parser.feed(buffer)
            if parser.nomoretags: break
            if len(buffer) < BUFFERSIZE: break
        usock.close()
        if parser.href == '': return None
        return urlparse.urljoin(url, parser.href)
    except:
        return None

if __name__ == '__main__':
    import sys
    print getRSSLink(sys.argv[1])
    
