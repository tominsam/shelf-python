#!/usr/bin/python
"""
Script for building the example.

Usage:
    python setup.py py2app
"""
from distutils.core import setup
import py2app
from glob import glob

version = "0.0.11"

plist = dict(
  CFBundleName="Shelf",
  NSMainNibFile="MainMenu",
  CFBundleIdentifier="org.jerakeen.pyshelf", # historical
  CFBundleShortVersionString=version,
  CFBundleVersion=version,
  NSHumanReadableCopyright="Copyright 2008 Tom Insam",

  # sparkle appcast url, for auto-updates
  SUFeedURL="http://jerakeen.org/code/shelf/appcast/"
)

setup(
    app=["main.py",],
    data_files= glob("*.nib") + glob("*.html") + glob("*.gif") + glob("*.py") + glob("*.css"),
    options=dict(py2app=dict(
        plist=plist,
        iconfile="Shelf.icns",
        frameworks=glob("*.framework"),
    )),
)

