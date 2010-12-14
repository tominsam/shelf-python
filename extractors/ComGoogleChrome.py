from ScriptingBridge import *
from Extractor import *
import urlparse
from Utilities import *

class ComGoogleChrome(Extractor):

    def __init__(self):
        super( ComGoogleChrome, self ).__init__()
        self.chrome = SBApplication.applicationWithBundleIdentifier_("com.google.Chrome")

    def clues(self):
        clues = []
        if not self.chrome.windows().count(): return

        # window 0 is always the foreground window? Seems it.
        tab = self.chrome.windows()[ 0 ].activeTab()
        
        # this is in one version of the chome API, but not others.
        if hasattr(tab, "exists"):
            if not tab.exists(): return # foreground window is not a browser window.
        
        self.clues_from_url( tab.URL() )
        if self.done:
            return

        # this is in one version of the chome API, but not others.
        if hasattr(tab, "source") and tab.source():
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

