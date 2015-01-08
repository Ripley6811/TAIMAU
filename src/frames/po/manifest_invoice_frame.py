#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Tix
import tkMessageBox
from invoice_form import main as invoice
from manifest_form import main as manifest
import label_prep_frame
#print 'invoice', type(frames.po.invoice)

U_PENCIL = u'\u270e'
U_TRUCK = u'\u26df'
U_DOLLAR = u'\uff04'
U_EXCLAMATION = u'\u203c'
U_CHECKMARK = u'\u2713'
U_STOPSIGN = u'\u26d4'
U_EYES = u'\U0001F440'
U_MONEYBAG = u'\U0001F4B0'

COL_PO = u'cyan'
COL_MANIFEST = u'PeachPuff2'
COL_INVOICE_PAID = u'gold'
COL_INVOICE_NOT_PAID = u'tomato'

def main(_):
    """Set up the comprehensive view for all records.

    Button to set number of records to load. Default to 25."""


    frame = Tix.Frame(_.po_frame)


    nRecords = Tix.StringVar()
    nRecords.set(25)
    nRecords.trace('w', lambda a,b,c: refresh())

    # Headers and (column number, col width)
    Hwidths = [
        (U_PENCIL, 3, COL_PO),
        (u'訂單編號', 15, COL_PO),
        (u'品名', 22, COL_PO),
        (U_TRUCK, 3, COL_MANIFEST),
        (u'出貨編號', 13, COL_MANIFEST),
        (u'日期', 9, COL_MANIFEST),
        (u'數量', 8, COL_MANIFEST),
        (u'單位', 5, COL_MANIFEST),
        (U_DOLLAR, 3, COL_INVOICE_PAID),
        (u'發票號碼', 13, COL_INVOICE_PAID),
        (u'發票日期', 9, COL_INVOICE_PAID),
        (u'發票數量', 8, COL_INVOICE_PAID),
        (u'價格', 8, COL_INVOICE_PAID),
        (u'規格', 8, COL_INVOICE_PAID),
        (u'總價', 10, COL_INVOICE_PAID),
        (u'已付', 13, COL_INVOICE_PAID),
    ]
    H = dict()
    for i, each in enumerate(Hwidths):
        H[each[0]] = (i, each[1], each[2])

    tree_box = Tix.Frame(frame)
    tree_box.pack(side='top', fill='both', expand=1)
    tree = Tix.Tree(tree_box, options='columns {}'.format(len(H)))
    tree.pack(expand=1, fill='both', side='top')

    rb_box = Tix.Frame(frame)
    rb_box.pack(side='bottom', fill='x')

    def view_totals():
        '''Total up the columns of selected rows.'''
        totaldict = {}
        totalshipped = 0
        totalinvoiced = 0
        totalvalue = 0
        for shipment_id in tree.hlist.info_selection():
            sm = _.dbm.session.query(_.dbm.ShipmentItem).get(shipment_id)
#            name = u'[{}] {}'.format(sm.order.product.specs, sm.order.product.label())
            name = u'{}'.format(sm.order.product.specs, sm.order.product.label())
            if totaldict.get(name) == None:
                totaldict[name] = [
                    sm.qty,
                    sm.order.product.SKU,
                    sm.invoiceitem[0].qty if sm.invoiceitem else 0,
                    sm.invoiceitem[0].total() if sm.invoiceitem else 0
                ]
            else:
                totaldict[name][0] += sm.qty
                totaldict[name][2] += sm.invoiceitem[0].qty if sm.invoiceitem else 0
                totaldict[name][3] += sm.invoiceitem[0].total() if sm.invoiceitem else 0
            totalshipped += totaldict[name][0]
            totalinvoiced += totaldict[name][2]
            totalvalue += totaldict[name][3]

        tkMessageBox.showinfo(
            u'Summary of totals',
            u'\n'.join(
                [u'{0}  \u26DF:{1[0]} {1[1]}  \U0001F4B0:{1[2]} {1[1]}  ${1[3]:,}'.format(
                    key, vals) for key, vals in totaldict.iteritems()]
            )
            + u'\n\nTOTAL'
            + u'\n      Shipped:  {:,}'.format(totalshipped)
            + u'\n      Invoiced:  {:,}'.format(totalinvoiced)
            + u'\n      Value:  ${:,}'.format(totalvalue)
        )


    def create_invoice():
        '''Check if invoiceitem exists already. Currently limited to one.'''
        for shipment_id in tree.hlist.info_selection():
            if len(_.dbm.session.query(_.dbm.ShipmentItem).get(shipment_id).invoiceitem) > 0:
                return
        invoice(_, tree.hlist.info_selection())

        try:
            for ref in _.refresh:
                ref()
        except AttributeError:
            pass


    def print_shipmentitem_labels():
        '''Organized shipping history report that can be printed.

        Use selected rows to make a shipping history list.
        Like items are totaled and displayed at the bottom.'''
        label_prep_frame.main(_, tree.hlist.info_selection())


    def mark_paid():
        '''Mark an invoice as paid.

        Auto-select rows from same invoice if not already selected.'''
        try:
            if _.extwin.state() == 'normal':
                if _.curr.cogroup.name in _.extwin.title():
                    # Focus existing frame and return
                    _.extwin.focus_set()
                    return
                else:
                    # Destroy existing frame and make new one
                    _.extwin.destroy()
        except:
            # Continue with frame creation
            pass

        _.extwin = Tix.Toplevel(width=700)
        _.extwin.title(u"{} {}".format(_.curr.cogroup.name, _.loc(U_TRUCK+u" Create Manifest", asText=True)))
        _.extwin.focus_set()

        _check_no = Tix.StringVar()
        tl=Tix.Label(_.extwin, text=u'Check #:')
        tl.grid(row=0,column=0, columnspan=2, sticky='nsew')
        te = Tix.Entry(_.extwin, textvariable=_check_no)
        te.grid(row=0,column=2, columnspan=2, sticky='nsew')

        # SUBMIT BUTTON
        tb = Tix.Button(_.extwin, textvariable=_.loc(U_CHECKMARK+u" Submit"),
                        bg="lawn green",
                        command=lambda:submit(),
                        activebackground="lime green")
        tb.grid(row=100, column=0, columnspan=2, sticky='ew')
        # CANCEL BUTTON
        tb = Tix.Button(_.extwin, textvariable=_.loc(U_STOPSIGN+u" Cancel"),
                        bg="tomato",
                        command=lambda:_.extwin.destroy(),
                        activebackground="tomato")
        tb.grid(row=100, column=2, columnspan=2, sticky='ew')

        def submit():
            for sid in tree.hlist.info_selection():
                sm = _.dbm.session.query(_.dbm.ShipmentItem).get(sid)
                sm.invoiceitem[0].invoice.paid = True
                sm.invoiceitem[0].invoice.check_no = _check_no.get()
            _.dbm.session.commit()

            _.extwin.destroy()
            try:
                for ref in _.refresh:
                    ref()
            except AttributeError:
                pass

    #--- ADD BUTTONS TO BOTTOM OF PANE.
    Tix.Button(
        rb_box, text=U_EYES, bg=u'lawn green',
        command=view_totals, font=(_.font, 18, 'bold'),
    ).pack(side='left', fill='x')
    Tix.Button(
        rb_box, textvariable=_.loc(u'Create Invoice'), bg=u'lawn green',
        command=create_invoice, font=(_.font, 18, 'bold'),
    ).pack(side='left', fill='x')
    Tix.Button(
        rb_box, textvariable=_.loc(u'Print Labels'), bg=u'lawn green',
        command=print_shipmentitem_labels, font=(_.font, 18, 'bold'),
    ).pack(side=u'left', fill='x')
    Tix.Button(
        rb_box, textvariable=_.loc(u'Mark as Paid'), bg=u'lawn green',
        command=mark_paid, font=(_.font, 18, 'bold'),
    ).pack(side=u'left', fill='x')


    rb_vals = (25, 50, 100, 500, 1000)
    options = dict(variable=nRecords, indicatoron=False)
    for val in rb_vals[::-1]:
        Tix.Radiobutton(rb_box, text=val, value=val, **options)\
            .pack(side='right')
    Tix.Label(rb_box, textvariable=_.loc(u'Number of records to show:'))\
        .pack(side='right')

    totalvalue = Tix.StringVar()
    Tix.Label(rb_box, textvariable=totalvalue)
    totalvalue.set(u'$0')

    #--- ADD HEADER LABELS TO TREE (TABLE) VIEW
    for key, (column, width, color) in H.iteritems():
        tree.hlist.header_create(column, text=key, headerbackground=color)
        tree.hlist.column_width(column, chars=width)

    #--- SET TREE (TABLE) CONFIGURATION OPTIONS
#    tree['opencmd'] = lambda dir=None, w=tree: opendir(w, dir)
    tree.hlist['header'] = True
    tree.hlist['separator'] = '~' # Default is gray
    tree.hlist['background'] = 'white' # Default is gray
    tree.hlist['selectforeground'] = 'white' # Default is gray
    tree.hlist['selectmode'] = 'extended' # Select multiple items
    tree.hlist['indent'] = 14 # Adjust indentation of children
    tree.hlist['wideselect'] = 1 # Color selection from end to end
    tree.hlist['font'] = _.font
#    tree['command'] = lambda *args: apply_selection()

    orderPopMenu = Tix.Menu(tree_box, tearoff=0)

    def orderoptions(event):
        orderPopMenu.post(event.x_root, event.y_root)
    tree.hlist.bind("<Double-Button-1>", orderoptions)


    def edit_shipment():
        sid = tree.hlist.info_selection()[0]
        smi = _.dbm.session.query(_.dbm.ShipmentItem).get(sid)
        manifest(_, manifest=smi.shipment, refresh=refresh)

    def edit_invoice():
        sid = tree.hlist.info_selection()[0]
        smi = _.dbm.session.query(_.dbm.ShipmentItem).get(sid)
        if len(smi.invoiceitem):
            invoice(_, invoice=smi.invoiceitem[0].invoice)
        try:
            for ref in _.refresh:
                ref()
        except AttributeError:
            pass

    def delete_shipmentitem():
        sid = tree.hlist.info_selection()[0]
        smi = _.dbm.session.query(_.dbm.ShipmentItem).get(sid)
        confirmation = tkMessageBox.askyesno(u'Delete Shipment Item',
            u'Confirm deletion:\n{0.shipment.shipmentdate} {0.order.product.name}'.format(smi))
        if confirmation:
            # Delete an associated invoice item.
            if len(smi.invoiceitem) >= 1:
                delete_invoiceitem()

            # Temp link to shipment/manifest record and delete item.
            ship_main = smi.shipment
            _.dbm.session.query(_.dbm.ShipmentItem)\
                         .filter(_.dbm.ShipmentItem.id == sid)\
                         .delete()

            # Delete manifest if no items are attached.
            if len(ship_main.items) == 0:
                sm_id = ship_main.id
                _.dbm.session.query(_.dbm.Shipment)\
                             .filter(_.dbm.Shipment.id == sm_id)\
                             .delete()

            # Commit changes.
            _.dbm.session.commit()

            try:
                for ref in _.refresh:
                    ref()
            except AttributeError:
                pass

    def delete_invoiceitem():
        sid = tree.hlist.info_selection()[0]
        smi = _.dbm.session.query(_.dbm.ShipmentItem).get(sid)
        try:
            invi = smi.invoiceitem[0]
            if invi:
                confirmation = tkMessageBox.askyesno(u'Delete Invoice Item',
                    u'Confirm deletion:\n{0.invoice.invoicedate} {0.order.product.name}'.format(invi))

                if confirmation:
                    # Link to main invoice and delete invoice item.
                    inv_main = invi.invoice
                    _.dbm.session.query(_.dbm.InvoiceItem)\
                                 .filter(_.dbm.InvoiceItem.id == invi.id)\
                                 .delete()

                    # Delete main invoice if there are no items.
                    if len(inv_main.items) == 0:
                        inv_id = inv_main.id
                        _.dbm.session.query(_.dbm.Invoice)\
                                     .filter(_.dbm.Invoice.id == inv_id)\
                                     .delete()

                    # Commit changes to database.
                    _.dbm.session.commit()

                    try:
                        for ref in _.refresh:
                            ref()
                    except AttributeError:
                        pass

        except IndexError:
            pass

    orderPopMenu.add_command(label=_.loc(u'View/edit manifest',1),
                             command=lambda: edit_shipment())
    orderPopMenu.add_command(label=_.loc(u'View/edit invoice',1),
                             command=lambda: edit_invoice())
    orderPopMenu.add_separator()
    orderPopMenu.add_command(label=_.loc(u'Delete manifest item',1),
                             command=lambda: delete_shipmentitem())
    orderPopMenu.add_command(label=_.loc(u'Delete invoice item',1),
                             command=lambda: delete_invoiceitem())

    #--- WRAPPER FOR MAKING TREE LIST ITEM STYLE
#    tds = lambda anchor, bg: Tix.DisplayStyle(
#        anchor=anchor,
#        bg=bg,
#        itemtype='text',
#        refwindow=tree.hlist,
#        font=_.font
#    )
    def _item_opts(hid, anchor=u'w', bg=u'grey'):
        _retval = dict(
            entry=hid,
            itemtype= Tix.TEXT,
            style= Tix.DisplayStyle(
                anchor=anchor,
                bg=bg,
                itemtype='text',
                refwindow=tree.hlist,
                font=_.font,
            )
        )
        return _retval

    mani_color = u'PeachPuff2'
    def refresh():
        try:
            _.curr.cogroup
        except KeyError:
            return
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
            tree.hlist.add(text=u'', **_item_opts(hid, 'w', COL_PO))
            tree.hlist.item_create(col=H[u'訂單編號'][0], text=rec.order.orderID, **_item_opts(hid, 'w', COL_PO))
            tree.hlist.item_create(col=H[u'品名'][0], text=u'{} ({})'.format(rec.order.product.label(), rec.order.product.specs), **_item_opts(hid, 'w', COL_PO))

            tree.hlist.item_create(col=3, text=u'', **_item_opts(hid, 'w', COL_MANIFEST))
            tree.hlist.item_create(col=H[u'出貨編號'][0], text=rec.shipment.shipment_no, **_item_opts(hid, 'w', COL_MANIFEST))
            tree.hlist.item_create(col=H[u'日期'][0], text=u'{0.month}月{0.day}日'.format(rec.shipment.shipmentdate), **_item_opts(hid, 'w', COL_MANIFEST))
            tree.hlist.item_create(col=H[u'數量'][0], text=rec.qty, **_item_opts(hid, 'e', COL_MANIFEST))
            tree.hlist.item_create(col=H[u'單位'][0], text=rec.order.product.SKU, **_item_opts(hid, 'w', COL_MANIFEST))

            if rec.invoiceitem:
                invi = rec.invoiceitem[0] #alias
                # SET INVOICE LINE COLOR BASED ON PAYMENT RECORDED OR NOT.
                invi_color = COL_INVOICE_PAID if invi.invoice.paid else COL_INVOICE_NOT_PAID
                # SET CHECK PAID TEXT. EITHER CHECK NUMBER OR SYMBOL.
                check_text = invi.invoice.check_no if invi.invoice.paid else U_EXCLAMATION
                if not check_text:
                    check_text = U_CHECKMARK

                tree.hlist.item_create(col=8, text=u'', **_item_opts(hid, 'w', invi_color))
                tree.hlist.item_create(col=H[u'發票號碼'][0], text=invi.invoice.invoice_no, **_item_opts(hid, 'w',invi_color))
                tree.hlist.item_create(col=H[u'發票日期'][0], text=u'{0.month}月{0.day}日'.format(invi.invoice.invoicedate), **_item_opts(hid, 'w',invi_color))
                tree.hlist.item_create(col=H[u'發票數量'][0], text=invi.qty, **_item_opts(hid, 'e',invi_color))
                tree.hlist.item_create(col=H[u'價格'][0], text=invi.order.price, **_item_opts(hid, 'e', invi_color))
                tree.hlist.item_create(col=H[u'規格'][0], text=invi.order.product.units if invi.order.product.unitpriced else u'', **_item_opts(hid, 'e', invi_color))
                tree.hlist.item_create(col=H[u'總價'][0], text=u'{:,}'.format(invi.total()), **_item_opts(hid, 'e', invi_color))
                tree.hlist.item_create(col=H[u'已付'][0], text=check_text, **_item_opts(hid, 'w', invi_color))

            #XXX: What does this for?...
            if len(rec.invoiceitem) > 1:
                tree.setmode(hid, 'open')





    _.mi_frame = frame
    _.mi_frame.refresh = refresh

    try:
        _.refresh.append(refresh)
    except KeyError:
        _.refresh = [refresh,]

    return frame