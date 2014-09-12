#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Tix
import matplotlib



def main(_):
    '''

    _ = state information object. See "main.py".
    '''

    _.product_edit = Tix.Frame(_.product_frame)

    mainf = Tix.Frame(_.product_edit)
    mainf.pack()

    Tix.Button(mainf, text="test1").pack(side='left')


    def refresh():
        pass


    _.product_edit.refresh = refresh
    try:
        _.refresh.append(refresh)
    except KeyError:
        _.refresh = [refresh,]