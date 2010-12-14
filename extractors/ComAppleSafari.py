from ScriptingBridge import *
from Extractor import *
import urlparse
from Utilities import *
from xml.etree.ElementTree import ElementTree

class ComAppleSafari(Extractor):

    def __init__(self):
        super( ComAppleSafari, self ).__init__()
        self.safari = SBApplication.applicationWithBundleIdentifier_("com.apple.safari")

    def clues(self):
        clues = []
        if not self.safari.windows().count(): return

        # window 0 is always the foreground window? Seems it.
        tab = self.safari.windows()[ 0 ].currentTab()
        if not tab.exists(): return # foreground window is not a browser window.
        
        self.clues_from_url( tab.URL() )
        if self.done: return

        if re.match( r'https://www.google.com/reader/', unicode(tab.URL()) ):
            # google reader. Try to investigate current item.
            js = """
                var link = null;
                var n = document.getElementById('entries').childNodes;
                for (var i = 0; i < n.length; i++) {
                    if (/expanded/.test(n[i].className)) {
                        var l = n[i];
                        var a = l.getElementsByClassName("entry-title-link")[0];
                        if (a) {
                            link = a.href;
                            break;
                        }
                    }
                }
                link;
            """
            link = self.safari.doJavaScript_in_(js, self.safari.windows()[0].currentTab())
            if link:
                self.clues_from_url( link )
                if self.done: return

        if tab.source():
            # look for microformats
            self.clues_from_html( tab.source(), tab.URL() )
            if self.done: return

            # look for rel="me" links
            relme = RelMeParser()
            try:
                relme.feed( tab.source() )
            except Exception:
                # bad page source
                return
            print_info("Found rel='me' links: %s"%( ",".join(relme.hrefs) ) )
            for link in relme.hrefs:
                profile = urlparse.urljoin( tab.URL(), link )
                # not sure what to do here. This might point somewhere
                # useful. It might not. In the case of flickr, it points
                # to a page that contains enough microformats that we
                # might be able to work out who they are, but I really
                # don't want to have to _fetch_ the page, not here.
                self.clues_from_url( profile )

    # I'm sure the microformats output format makes sense _somewhere_
    def tree_to_dict(tree):
        pass



from sgmllib import SGMLParser

class RelMeParser(SGMLParser):
    def reset(self):
        SGMLParser.reset(self)
        self.hrefs = []
    
    def do_a( self, attrs ):
        if not ('rel', 'me') in attrs: return
        self.hrefs += filter( lambda l: re.match(r'http', l), [e[1] for e in attrs if e[0]=='href'] )
