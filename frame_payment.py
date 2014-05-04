#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Tkinter as Tk
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
    info.listbox.rec_invoices = Tk.Listbox(frameIn, selectmode=Tk.MULTIPLE,
                         yscrollcommand=scrollbar2.set,
                         font=(info.settings.font, "12"), height=100, exportselection=0)
#    info.listbox.rec_invoices.bind("<Double-Button-1>", lambda _:copyrecord(info,True))
    scrollbar2.config(command=info.listbox.rec_invoices.yview)
    scrollbar2.pack(side=Tk.RIGHT, fill=Tk.Y)
    info.listbox.rec_invoices.pack(side=Tk.TOP, fill=Tk.BOTH)
    # Add right-click popup menu
    orderPopMenu = Tk.Menu(frameIn, tearoff=0)
    def refresh_listbox_item(id, index):
        info.method.refresh_listbox_item(id, index)

#
    def edit_invoice(info):
        rec_ID = info.order_rec_IDs[info.listbox.rec_invoices.index(Tk.ACTIVE)]
#        info.method.reload_orders(info)
#        info.method.refresh_listboxes(info)

#    orderPopMenu.add_command(label=u"編輯 (下劃線的記錄)", command=lambda:copyrecord(info, editmode=True))
#    orderPopMenu.add_command(label=u'切換:已交貨', command=lambda:toggle_delivered(info))
#    orderPopMenu.add_command(label=u'切換:已支付', command=lambda:toggle_paid(info))
    orderPopMenu.add_command(label=u'顯示發票', command=lambda:edit_invoice(info))

    def orderoptions(event):
        orderPopMenu.post(event.x_root, event.y_root)
    info.listbox.rec_invoices.bind("<Button-3>", orderoptions)
#    info.listbox.rec_invoices.bind("<F1>", lambda _:toggle_delivered(info))
#    info.listbox.rec_invoices.bind("<F2>", lambda _:toggle_paid(info))
#    info.listbox.rec_invoices.insert(0,*orderlist)






    frameInvoice = fs = ttk.Frame(frame)
    def reload_invoice_frame():

        if info.incoming:
            seller_opts = [b.name for b in info.dmv2.branches(info.curr_company)]
            buyer_opts = [u'台茂',u'富茂',u'永茂']
        else:
            seller_opts = [u'台茂',u'富茂',u'永茂']
            buyer_opts = [b.name for b in info.dmv2.branches(info.curr_company)]
        smenu = info.invoices.seller_menu['menu']
        smenu.delete(0,Tk.END)
        bmenu = info.invoices.buyer_menu['menu']
        bmenu.delete(0,Tk.END)
        [smenu.add_command(label=choice, command=Tk._setit(seller_str, choice)) for choice in seller_opts]
        [bmenu.add_command(label=choice, command=Tk._setit(buyer_str, choice)) for choice in buyer_opts]
        try:
            seller_str.set(seller_opts[0])
            buyer_str.set(buyer_opts[0])
        except IndexError:
            tkMessageBox.showwarning(u'Company not in catalog.', u'Add this company to the catalog\nto avoid future errors.')


        # Clean up or delete previous data
        list_indices = map(int, info.listbox.rec_invoices.curselection())
        info.invoices.order_IDs = [info.order_rec_IDs[i] for i in list_indices]
        info.invoices.order_recs = [info.order_records[i] for i in list_indices]
        info.invoices.totalskus = [rec.totalskus for rec in info.invoices.order_recs]
        info.invoices.qty_invoiced = [rec.qty_invoiced() for rec in info.invoices.order_recs]

        plength = len(list_indices)
        info.invoices.activated = [False] * plength
        info.invoices.entry_amt = [Tk.StringVar() for i in range(plength)]
        info.invoices.allpaid = [Tk.BooleanVar() for i in range(plength)]

#        for i in range(plength):
#            if info.invoices.totalcharge[i] == info.invoices.qty_invoiced[i]:
#                info.invoices.allpaid[i].set(True)

        def show_invoice(i, j):
            print 'show', (i,j)
            invoice_rec = info.invoices.order_recs[i].invoices[j]
            info.invoices.redo_indices = list(list_indices)
            display_invoice_for_edit(info, invoice_rec)


        def del_invoice(i, j, b0, b1):
            print 'delete', (i,j)
            r = info.invoices.order_recs[i]
            p = r.invoices[j]
            delete = tkMessageBox.askokcancel(u'Delete invoice?',
                                     u'Confirm to delete invoice and all items?:\n{} on {}'
                                     .format(p.invoice.invoice_no,p.invoice.invoicedate))
            if delete:
                info.dmv2.session.query(info.dmv2.InvoiceItem).filter_by(invoice_no=p.invoice_no).delete()
                info.dmv2.session.query(info.dmv2.Invoice).filter_by(invoice_no=p.invoice_no).delete()
                info.dmv2.session.commit()
#                info.dmv2.update_order(r.id, dict(delivered=False))
                b0.config(bg=u'red', state=Tk.DISABLED)
                b1.config(bg=u'gray24', state=Tk.DISABLED)
#                info.dmv2.session.commit()

                redo_indices = list(list_indices)
                info.method.reload_orders(info)
                info.method.refresh_listboxes(info)
#                reset_order_fields()
#                reload_invoice_frame()
                for index in redo_indices:
                    info.listbox.rec_invoices.selection_set(index)
                info.invoices.qty_invoiced = [rec.qty_invoiced() for rec in info.invoices.order_recs]


        # Fill-in or clear out the desired quantity for a product.
        def match_value(row):
            tmp = info.invoices.totalskus[row]
            dif = tmp - info.invoices.order_recs[row].qty_invoiced()
            if str(dif) != info.invoices.entry_amt[row].get() and dif != 0:
                info.invoices.entry_amt[row].set(dif)
            else:
                # Clear field if the number was already entered (undo auto-entry)
                info.invoices.entry_amt[row].set(u'')
            info.invoices.entryWs[row].focus()
            info.invoices.entryWs[row].icursor(Tk.END)
            info.invoices.entryWs[row].selection_range(0, Tk.END)


        def activate():
            buyers = set()
            sellers = set()
            try:
                for row in range(plength):
                    buyers.add(info.invoices.order_recs[row].buyer)
                    sellers.add(info.invoices.order_recs[row].seller)
                    entry_amt = 0
                    try:
                        entry_amt = int(info.invoices.entry_amt[row].get())
                    except:
                        pass

                    activated = True if entry_amt > 0 else False

                    info.invoices.activated[row] = activated
                    info.invoices.buttons[row].config(bg='cyan' if activated else 'slate gray',
                                                    fg='black' if activated else 'snow')
#                    if entry_amt + info.invoices.qty_invoiced[row] >= info.invoices.totalcharge[row]:
#                        info.invoices.allpaid[row].set(True)
#                    else:
#                        info.invoices.allpaid[row].set(False)
            except:
                pass
            #Set buyer seller. Show conflicts.
            if len(buyers) == 1:
                buyer_str.set(list(buyers)[0])
            else:
                buyer_str.set(u'[{}]'.format(u','.join(buyers)))
            if len(sellers) == 1:
                seller_str.set(list(sellers)[0])
            else:
                seller_str.set(u'[{}]'.format(u','.join(sellers)))

            #Attempt to guess the first two letters of invoice from previous invoices.


        # Delete previous widgets if they exist.
        try:
            for i in range(len(info.invoices.buttons)):
                info.invoices.buttons.pop().destroy()
                info.invoices.entryWs.pop().destroy()
                info.invoices.totalSKUsLabel.pop().destroy()

            for i in range(len(info.invoices.widgets)):
                info.invoices.widgets.pop().destroy()
        except:
            pass

        info.invoices.buttons = []
        info.invoices.entryWs = []
        info.invoices.totalSKUsLabel = []
        info.invoices.widgets = [] # Holder for all other elements to delete on refresh.

        rowsize = "12"
        for i, each in enumerate([u'品名',u'這次SKUs',u'剩下/总量(總額)',u'发票歷史']):#,u'全交了?'
            Tk.Label(fs, text=each, font=(info.settings.font, rowsize)).grid(row=0,column=i)

        # Add new product rows
        font = (info.settings.font, rowsize)
        for row, rec in enumerate(info.invoices.order_recs):
            #TODO: Have button fill in data from last order, i.e. quantity, taxed.
            bw = Tk.Button(fs, text=rec.product.summary, bg=u'slate gray',
                          font=font, command=lambda i=row:match_value(i))
            bw.grid(row=row+10, column=0, sticky=Tk.W+Tk.E)
            info.invoices.buttons.append(bw)

            ew = Tk.Entry(fs, textvariable=info.invoices.entry_amt[row], font=font, width=8, justify=Tk.CENTER)
            ew.grid(row=row+10,column=1)
            ew.config(selectbackground=u'LightSkyBlue1', selectforeground=u'black')
            info.invoices.entryWs.append(ew)
            info.invoices.entry_amt[row].trace("w", lambda *args:activate())

            text=u'{} / {} (${})'.format(rec.qty_shipped()-rec.qty_invoiced(),
                                         rec.totalskus,
                                         rec.totalcharge)
            lw = Tk.Label(fs, font=font, text=text, justify=Tk.CENTER)
            lw.grid(row=row+10,column=2)#, sticky=Tk.W)
            info.invoices.totalSKUsLabel.append(lw)

#            cw = Tk.Checkbutton(fs, text=u'全交了', variable=info.invoices.allpaid[row], command=lambda i=row:adj_skus(i))
#            cw.grid(row=row+10, column=3)#, columnspan=2)
#            info.invoices.widgets.append(cw)


            """#TODO: Add buyer/seller branch switcher/verification. Maybe Payments window is better."""

            """#TODO: Show buttons for previous invoices."""

            for col, inv_item in enumerate(rec.invoices):
                bw = Tk.Button(fs, text=u'{} ${} ({}/{})'.format(
                                    inv_item.invoice.seller if info.incoming else inv_item.invoice.buyer,
                                    inv_item.subtotal(),
                                    inv_item.invoice.invoicedate.month,
                                    inv_item.invoice.invoicedate.day
                                    ),
                               bg=u'khaki2',font=font,
                               command=lambda i=row, j=col:show_invoice(i,j))
                bw.grid(row=row+10, column=3+col*2, sticky=Tk.W+Tk.E)
                info.invoices.widgets.append(bw)
                bx = Tk.Button(fs, text=u'X', bg=u'red', font=font)
                bx.config(command=lambda i=row, j=col, b0=bw, b1=bx:del_invoice(i,j,b0,b1))
                bx.grid(row=row+10, column=4+col*2, sticky=Tk.W)
                info.invoices.widgets.append(bx)

        activate()
    #END: reload_invoice_frame()

    def set_inv_number():
        try:
            if len(invoice_number_str.get()) <= 2 and u'[' not in seller_str.get():
                code = info.invoices.codes.get(seller_str.get(), None)
                if code != None:
                    invoice_number_str.set(code)
                else:
                    query = info.dmv2.session.query(info.dmv2.Invoice) \
                                        .filter_by(seller=seller_str.get()) \
                                        .order_by('invoicedate')
                    invoiceset = query.all()[::-1]

                    for inv in invoiceset:
                        if inv.invoice_no[:2].isalpha():
                            invoice_number_str.set(inv.invoice_no[:2])
                            key = seller_str.get()
                            info.invoices.codes[key] = inv.invoice_no[:2]
                            break
        except:
            pass


    info.listbox.rec_invoices.bind("<ButtonRelease-1>", lambda _:reload_invoice_frame())

    # Add order fields
    invoice_date_str = Tk.StringVar()
    invoice_number_str = Tk.StringVar()
    invoice_note_str = Tk.StringVar()
    invoice_check_str = Tk.StringVar()
    invoice_truck_str = Tk.StringVar()
    seller_str = Tk.StringVar()
    seller_str.trace('w', lambda *args:set_inv_number())
    buyer_str = Tk.StringVar()


    def submit_order():
        #TODO: Check if invoice number already used and confirm to attach to previous
        if u'[' in seller_str.get():
            tkMessageBox.showerror(u'Multiple sellers selected.', u'Please select one supplier for this invoice.')
            return
        if u'[' in buyer_str.get():
            tkMessageBox.showerror(u'Multiple buyers selected.', u'Please select one client for this invoice.')
            return

        if len(invoice_number_str.get()) <=2:
            okay = tkMessageBox.askokcancel(u'Invoice number warning', u'You did not enter an invoice number (發票號碼).\Submit anyway?')
            if not okay:
                return
        for i, (include, rec) in enumerate(zip(info.invoices.activated,info.invoices.order_recs)):
            if include:
                # SET delivery date.
                idate = datetime.date(*map(int,invoice_date_str.get().split('-')))

                # Create dictionary for database insert.
                inv_dict = dict(
                    invoice_no= invoice_number_str.get(), #Same for all
                    seller= seller_str.get(),
                    buyer= buyer_str.get(),


                    invoicedate= idate, #Same for all

                    invoicenote= invoice_note_str.get(), #Same for all
#                    truck= invoice_truck_str.get(),
                )
                item_dict = dict(
                    invoice_no= invoice_number_str.get(), #Same for all

                    order_id= rec.id,

                    sku_qty= int(info.invoices.entry_amt[i].get()),
                )

                if len(invoice_number_str.get()) > 2:
                    key = seller_str.get()
                    info.invoices.codes[key]=invoice_number_str.get()[:2]

                # If check number is entered then update payment fields.
                if invoice_check_str.get():
                    inv_dict['check_no'] = invoice_check_str.get()
                    inv_dict['paid'] = True
                    #TODO: Allow user entry of date
                    inv_dict['paydate'] = datetime.date.today()


#                print inv_dict
                info.dmv2.append_invoice_item(inv_dict, item_dict)



        if not incoming:
            show_form()
        info.method.reload_orders(info)
        info.method.refresh_listboxes(info)
        reset_order_fields()
        reload_invoice_frame()
    #END: submit_order()

    def show_form():
        pass

    def reset_order_fields():
        for entry in info.invoices.entry_amt:
            entry.set(u'')
        invoice_number_str.set(u'')
        invoice_note_str.set(u'')
        invoice_check_str.set(u'')
        invoice_truck_str.set(u'')
        invoice_date_str.set(datetime.date.today())

    def date_picker():
        dp.Calendar(fi, textvariable=invoice_date_str).grid(row=100, column=0, rowspan=4,columnspan=3, sticky=Tk.W+Tk.E)


    frameInfo = fi = ttk.Frame(frame, height=6, borderwidth=10, relief=Tk.RAISED)
    separator = Tk.Frame(fi, height=6, borderwidth=6, relief=Tk.SUNKEN)
    separator.grid(row=0, column=0, columnspan=10, sticky=Tk.W+Tk.E, padx=5, pady=5)


    info.invoices.seller_menu = Tk.OptionMenu(fi, seller_str, None)
    info.invoices.seller_menu.grid(row=90, column=0)
    Tk.Label(fi, text=u'> \u26DF > \u26DF > \u26DF >').grid(row=90, column=1)
    info.invoices.buyer_menu = Tk.OptionMenu(fi, buyer_str, u'台茂')
    info.invoices.buyer_menu.grid(row=90, column=2)

    Tk.Label(fi, text=u'Invoice Date 發票日期').grid(row=100, column=0)
    Tk.Button(fi, textvariable=invoice_date_str, command=date_picker, bg='DarkGoldenrod1').grid(row=100, column=1)

    Tk.Label(fi, text=u'Invoice \u2116 發票編號').grid(row=101, column=0)
    Tk.Entry(fi, textvariable=invoice_number_str).grid(row=101, column=1, sticky=Tk.W+Tk.E)

    Tk.Label(fi, text=u'Invoice Note 備註').grid(row=102, column=0)
    Tk.Entry(fi, textvariable=invoice_note_str).grid(row=102, column=1, columnspan=10, sticky=Tk.W+Tk.E)

    Tk.Label(fi, text=u'Check \u2116').grid(row=103, column=0)
    Tk.Entry(fi, textvariable=invoice_check_str).grid(row=103, column=1, sticky=Tk.W+Tk.E)
#
#    Tk.Label(fi, text=u'Truck 槽車號碼').grid(row=103, column=2)
#    Tk.Entry(fi, textvariable=invoice_truck_str).grid(row=103, column=3, sticky=Tk.W+Tk.E)

    b = Tk.Button(fi, text=u'Submit Invoice', command=submit_order)
    b.grid(row=100, column=2)
    b.config(bg='SpringGreen2')

    if not incoming:
        b = Tk.Button(fi, text=u'Preview 發票', command=show_form)
        b.grid(row=100, column=3)
        b.config(bg='light salmon')
    invoice_date_str.set(datetime.date.today())

    separator = Tk.Frame(fi, height=6, borderwidth=6, relief=Tk.SUNKEN)
    separator.grid(row=200, column=0, columnspan=10, sticky=Tk.W+Tk.E, padx=5, pady=5)

    # Refresh is called from the load company method
    #TODO: Refresh after adding a product
    info.method.reload_invoice_frame = reload_invoice_frame
#    reset_order_fields()





    frameInvoice.pack(side=Tk.BOTTOM, fill=Tk.BOTH)
    frameInfo.pack(side=Tk.BOTTOM, fill=Tk.BOTH)
#    frameIn2.pack(side=Tk.TOP, fill=Tk.BOTH)
    frameIn.pack(fill=Tk.BOTH)


def display_invoice_for_edit(info, inv_item):
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
        for index in info.invoices.redo_indices:
            info.listbox.rec_invoices.selection_set(index)
        info.invoices.qty_invoiced = [rec.qty_invoiced() for rec in info.invoices.order_recs]




    cell_config = dict(
        font= (info.settings.font, "15", u'bold'),
        bg= u'cornsilk',
        height=2,
    )


    branch = info.dmv2.get_branch(invoice.buyer)


    #TODO: Auto-fill the first two letters from previous invoice
#    fapiao = u'發票號碼'.format(u'')
#    invoiceID_str = Tk.StringVar()
    Tk.Label(info.invoiceWin, text=u'發票號碼: {}'.format(u' '.join(inv_no)), **cell_config).grid(row=0,column=0, columnspan=2, sticky=Tk.W+Tk.E)
#    Tk.Label(info.invoiceWin, text=).grid(row=1,column=0, columnspan=2, sticky=Tk.W+Tk.E)

    cell_config.update(anchor=Tk.W)

    kehu = u'買 受 人: {}'.format(branch.fullname)
    Tk.Label(info.invoiceWin, text=kehu, **cell_config).grid(row=2,column=0, columnspan=2, sticky=Tk.W+Tk.E)

    tongyi = u'統一編號: {}'.format(u' '.join(branch.tax_id))
    Tk.Label(info.invoiceWin, text=tongyi, **cell_config).grid(row=3,column=0, columnspan=2, sticky=Tk.W+Tk.E)

    riqi = u'中 華 民 國 103年 {0.month}月 {0.day}日'.format(invoice.invoicedate)
    Tk.Label(info.invoiceWin, text=riqi, **cell_config).grid(row=3,column=2, columnspan=2, sticky=Tk.W+Tk.E)

#    huodan = u'貨單編號: {}'.format(ship_id)
#    Tk.Label(info.invoiceWin, text=huodan, **cell_config).grid(row=2,column=4, columnspan=2, sticky=Tk.W+Tk.E)


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

