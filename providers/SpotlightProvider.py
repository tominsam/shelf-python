from Provider import *
from urllib import quote
from Utilities import *

import time
import Cache

class SpotlightAtom( ProviderAtom ):
  def __init__(self, provider, url):
    ProviderAtom.__init__( self, provider, url )
    clue = self.provider.clue
    self.results = None
    if clue.emails():
      if url == 'Recent Messages':
        # query messages
        predicate = "(kMDItemContentType = 'com.apple.mail.emlx') && (" + \
         '||'.join(["((kMDItemAuthorEmailAddresses = '%s') || (kMDItemRecipientEmailAddresses = '%s'))" % (m, m) for m in clue.emails()]) + \
         ")"
      else:
        # query attachments
        # exclude image, text and html files that are sometimes wrongly attached to emails
        exclusions = ['public.image','public.text']
        predicate = "(" + \
        '&&'.join(["(kMDItemContentTypeTree != '%s')" % e for e in exclusions]) + \
        ") && (" + \
        '||'.join(["(kMDItemWhereFroms like '*%s*')" % m for m in clue.emails()]) + \
        ')'
      self.proxy = queryProxy.alloc().init()
      setattr(self.proxy, 'atom', self)
      setattr(self.proxy, 'predicate', predicate)
      self.proxy.start()

  def sortOrder(self):
    return MAX_SORT_ORDER - 1
  
  def body(self):
    if not self.results: return None
    body = []
    for r in self.results[:10]:
      body.append('<p><a href="shelf:file://%s">%s</a></p>' % (r.valueForAttribute_('kMDItemPath'),r.valueForAttribute_('kMDItemDisplayName')))
    return ''.join(body)
  
# proxy NSObject class to receive notifications
class queryProxy(NSObject):
  def init(self):
    self = super(queryProxy, self).init()
    if not self: return
    self.atom = None
    self.predicate = None
    return self
  
  def start(self):
    self.query = NSMetadataQuery.alloc().init()
    self.query.setPredicate_(NSPredicate.predicateWithFormat_(self.predicate))
    self.query.setSortDescriptors_(NSArray.arrayWithObject_(NSSortDescriptor.alloc().initWithKey_ascending_('kMDItemContentCreationDate',False)))
    NSNotificationCenter.defaultCenter().addObserver_selector_name_object_(self, self.gotSpotlightData_, NSMetadataQueryDidFinishGatheringNotification, self.query)
    self.query.startQuery()
  
  def gotSpotlightData_(self, notification):
    query = notification.object()
    print "Got %d results for %s." % (len(query.results()), self.predicate)
    self.atom.results = query.results()
    self.atom.changed()

class SpotlightProvider( Provider ):
  
  def atomClass(self):
    return SpotlightAtom

  def provide(self):
    self.atoms = [ SpotlightAtom(self, "Recent Messages"), SpotlightAtom(self, "Attachments") ]
