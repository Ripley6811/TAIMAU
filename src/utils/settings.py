#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json

if not os.path.exists('settings.json'):
    if os.path.exists('../../settings.json'):
        os.chdir(os.pardir)
        os.chdir(os.pardir)

def load():
    try:
        with open('settings.json', 'r') as rfile:
            js = json.load(rfile)
        rfile.close()
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