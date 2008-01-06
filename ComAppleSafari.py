from ScriptingBridge import *
from Extractor import *
import microformatparser

class ComAppleSafari(Extractor):

    def __init__(self):
        super( ComAppleSafari, self ).__init__()
        self.safari = SBApplication.applicationWithBundleIdentifier_("com.apple.safari")

    def clues(self):
        clues = []

        # window 0 is always the foreground window?
        tab = self.safari.windows()[ 0 ].currentTab()
        clues += self.clues_from_url( tab.URL() )
        # TODO - look for embedded hcard?
        
        if len(clues) == 0 and tab.source():
            feeds = microformatparser.parse( tab.source() )
            if len(feeds) > 0:
                # I'm going to assume that the _first_ microformat on the page
                # is the person the page is about. I can't really do better
                # than that, can I?
                # TODO - yes, I can. Look for 'rel="me"'
                feed = feeds[0]
                vcards = [ tree for name, tree in feed if name =='vcard']
                if len(vcards) > 0:
                    card = dict(vcards[0])
                    if 'url' in card:
                        clues += self.clues_from_url( card['url'] )

                    if 'email' in card:
                        for addr in card['email']:
                            # bloody flickr
                            e = re.sub(r'\s*\[\s*at\s*\]\s*', '@', addr[1])
                            clues += self.clues_from_email( e )

                    if 'family-name' in card and 'given-name' in card:
                        # TODO - check ordering here for .jp issues? Gah.
                        clues += self.clues_from_names( card['given-name'], card['family-name'] )
                    
                    if len(clues) == 0:
                        print "Can't get anything useful from %s"%(repr(card))
            
        return clues
    
    # I'm sure the microformats output format makes sense _somewhere_
    def tree_to_dict(tree):
        pass
