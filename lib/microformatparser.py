# from http://phildawes.net/microformats/microformatparser.html
# changed by tom to understand multiple classes ina single class="foo bar baz" stanza



#!/usr/bin/env python
#
# Microformat parser hack
# - My lame attempt to build a generic microformat parser engine
# (C) Phil Dawes 2005
# Distributed under a New BSD style license:
# See: http://www.opensource.org/licenses/bsd-license.php
#
# Usage: python ./

import sys
import urlparse
from HTMLParser import HTMLParser
import re
import urllib2

class MicroformatSchema:

    def __init__(self,props,parentprops):
        self.props = props
        self.parentprops = parentprops

    def isValidProperty(self,prop):
        if prop in self.props + self.parentprops:
            return True
        return False

    def isParentProperty(self,prop):
        return prop in self.parentprops

vcardprops = MicroformatSchema(['fn','family-name', 'given-name', 'additional-name', 'honorific-prefix', 'honorific-suffix', 'nickname', 'sort-string','url','email','type','tel','post-office-box', 'extended-address', 'street-address', 'locality', 'region', 'postal-code', 'country-name', 'label', 'latitude', 'longitude', 'tz', 'photo', 'logo', 'sound', 'bday','title', 'role','organization-name', 'organization-unit','category', 'note','class', 'key', 'mailer', 'uid', 'rev'],['n','email','adr','geo','org','tel'])

veventprops = MicroformatSchema(["summary","url","dtstart","dtend","location"],[])

SCHEMAS= {'vcard':vcardprops,'vevent':veventprops}

class nodeitem:
    def __init__(self,id,tag,predicates,attrs,nested):
        self.tag = tag
        self.id = id
        self.predicates = predicates
        self.attrs = attrs
        self.nested = nested

    def __repr__(self):
        return "<nodeitem %s, %s, %s, %s, %s>"%(self.tag, self.id, self.predicates,
                                            self.attrs,self.nested)

class MicroformatToStmts(HTMLParser):
    def __init__(self,url):
        self.url = url
        HTMLParser.__init__(self)
        self.nodestack = []
        self.nodemap = {}
        self.chars = ""
        self.tree = []
        self.treestack = []

    def _getattr(self,name,attrs):
        for attr in attrs:
            if name == attr[0]: return attr[1]    

    def predicateIsAParent(self,pred):
        if SCHEMAS[self.currentCompoundFormat].isParentProperty(pred):
            return True
        return False
        
    def handle_starttag(self, elementtag, attrs):
        self.chars=""
        if self.currentlyInAMicroformat():
            try:
                preds = self._getattr("class",attrs).split()
            except AttributeError:
                self.nodestack.append(nodeitem(1,elementtag,None,attrs,False))
                return

            prevpreds = []
            #while 1:
            nested = False
            while 1:
                if prevpreds == preds:
                    break
                prevpreds = preds
                if self.predicateIsAParent(preds[0]):
                    self.openParentProperty(preds[0])
                    nested = True

                if elementtag == "img":
                    self.emitAttributeAsPropertyIfExists('src',attrs, preds)
                elif elementtag == "a":
                    self.emitAttributeAsPropertyIfExists('href',attrs, preds)
                    self.emitAttributeAsPropertyIfExists('title',attrs, preds)
                elif elementtag == "abbr":
                    self.emitAttributeAsPropertyIfExists('title',attrs, preds)
                
            self.nodestack.append(nodeitem(1,elementtag,preds,attrs,nested))

        elif self.nodeStartsAMicroformat(attrs):

            classattrs = self._getattr('class',attrs).split()
            for classattr in classattrs:
                if classattr in SCHEMAS.keys():
                    self.currentCompoundFormat = classattr
                    break
            self.nodestack.append(nodeitem(1,elementtag,[self._getattr('class',attrs)],attrs,True))
            self.tree.append([])
            self.treestack = [self.tree[-1]] # opening tree stack frame
            self.openParentProperty(self.currentCompoundFormat)

    def openParentProperty(self,prop):
        self.treestack[-1].append((prop,[]))
        self.treestack.append(self.treestack[-1][-1][1])
                    
    def currentlyInAMicroformat(self):
        return self.nodestack != []

    def nodeStartsAMicroformat(self, attrs):
        class_attr = self._getattr('class',attrs)
        if not class_attr: return False
        for a in class_attr.split():
            if a in SCHEMAS.keys(): return True
        return False

    def emitAttributeAsPropertyIfExists(self, attrname, attrs, preds):
        obj = self._getattr(attrname,attrs)
        if obj is not None:
            try:
                pred = preds[0]
                if SCHEMAS[self.currentCompoundFormat].isValidProperty(pred):
                    if attrname in ("href","src"):
                        obj = urlparse.urljoin(self.url,obj)
                    obj = self.makeDatesParsable(pred,obj)
                    self.addPropertyValueToOutput(pred,obj)
                del preds[0]
            except IndexError:
                pass

    def addPropertyValueToOutput(self,prop,val):
        self.treestack[-1].append((prop,val))
        
    def handle_endtag(self,tag):
        if self.currentlyInAMicroformat():
            while 1:
                try:
                    item = self.nodestack.pop()
                except IndexError:
                    return # no more elements
                if item.tag == tag:
                    break  # found it!

            # if there's still predicates, then output the text as object
            if item.predicates and item.predicates != [] and self.chars.strip() != "":
                #if item.tag == 'a':
                #    print "ITEM:a",self.treestack
                preds = item.predicates
                self.treestack[-1].append((preds[0],self.chars))
                del preds[0]
            if item.nested == 1:
                self.treestack.pop()
            self.chars = ""

    # HTMLPARSER interface
    def handle_data(self,content):
        if self.hasPredicatesPending():
            content = content.strip()
            if content == "":
                return        
            self.chars += content

    def hasPredicatesPending(self):
        for n in self.nodestack:
            if n.predicates != []:
                return 1
        return 0

    # hack to stop dates like '20051005' being interpreted as floats downstream
    def makeDatesParsable(self,p,o):
        if p in ["dtstart","dtend"]:
            try:
                float(o) # can it be interpreted as a float?
                o = "%s-%s-%s"%(o[:4],o[4:6],o[6:])
            except ValueError:
                pass
        return o


def printTree(tree,tab=""):
    for p,v in tree:
        if isinstance(v,list):
            print tab + p
            printTree(v,tab+"    ")
        else:
            print tab + unicode(p),":",v

def printTreeStack(treestack,tab=""):
    for t in treestack:
        if isinstance(t,list):
            printTreeStack(t,tab+"    ")
        else:
            print t

def parse(f,url="http://dummyurl.com/"):
    m = MicroformatToStmts(url)
    try:
        s = f.read()
    except AttributeError:
        s = f
    m.feed(s)
    m.close()

    return m.tree
    

if __name__ == "__main__":
    import urllib
    if len(sys.argv) == 1:
        print "Usage:",sys.argv[0],"<url>"
        sys.exit(0)
    else:
        for url in sys.argv[1:]:
            trees = parse(urllib.urlopen(url),url)
        for tree in trees:
            printTree(tree)
