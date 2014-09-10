#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Tix
import tkMessageBox
from make_invoice import main as make_invoice
from pdf_tools import activity_report


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
        u'已付' : (11, 5),
    }

    tree_box = Tix.Frame(frame)
    tree_box.pack(side='top', fill='both', expand=1)
    tree = Tix.Tree(tree_box, options='columns {}'.format(len(H)))
    tree.pack(expand=1, fill='both', side='top')

    rb_box = Tix.Frame(frame)
    rb_box.pack(side='bottom', fill='x')

    def view_totals():
        '''Total up the columns of selected rows.'''
        totaldict = {}
        for shipment_id in tree.hlist.info_selection():
            sm = _.dbm.session.query(_.dbm.ShipmentItem).get(shipment_id)
            name = u'[{}] {}'.format(sm.order.product.specs, sm.order.product.label())
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

        tkMessageBox.showinfo(
            u'Summary of totals',
            '\n'.join(
                [u'{0}  \u26DF:{1[0]} {1[1]}  \U0001F4B0:{1[2]} {1[1]}  ${1[3]}'.format(
                    key, vals) for key, vals in totaldict.iteritems()]
            )
        )


    def create_invoice():
        '''Check if invoiceitem exists already. Currently limited to one.'''
        for shipment_id in tree.hlist.info_selection():
            if len(_.dbm.session.query(_.dbm.ShipmentItem).get(shipment_id).invoiceitem) > 0:
                return
        make_invoice(_, tree.hlist.info_selection())

    def create_report():
        '''Organized shipping history report that can be printed.

        Use selected rows to make a shipping history list.
        Like items are totaled and displayed at the bottom.'''
        activity_report.main(_)

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
        _.extwin.title(u"{} {}".format(_.curr.cogroup.name, _.loc(u"\u26DF Create Manifest", asText=True)))
        _.extwin.focus_set()

        _check_no = Tix.StringVar()
        tl=Tix.Label(_.extwin, text=u'Check #:')
        tl.grid(row=0,column=0, columnspan=2, sticky='nsew')
        te = Tix.Entry(_.extwin, textvariable=_check_no)
        te.grid(row=0,column=2, columnspan=2, sticky='nsew')

        # SUBMIT BUTTON
        tb = Tix.Button(_.extwin, textvariable=_.loc(u"\u2713 Submit"),
                        bg="lawn green",
                        command=lambda:submit(),
                        activebackground="lime green")
        tb.grid(row=100, column=0, columnspan=2, sticky='ew')
        # CANCEL BUTTON
        tb = Tix.Button(_.extwin, textvariable=_.loc(u"\u26D4 Cancel"),
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
                _.refresh()
            except:
                pass


    Tix.Button(
        rb_box, text=u'\U0001F440', bg=u'lawn green',
        command=view_totals, font=(_.font, 18, 'bold'),
    ).pack(side='left', fill='x')
    Tix.Button(
        rb_box, textvariable=_.loc(u'Create Invoice'), bg=u'lawn green',
        command=create_invoice, font=(_.font, 18, 'bold'),
    ).pack(side='left', fill='x')
    Tix.Button(
        rb_box, textvariable=_.loc(u'Activity Report'), bg=u'lawn green',
        command=create_report, font=(_.font, 18, 'bold'),
    ).pack(side=u'left', fill='x')
    Tix.Button(
        rb_box, textvariable=_.loc(u'Mark as Paid'), bg=u'lawn green',
        command=mark_paid, font=(_.font, 18, 'bold'),
    ).pack(side=u'left', fill='x')


    rb_vals = (20, 50, 100, 1000)
    options = dict(variable=nRecords, indicatoron=False)
    for val in rb_vals[::-1]:
        Tix.Radiobutton(rb_box, text=val, value=val, **options)\
            .pack(side='right')
    Tix.Label(rb_box, textvariable=_.loc(u'Number of records to show:'))\
        .pack(side='right')

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
#    tree['command'] = lambda *args: apply_selection()

    orderPopMenu = Tix.Menu(tree_box, tearoff=0)

    def orderoptions(event):
        orderPopMenu.post(event.x_root, event.y_root)
    tree.hlist.bind("<Double-Button-1>", orderoptions)

#    def apply_selection():
#        '''Show hlist selection code. Which is also the shipment record id.'''
#        print tree.hlist.info_selection()

    def edit_shipment():
        pass
    def edit_invoice():
        pass
    def delete_shipment():
        sid = tree.hlist.info_selection()[0]
        smi = _.dbm.session.query(_.dbm.ShipmentItem).get(sid)
        confirmation = tkMessageBox.askyesno(u'Delete Shipment Item',
            u'Confirm deletion:\n{0.shipment.shipmentdate} {0.order.product.name}'.format(smi))
        if confirmation:
            if len(smi.invoiceitem) >= 1:
                delete_invoice()

            nItems = len(smi.shipment.items)
            if nItems == 1:
                sm_id = smi.shipment.id
                _.dbm.session.query(_.dbm.Shipment).filter(_.dbm.Shipment.id == sm_id).delete()
            _.dbm.session.query(_.dbm.ShipmentItem).filter(_.dbm.ShipmentItem.id == sid).delete()
            _.dbm.session.commit()

            try:
                _.refresh()
            except:
                pass

    def delete_invoice():
        sid = tree.hlist.info_selection()[0]
        smi = _.dbm.session.query(_.dbm.ShipmentItem).get(sid)
        try:
            invi = smi.invoiceitem[0]
            if invi:
                confirmation = tkMessageBox.askyesno(u'Delete Invoice Item',
                    u'Confirm deletion:\n{0.invoice.invoicedate} {0.order.product.name}'.format(invi))

                if confirmation:
                    nItems = len(invi.invoice.items)
                    if nItems == 1:
                        invi_id = invi.invoice.id
                        _.dbm.session.query(_.dbm.Invoice).filter(_.dbm.Invoice.id == invi_id).delete()
                    _.dbm.session.query(_.dbm.InvoiceItem).filter(_.dbm.InvoiceItem.id == invi.id).delete()
                    _.dbm.session.commit()

                    try:
                        _.refresh()
                    except:
                        pass

        except IndexError:
            pass

    orderPopMenu.add_command(label=u'編輯出貨單', command=lambda: edit_shipment())
    orderPopMenu.add_command(label=u'編輯發票', command=lambda: edit_invoice())
    orderPopMenu.add_separator()
    orderPopMenu.add_command(label=u'刪除出貨單', command=lambda: delete_shipment())
    orderPopMenu.add_command(label=u'刪除發票', command=lambda: delete_invoice())

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
        try:
            _.curr.cogroup
        except AttributeError:
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
                tree.hlist.item_create(hid, col=H[u'已付'][0], text=u'\u2713' if invi.invoice.paid else u'\u203C', itemtype=Tix.TEXT, style=tds('w',inv_color if invi.invoice.paid else 'tomato'))

            if len(rec.invoiceitem) > 1:
                tree.setmode(hid, 'open')





    _.mi_frame = frame
    _.mi_frame_refresh = refresh
    return frame