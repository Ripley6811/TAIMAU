#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Tix


def main(_):
    """Set up the comprehensive view for all records.

    Button to set number of records to load. Default to 20."""

    #### USE THIS TO INTEGRATE FRAME INTO MAIN WINDOW ####
#    repack_info = _.po_center.pack_info()
#    _.po_center.pack_forget() # .pack(**repack_info)

    frame = Tix.Frame(_.po_frame)
#    frame.pack(side='left', fill='both')



    nRecords = Tix.StringVar()
    nRecords.set(20)
    nRecords.trace('w', lambda a,b,c: refresh())

    # Headers and (column number, col width)
    H = {
        u'No.'  : (0, 18),
        u'日期' : (1, 12),
        u'品名' : (2, 24),
        u'訂單數量' : (3, 9),
        u'單位' : (4, 5),
        u'價格' : (5, 10),
        u'出貨數量' : (6, 9),
        u'發票數量' : (7, 9),
        u'總價' : (8, 10),
        u'截止?' : (9, 7),
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

    for key, (col, width) in H.iteritems():
        tree.hlist.header_create(col, text=key, headerbackground='cyan')
        tree.hlist.column_width(col, chars=width)

    tree['opencmd'] = lambda dir=None, w=tree: opendir(w, dir)
    tree.hlist['header'] = True
    tree.hlist['separator'] = '~' # Default is gray
    tree.hlist['background'] = 'white' # Default is gray
    tree.hlist['selectforeground'] = 'white' # Default is gray
    tree.hlist['selectmode'] = 'extended' # Select multiple items
    tree.hlist['indent'] = 14 # Adjust indentation of children
    tree.hlist['wideselect'] = 1 # Color selection from end to end
    tree.hlist['font'] = _.font

    tds = lambda anchor, bg: Tix.DisplayStyle(
        anchor=anchor,
        bg=bg,
        itemtype='text',
        refwindow=tree.hlist,
        font=_.font
    )

    po_color = u'PeachPuff2'
    def refresh():
        try:
            _.curr.cogroup
        except AttributeError:
            return
        query = _.dbm.session.query(_.dbm.Order)
        if _.sc_mode == u's':
            query = query.filter_by(is_purchase=True)
        elif _.sc_mode == u'c':
            query = query.filter_by(is_sale=True)
        query = query.join(_.dbm.Order.parent)
        query = query.filter_by(name=_.curr.cogroup.name)
        query = query.order_by(_.dbm.Order.orderdate.desc())
        query = query.limit(nRecords.get())
        orders = query.all()

        tree.hlist.delete_all()
        for order in orders:
            hid = str(order.id)
            tree.hlist.add(hid, text=order.orderID, itemtype=Tix.TEXT, style=tds('w',po_color))
            tree.hlist.item_create(hid, col=H[u'日期'][0], text=order.orderdate, itemtype=Tix.TEXT, style=tds('w',po_color))
            tree.hlist.item_create(hid, col=H[u'品名'][0], text=u'{} ({})'.format(order.product.label(), order.product.specs), itemtype=Tix.TEXT, style=tds('w',po_color))
            tree.hlist.item_create(hid, col=H[u'訂單數量'][0], text=order.qty, itemtype=Tix.TEXT, style=tds('e',po_color))
            tree.hlist.item_create(hid, col=H[u'單位'][0], text=order.product.SKU, itemtype=Tix.TEXT, style=tds('w',po_color))
            tree.hlist.item_create(hid, col=H[u'價格'][0], text=order.price, itemtype=Tix.TEXT, style=tds('center',po_color))
#            tree.hlist.item_create(hid, col=H[u'總價'][0], text=u'{:,}'.format(int(round(order.subtotal))), itemtype=Tix.TEXT)
            tree.hlist.item_create(hid, col=H[u'出貨數量'][0], text=order.qty_shipped(), itemtype=Tix.TEXT, style=tds('e',po_color))
            tree.hlist.item_create(hid, col=H[u'發票數量'][0], text=order.qty_invoiced(), itemtype=Tix.TEXT, style=tds('e',po_color if order.all_invoiced() else 'tomato' ))
            tree.hlist.item_create(hid, col=H[u'總價'][0], text=round(order.shipped_value(),1), itemtype=Tix.TEXT, style=tds('e',po_color))
#            tree.hlist.item_create(hid, col=H[u'PO Closed?'][0], text=u'\u2610' if order.is_open else u'\u2612', itemtype=Tix.TEXT, style=tds('center',po_color))
            tree.hlist.item_create(hid, col=H[u'截止?'][0], text=u'\u26AA' if order.is_open else u'\u2605', itemtype=Tix.TEXT, style=tds('center',po_color))

            if len(order.shipments) + len(order.invoices):
                tree.setmode(hid, 'open')

#    try:
#        refresh()
#    except AttributeError:
#        print("AttributeError: CoGroup not defined")

    def opendir(tree, path):
        if _.debug:
            print 'HList path:', path
        entries = tree.hlist.info_children(path)
        if entries: # Show previously loaded entries
            for entry in entries:
                tree.hlist.show_entry(entry)
            return

        if u'shipment' not in path:
            # SHOW SHIPMENTS
#            order = _.dbm.session.query(_.dbm.Order).get(int(path))
            query = _.dbm.session.query(_.dbm.ShipmentItem)
            query = query.join(_.dbm.Order)
            query = query.filter(_.dbm.Order.id == int(path))
            query = query.join(_.dbm.Shipment)
            query = query.order_by(_.dbm.Shipment.shipmentdate.desc())
            shipments = query.all()
            nrecs = len(shipments)
            for i, rec in enumerate(shipments):
                hid = path+'~shipment:{}'.format(rec.id)
                tree.hlist.add(hid, itemtype=Tix.TEXT, text=rec.shipment.shipment_no)
                tree.hlist.item_create(hid, col=H[u'日期'][0], text=rec.shipment.shipmentdate, itemtype=Tix.TEXT)
                tree.hlist.item_create(hid, col=H[u'品名'][0], text=u' \u26DF #{}'.format(nrecs-i), itemtype=Tix.TEXT)
                tree.hlist.item_create(hid, col=H[u'出貨數量'][0], text=rec.qty, itemtype=Tix.TEXT, style=tds('e','DarkSeaGreen1'))
#                tree.hlist.item_create(hid, col=H[u'單位'][0], text=rec.order.product.UM, itemtype=Tix.TEXT)

                if rec.invoiceitem:
                    tree.setmode(hid, 'open')


        elif u'invoice' not in path:
            # SHOW INVOICES
            query = _.dbm.session.query(_.dbm.InvoiceItem)
            query = query.join(_.dbm.ShipmentItem)
            query = query.filter(_.dbm.ShipmentItem.id == int(path.split(":")[-1]))
            query = query.join(_.dbm.Invoice)
            query = query.order_by(_.dbm.Invoice.invoicedate.desc())
            invoices = query.all()
            nrecs = len(invoices)
            for i, rec in enumerate(invoices):
                hid = path+'~invoice:{}'.format(rec.id)
                tree.hlist.add(hid, itemtype=Tix.TEXT, text=rec.invoice.invoice_no)
                tree.hlist.item_create(hid, col=H[u'日期'][0], text=rec.invoice.invoicedate, itemtype=Tix.TEXT)
                tree.hlist.item_create(hid, col=H[u'品名'][0], text=u' \U0001F4B0 #{}'.format(nrecs-i), itemtype=Tix.TEXT)
                tree.hlist.item_create(hid, col=H[u'發票數量'][0], text=rec.qty, itemtype=Tix.TEXT, style=tds('e','RosyBrown1'))






    _.all_frame = frame
    _.all_frame_refresh = refresh
    return frame









