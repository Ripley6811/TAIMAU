#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Tix
import tkMessageBox
import datetime

from utils import date_picker


def main(_, shipment_ids=None, invoice=None):
    '''Create a new invoice from a list of shipped items or review and edit
    an existing invoice.

    shipment_ids: List of shipment items to include in new invoice.
    invoice: Existing invoice for editing. If None, then create new invoice.'''

    #### NEW POPUP WINDOW: LIMIT TO ONE ####
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

    _.extwin = Tix.Toplevel(_.parent)
    _.extwin.title(u"{} {}".format(_.curr.cogroup.name, _.loc(u"+ PO", asText=True)))
    _.extwin.geometry(u'+{}+{}'.format(_.parent.winfo_rootx()+100, _.parent.winfo_rooty()))
    _.extwin.focus_set()

    head_frame = Tix.Frame(_.extwin)
    head_frame.pack(side='top', fill='x', expand=1)

    main_frame = Tix.Frame(_.extwin)
    main_frame.pack(side='top', fill='both', expand=1)


    #### VARIABLES FOR RECORD ENTRY ####
    ####################################
    if shipment_ids:
        shipments = [_.dbm.session.query(_.dbm.ShipmentItem).get(_id) for _id in shipment_ids]
    elif invoice:
        shipments = [item.shipmentitem for item in invoice.items]
    else:
        tkMessageBox.showerror(u'Invoice view error',
                               u'Empty shipment id list and no invoice id.')
    # InvoiceItem
    _order_id = []
    _shipment_id = []
    _qty = []

    # Invoice
    _invoice_no = Tix.StringVar()
    _invoice_no.trace('w', lambda *args: _invoice_no.set(_invoice_no.get().upper()[:10]))
    _seller = Tix.StringVar()
    _buyer = Tix.StringVar()
    _note = Tix.StringVar()
    _company_no = Tix.StringVar()

    _date = Tix.StringVar()


    if invoice:
        _invoice_no.set(invoice.invoice_no)
        _note.set(invoice.invoicenote)



    cell_config = dict(
        font= (_.font, 16, u'bold'),
        bg= u'cornsilk',
        height= 2,
        anchor='w',
    )




    if invoice:
        b = Tix.Button(head_frame, textvariable=_date, bg='DarkGoldenrod1',
                       font=(_.font, 20))
        b['command'] = lambda curr_date=invoice.invoicedate: pick_date(curr_date)
        b.grid(row=0, rowspan=3, column=4, columnspan=4, sticky='nsew')

        _date.set(invoice.invoicedate)

        def pick_date(curr_date):
            cal = date_picker.Calendar(head_frame,
                                       textvariable=_date,
                                       destroy=True,
                                       month=curr_date.month,
                                       year=curr_date.year,
                                       day=curr_date.day)
            cal.grid(row=0, rowspan=3, column=4, columnspan=4, sticky='nsew')
    else:
        cal = date_picker.Calendar(head_frame)
        cal.grid(row=0, rowspan=3, column=4, columnspan=4, sticky='nsew')
    head_frame.columnconfigure(4,weight=1)
#    riqi = u'貨單日期: {0.year}年 {0.month}月 {0.day}日'.format(order.shipments[0].shipmentdate)
#    tl=Tix.Label(main_frame, text=riqi, **cell_config)
#    tl.grid(row=1,column=4, columnspan=2, sticky='ew')

    tl=Tix.Label(head_frame, text=u'發票號碼:', **cell_config)
    tl.grid(row=0,column=0, sticky='nsew')
    te = Tix.Entry(head_frame, textvariable=_invoice_no, font=(_.font, 20, 'bold'))
    te.grid(row=0,column=1, sticky='nsew')

    query_config = dict(
        relief= 'sunken',
        font= (_.font, 18, u'bold',),
        bg= u'yellow'
    )

    buyer_box = Tix.Frame(head_frame)
    tl=Tix.Label(head_frame, text=u'買 受 人:', **cell_config)
    tl.grid(row=1,column=0, sticky='nsew')
    buyer = Tix.StringVar()
    if _.sc_mode == 'c':
        for branch in shipments[0].order.parent.branches:
            tr = Tix.Radiobutton(buyer_box, text=branch.name, value=branch.name,
                            variable=buyer, indicatoron=False, **query_config)
            tr.pack(side='left', fill='both', expand=1)
    else:
        for branch in (u'台茂', u'富茂', u'永茂'):
            tr = Tix.Radiobutton(buyer_box, text=branch, value=branch,
                            variable=buyer, indicatoron=False, **query_config)
            tr.pack(side='left', fill='both', expand=1)
    buyer_box.grid(row=1, column=1, sticky='nsew')

    tl=Tix.Label(head_frame, text=u'統一編號:', **cell_config)
    tl.grid(row=2,column=0, sticky='nsew')
    te = Tix.Label(head_frame, textvariable=_company_no, **cell_config)
    te.grid(row=2,column=1, sticky='nsew')
    buyer.trace('w', lambda a,b,c:
                _company_no.set(_.dbm.get_branch(buyer.get()).tax_id)
    )
    if invoice:
        buyer.set(invoice.buyer)
    else:
        buyer.set(shipments[0].order.buyer)




    cell_config = dict(
        font= (_.font, 15),
        bg= u'LightSteelBlue1',
        relief='raised',
    )
    for i, each in enumerate([u'品名',u'數量',u'單價',u'金額',u'備註']):
        tl=Tix.Label(main_frame, text=each, **cell_config)
        tl.grid(row=0,column=i*2, columnspan=2, sticky='nsew')
    Tix.Label(main_frame, text=u'銷售額合計', **cell_config).grid(row=50,column=2, columnspan=4, sticky='ew')
    Tix.Label(main_frame, text=u'統一發票專用章', **cell_config).grid(row=50,column=8, columnspan=2, sticky='ew')
    Tix.Label(main_frame, text=u'營  業  稅', **cell_config).grid(row=51,column=2, columnspan=4, sticky='ew')
    Tix.Label(main_frame, text=u'總      計', **cell_config).grid(row=52,column=2, columnspan=4, sticky='ew')


    cell_config = dict(
        relief= 'sunken',
        font= (_.font, 15, u'bold',),
        bg= u'wheat'
    )


    totaldict = {}
    for sm in shipments:
        name = u'{} ({})'.format(sm.order.product.label(), sm.order.product.specs)
        if totaldict.get(name) == None:
            totaldict[name] = [
                sm.qty * sm.order.product.units if sm.order.product.unitpriced else sm.qty,
                sm.order.product.UM if sm.order.product.unitpriced else sm.order.product.SKU,
                sm.order.price,
                sm.order.product.units if sm.order.product.unitpriced else 1,
                sm.order.orderID,
                sm.order.product.unitpriced
            ]
        else:
            totaldict[name][0] += sm.qty * sm.order.product.units if sm.order.product.unitpriced else sm.qty

    totals = []
    r = lambda x: int(x) if x.is_integer() else x
    for row, (key, vals) in enumerate(totaldict.iteritems()):
        try:
            vals[0] = r(vals[0])
        except AttributeError as e:
            print "ATTRIBUTE ERROR CAUGHT:", e
        try:
            vals[2] = r(vals[2])
        except AttributeError as e:
            print "ATTRIBUTE ERROR CAUGHT:", e
        Tix.Label(main_frame, text=u' {} '.format(key), **cell_config).grid(row=row+1,column=0, columnspan=2, sticky='nsew')
        Tix.Label(main_frame, text=u' {0} {1} '.format(*vals), **cell_config).grid(row=row+1,column=2, columnspan=2, sticky='nsew')
        Tix.Label(main_frame, text=u' $ {2} '.format(*vals), **cell_config).grid(row=row+1,column=4, columnspan=2, sticky='nsew')
        totals.append( vals[0] * vals[2] )
        Tix.Label(main_frame, text=u' $ {} '.format(totals[-1]), **cell_config).grid(row=row+1,column=6, columnspan=2, sticky='nsew')
        Tix.Label(main_frame, text=u' PO:{4} '.format(*vals), **cell_config).grid(row=row+1,column=8, columnspan=2, sticky='nsew')
    total = int(round(sum(totals), 0))
    tax = int(round(0.05 * total, 0))
    taxtotal = total + tax
    Tix.Label(main_frame, text=u' $ {} '.format(total), **cell_config).grid(row=50,column=6, columnspan=2, sticky='ew')
    Tix.Label(main_frame, text=u' $ {} '.format(tax), **cell_config).grid(row=51,column=6, columnspan=2, sticky='ew')
    Tix.Label(main_frame, text=u' $ {} '.format(taxtotal), **cell_config).grid(row=52,column=6, columnspan=2, sticky='ew')


    seller_box = Tix.Frame(main_frame)
    seller = Tix.StringVar()
    seller.set(shipments[0].order.seller)
    if _.sc_mode == 's':
        for branch in shipments[0].order.parent.branches:
            tr = Tix.Radiobutton(seller_box, text=branch.name, value=branch.name,
                            variable=seller, indicatoron=False, **query_config)
            tr.pack(side='left', fill='both', expand=1)
            if seller.get() == branch.name:
                tr.invoke()
    else:
        for branch in (u'台茂', u'富茂', u'永茂'):
            tr = Tix.Radiobutton(seller_box, text=branch, value=branch,
                            variable=seller, indicatoron=False, **query_config)
            tr.pack(side='left', fill='both', expand=1)
    seller_box.grid(row=51, rowspan=2, column=8, columnspan=2, sticky='nsew')
    seller.trace('w', lambda a,b,c: seller.get() ) # Forces an update (!?)
    if invoice:
        seller.set(invoice.seller)
    else:
        seller.set(shipments[0].order.seller)


    # Preset the invoice beginning digits from previous invoice
    if invoice == None:
        try:
            query = _.dbm.session.query(_.dbm.Invoice)
            query = query.filter(_.dbm.Invoice.seller == seller.get())
            query = query.order_by(_.dbm.Invoice.invoicedate.desc())
            latest_invi = query.first()
            _invoice_no.set(latest_invi.invoice_no[:6])
        except:
            pass





    sep = Tix.Frame(main_frame, relief='ridge', height=8, bg="LightSteelBlue1")
    sep.grid(row=999, column=0, columnspan=20, sticky='nsew')







    # SUBMIT BUTTON
    tb = Tix.Button(main_frame, textvariable=_.loc(u"\u2713 Submit"),
                    bg="lawn green",
                    command=lambda:submit(invoice),
                    activebackground="lime green")
    tb.grid(row=1000, column=0, columnspan=8, sticky='ew')

    # CANCEL BUTTON
    tb = Tix.Button(main_frame, textvariable=_.loc(u"\u26D4 Cancel"),
                    bg="tomato",
                    command=lambda:exit_win(),
                    activebackground="tomato")
    tb.grid(row=1000, column=8, columnspan=6, sticky='ew')

    def exit_win():
        _.extwin.destroy()

    def submit(invoice):
        if len(_invoice_no.get()) != 10:
            ok = tkMessageBox.askokcancel(u'Invoice number validation failure.',
                       u'Invoice number is not 10 characters\ncontinue anyway?')
            if not ok:
                _.extwin.focus_set()
                return
        if invoice == None:
            if cal.selection in (None, u''):
                return
            invoice = _.dbm.existing_invoice(_invoice_no.get(),
                                             cal.selection,
                                             _.curr.cogroup.name)
            if invoice:
                confirm = tkMessageBox.askyesno(u'Invoice number exists.',
                                      u'Add items to existing invoice?')
                if not confirm:
                    _.extwin.focus_set()
                    return
            if invoice == None:
                invoice = _.dbm.Invoice(
                    invoicedate = cal.selection,
                    invoice_no = _invoice_no.get().upper(),
                    invoicenote = _note.get(),
                    seller = seller.get(),
                    buyer = buyer.get(),
                )
            for sm in shipments:
                item = _.dbm.InvoiceItem(
                    order = sm.order,
                    shipmentitem = sm,
                    invoice = invoice,
                    qty = sm.qty,
                )
                _.dbm.session.add(item)
            _.dbm.session.commit()
        else: #if invoice
            invoice.invoicedate = datetime.date(*[int(z) for z in _date.get().split(u'-')])
            invoice.invoice_no = _invoice_no.get().upper()
            invoice.invoicenote = _note.get()
            invoice.seller = seller.get()
            invoice.buyer = buyer.get()
            _.dbm.session.commit()

        exit_win()

        try:
            for ref in _.refresh:
                ref()
        except:
            pass




if __name__ == '__main__':
    main()











