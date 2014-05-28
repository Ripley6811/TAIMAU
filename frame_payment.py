#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Tkinter as Tk
from Tkinter import EXTENDED, TOP, END
import tkMessageBox
import ttk
import tkFont
import date_picker as dp
import datetime


def format_pay_info(record):
    '''TODO: Replace delivery date with invoice date if available.'''
    pdate = record.duedate
    txt = u''
    txt += u'\u2691' if record.all_shipped() else u'\u2690'
    txt += u'\u2611' if record.all_paid() else u'\u2610'
    txt += u'\u269A' if record.applytax else u'  '
    txt += u'  {}\u2794{}'.format(record.seller, record.buyer)
    try:
        ddate = record.invoices[0].invoicedate if record.invoices[0].invoicedate else record.orderdate
        txt += u'  \u26DF{}/{}/{}'.format(ddate.year,ddate.month,ddate.day)
    except:
        pass
    txt += u'  {}'.format(record.product.inventory_name)
    txt += u'  ${}'.format(record.totalcharge)
    if len(record.invoices) > 0:
        txt += u'  \u2116 {}'.format(record.invoices[0].invoice_no)
    if pdate:
        txt += u'  \u2696{}/{}/{}'.format(pdate.year,pdate.month,pdate.day)
    return txt


def convert_date(adate):
    '''Converts a formatted string to a datetime.date object or from date to str
    depending on input.'''
    if isinstance(adate,str):

        strdate = adate
        # Try different separators until one produces a list of len 2 or 3
        for sep in [None,'/','-','\\']:
            if 2 <= len(adate.split(sep)) <=3:
                strdate = adate.split(sep)
                break
        print '    strdate', strdate
        try:
            # If len three, assume date is given last, if two then use closest year
            if len(strdate) == 3:
                return datetime.date(int(strdate[2]),int(strdate[0]),int(strdate[1]))
            else:
                dnow = datetime.date.today()
                dates = [datetime.date(dnow.year+x,int(strdate[0]),int(strdate[1])) for x in [-1,0,1]]
                diff = [abs((x-dnow).days) for x in dates]
                return dates[diff.index(min(diff))]
        except:
            raise TypeError, "Date not in the form MM/DD or MM/DD/YYYY"
    elif isinstance(adate,datetime.date):
        #Convert datetime object to string
        return u'{}/{}/{}'.format(adate.month,adate.day,adate.year)


def set_invoice_frame(frame, info):
    info.invoices = info.__class__()
    info.invoices.codes = dict()
    incoming = info.incoming = False if info.src == 'Sales' else True

    frameIn = ttk.Frame(frame)

    scrollbar2 = Tk.Scrollbar(frameIn, orient=Tk.VERTICAL)
    info.listbox.rec_invoices = Tk.Listbox(frameIn, selectmode=EXTENDED,
                         yscrollcommand=scrollbar2.set,
                         font=(info.settings.font, "12"), height=100, exportselection=0)
#    info.listbox.rec_invoices.bind("<Double-Button-1>", lambda _:copyrecord(info,True))
    scrollbar2.config(command=info.listbox.rec_invoices.yview)
    scrollbar2.pack(side=Tk.RIGHT, fill=Tk.Y)
    info.listbox.rec_invoices.pack(side=TOP, fill=Tk.BOTH)
    # Add right-click popup menu
    def refresh_invoice_listbox():
        # Add previous orders to order listbox
        info.listbox.rec_invoices.delete(0, Tk.END)

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
            no_ship_color = dict(bg=u'pale green', selectbackground=u'yellow',
                                 selectforeground=u'black')
            info.listbox.rec_invoices.insert(i, each)
            ins_colors = shipped_color if invoice_recs[i][2].paid else no_ship_color
            info.listbox.rec_invoices.itemconfig(i, ins_colors)
    info.method.refresh_invoice_listbox = refresh_invoice_listbox

    info.listbox.rec_invoices.bind("<Double-Button-1>", lambda _: display_invoice_for_edit(info))


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

    info.invoiceWin = Tk.Toplevel(width=700)
    info.invoiceWin.title(u"Invoice: {}".format(inv_no))

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
    Tk.Label(info.invoiceWin, text=u'發票號碼: {}'.format(u' '.join(inv_no)), **cell_config).grid(row=0,column=0, columnspan=2, sticky=Tk.W+Tk.E)
#    Tk.Label(info.invoiceWin, text=).grid(row=1,column=0, columnspan=2, sticky=Tk.W+Tk.E)

    cell_config.update(anchor=Tk.W)

    kehu = u'買 受 人: {}'.format(branch.fullname)
    Tk.Label(info.invoiceWin, text=kehu, **cell_config).grid(row=2,column=0, columnspan=2, sticky=Tk.W+Tk.E)

    tongyi = u'統一編號: {}'.format(u' '.join(branch.tax_id))
    Tk.Label(info.invoiceWin, text=tongyi, **cell_config).grid(row=3,column=0, columnspan=2, sticky=Tk.W+Tk.E)

    riqi = u'中 華 民 國 103年 {0.month}月 {0.day}日'.format(invoice.invoicedate)
    Tk.Label(info.invoiceWin, text=riqi, **cell_config).grid(row=3,column=2, columnspan=2, sticky=Tk.W+Tk.E)


    cell_config = dict(
        font= (info.settings.font, "15"),
        bg= u'LightSteelBlue1',
        relief=Tk.RAISED,
    )
    for i, each in enumerate([u'品名',u'數量',u'單價',u'金額',u'備註']):
        Tk.Label(info.invoiceWin, text=each, **cell_config).grid(row=9,column=i, sticky=Tk.W+Tk.E)

    Tk.Label(info.invoiceWin, text=u'銷售額合計', **cell_config).grid(row=50,column=1, columnspan=2, sticky=Tk.W+Tk.E)
    Tk.Label(info.invoiceWin, text=u'統一發票專用章', **cell_config).grid(row=50,column=4, columnspan=2, sticky=Tk.W+Tk.E)
    Tk.Label(info.invoiceWin, text=u'營  業  稅', **cell_config).grid(row=51,column=1, columnspan=2, sticky=Tk.W+Tk.E)
    Tk.Label(info.invoiceWin, text=u'總      計', **cell_config).grid(row=52,column=1, columnspan=2, sticky=Tk.W+Tk.E)


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
        pinming = u' {} '.format(inv.order.product.summary)
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
        Tk.Label(info.invoiceWin, text=pinming, **config).grid(row=10+row,column=0, sticky=Tk.W+Tk.E)
#        Tk.Label(info.invoiceWin, text=guige, **config).grid(row=10+row,column=1, sticky=Tk.W+Tk.E)
        Tk.Label(info.invoiceWin, text=shuliang, **config).grid(row=10+row,column=1, sticky=Tk.W+Tk.E)
        Tk.Label(info.invoiceWin, text=danjia, **config).grid(row=10+row,column=2, sticky=Tk.W+Tk.E)
#        Tk.Label(info.invoiceWin, bg=u'gray30', fg=u'gray70', text=u'  {}  '.format(order.product.SKUlong)).grid(row=10+row,column=4, sticky=Tk.W+Tk.E)
        Tk.Label(info.invoiceWin, text=jin_e, **config).grid(row=10+row,column=3, sticky=Tk.W+Tk.E)

    heji = Tk.StringVar()
    Tk.Label(info.invoiceWin, textvariable=heji, **cell_config).grid(row=50,column=3, sticky=Tk.W+Tk.E)
    heji.set(u'  $ {}  '.format(sum([inv.subtotal() for inv in invoiceset])))

    bigtext_config = dict(cell_config)
    bigtext_config.update(font=(info.settings.font, "30"))
    sellertxt = Tk.StringVar()
    Tk.Label(info.invoiceWin, textvariable=sellertxt, **bigtext_config).grid(row=51,column=4, rowspan=2, sticky=Tk.W+Tk.E+Tk.N+Tk.S)
    sellertxt.set(u'  {{ {} }}  '.format(orderset[0].seller))

    #Tax and Total after tax based on subtotal of all products. NOT taxed individually, which may give a different total.
    yingshui = Tk.StringVar()
    Tk.Label(info.invoiceWin, textvariable=yingshui, **cell_config).grid(row=51,column=3, sticky=Tk.W+Tk.E)
    yingshui.set(u'  $ {}  '.format(int(round(sum([inv.subtotal() for inv in invoiceset]) * (0.05 if inv_item.order.applytax else 0.0)))))

    zongji = Tk.StringVar()
    Tk.Label(info.invoiceWin, textvariable=zongji, **cell_config).grid(row=52,column=3, sticky=Tk.W+Tk.E)
    zongji.set(u'  $ {}  '.format(int(round(sum([inv.subtotal() for inv in invoiceset]) * (1.05 if inv_item.order.applytax else 1.0)))))



    allpaid = Tk.BooleanVar()
    ttk.Label(info.invoiceWin, text=u'Mark invoice as paid?').grid(row=100,column=0)
    Tk.Radiobutton(info.invoiceWin, text="Yes", variable=allpaid, value=True)\
            .grid(row=100,column=1)
    Tk.Radiobutton(info.invoiceWin, text="No", variable=allpaid, value=False)\
            .grid(row=100,column=2)
    allpaid.set(invoice.paid)

    check_no = Tk.StringVar()
    ttk.Label(info.invoiceWin, text=u'Check number').grid(row=101,column=0)
    ttk.Entry(info.invoiceWin, textvariable=check_no, width=20).grid(row=101,column=1,columnspan=2)
    if invoice.check_no not in [None, u'None']:
        check_no.set(invoice.check_no)

    Tk.Button(info.invoiceWin, text="Update & Close Window", command=lambda:submit_changes(info)).grid(row=103,column=0,columnspan=3)

