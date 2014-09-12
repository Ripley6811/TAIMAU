#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Tix
import matplotlib



def main(_):
    '''

    _ = state information object. See "main.py".
    '''

    _.product_price = Tix.Frame(_.product_frame)
    mainf = Tix.Frame(_.product_price)
    mainf.pack()

    Tix.Button(mainf, text="test2").pack(side='left')



    def refresh():
        pass


    _.product_price.refresh = refresh
    try:
        _.refresh.append(refresh)
    except KeyError:
        _.refresh = [refresh,]