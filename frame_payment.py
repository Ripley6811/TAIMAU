#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Tkinter as Tk
from Tkinter import EXTENDED, TOP, END, N, S, E, W, BOTTOM, X
import tkMessageBox
import ttk
import tkFont
import date_picker as dp
import datetime
import Tix



def set_invoice_frame(frame, info):
    info.invoices = info.__class__()
    info.invoices.codes = dict()
    info.invoices.selection = Tk.StringVar()
#    incoming = info.incoming = False if info.src == 'Sales' else True

    frameIn = ttk.Frame(frame)

    info.invoices.filterterm_SV = Tk.StringVar()

    tle = Tix.LabelEntry(frameIn, label=u'Filter:')
    tle.entry.configure(textvariable=info.invoices.filterterm_SV)
    tle.pack(side=TOP, fill=X)

    create_payment_button = Tk.Button(frameIn, text=u'$ $ $ Multiple Invoice Payment Information $ $ $',
                                       bg=u'light salmon')
    create_payment_button.pack(side=BOTTOM, fill=X)

    scrollbar2 = Tk.Scrollbar(frameIn, orient=Tk.VERTICAL)
    info.listbox.rec_invoices = Tk.Listbox(frameIn, selectmode=EXTENDED,
                         yscrollcommand=scrollbar2.set,
                         font=(info.settings.font, "12"), height=100, exportselection=0)
#    info.listbox.rec_invoices.bind("<Double-Button-1>", lambda _:copyrecord(info,True))
    scrollbar2.config(command=info.listbox.rec_invoices.yview)
    scrollbar2.pack(side=Tk.RIGHT, fill=Tk.Y)
    info.listbox.rec_invoices.pack(side=TOP, fill=Tk.BOTH)


    def store_indices(info):
        indices = map(int, info.listbox.rec_invoices.curselection())
        info.invoices.selection.set(indices)


    def create_payment():
#        indices = map(int, info.listbox.rec_invoices.curselection())
#        invoices = [info.invoices.invoice_recs[i][-1] for i in indices]
        create_payment_form()


    create_payment_button['command'] = create_payment


    # Add right-click popup menu
    def refresh_invoice_listbox():
        # Add previous orders to order listbox
        info.listbox.rec_invoices.delete(0, END)

        # List of order summaries
        query = info.dmv2.session.query
        Invoice = info.dmv2.Invoice
        InvoiceItem = info.dmv2.InvoiceItem
        Order = info.dmv2.Order
        one_year = datetime.date.today() - datetime.timedelta(366)
        invoice_recs = query(InvoiceItem, Order, Invoice).join('order')\
                        .filter_by(group = info.curr_company).join('invoice')\
                        .filter(Invoice.invoicedate > one_year)\
                        .order_by(Invoice.invoicedate.desc()).all()
        info.invoices.invoice_recs = invoice_recs

        tmp = [rec[0].listbox_summary() for rec in invoice_recs]

        #TODO: Different colors for different products. Not necessary...
        for i, each in enumerate(tmp):
            shipped_color = dict(bg=u'SlateGray4', fg=u'gray79',
                                 selectbackground=u'tomato',
                                 selectforeground=u'black')
            no_ship_color = dict(bg=u'khaki', selectbackground=u'yellow',
                                 selectforeground=u'black')
            info.listbox.rec_invoices.insert(i, each)
            ins_colors = shipped_color if invoice_recs[i][2].paid else no_ship_color
            info.listbox.rec_invoices.itemconfig(i, ins_colors)
    info.method.refresh_invoice_listbox = refresh_invoice_listbox

    info.listbox.rec_invoices.bind("<Double-Button-1>", lambda _: display_invoice_for_edit(info))
    info.listbox.rec_invoices.bind("<ButtonRelease-1>", lambda _: store_indices(info))


    orderPopMenu = Tk.Menu(frameIn, tearoff=0)

    def delete_order(info):
        inv_item, _, _ = info.invoices.invoice_recs[info.listbox.rec_invoices.index(Tk.ACTIVE)]
        info.dmv2.session.query(info.dmv2.InvoiceItem).filter_by(id=inv_item.id).delete()
        info.dmv2.session.commit()
        info.method.reload_orders(info)
        info.method.refresh_listboxes(info)
#        info.method.refresh_manifest_listbox()
        info.method.refresh_invoice_listbox()

    orderPopMenu.add_command(label=u'刪除', command=lambda: delete_order(info))

    def orderoptions(event):
        orderPopMenu.post(event.x_root, event.y_root)
    info.listbox.rec_invoices.bind("<Button-3>", orderoptions)

    frameIn.pack(fill=Tk.BOTH)

    def apply_list_filter(*args):
        lb = info.listbox.rec_invoices # Temp short name
        ft = info.invoices.filterterm_SV.get() # Temp short name
        for i in range(lb.size()):
            if ft in lb.get(i):
                lb.itemconfig(i, fg=u'black')
            else:
                lb.itemconfig(i, fg=u'gray72')

    info.invoices.filterterm_SV.trace('w',apply_list_filter)


    def create_payment_form():
        fi = Tix.Toplevel(width=700)
        fi.title(u"New Invoice Form")

        def date_picker():
            _=dp.Calendar(fi, textvariable=date_SV)
            _.grid(row=0, column=0, rowspan=30, columnspan=6, sticky=W+E+N+S)

        paid_BV = Tk.BooleanVar()
        paid_BV.set(True)
        date_SV = Tk.StringVar()
        check_SV = Tk.StringVar()
        total_SV = Tk.StringVar()
        count_SV = Tk.StringVar()
        inv_names_SV = Tk.StringVar()

        ttk.Label(fi, text=u'Total:', anchor=E).grid(row=1, column=0, sticky=W+E)
        ttk.Label(fi, textvariable=total_SV, anchor=W).grid(row=1, column=1, columnspan=2, sticky=W+E)

        ttk.Label(fi, text=u'Invoice(s):', anchor=E).grid(row=2, column=0, sticky=W+E)
        ttk.Label(fi, textvariable=count_SV).grid(row=2, column=1, sticky=W+E)
        ttk.Label(fi, textvariable=inv_names_SV, anchor=W).grid(row=2, column=10, sticky=W+E)

        ttk.Label(fi, text=u'Pay Date:', anchor=E).grid(row=3, column=0, sticky=W+E)
        ttk.Button(fi, textvariable=date_SV, command=date_picker).grid(row=3, column=1, columnspan=2, sticky=W)
        date_SV.set(datetime.date.today())

        ttk.Label(fi, text=u'Mark invoice(s) as paid?').grid(row=1000,column=0)
        Tk.Radiobutton(fi, text="Yes", variable=paid_BV, value=True)\
                .grid(row=1000,column=1)
        Tk.Radiobutton(fi, text="No", variable=paid_BV, value=False)\
                .grid(row=1000,column=2)

        ttk.Label(fi, text=u'Check number').grid(row=1001,column=0)
        ttk.Entry(fi, textvariable=check_SV, width=20).grid(row=1001,column=1,columnspan=2)


        sb = Tk.Button(fi, text="Update & Close Window")
        sb.grid(row=1003,column=0,columnspan=3)

        def submit_changes():
            indices = eval(info.invoices.selection.get())
            invoices = set([info.invoices.invoice_recs[i][-1] for i in indices])
            for each in invoices:
                query = info.dmv2.session.query
                Invoice = info.dmv2.Invoice
                q = query(Invoice).filter_by(invoice_no=each.invoice_no)
                q.update(dict(
                    check_no=check_SV.get(),
                    paid=paid_BV.get(),
                    paydate=datetime.date(*map(int,date_SV.get().split('-'))),
                ))
            info.dmv2.session.commit()
            fi.destroy()
            info.method.reload_orders(info)
            info.method.refresh_listboxes(info)
            info.method.refresh_invoice_listbox()
        sb['command'] = submit_changes


        def update_total(*args):
            indices = eval(info.invoices.selection.get())
            invoices = set([info.invoices.invoice_recs[i][-1] for i in indices])

            value = sum([inv.taxtotal() for inv in invoices])
            total_SV.set(u'${:,.2f}'.format(value))

            invoice_numbers = set([inv.invoice_no for inv in invoices])
            inv_names_SV.set(u', '.join(invoice_numbers))
            count_SV.set(u'({})'.format(len(invoice_numbers)))
        info.invoices.selection.trace('w', update_total)
        # Enter initial values.
        update_total()


def display_invoice_for_edit(info, inv_item=None):
    lindex = info.listbox.rec_invoices.index(Tk.ACTIVE)
    if not inv_item:
        inv_item = info.invoices.invoice_recs[lindex][0] #tuple(Shipment, Order)

    invoice = inv_item.invoice
    inv_no = inv_item.invoice_no
    query_id = inv_item.id
    if inv_no in [None,u'None',u'']:
        tkMessageBox.showerror(u'Bad invoice number',u'Invoice number not entered.\nShowing single record invoice...')
        inv_no = u'NOT ENTERED'
        invoiceset = [inv_item]
    else:
        invoiceset = invoice.items
#    print repr(inv_no), repr(invoiceset)
    orderset = [inv.order for inv in invoiceset]

    try:
        if info.invoiceWin.state() == 'normal':
            info.invoiceWin.focus_set()
        return
    except:
        pass

    info.invoiceWin = Tk.Toplevel(width=1200, height=600)
    info.invoiceWin.title(u"Invoice: {}".format(inv_no))


    yscrollbar = Tk.Scrollbar(info.invoiceWin)
    yscrollbar.grid(row=0, column=1, sticky=N+S)
    xscrollbar = Tk.Scrollbar(info.invoiceWin, orient=Tk.HORIZONTAL)
    xscrollbar.grid(row=1, column=0, sticky=E+W)
    canvas = Tk.Canvas(info.invoiceWin, width=900, height=600, #scrollregion=(0, 0, 1200, 600),
                yscrollcommand=yscrollbar.set,
                xscrollcommand=xscrollbar.set)
    canvas.grid(row=0, column=0, sticky=N+S+E+W)
    yscrollbar.config(command=canvas.yview)
    xscrollbar.config(command=canvas.xview)

    #
    # create canvas contents

    frame = Tk.Frame(canvas)
#    frame.rowconfigure(1, weight=1)
#    frame.columnconfigure(1, weight=1)

    def submit_changes(info):
        #Check field entries
        updates = dict(
            paid= allpaid.get(),
        )
        if allpaid.get() and not isinstance(invoice.paydate,datetime.date):
            updates.update(paydate= datetime.date.today())
        if check_no.get():
            updates.update(check_no= check_no.get())
            if not allpaid.get():
                confirmed = tkMessageBox.askyesno(u'Mismatch error',u'You checked "not paid" but entered a check number...\nContinue with submission?')
                if not confirmed:
                    info.invoiceWin.focus_set()
                    return False

        info.invoiceWin.destroy()

        info.dmv2.session.query(info.dmv2.Invoice).filter_by(invoice_no=inv_no).update(updates)
        info.dmv2.session.commit()

        info.method.reload_orders(info)
        info.method.refresh_listboxes(info)
        info.method.refresh_invoice_listbox()
#        for index in info.invoices.redo_indices:
#            info.listbox.rec_invoices.selection_set(index)




    cell_config = dict(
        font= (info.settings.font, "15", u'bold'),
        bg= u'cornsilk',
        height=2,
    )


    branch = info.dmv2.get_branch(invoice.buyer)


    #TODO: Auto-fill the first two letters from previous invoice
    Tk.Label(frame, text=u'發票號碼: {}'.format(u' '.join(inv_no)), **cell_config).grid(row=0,column=0, columnspan=2, sticky=Tk.W+Tk.E)
#    Tk.Label(frame, text=).grid(row=1,column=0, columnspan=2, sticky=Tk.W+Tk.E)

    cell_config.update(anchor=Tk.W)

    kehu = u'買 受 人: {}'.format(branch.fullname)
    Tk.Label(frame, text=kehu, **cell_config).grid(row=2,column=0, columnspan=2, sticky=Tk.W+Tk.E)

    tongyi = u'統一編號: {}'.format(u' '.join(branch.tax_id))
    Tk.Label(frame, text=tongyi, **cell_config).grid(row=3,column=0, columnspan=2, sticky=Tk.W+Tk.E)

    riqi = u'中 華 民 國 103年 {0.month}月 {0.day}日'.format(invoice.invoicedate)
    Tk.Label(frame, text=riqi, **cell_config).grid(row=3,column=2, columnspan=2, sticky=Tk.W+Tk.E)


    cell_config = dict(
        font= (info.settings.font, "15"),
        bg= u'LightSteelBlue1',
        relief=Tk.RAISED,
    )
    for i, each in enumerate([u'品名',u'數量',u'單價',u'金額',u'備註']):
        Tk.Label(frame, text=each, **cell_config).grid(row=9,column=i, sticky=Tk.W+Tk.E)

    Tk.Label(frame, text=u'銷售額合計', **cell_config).grid(row=550,column=1, columnspan=2, sticky=Tk.W+Tk.E)
    Tk.Label(frame, text=u'統一發票專用章', **cell_config).grid(row=550,column=4, columnspan=2, sticky=Tk.W+Tk.E)
    Tk.Label(frame, text=u'營  業  稅', **cell_config).grid(row=551,column=1, columnspan=2, sticky=Tk.W+Tk.E)
    Tk.Label(frame, text=u'總      計', **cell_config).grid(row=552,column=1, columnspan=2, sticky=Tk.W+Tk.E)


    mani_font = (info.settings.font, "15")
    cell_config = dict(
        relief= Tk.SUNKEN,
        font= mani_font+(u'bold',),
        bg= u'wheat'
    )
    query_config = dict(
        relief= Tk.SUNKEN,
        font= mani_font+(u'bold',),
        bg= u'yellow'
    )
    for row, (inv, order) in enumerate(zip(invoiceset, orderset)):
        config = query_config if inv.id == query_id else cell_config
#        print shipment
#        print '  ', order
        pinming = u' {} '.format(inv.order.product.label())
#        guige = u' ({} {} / {}) '.format(inv.order.product.units, inv.order.product.UM, inv.order.product.SKU)
#        jianshu = u'  {} {}  '.format(inv.sku_qty, order.product.UM if order.product.SKU == u'槽車' else order.product.SKU)
        by_unit = inv.order.product.unitpriced
#        qty = inv.sku_qty
#        try:
#            qty = int(order.totalskus * (inv.amount() / order.totalcharge))
#        except:
#            print order.totalskus , '* (', inv.amount(), '/', order.totalcharge
#        if by_unit:
#            qty *= order.product.units
        priced_qty = (inv.sku_qty * inv.order.product.units) if by_unit else inv.sku_qty
        priced_qty = int(priced_qty) if int(priced_qty) == priced_qty else priced_qty
        meas = inv.order.product.UM if by_unit else inv.order.product.SKU
        if meas == u'槽車':
            meas = inv.order.product.UM
#        if int(order.price * qty) != int(inv.amount() * 100.0/105.0):
#            tkMessageBox.showwarning(u'Calculation mismatch error',u'{} != {} ({})\nPlease verify totals by hand!'.format(int(order.price * qty), int(inv.amount * 100.0/105.0), inv.amount * 100.0/105.0))
#        print int(order.price * qty), '==?', int(inv.amount * 100.0/105.0), '(', inv.amount * 100.0/105.0, ')'
        shuliang = u'  {} {}  '.format(priced_qty, meas)
        price = inv.order.price
        danjia = u'  $ {}  '.format(int(price) if int(price) == price else price)
        jin_e = u'  $ {}  '.format(inv.subtotal())
#        this_units = u'  {} {}  '.format(order.product.units * inv.sku_qty, order.product.UM)
        Tk.Label(frame, text=pinming, **config).grid(row=10+row,column=0, sticky=Tk.W+Tk.E)
#        Tk.Label(frame, text=guige, **config).grid(row=10+row,column=1, sticky=Tk.W+Tk.E)
        Tk.Label(frame, text=shuliang, **config).grid(row=10+row,column=1, sticky=Tk.W+Tk.E)
        Tk.Label(frame, text=danjia, **config).grid(row=10+row,column=2, sticky=Tk.W+Tk.E)
#        Tk.Label(frame, bg=u'gray30', fg=u'gray70', text=u'  {}  '.format(order.product.SKUlong)).grid(row=10+row,column=4, sticky=Tk.W+Tk.E)
        Tk.Label(frame, text=jin_e, **config).grid(row=10+row,column=3, sticky=Tk.W+Tk.E)

    heji = Tk.StringVar()
    Tk.Label(frame, textvariable=heji, **cell_config).grid(row=550,column=3, sticky=Tk.W+Tk.E)
    heji.set(u'  $ {}  '.format(sum([inv.subtotal() for inv in invoiceset])))

    bigtext_config = dict(cell_config)
    bigtext_config.update(font=(info.settings.font, "30"))
    sellertxt = Tk.StringVar()
    Tk.Label(frame, textvariable=sellertxt, **bigtext_config).grid(row=551,column=4, rowspan=2, sticky=Tk.W+Tk.E+Tk.N+Tk.S)
    sellertxt.set(u'  {{ {} }}  '.format(orderset[0].seller))

    #Tax and Total after tax based on subtotal of all products. NOT taxed individually, which may give a different total.
    yingshui = Tk.StringVar()
    Tk.Label(frame, textvariable=yingshui, **cell_config).grid(row=551,column=3, sticky=Tk.W+Tk.E)
    yingshui.set(u'  $ {}  '.format(int(round(sum([inv.subtotal() for inv in invoiceset]) * (0.05 if inv_item.order.applytax else 0.0)))))

    zongji = Tk.StringVar()
    Tk.Label(frame, textvariable=zongji, **cell_config).grid(row=552,column=3, sticky=Tk.W+Tk.E)
    zongji.set(u'  $ {}  '.format(int(round(sum([inv.subtotal() for inv in invoiceset]) * (1.05 if inv_item.order.applytax else 1.0)))))



    allpaid = Tk.BooleanVar()
    ttk.Label(frame, text=u'Mark invoice as paid?').grid(row=1000,column=0)
    Tk.Radiobutton(frame, text="Yes", variable=allpaid, value=True)\
            .grid(row=1000,column=1)
    Tk.Radiobutton(frame, text="No", variable=allpaid, value=False)\
            .grid(row=1000,column=2)
    allpaid.set(invoice.paid)

    check_no = Tk.StringVar()
    ttk.Label(frame, text=u'Check number').grid(row=1001,column=0)
    ttk.Entry(frame, textvariable=check_no, width=20).grid(row=1001,column=1,columnspan=2)
    if invoice.check_no not in [None, u'None']:
        check_no.set(invoice.check_no)

    Tk.Button(frame, text="Update & Close Window", command=lambda:submit_changes(info)).grid(row=1003,column=0,columnspan=3)

    canvas.create_window(0, 0, anchor=Tk.NW, window=frame)

    frame.update_idletasks()

    canvas.config(scrollregion=canvas.bbox("all"))
