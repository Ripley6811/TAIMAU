#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil
import tkMessageBox
import urllib2
from StringIO import StringIO
from zipfile import ZipFile
from requests import get as urlopen

def update(_, settings):
    response = urllib2.urlopen("https://github.com/Ripley6811/TAIMAU")
    html = response.read()
    prestring = 'commit/'
    start = html.find(prestring) + len(prestring)
    end = html.find('"', start)

    if _.debug:
        print start, end, html[start: end]
    SHA = html[start: end]

    # Check if commit number is stored in settings.
    # Save and exit if it is not there.
    try:
        print u"Settings SHA:"
        print u"\t" + settings.load()['commit']
    except KeyError:
        settings.update(commit = SHA)
        return

    print u"Latest commit SHA:"
    print "\t" + SHA
#==============================================================================
# Compare SHA in settings to web site latest
#==============================================================================
    if SHA == settings.load()['commit']:
        title = message = u'Program is up to date!'
        tkMessageBox.showinfo(title, message)
        return
    else:
        title = u'New version available!'
        message = u'Current:\n  ' + settings.load()['commit']
        message += u'\nLatest:\n  ' + SHA
        message += u'\n\nNew version is available.\nUpdate now?'
        confirm = tkMessageBox.askyesno(title, message)
        if not confirm:
            return
        else:
            src_url = "https://github.com/Ripley6811/TAIMAU/archive/master.zip"
            zipr = urlopen(src_url)
            zf = ZipFile(StringIO(zipr.content))
            zf.extractall()

            # Copy files from master to src
            #XXX: From http://stackoverflow.com/questions/7419665/python-move-and-overwrite-files-and-folders
            root_src_dir = os.path.join(os.getcwd(),"TAIMAU-master\\src")
            root_dst_dir = os.path.join(os.getcwd(),"src")

            for src_dir, dirs, files in os.walk(root_src_dir):
                dst_dir = src_dir.replace(root_src_dir, root_dst_dir)
                if not os.path.exists(dst_dir):
                    os.mkdir(dst_dir)
                for file_ in files:
                    src_file = os.path.join(src_dir, file_)
                    dst_file = os.path.join(dst_dir, file_)
                    if os.path.exists(dst_file):
                        os.remove(dst_file)
                    shutil.move(src_file, dst_dir)

            # Delete the temp repo folder.
            shutil.rmtree(os.path.join(os.getcwd(),"TAIMAU-master"))

            # Update commit SHA in settings file.
            settings.update(commit = SHA)

            # Prompt user to restart program.
            title = u'Restart required.'
            message = u'Restart the program for latest version.'
            tkMessageBox.showwarning(title, message)