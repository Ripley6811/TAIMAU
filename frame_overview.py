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
:SINCE: Sat Jun 07 08:17:53 2014
:VERSION: 0.1
"""

import Tix
from Tix import N, S, E, W, BOTTOM, TOP, BOTH, END, X, EXTENDED

def create_frame(frame, info):

    editb = Tix.Button(frame, text=u"編輯紀錄", bg=u'light salmon')
    editb.pack(side=TOP, fill=X)

    def show_selection():
#        print tree.hlist.cget('value')
        print tree.hlist.info_selection()
        print tree.hlist.item_configure('5774', 0)
    editb['command'] = show_selection

    # Headers and (column number, col width)
    H = {
        u'No.'  : (0, 18),
        u'Date' : (1, 12),
        u'品名' : (2, 24),
        u'數量' : (3, 10),
        u'單位' : (4, 8),
        u'價格' : (5, 10),
        u'總價' : (6, 14),
        u'PAID' : (7, 6),
        u''     : (8, 10)
    }
    tree = Tix.Tree(frame, options='columns {}'.format(len(H)), height=1000)
    tree.pack(expand=1, fill=Tix.BOTH, side=Tix.TOP)
    tree['opencmd'] = lambda dir=None, w=tree: opendir(w, dir)
    tree.hlist['header'] = True
    tree.hlist['separator'] = '~' # Default is gray
    tree.hlist['background'] = 'white' # Default is gray
    tree.hlist['selectforeground'] = 'white' # Default is gray
    tree.hlist['selectmode'] = EXTENDED # Select multiple items
    tree.hlist['indent'] = 14 # Adjust indentation of children
    tree.hlist['wideselect'] = 1 # Color selection from end to end
    tree.hlist['font'] = info.settings.font
    params = dict(
        itemtype=Tix.TEXT,
        refwindow=tree.hlist,
        font=info.settings.font,
    )
    styleRorder = Tix.DisplayStyle(anchor=Tix.E, bg=u'white', **params)
    styleCorder = Tix.DisplayStyle(anchor=Tix.CENTER, bg=u'white', **params)
    styleLorder = Tix.DisplayStyle(anchor=Tix.W, bg=u'white', **params)
    styleRship = Tix.DisplayStyle(anchor=Tix.E, bg=u'honeydew2', **params)
    styleCship = Tix.DisplayStyle(anchor=Tix.CENTER, bg=u'honeydew2', **params)
    styleLship = Tix.DisplayStyle(anchor=Tix.W, bg=u'honeydew2', **params)
    styleRinv = Tix.DisplayStyle(anchor=Tix.E, bg=u'PeachPuff2', **params)
    styleCinv = Tix.DisplayStyle(anchor=Tix.CENTER, bg=u'PeachPuff2', **params)
    styleLinv = Tix.DisplayStyle(anchor=Tix.W, bg=u'PeachPuff2', **params)
    for key, (col, width) in H.iteritems():
        tree.hlist.header_create(col, text=key, headerbackground='cyan')
        tree.hlist.column_width(col, chars=width)

    # Add orders from current company selection.
    def refresh_po_tree():
        tree.hlist.delete_all()
        for rec in info.order_records:
            hid = str(rec.id)
            tree.hlist.add(hid, itemtype=Tix.TEXT, text=rec.orderID)
            tree.hlist.item_create(hid, col=H[u'Date'][0], text=rec.orderdate, itemtype=Tix.TEXT, style=styleCorder)
            tree.hlist.item_create(hid, col=H[u'品名'][0], text=rec.product.label())
            tree.hlist.item_create(hid, col=H[u'數量'][0], text=rec.totalskus, itemtype=Tix.TEXT, style=styleRorder)
            tree.hlist.item_create(hid, col=H[u'單位'][0], text=rec.product.UM)
            tree.hlist.item_create(hid, col=H[u'價格'][0], text=rec.price, itemtype=Tix.TEXT, style=styleRorder)
            tree.hlist.item_create(hid, col=H[u'總價'][0], text=u'{:,}'.format(int(round(rec.subtotal))), itemtype=Tix.TEXT, style=styleRorder)
            if rec.all_paid():
                tree.hlist.item_create(hid, col=H[u'PAID'][0], text=u'\u2713', itemtype=Tix.TEXT, style=styleCorder)
            if len(rec.shipments) + len(rec.invoices):
                tree.setmode(str(rec.id), 'open')
    info.method.refresh_po_tree = refresh_po_tree

    def opendir(tree, path):
        order = info.dmv2.session.query(info.dmv2.Order).get(int(path.split('~')[0]))
        if 'shipments' in path:
            entries = tree.hlist.info_children(path)
            if entries: # Show previously loaded entries
                for entry in entries:
                    tree.hlist.show_entry(entry)
                return
            else: # Add items to entries
                for rec in order.shipments:
                    hid = path+'~'+str(rec.id)
                    tree.hlist.add(hid, itemtype=Tix.IMAGETEXT, text=rec.shipmentID)
                    tree.hlist.item_create(hid, col=H[u'Date'][0], text=rec.shipmentdate, itemtype=Tix.TEXT, style=styleCship)
                    tree.hlist.item_create(hid, col=H[u'品名'][0], text=rec.order.product.label(), itemtype=Tix.TEXT, style=styleCship)
                    tree.hlist.item_create(hid, col=H[u'數量'][0], text=rec.sku_qty, itemtype=Tix.TEXT, style=styleRship)
                    tree.hlist.item_create(hid, col=H[u'單位'][0], text=rec.order.product.UM, itemtype=Tix.TEXT, style=styleLship)
#                    tree.hlist.item_create(hid, col=H[u'價格'][0], text=rec.order.price)
        if 'invoices' in path:
            entries = tree.hlist.info_children(path)
            if entries: # Show previously loaded entries
                for entry in entries:
                    tree.hlist.show_entry(entry)
                return
            else: # Add items to entries
                for rec in order.invoices:
                    hid = path+'~'+str(rec.id)
                    tree.hlist.add(hid, itemtype=Tix.TEXT, text=rec.invoice_no)
                    tree.hlist.item_create(hid, col=H[u'Date'][0], text=rec.invoice.invoicedate, itemtype=Tix.TEXT, style=styleCinv)
                    tree.hlist.item_create(hid, col=H[u'品名'][0], text=rec.order.product.label(), itemtype=Tix.TEXT, style=styleCinv)
                    tree.hlist.item_create(hid, col=H[u'數量'][0], text=rec.sku_qty, itemtype=Tix.TEXT, style=styleRinv)
                    tree.hlist.item_create(hid, col=H[u'單位'][0], text=rec.order.product.UM, itemtype=Tix.TEXT, style=styleLinv)
                    tree.hlist.item_create(hid, col=H[u'總價'][0], text=u'{:,}'.format(rec.subtotal()), itemtype=Tix.TEXT, style=styleRinv)
                    if rec.invoice.paid:
                        tree.hlist.item_create(hid, col=H[u'PAID'][0], text=u'\u2713', itemtype=Tix.TEXT, style=styleCinv)
        else:
            entries = tree.hlist.info_children(path)
            if entries: # Show previously loaded entries
                for entry in entries:
                    tree.hlist.show_entry(entry)
                return
            else: # Add items to entries
                if len(order.shipments) > 0:
                    hid = path+'~shipments'
                    tree.hlist.add(hid, itemtype=Tix.TEXT, text=u'出貨單-----')
#                    tree.hlist.item_create(hid, col=H[u'Date'][0], text='------------------------------------')
                    tree.hlist.item_create(hid, col=H[u'品名'][0], text='-----({} records)-----'.format(len(order.shipments)), itemtype=Tix.TEXT, style=styleCorder)
                    tree.hlist.item_create(hid, col=H[u'數量'][0], text='({}'.format(order.qty_shipped()), itemtype=Tix.TEXT, style=styleRorder)
                    tree.hlist.item_create(hid, col=H[u'單位'][0], text='{})-----------'.format(order.product.UM), itemtype=Tix.TEXT, style=styleLorder)
#                    tree.hlist.item_create(hid, col=H[u'價格'][0], text='------------------------------------')
#                    tree.hlist.item_create(hid, col=H[u'總價'][0], text='------------------------------------')
                    tree.setmode(hid, 'open')
                    if len(order.shipments) < 5:
                        opendir(tree, hid)
                if len(order.invoices) > 0:
                    hid = path+'~invoices'
                    tree.hlist.add(hid, itemtype=Tix.TEXT, text=u'發票-------')
#                    tree.hlist.item_create(hid, col=H[u'Date'][0], text='------------------------------------')
                    tree.hlist.item_create(hid, col=H[u'品名'][0], text='-----({} records)-----'.format(len(order.invoices)), itemtype=Tix.TEXT, style=styleCorder)
                    tree.hlist.item_create(hid, col=H[u'數量'][0], text='({}'.format(order.qty_invoiced()), itemtype=Tix.TEXT, style=styleRorder)
                    tree.hlist.item_create(hid, col=H[u'單位'][0], text='{})-----------'.format(order.product.UM), itemtype=Tix.TEXT, style=styleLorder)
#                    tree.hlist.item_create(hid, col=H[u'價格'][0], text='------------------------------------')
                    tree.hlist.item_create(hid, col=H[u'總價'][0], text=u'({:,})'.format(order.qty_quote(order.total_paid())), itemtype=Tix.TEXT, style=styleRorder)
                    tree.setmode(hid, 'open')
                    if len(order.invoices) < 5:
                        opendir(tree, hid)
                separator = path+'~---'
                tree.hlist.add(separator, itemtype=Tix.TEXT, text=u'---------------------------------------')
                for i in range(1, len(H)):
                    tree.hlist.item_create(separator, col=i, text='----------------------------------------------')


























