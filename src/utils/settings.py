#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

def load():
    try:
        with open('data/settings', 'r') as rfile:
            js = json.load(rfile)
        rfile.close()
        return js
    except:
        return dict()

def update(**kwargs):
    js = load()
    js.update(**kwargs)
    with open('data/settings', 'w') as wfile:
        json.dump(js, wfile, indent=4)
    wfile.close()
    return True