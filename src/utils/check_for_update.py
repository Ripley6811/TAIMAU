#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Tix
import tkMessageBox
import datetime
import urllib2
from StringIO import StringIO
from zipfile import ZipFile

def update(_, settings):
    response = urllib2.urlopen("https://github.com/Ripley6811/TAIMAU")
    html = response.read()
    prestring = u'commit/'
    start = html.find(prestring) + len(prestring) + 1
    end = html.find('" class', start)

    if _.debug:
        print start, end, html[start: end]
    SHA = html[start: end]

    # Check if commit number is stored in settings.
    # Save and exit if it is not there.
    try:
        print u"Latest commit SHA:"
        print u"\t" + settings.load()[u'commit']
    except KeyError:
        settings.update(commit = SHA)
        return

#==============================================================================
# Compare SHA in settings to web site latest
#==============================================================================
    if SHA == settings.load()[u'commit']:
        title = message = u'Program is up to date!'
        tkMessageBox.showinfo(title, message)
        return
    else:
        title = u'New version available!'
        message = u'New version is available.\nUpdate now?'
        confirm = tkMessageBox.askyesno(title, message)
        if not confirm:
            return
        else:
            zipf = urllib2.urlopen("https://github.com/Ripley6811/TAIMAU/archive/master.zip")
            with open("temp_github_repo.zip", "w") as wf:
                wf.write(zipf.read())
            wf.close()
