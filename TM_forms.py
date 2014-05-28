#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
summary

description

:REQUIRES:

:TODO:

:AUTHOR: Ripley6811
:ORGANIZATION: None
:CONTACT: python@boun.cr
:SINCE: Mon May 26 20:02:15 2014
:VERSION: 0.1
"""
#===============================================================================
# PROGRAM METADATA
#===============================================================================
__author__ = 'Ripley6811'
__contact__ = 'python@boun.cr'
__copyright__ = ''
__license__ = ''
__date__ = 'Mon May 26 20:02:15 2014'
__version__ = '0.1'

#===============================================================================
# IMPORT STATEMENTS
#===============================================================================
#from numpy import *  # IMPORTS ndarray(), arange(), zeros(), ones()
#set_printoptions(precision=5)
#set_printoptions(suppress=True)
#from visual import *  # IMPORTS NumPy.*, SciPy.*, and Visual objects (sphere, box, etc.)
#import matplotlib.pyplot as plt  # plt.plot(x,y)  plt.show()
#from pylab import *  # IMPORTS NumPy.*, SciPy.*, and matplotlib.*
#import os  # os.walk(basedir) FOR GETTING DIR STRUCTURE
#import pickle  # pickle.load(fromfile)  pickle.dump(data, tofile)
#from tkFileDialog import askopenfilename, askopenfile
#from collections import namedtuple
#from ctypes import *
#import glob
#import random
#import cv2
import Tkinter as Tk

#===============================================================================
# METHODS
#===============================================================================

def manifest_form(parent, shipment_items, highlight_id=None,
             font="NSimSun", font_size="15"):
    '''
    This method creates a frame set up to appear like the hardcopy manifest.
    Displays all items belonging to the same manifest form.
    Highlights the parameter item.
    '''
    #XXX: There's a chance that the ship_id might repeat, so check matching date as well.
#    ship_id = shipment.shipmentID
#    ship_date = shipment.shipmentdate

    shipmentset = shipment_items


    cell_config = dict(
        font= (font, font_size, u'bold'),
        bg= u'cornsilk',
        height= 2,
    )

    seller_name = shipmentset[0].order.seller
    buyer_name = shipmentset[0].order.buyer

    kehu = u'客戶名稱: {}'.format(buyer_name)
    _=Tk.Label(parent, text=kehu, **cell_config)
    _.grid(row=1,column=0, columnspan=2, sticky=Tk.W+Tk.E)

    try:
        branch = ([br for br in shipmentset[0].order.parent.branches
                    if br.name == buyer_name][0])

        sellertxt = u'{}'.format(seller_name)
        _=Tk.Label(parent, text=sellertxt, **cell_config)
        _.grid(row=0, column=0, columnspan=6, sticky=Tk.W+Tk.E)

        cell_config.update(anchor=Tk.W)

        contactname = branch.contacts[0].name if len(branch.contacts) else u''
        lianluo = u'聯 絡 人: {}'.format(contactname)
        _=Tk.Label(parent, text=lianluo, **cell_config)
        _.grid(row=2,column=0, columnspan=2, sticky=Tk.W+Tk.E)

        contactphone = branch.contacts[0].phone if len(branch.contacts) else branch.phone
        dianhua = u'聯絡電話: {}'.format(contactphone)
        _=Tk.Label(parent, text=dianhua, **cell_config)
        _.grid(row=3,column=0, columnspan=6, sticky=Tk.W+Tk.E)

        shipaddress = branch.address_shipping if branch.address_shipping else branch.address_office
        songhuo = u'送貨地址: {}'.format(shipaddress)
        _=Tk.Label(parent, text=songhuo, **cell_config)
        _.grid(row=4,column=0, columnspan=6, sticky=Tk.W+Tk.E)

        tongyi = u'統一編號: {}'.format(branch.tax_id)
        _=Tk.Label(parent, text=tongyi, **cell_config)
        _.grid(row=1,column=2, columnspan=2, sticky=Tk.W+Tk.E)

        fapiao = u'發票號碼: {}'.format(u'')
        _=Tk.Label(parent, text=fapiao, **cell_config)
        _.grid(row=2,column=2, columnspan=2, sticky=Tk.W+Tk.E)
    except Exception:
        sellertxt = u'{} ({})'.format(seller_name, shipmentset[0].order.parent.name)
        _=Tk.Label(parent, text=sellertxt, **cell_config)
        _.grid(row=0, column=0, columnspan=6, sticky=Tk.W+Tk.E)
        cell_config.update(anchor=Tk.W)

    riqi = u'貨單日期: {0.year}年 {0.month}月 {0.day}日'.format(shipmentset[0].shipmentdate)
    _=Tk.Label(parent, text=riqi, **cell_config)
    _.grid(row=1,column=4, columnspan=2, sticky=Tk.W+Tk.E)

    huodan = u'貨單編號: {}'.format(shipmentset[0].shipmentID)
    _=Tk.Label(parent, text=huodan, **cell_config)
    _.grid(row=2,column=4, columnspan=2, sticky=Tk.W+Tk.E)


    cell_config = dict(
        font= (font, font_size),
        bg= u'LightSteelBlue1',
        relief=Tk.RAISED,
    )
    for i, each in enumerate([u'品名',u'規格/包裝',u'件數',u'數量',u'包裝描述',u'出貨資訊']):
        _=Tk.Label(parent, text=each, **cell_config)
        _.grid(row=9,column=i, sticky=Tk.W+Tk.E)


    cell_config = dict(
        relief= Tk.SUNKEN,
        font= (font, font_size, u'bold',),
        bg= u'wheat'
    )
    query_config = dict(
        relief= Tk.SUNKEN,
        font= (font, font_size, u'bold',),
        bg= u'yellow'
    )
    for row, shipment in enumerate(shipmentset):
        order = shipment.order
        product = order.product
        config = query_config if shipment.id == highlight_id else cell_config

        pinming = u' {} '.format(product.product_label if product.product_label else product.inventory_name)
        guige = u'  {} {} / {}  '.format(product.units, product.UM, product.SKU)
        if product.SKU == u'槽車':
            guige = u'  槽車  '
        qty = shipment.sku_qty
        qty = int(qty) if int(qty)==qty else qty
        jianshu = u'  {} {}  '.format(qty, product.UM if product.SKU == u'槽車' else product.SKU)
        units = product.units * shipment.sku_qty
        units = int(units) if int(units)==units else units
        this_units = u'  {} {}  '.format(units, product.UM)
        Tk.Label(parent, text=pinming, **config).grid(row=10+row,column=0, sticky=Tk.W+Tk.E)
        Tk.Label(parent, text=guige, **config).grid(row=10+row,column=1, sticky=Tk.W+Tk.E)
        Tk.Label(parent, text=jianshu, **config).grid(row=10+row,column=2, sticky=Tk.W+Tk.E)
        Tk.Label(parent, text=this_units, **config).grid(row=10+row,column=3, sticky=Tk.W+Tk.E)
        Tk.Label(parent, bg=u'gray30', fg=u'gray70', text=u'  {}  '.format(product.SKUlong)).grid(row=10+row,column=4, sticky=Tk.W+Tk.E)
        dispnote = order.ordernote
        if order.orderID:
            dispnote = u'PO#:{} Note:{}'.format(order.orderID, dispnote)
        Tk.Label(parent, text=u'  {}  '.format(dispnote), **config).grid(row=10+row,column=5, sticky=Tk.W+Tk.E)

#        Tk.Button(parent, text=u'Print Labels', command=lambda x=shipment.id:print_labels(x)).grid(row=10+row,column=6, sticky=Tk.W+Tk.E)







#===============================================================================
# MAIN METHOD AND TESTING AREA
#===============================================================================




if __name__ == '__main__':
    print "TM_forms.py"
    print "Nothing to see here."
    pass



#===============================================================================
# QUICK REFERENCE
#===============================================================================
'''Templates and markup notes

>>SPYDER Note markers
    #XXX: !
    #TODO: ?
    #FIXME: ?
    #HINT: !
    #TIP: !


>>SPHINX markup
    :Any words between colons: Description following.
        Indent any continuation and it will be concatenated.
    .. warning:: ...
    .. note:: ...
    .. todo:: ...

    - List items with - or +
    - List item 2

    For a long hyphen use ---

    Start colored formatted code with >>> and ...

    **bold** and *italic* inline emphasis


>>SPHINX Method simple doc template (DIY formatting):
    """ summary

    description

    - **param** --- desc
    - *return* --- desc
    """

>>SPHINX Method longer template (with Sphinx keywords):
    """ summary

    description

    :type name: type optional
    :arg name: desc
    :returns: desc

    (optional intro to block)::

        Skip line and indent monospace block

    >>> python colored code example
    ... more code
    """

See http://scienceoss.com/use-sphinx-for-documentation/ for more details on
running Sphinx
'''
