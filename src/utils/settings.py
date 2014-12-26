#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json

# Set default path to this file then up two levels to find settings.json.
os.chdir(os.path.dirname(__file__))
if not os.path.exists('settings.json'):
    if os.path.exists('../../settings.json'):
        os.chdir(os.pardir)
        os.chdir(os.pardir)

def load(subdir=None):
    """Load the settings.json as a dictionary object.

    Get a dict object of the json data stored in settings.json or a
    sub-directory of that object. If 'subdir' is not a dict object then
    it raises a type error.
    """
    try:
        with open('settings.json', 'r') as rfile:
            js = json.load(rfile)
        rfile.close()
        if subdir:
            if isinstance(js.get(subdir, {}), dict):
                return js.get(subdir)
            else:
                raise TypeError, u"Attribute is not a dict object."
        else:
            return js
    except IOError as e:
        print e
        print 'CWD:', os.getcwd()
        return dict()

def update(**kwargs):
    js = load()
    js.update(**kwargs)
    with open('settings.json', 'w') as wfile:
        json.dump(js, wfile, indent=4)
    wfile.close()
    return True