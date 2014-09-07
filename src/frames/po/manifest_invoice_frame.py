#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Tix


def main(_):
    """Set up the comprehensive view for all records.

    Button to set number of records to load. Default to 10."""


    frame = Tix.Frame(_.po_frame)


    nRecords = Tix.StringVar()
    nRecords.set(20)
    nRecords.trace('w', lambda a,b,c: refresh())

    # Headers and (column number, col width)
    H = {
        u'出貨編號'  : (0, 13),
        u'日期' : (1, 9),
        u'品名' : (2, 20),
        u'數量' : (3, 8),
        u'單位' : (4, 5),

        u'發票號碼' : (5, 13),
        u'發票日期' : (6, 9),
        u'發票數量' : (7, 8),
        u'價格' : (8, 8),
        u'規格' : (9, 8),
        u'總價' : (10, 10),
    }

    tree_box = Tix.Frame(frame)
    tree_box.pack(side='top', fill='both', expand=1)
    tree = Tix.Tree(tree_box, options='columns {}'.format(len(H)))
    tree.pack(expand=1, fill='both', side='top')

    rb_box = Tix.Frame(frame)
    rb_box.pack(side='bottom', fill='x')

    Tix.Label(rb_box, textvariable=_.loc(u'Number of records to show:'))\
        .pack(side='left')
    rb_vals = (20, 50, 100, 1000)
    options = dict(variable=nRecords, indicatoron=False)
    for val in rb_vals:
        Tix.Radiobutton(rb_box, text=val, value=val, **options)\
            .pack(side='left')

    totalvalue = Tix.StringVar()
    Tix.Label(rb_box, textvariable=totalvalue)
    totalvalue.set(u'$0')

    for key, (col, width) in H.iteritems():
        tree.hlist.header_create(col, text=key, headerbackground='cyan')
        tree.hlist.column_width(col, chars=width)

#    tree['opencmd'] = lambda dir=None, w=tree: opendir(w, dir)
    tree.hlist['header'] = True
    tree.hlist['separator'] = '~' # Default is gray
    tree.hlist['background'] = 'white' # Default is gray
    tree.hlist['selectforeground'] = 'white' # Default is gray
    tree.hlist['selectmode'] = 'extended' # Select multiple items
    tree.hlist['indent'] = 14 # Adjust indentation of children
    tree.hlist['wideselect'] = 1 # Color selection from end to end
    tree.hlist['font'] = _.font
    tree['command'] = lambda *args: apply_selection()

    def apply_selection():
        #TODO: Add button to create activity report from selection!
        print tree.hlist.info_selection()

    tds = lambda anchor, bg: Tix.DisplayStyle(
        anchor=anchor,
        bg=bg,
        itemtype='text',
        refwindow=tree.hlist,
        font=_.font
    )

    po_color = u'PeachPuff2'
    inv_color = u'gold'
    def refresh():
        # SQL query for shipments (items)
        query = _.dbm.session.query(_.dbm.ShipmentItem)
        query = query.join(_.dbm.Shipment)
        query = query.order_by(_.dbm.Shipment.shipmentdate.desc())
        query = query.join(_.dbm.Order)
        if _.sc_mode == u's':
            query = query.filter_by(is_purchase=True)
        elif _.sc_mode == u'c':
            query = query.filter_by(is_sale=True)
        query = query.join(_.dbm.Order.parent)
        query = query.filter_by(name=_.curr.cogroup.name)
        query = query.limit(nRecords.get())
        shipments = query.all()

        tree.hlist.delete_all()
        for rec in shipments:
            hid = str(rec.id)
            tree.hlist.add(hid, text=rec.shipment.shipment_no, itemtype=Tix.TEXT, style=tds('w',po_color))
            tree.hlist.item_create(hid, col=H[u'日期'][0], text=u'{0.month}月{0.day}日'.format(rec.shipment.shipmentdate), itemtype=Tix.TEXT, style=tds('w',po_color))
            tree.hlist.item_create(hid, col=H[u'品名'][0], text=u'{} ({})'.format(rec.order.product.label(), rec.order.product.specs), itemtype=Tix.TEXT, style=tds('w',po_color))
            tree.hlist.item_create(hid, col=H[u'數量'][0], text=rec.qty, itemtype=Tix.TEXT, style=tds('e',po_color))
            tree.hlist.item_create(hid, col=H[u'單位'][0], text=rec.order.product.SKU, itemtype=Tix.TEXT, style=tds('w',po_color))

            if rec.invoiceitem:
                invi = rec.invoiceitem[0] #alias
                tree.hlist.item_create(hid, col=H[u'發票號碼'][0], text=invi.invoice.invoice_no, itemtype=Tix.TEXT, style=tds('w',inv_color))
                tree.hlist.item_create(hid, col=H[u'發票日期'][0], text=u'{0.month}月{0.day}日'.format(invi.invoice.invoicedate), itemtype=Tix.TEXT, style=tds('w',inv_color))
                tree.hlist.item_create(hid, col=H[u'發票數量'][0], text=invi.qty, itemtype=Tix.TEXT, style=tds('e',inv_color if rec.qty == invi.qty else u'tomato'))
                tree.hlist.item_create(hid, col=H[u'價格'][0], text=invi.order.price, itemtype=Tix.TEXT, style=tds('e', inv_color))
                tree.hlist.item_create(hid, col=H[u'規格'][0], text=invi.order.product.units if invi.order.product.unitpriced else u'', itemtype=Tix.TEXT, style=tds('e', inv_color))
                tree.hlist.item_create(hid, col=H[u'總價'][0], text=invi.total(), itemtype=Tix.TEXT, style=tds('e',inv_color))

            if len(rec.invoiceitem) > 1:
                tree.setmode(hid, 'open')

    _.mi_frame = frame
    _.mi_frame_refresh = refresh
    return frame