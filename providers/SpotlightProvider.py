from Provider import *
from urllib import quote
from Utilities import *

import time
import Cache

class SpotlightAtom( ProviderAtom ):
  def __init__(self, provider, url):
    ProviderAtom.__init__( self, provider, url )
    clue = self.provider.clue
    if clue.emails():
      print "Clue:", clue.emails()
      self.proxy = queryProxy.alloc().init()
      setattr(self.proxy, 'provider', provider)
      setattr(self.proxy, 'emails', clue.emails())
      self.proxy.performSelector_withObject_afterDelay_('start', None, 0.1 )

  def sortOrder(self):
    return MAX_SORT_ORDER - 1
    
class queryProxy(NSObject):
  def init(self):
    self = super(queryProxy, self).init()
    if not self: return
    self.provider = None
    self.emails = None
    self.query = None
    return self
  
  def start(self):
    # exclude image, text and html files that are sometimes wrongly attached to emails
    exclusions = ['public.image','public.text']
    self.query = NSMetadataQuery.alloc().init()
    # The easy bit - all e-mails where these addresses are seen
    predicate = "((kMDItemContentType = 'com.apple.mail.emlx') && (" + \
    '||'.join(["((kMDItemAuthorEmailAddresses = '%s') || (kMDItemRecipientEmailAddresses = '%s'))" % (m, m) for m in self.emails]) + \
    ")"
    predicate += " || (" + \
    '&&'.join(["(kMDItemContentTypeTree != '%s')" % e for e in exclusions]) + \
    ") && (" + \
    '||'.join(["(kMDItemWhereFroms like '*%s*')" % m for m in self.emails]) + \
    '))'
    print predicate
    self.query.setPredicate_(NSPredicate.predicateWithFormat_(predicate))
    self.query.setSortDescriptors_(NSArray.arrayWithObject_(NSSortDescriptor.alloc().initWithKey_ascending_('kMDItemContentCreationDate',False)))
    NSNotificationCenter.defaultCenter().addObserver_selector_name_object_(self, self.gotSpotlightData_, NSMetadataQueryDidFinishGatheringNotification, self.query)
    self.query.startQuery()
  
  def gotSpotlightData_(self, notification):
    query = notification.object()
    print "Query results: ", len(query.results())
    self.provider.changed()

class SpotlightProvider( Provider ):
  
  def atomClass(self):
    return SpotlightAtom

  def provide(self):
    self.atoms = [ SpotlightAtom(self, "") ]
