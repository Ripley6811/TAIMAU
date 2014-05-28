#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Tkinter as Tk
from Tkinter import N, S, E, W, BOTTOM, TOP, BOTH, END
import tkMessageBox
import ttk
#import tkFont
import datetime
#import frame_company_editor
import locale
import date_picker as dp
import Tix
locale.setlocale(locale.LC_ALL, '')

def make_order_entry_frame(frame, info):
    info.order = info.__class__()
    incoming = False if info.src == 'Sales' else True
    frameIn = ttk.Frame(frame)
    #TODO: remove edit button and rely on double-click for editing
    editb = Tk.Button(frameIn, text=u"編輯紀錄", bg=u'light salmon')
    editb.pack(side=BOTTOM, fill=Tk.X)
    create_manifest_button = Tk.Button(frameIn, text=u'\u26DF 創造出貨表 \u26DF',
                                       bg=u'light salmon')
    create_manifest_button.pack(side=BOTTOM, fill=Tk.X)
#    b = Tk.Button(frameIn, text=u"編輯 (下劃線的記錄)",
#            command=lambda:copyrecord(info,True))
#    b.pack(side=Tk.BOTTOM, fill=Tk.X)
    scrollbar2 = Tk.Scrollbar(frameIn, orient=Tk.VERTICAL)
    info.listbox.rec_orders = Tk.Listbox(frameIn, selectmode=Tk.EXTENDED,
                         yscrollcommand=scrollbar2.set,
                         font=(info.settings.font, "12"), height=100, exportselection=0)

    def get_index_edit_PO():

        selected_index = info.listbox.rec_orders.index(Tk.ACTIVE)
        order_id = info.order_rec_IDs[selected_index]
        record = info.dmv2.get_order(order_id)
        edit_PO(record)


    def get_index_make_manifest():
        indices = map(int, info.listbox.rec_orders.curselection())
        orderIDs = [info.order_rec_IDs[i] for i in indices]
        orders = [info.dmv2.get_order(oid) for oid in orderIDs]

        create_manifest_form(orders)


#    info.listbox.rec_orders.bind("<ButtonRelease-1>", lambda _:set_info_rec(info))
    info.listbox.rec_orders.bind("<Double-Button-1>", lambda _: get_index_edit_PO())
    editb['command'] = get_index_edit_PO # Method
    create_manifest_button['command'] = get_index_make_manifest # Method
    scrollbar2.config(command=info.listbox.rec_orders.yview)
    scrollbar2.pack(side=Tk.RIGHT, fill=Tk.Y)
    info.listbox.rec_orders.pack(side=TOP, fill=BOTH)
    # Add right-click popup menu
    orderPopMenu = Tk.Menu(frameIn, tearoff=0)
    def refresh_order_listbox_all():
        '''Refresh the record lists for each frame.
        '''
        # Add previous orders to order listbox
        info.listbox.rec_orders.delete(0, END)

        # List of order summaries
        tmp = [rec.listbox_summary() for rec in info.order_records]

        #TODO: Different colors for different products. Not necessary...
        for i, each in enumerate(tmp):
            info.listbox.rec_orders.insert(i, each)
            info.listbox.rec_orders.itemconfig(i, bg=u'lavender',
                                               selectbackground=u'dark orchid')
#            shipped_color = dict(bg=u'SlateGray4', fg=u'gray79',
#                                 selectbackground=u'tomato',
#                                 selectforeground=u'black')
#            no_ship_color = dict(bg=u'pale green', selectbackground=u'yellow',
#                                 selectforeground=u'black')
#            info.listbox.rec_manifest.insert(i, each)
#            ins_colors = shipped_color if info.order_records[i].all_shipped() else no_ship_color
#            info.listbox.rec_manifest.itemconfig(i, ins_colors)


    def refresh_order_listbox_item(id, index):
        #TODO: Refactor this and the list refresh in main to be consistent.
        recvals = info.dmv2.get_order(id)
        info.listbox.rec_orders.delete(index)
        info.listbox.rec_orders.insert(index, recvals.listbox_summary())
        info.listbox.rec_orders.select_clear(0, Tk.END)
        info.listbox.rec_orders.select_set(index)
        info.listbox.rec_orders.activate(index)

        no_ship_color = dict(bg=u'lavender', selectbackground=u'dark orchid')
        shipped_color = dict(bg=u'DarkOliveGreen1', selectbackground=u'firebrick1')
        insert_colors = shipped_color if info.order_records[index].all_shipped() else no_ship_color
        info.listbox.rec_orders.itemconfig(index, insert_colors)

    info.method.refresh_order_listbox_item = refresh_order_listbox_item

#    def toggle_delivered(info):
#        #TODO: Auto enter and attach a shipment
#        active_index = info.listbox.rec_orders.index(Tk.ACTIVE)
#        rec_id = info.order_rec_IDs[active_index]
#        rec = info.dmv2.get_order(rec_id)
#        updates = dict(delivered=False if rec.delivered else True)
##        if u'.0' in rec.deliveryID:
##            updates['deliveryID'] = '{:0>7}'.format(int(float(rec.deliveryID)))
#        info.dmv2.update_order(rec_id, updates)
#        refresh_order_listbox_item(rec_id, active_index)
#
#
#    def toggle_paid(info):
#        #TODO: Auto enter and attach a payment
#        active_index = info.listbox.rec_orders.index(Tk.ACTIVE)
#        rec_id = info.order_rec_IDs[active_index]
#        rec = info.dmv2.get_order(rec_id)
#        updates = dict(paid=False if rec.paid else True)
#        info.dmv2.update_order(rec_id, updates)
#        refresh_order_listbox_item(rec_id, active_index)

    def delete_order(info):
        info.dmv2.delete_order(info.order_rec_IDs[info.listbox.rec_orders.index(Tk.ACTIVE)])
        info.method.reload_orders(info)
        refresh_order_listbox_all()
        info.method.refresh_manifest_listbox()
        info.method.refresh_invoice_listbox()

#    orderPopMenu.add_command(label=u"編輯 (下劃線的記錄)", command=lambda:copyrecord(info, editmode=True))
#    orderPopMenu.add_command(label=u'切換:已交貨', command=lambda:toggle_delivered(info))
#    orderPopMenu.add_command(label=u'切換:已支付', command=lambda:toggle_paid(info))
    orderPopMenu.add_command(label=u'刪除', command=lambda: delete_order(info))

    def orderoptions(event):
        orderPopMenu.post(event.x_root, event.y_root)
    info.listbox.rec_orders.bind("<Button-3>", orderoptions)
#    info.listbox.rec_orders.bind("<F1>", lambda _:toggle_delivered(info))
#    info.listbox.rec_orders.bind("<F2>", lambda _:toggle_paid(info))
#    info.listbox.rec_orders.insert(0,*orderlist)






    frameProducts = fp = Tix.Frame(frame)
    def toggle_tax_all():
        info.order.applytax.set(not info.order.applytax.get())
    def reload_products_frame():
        # Clean up or delete previous data
        info.order.products = info.dmv2.products(info)
        plength = len(info.order.products)
        info.order.activated = [False] * plength
        info.order.qty = [Tk.StringVar() for i in range(plength)]
        info.order.price = [Tk.StringVar() for i in range(plength)]
        info.order.subtotal = [Tk.StringVar() for i in range(plength)]
        info.order.taxed = [Tk.StringVar() for i in range(plength)]
        info.order.total = [Tk.StringVar() for i in range(plength)]
        info.order.applytax = Tk.BooleanVar()
        info.order.applytax.trace("w", lambda *args: activate())
        info.order.recent_orders = []
        for rec in info.order.products:
            info.order.recent_orders.append(
                        info.dmv2.get_product_recent_order(rec.MPN, update=True))



        # Fill-in or clear out the desired quantity for a product.
        def match_qty(row):
            if info.order.recent_orders[row] != None:
                tmp = info.order.recent_orders[row].totalskus
                if str(tmp) != info.order.qty[row].get():
                    info.order.qty[row].set(info.order.recent_orders[row].totalskus)
                    info.order.price[row].set(info.order.recent_orders[row].price)
                else:
                    # Clear field if the number was already entered (undo auto-entry)
                    info.order.qty[row].set(u'')
            info.order.entryWs[row].focus()
            info.order.entryWs[row].icursor(Tk.END)
            info.order.entryWs[row].selection_range(0, Tk.END)

        def activate():
            try:
                st = 0.0
                for row in range(plength):
                    product = info.order.products[row]
                    qty = 0
                    price = 0.0
                    try:
                        qty = int(info.order.qty[row].get())
                    except Exception:
                        pass #info.order.qty[row].set(u'')
                    try:
                        price = float(info.order.price[row].get())
                    except Exception:
                        pass #info.order.price[row].set(u'0.0')

                    activated = True if qty > 0 else False

                    info.order.activated[row] = activated
                    info.order.buttons[row].config(bg='cyan' if activated else 'slate gray',
                                                    fg='black' if activated else 'snow')
                    info.order.labelSubtotal[row].config(bg='cyan' if activated else 'slate gray',
                                                    fg='black' if activated else 'snow')
                    info.order.labelTaxed[row].config(bg='cyan' if activated & info.order.applytax.get() else 'slate gray',
                                                    fg='black' if activated else 'snow')
                    info.order.labelTotal[row].config(bg='cyan' if activated else 'slate gray',
                                                    fg='black' if activated else 'snow')

                    # Calculate subtotal for item and order subtotal
                    x = qty * price * (product.units if product.unitpriced else 1.0)
                    st += x
                    info.order.subtotal[row].set(locale.currency(x, grouping=True))
                    subtax = x*0.05 if info.order.applytax.get() else 0.0
                    info.order.taxed[row].set(locale.currency(subtax, grouping=True))
                    info.order.total[row].set(locale.currency(x+subtax, grouping=True))
                subtotal.set(locale.currency(st, grouping=True))
                subtax = st*0.05 if info.order.applytax.get() else 0.0
                tax_amt.set(locale.currency(subtax, grouping=True))
                totalcharge.set(locale.currency(st+subtax, grouping=True))


                for i in range(plength):
                    if info.order.activated[i] == True and info.order.recent_orders[i] != None:
                        seller_str.set(info.order.recent_orders[i].seller)
                        buyer_str.set(info.order.recent_orders[i].buyer)
                        break

            except Exception:
                info.order.products = info.dmv2.products(info)
                for rec in info.order.products:
                    info.order.recent_orders.append(
                                info.dmv2.get_product_recent_order(rec.MPN, update=True))
                activate()

        # Delete previous widgets if they exist.
        try:
            for i in range(len(info.order.buttons)):
                info.order.buttons.pop().destroy()
                info.order.entryWs.pop().destroy()
                info.order.labelSubtotal.pop().destroy()
                info.order.labelTaxed.pop().destroy()
                info.order.labelTotal.pop().destroy()

            for i in range(len(info.order.widgets)):
                info.order.widgets.pop().destroy()
        except Exception:
            pass
        info.order.buttons = []
        info.order.entryWs = []
        info.order.labelSubtotal = []
        info.order.labelTaxed = []
        info.order.labelTotal = []
        info.order.widgets = [] # Holder for all other elements to delete.

        balloon = Tix.Balloon(fp)
        col2 = 6
        # Add new product rows
        for row, product in enumerate(info.order.products):
            #TODO: Have button fill in data from last order, i.e. quantity, taxed.
            prodtext = product.summary
            if product.ASE_PN:
                prodtext = u'{}'.format(prodtext)
            bw = Tix.Button(fp, text=prodtext, bg='grey', anchor="w")
            bw['command'] = lambda i=row: match_qty(i)
            bw.grid(row=row/2, column=row%2 * col2, sticky=W+E)
            info.order.buttons.append(bw)
            balloonmsg = u'產品編號# {} : '.format(product.ASE_PN) if product.ASE_PN else u''
            balloonmsg += u'{} '.format(product.inventory_name)
            if product.note:
                try:
                    balloonmsg += u': {}'.format(product.note[:product.note.index('{')])
                except:
                    balloonmsg += u': {}'.format(product.note)
            balloon.bind_widget(bw, balloonmsg=balloonmsg)


            ew = Tk.Entry(fp, textvariable=info.order.qty[row], width=7, justify="center")
            ew.grid(row=row/2, column=row%2 * col2 + 1)
            ew.config(selectbackground=u'LightSkyBlue1', selectforeground=u'black')
            ew.config(highlightcolor=u'cyan', highlightthickness=4)
            info.order.entryWs.append(ew)
            info.order.qty[row].trace("w", lambda *args:activate())

            lw = Tk.Label(fp, text=u'{},'.format(product.SKU), justify="left", anchor="w")
            lw.grid(row=row/2, column=row%2 * col2 + 2, sticky="w")
            info.order.widgets.append(lw)

            lw = Tk.Label(fp, text=u'$', justify="right", anchor="e")
            lw.grid(row=row/2, column=row%2 * col2 + 3, sticky="e")
            info.order.widgets.append(lw)

            ew = Tk.Entry(fp, textvariable=info.order.price[row], width=6)
            ew.grid(row=row/2, column=row%2 * col2 + 4)
            info.order.widgets.append(ew)
            info.order.price[row].set(product.curr_price)
            info.order.price[row].trace("w", lambda *args:activate())
#            info.order.price[row].set(product.curr_price)

            txt = u'per {}'.format(product.UM if product.unitpriced else product.SKU)
            lw = Tk.Label(fp, text=txt, width=8, anchor="w")
            lw.grid(row=row/2, column=row%2 * col2 + 5)
            info.order.widgets.append(lw)





            lw = Tk.Label(fp, textvariable=info.order.subtotal[row], width=12)
#            lw.grid(row=row,column=5)
            info.order.labelSubtotal.append(lw)

            lw = Tk.Label(fp, textvariable=info.order.taxed[row], width=12)
#            lw.grid(row=row,column=6)
            info.order.labelTaxed.append(lw)

            lw = Tk.Label(fp, textvariable=info.order.total[row], width=12)
#            lw.grid(row=row,column=7)
            info.order.labelTotal.append(lw)
        info.order.applytax.set(True)
    #END: reload_products_frame()

    # Add order fields
    def plate_capitalize():
        #TODO: Auto-fill with plate by matching first letters.
        before = shipment_truck_str.get()
        if len(before) > 0:
            after = before.upper()
            if before != after:
                shipment_truck_str.set(after)
            plate_list = info.dmv2.session.query(info.dmv2.Vehicle.id).all()
            plate_list = [p.id for p in plate_list]
            for plate in plate_list:
                if plate.startswith(after):
                    shipment_truck_str.set(plate)
                    break
        before = order_number_str.get()
        if len(before) > 0:
            after = before.upper()
            if before != after:
                order_number_str.set(after)


    subtotal = Tk.StringVar()
    tax_amt = Tk.StringVar()
    totalcharge = Tk.StringVar()
    order_duedate_str = Tk.StringVar()
    orderdate_str = Tk.StringVar()
    duedate_str = Tk.StringVar()
#    order_date_label = Tk.StringVar()
    order_number_str = Tk.StringVar()
    order_number_str.trace('w', lambda *args:plate_capitalize())
#    order_number_label = Tk.StringVar()
    order_delivered_bool = Tk.BooleanVar()
    order_delivered_bool.set(False)
#    order_taxed_bool = Tk.BooleanVar()
#    order_taxed_bool.set(True)
    order_note_str = Tk.StringVar()
#    order_note_label = Tk.StringVar()
    shipment_driver_str = Tk.StringVar()
    shipment_truck_str = Tk.StringVar()
    shipment_truck_str.trace('w', lambda *args:plate_capitalize())
    Tk.Label(fp, text=u'Subtotal').grid(row=100, column=1, columnspan=3)
    Tk.Label(fp, textvariable=subtotal).grid(row=101, column=1, columnspan=3)
    _=Tk.Button(fp, text=u'Tax (?)', command=toggle_tax_all, bg='violet')
    _.grid(row=100, column=4, columnspan=2)
    Tk.Label(fp, textvariable=tax_amt).grid(row=101, column=4, columnspan=2)
    Tk.Label(fp, text=u'Total').grid(row=100, column=6, columnspan=1, sticky=Tk.W)
    Tk.Label(fp, textvariable=totalcharge).grid(row=101, column=6, columnspan=1, sticky=Tk.W)

    def submit_order():
        #TODO: Send price update in product except when zero or matched
        session = info.dmv2.session
        Order = info.dmv2.Order
        Shipment = info.dmv2.Shipment
        if u'[' in seller_str.get() or not seller_str.get():
            tkMessageBox.showerror(u'Seller selection error.', u'Please select one supplier for this invoice.')
            return
        if u'[' in buyer_str.get() or not buyer_str.get():
            tkMessageBox.showerror(u'Buyer selection error.', u'Please select one client for this invoice.')
            return

        for i, item in enumerate(info.order.activated):
            if item:
                print i, "\b  submit order for", repr(info.order.products[i].MPN)
                product = info.order.products[i]
                # SET order and due dates. Order date cannot follow a due date.
                odate = datetime.date.today()
                ddate = datetime.date(*map(int,order_duedate_str.get().split('-')))
                if odate > ddate:
                    odate = ddate

                # SET seller and buyer information.
                seller = seller_str.get()
                buyer = buyer_str.get()

                # Create dictionary for database insert.
                qty = int(info.order.qty[i].get())
                price = float(info.order.price[i].get())
                x = qty * price * (product.units if product.unitpriced else 1.0)
                order = Order(
                    group= info.curr_company, #Same for all
                    seller= seller,
                    buyer= buyer,

                    MPN= product.MPN,

                    price= float(info.order.price[i].get()),
                    totalskus= int(info.order.qty[i].get()),
                    totalunits= float(float(info.order.qty[i].get())*product.units),
                    subtotal= float(x),
                    applytax= bool(info.order.applytax.get()), #Same for all

                    orderdate= odate, #Same for all
                    duedate= ddate, #Same for all

                    orderID= order_number_str.get(), #Same for all
                    ordernote= order_note_str.get(), #Same for all

#                    delivered= order_delivered_bool.get(),  #Same for all
                    is_sale= not incoming, #Same for all
                )

                # Insert shipment record if marked as delivered.
                delivered = order_delivered_bool.get()
                if delivered == True:
                    print "Add a completed shipment record to order #"

                    ship_dict = dict(
                        sku_qty= order.totalskus,

                        shipmentdate= order.duedate,
                        shipmentID= order.orderID,
                        shipmentnote= order.ordernote,
                        driver= shipment_driver_str.get(),
                        truck= shipment_truck_str.get(),
                    )
                    shipment = Shipment(**ship_dict)
                    shipment.order = order
                    order.orderID = u''
                    order.ordernote = u''
#                    session.add(shipment) #Not necessary when backref exists.

                # Insert new record into the database.
                session.add(order)
                session.commit()


        info.method.reload_orders(info)
        refresh_order_listbox_all()
        reset_order_fields()
#        toggle_delivery_labels() #TIP: Can change this to adding a trace on the BoolenVar.
    #END: submit_order()


    def reset_order_fields():
        for entry in info.order.qty:
            entry.set(u'')
        order_number_str.set(u'')
        order_note_str.set(u'')
        shipment_truck_str.set(u'')
#        order_delivered_bool.set(False)
#        order_duedate_str.set(datetime.date.today())

    def date_picker(tvar=None):
        if not tvar:
            tvar = order_duedate_str
        _=dp.Calendar(fp, textvariable=tvar)
        _.grid(row=100, column=0, rowspan=3, columnspan=3, sticky=Tk.W+Tk.E)

#    def toggle_delivery_labels():
#        if order_delivered_bool.get():
#            order_date_label.set(u'Delivery Date')
#            order_note_label.set(u'Delivery Note')
#            order_number_label.set(u'Delivery Number')
#            driver_field.config(state=Tk.NORMAL)
#            truck_field.config(state=Tk.NORMAL)
#        else:
#            order_date_label.set(u'Due Date')
#            order_note_label.set(u'Order Note')
#            order_number_label.set(u'Order Number')
#            driver_field.config(state=Tk.DISABLED)
#            truck_field.config(state=Tk.DISABLED)


    seller_str = Tk.StringVar()
    buyer_str = Tk.StringVar()

    # Add 'edit' functionality (disable manifest and invoice entry)
    def edit_PO(po_rec=None):
        """
        Create or edit a PO form.
        """
        if po_rec == None and not any(info.order.activated):
            return

        editPOwin = Tix.Toplevel(width=700)
        if po_rec == None:
            editPOwin.title(u"New Purchase Order (PO) Form")
        else:
            editPOwin.title(u"({}) Editing PO: {}".format(po_rec.id, po_rec.orderID))

        def date_picker(tvar=None):
            if not tvar:
                tvar = order_duedate_str
            _=dp.Calendar(editPOwin, textvariable=tvar)
            _.grid(row=0, column=0, rowspan=30, columnspan=6, sticky=W+E+N+S)

        # PO number, supplier and buyer fields
        Tk.Label(editPOwin, text=u'PO編號').grid(row=0, column=0)
        Tk.Label(editPOwin, text=u'供貨商').grid(row=1, column=0)
        Tk.Label(editPOwin, text=u'客戶名稱').grid(row=2, column=0)
        Tk.Label(editPOwin, text=u'應稅?').grid(row=3, column=0)
        Tk.Label(editPOwin, text=u'PO備註').grid(row=4, column=0)

        _=Tk.Entry(editPOwin, textvariable=order_number_str)
        _.grid(row=0, column=1, columnspan=2, sticky=W+E)

        info.order.seller_menu = Tk.OptionMenu(editPOwin, seller_str, None)
        info.order.seller_menu.grid(row=1, column=1, columnspan=2)
        info.order.seller_menu.config(bg=u'DarkOrchid4', fg=u'white')
        info.order.buyer_menu = Tk.OptionMenu(editPOwin, buyer_str, u'台茂')
        info.order.buyer_menu.grid(row=2, column=1, columnspan=2)
        info.order.buyer_menu.config(bg=u'DarkOrchid4', fg=u'white')

        # Order date and due date fields
        l = Tk.Label(editPOwin, text=u'訂貨日')
        b = Tk.Button(editPOwin, textvariable=orderdate_str, bg='DarkGoldenrod1')
        b['command'] = lambda tv=orderdate_str: date_picker(tv)
        l.grid(row=0, column=3)
        b.grid(row=0, column=4)
        orderdate_str.set(datetime.date.today())

        l = Tk.Label(editPOwin, text=u'到期日')
        b = Tk.Button(editPOwin, textvariable=duedate_str, bg='DarkGoldenrod1')
        b['command'] = lambda tv=duedate_str: date_picker(tv)
        l.grid(row=1, column=3)
        b.grid(row=1, column=4)
        duedate_str.set(datetime.date.today())

        def submit_new_order():
            '''
            #TODO: Confirm commiting changes to product info one-by-one.
            #       Changes to price, others(?)
            '''
            session = info.dmv2.session
            Order = info.dmv2.Order
            Shipment = info.dmv2.Shipment
            InvoiceItem = info.dmv2.InvoiceItem
            Invoice = info.dmv2.Invoice
            if u'[' in seller_str.get() or not seller_str.get():
                tkMessageBox.showerror(u'Seller selection error.', u'Please select one supplier for this invoice.')
                return
            if u'[' in buyer_str.get() or not buyer_str.get():
                tkMessageBox.showerror(u'Buyer selection error.', u'Please select one client for this invoice.')
                return


            # SET seller and buyer information.
            seller = seller_str.get()
            buyer = buyer_str.get()
            delivered = delivered_bool.get()
            invoiced = invoiced_bool.get()
            if invoiced == True and invoice_no.get():
                inv_dict = dict(
                    seller= seller,
                    buyer= buyer,

                    invoice_no= invoice_no.get(),
                    invoicedate= datetime.date(*map(int,invoicedate.get().split('-'))),
                    invoicenote= invoicenote.get(),
                )
                invoice = Invoice(**inv_dict)
                session.add(invoice)

            for i, product in enumerate(products):
                # SET order and due dates. Order date cannot follow a due date.
                odate = datetime.date(*map(int,orderdate_str.get().split('-')))
                ddate = datetime.date(*map(int,duedate_str.get().split('-')))


                # Create dictionary for database insert.
                qty = int(p_qty[i].get())
                price = float(pcost[i].get())
                x = qty * price * (product.units if product.unitpriced else 1.0)
                order = Order(
                    group= info.curr_company, #Same for all
                    seller= seller,
                    buyer= buyer,

                    MPN= product.MPN,

                    price= float(pcost[i].get()),
                    totalskus= int(p_qty[i].get()),
                    totalunits= float(float(p_qty[i].get())*product.units),
                    subtotal= float(x),
                    applytax= bool(info.order.applytax.get()), #Same for all

                    orderdate= odate, #Same for all
                    duedate= ddate, #Same for all

                    orderID= order_number_str.get(), #Same for all
                    ordernote= order_note_str.get(), #Same for all

                    is_sale= not incoming, #Same for all
                )

                # Insert shipment record if marked as delivered.
                if delivered == True and deliveryID.get():
                    print "Add a completed shipment record to order #"

                    ship_dict = dict(
                        sku_qty= int(p_qty[i].get()),

                        shipmentdate= datetime.date(*map(int,deliverydate.get().split('-'))),
                        shipmentID= deliveryID.get(),
                        shipmentnote= deliverynote.get(),
                        driver= deliverydriver.get(),
                        truck= deliverytruck.get(),
                    )
                    shipment = Shipment(**ship_dict)
                    shipment.order = order
#                    session.add(shipment) #Not necessary when backref exists.

                # Insert shipment record if marked as delivered.
                if invoiced == True and invoice_no.get():
                    print "Add a completed invoice record to order #"


                    invit_dict = dict(
                        sku_qty= int(p_qty[i].get()),
                    )
                    invoice_item = InvoiceItem(**invit_dict)
                    invoice_item.order = order
                    invoice_item.invoice = invoice


                # Insert new record into the database.
                session.add(order)
                session.commit()


            info.method.reload_orders(info)
            refresh_order_listbox_all()
            reset_order_fields()
            editPOwin.destroy()
            info.method.refresh_manifest_listbox()
            info.method.refresh_invoice_listbox()
        ############ END submit_new_order

        def submit_order_updates():
            session = info.dmv2.session
            Order = info.dmv2.Order


            for i, order in enumerate(prodorders):
                product = order.product
                odate = datetime.date(*map(int,orderdate_str.get().split('-')))
                ddate = datetime.date(*map(int,duedate_str.get().split('-')))
                qty = int(p_qty[i].get())
                price = float(pcost[i].get())
                x = qty * price * (product.units if product.unitpriced else 1.0)
                #"group" and "MPN" will not change
                updates = dict(
                    seller= seller_str.get(),
                    buyer= buyer_str.get(),

                    price= float(pcost[i].get()),
                    totalskus= int(p_qty[i].get()),
                    totalunits= float(float(p_qty[i].get())*product.units),
                    subtotal= float(x),
                    applytax= bool(info.order.applytax.get()), #Same for all

                    orderdate= odate, #Same for all
                    duedate= ddate, #Same for all

                    orderID= order_number_str.get(), #Same for all
                    ordernote= order_note_str.get(), #Same for all
                )
                session.query(Order).filter_by(id=order.id).update(updates)
            session.commit()
            info.method.reload_orders(info)
            refresh_order_listbox_all()
            reset_order_fields()
            editPOwin.destroy()
            info.method.refresh_manifest_listbox()
            info.method.refresh_invoice_listbox()


        if po_rec == None:
            submit_order = submit_new_order
        else:
            submit_order = submit_order_updates

        submitb = Tix.Button(editPOwin, text=u'Submit Order')
        submitb.grid(row=2, column=3, columnspan=2, rowspan=2)
        submitb.config(bg='SpringGreen2')
        submitb['command'] = submit_order

        # Tax boolean
        rb1 = Tk.Radiobutton(editPOwin, text="是", variable=info.order.applytax, value=True)
        rb2 = Tk.Radiobutton(editPOwin, text="不應稅", variable=info.order.applytax, value=False)
        rb1.grid(row=3, column=1)
        rb2.grid(row=3, column=2)

        _=Tk.Entry(editPOwin, textvariable=order_note_str)
        _.grid(row=4, column=1, columnspan=5, sticky=W+E)

        # Set seller and buyer selection lists
        if info.incoming:
            seller_opts = [c.name for c in info.dmv2.branches(info.curr_company)]
            buyer_opts = [u'台茂',u'富茂',u'永茂']
        else:
            seller_opts = [u'台茂',u'富茂',u'永茂']
            buyer_opts = [c.name for c in info.dmv2.branches(info.curr_company)]
        smenu = info.order.seller_menu['menu']
        smenu.delete(0,Tk.END)
        bmenu = info.order.buyer_menu['menu']
        bmenu.delete(0,Tk.END)
        [smenu.add_command(label=choice, command=Tk._setit(seller_str, choice)) for choice in seller_opts]
        [bmenu.add_command(label=choice, command=Tk._setit(buyer_str, choice)) for choice in buyer_opts]


        separator = Tk.Frame(editPOwin, height=2, borderwidth=2, relief=Tk.SUNKEN)
        separator.grid(row=5, column=0, columnspan=10, sticky=W+E, padx=5, pady=5)


        '''
        Display the products in this order.
        Arrange products and entry fields in a separate frame.
        '''
        prod_frame = Tk.Frame(editPOwin)

        prodorders = [] # For loading previous PO

        products = [] # For products in new PO
        Tk.Label(prod_frame, text=u'品名(包裝)').grid(row=0, column=0)
        pname = []
        Tk.Label(prod_frame, text=u'數量(Qty)').grid(row=0, column=1)
        p_qty = []
        Tk.Label(prod_frame, text=u'SKU').grid(row=0, column=2)
        p_sku = []
        # u"$" in column=3
        Tk.Label(prod_frame, text=u'單價').grid(row=0, column=3, columnspan=2)
        pcost = []
        # u"per" in column=5
        Tk.Label(prod_frame, text=u'單位').grid(row=0, column=5, columnspan=2)
        punit = []
        Tk.Label(prod_frame, text=u'(單位總數)').grid(row=0, column=7)
        putot = []


        def show_total_units(*args):
            '''Display the total unit amount for each item based on
            SKU quantity and units per SKU in the product data.
            '''
            r = range(len(prodorders)) if po_rec else range(len(products))
            for i in r:
                try:
                    units = prodorders[i].product.units if po_rec else products[i].units
                    UM = prodorders[i].product.UM if po_rec else products[i].UM
                    tot_units = int(p_qty[i].get()) * units
                    # Convert to int if total is a whole number.
                    if tot_units.is_integer():
                        tot_units = int(tot_units)
                    putot[i].set(u'( {}{} )'.format(tot_units, UM))
                except ValueError:
                    putot[i].set(u'# Error')




        prod_frame.grid(row=8, column=0, columnspan=6, sticky=N+S+W+E)

        '''
        Add manifest and invoice entry options if it is a new order.
        Intended for orders that are all shipped and invoiced together.
        '''
        delivered_bool = Tk.BooleanVar(); delivered_bool.set(False)
        deliveryID = Tk.StringVar()
        deliverydate = Tk.StringVar()
        deliverydriver = Tk.StringVar()
        deliverytruck = Tk.StringVar()
        deliverynote = Tk.StringVar()
        invoiced_bool = Tk.BooleanVar(); invoiced_bool.set(False)
        invoice_no = Tk.StringVar()
        invoicedate = Tk.StringVar()
        invoicenote = Tk.StringVar()
        if po_rec == None:
            for i, is_activated in enumerate(info.order.activated):
                if is_activated:
                    row = i + 1
                    product = info.order.products[i]
                    products.append(product)

                    pname.append(Tk.StringVar())
                    pname[-1].set(product.label())
                    p_qty.append(Tk.StringVar())
                    p_qty[-1].set(info.order.qty[i].get())
                    p_sku.append(Tk.StringVar())
                    p_sku[-1].set(product.SKU)
                    pcost.append(Tk.StringVar())
                    pcost[-1].set(info.order.price[i].get())
                    punit.append(Tk.StringVar())
                    punit[-1].set(product.UM)
                    putot.append(Tk.StringVar())
                    putot[-1].set(u'')

                    p_qty[-1].trace('w', show_total_units )

                    Tk.Label(prod_frame, textvariable=pname[-1], anchor=W, bg=u'cyan').grid(row=row, column=0, sticky=W)
                    Tk.Entry(prod_frame, textvariable=p_qty[-1], width=8).grid(row=row, column=1)
                    Tk.Label(prod_frame, textvariable=p_sku[-1], anchor=W).grid(row=row, column=2, sticky=W)
                    Tk.Label(prod_frame, text=u'$', anchor=E).grid(row=row, column=3, sticky=E)
                    Tk.Entry(prod_frame, textvariable=pcost[-1], width=8).grid(row=row, column=4)
                    Tk.Label(prod_frame, text=u'per').grid(row=row, column=5)
                    Tk.Label(prod_frame, textvariable=punit[-1]).grid(row=row, column=6)
                    Tk.Label(prod_frame, textvariable=putot[-1], anchor=E).grid(row=row, column=7, sticky=E)
            show_total_units()

            # Delivery info entry
            separator = Tk.Frame(editPOwin, height=6, borderwidth=6, relief=Tk.SUNKEN)
            separator.grid(row=9, column=0, columnspan=10, sticky=W+E, padx=5, pady=5)
            delivery_fields = []
            delivered_bool.set(False)
            Tk.Checkbutton(editPOwin, text=u'輸入出貨表 \u26DF (捷徑全交)', variable=delivered_bool).grid(row=10, column=0, columnspan=6)
            Tk.Label(editPOwin, text=u'貨單編號').grid(row=11, column=0)
            Tk.Label(editPOwin, text=u'貨單日期').grid(row=11, column=3)
            Tk.Label(editPOwin, text=u'送貨司機').grid(row=12, column=0)
            Tk.Label(editPOwin, text=u'送貨卡車').grid(row=12, column=3)
            Tk.Label(editPOwin, text=u'貨單備註').grid(row=13, column=0)
            entry = Tk.Entry(editPOwin, textvariable=deliveryID)
            entry.grid(row=11, column=1, columnspan=2, sticky=Tk.W+Tk.E)
            delivery_fields.append(entry)
            b = Tk.Button(editPOwin, textvariable=deliverydate, bg='DarkGoldenrod1')
            b['command'] = lambda tv=deliverydate: date_picker(tv)
            b.grid(row=11, column=4)
            deliverydate.set(datetime.date.today())
            delivery_fields.append(b)
            entry = Tk.Entry(editPOwin, textvariable=deliverydriver)
            entry.grid(row=12, column=1, columnspan=2, sticky=W+E)
            delivery_fields.append(entry)
            entry = Tk.Entry(editPOwin, textvariable=deliverytruck)
            entry.grid(row=12, column=4, columnspan=2, sticky=W+E)
            delivery_fields.append(entry)
            entry = Tk.Entry(editPOwin, textvariable=deliverynote)
            entry.grid(row=13, column=1, columnspan=6, sticky=W+E)
            delivery_fields.append(entry)


            def toggle_delivery_fields():
                if delivered_bool.get():
                    for field in delivery_fields:
                        field.config(state=Tk.NORMAL)
                else:
                    for field in delivery_fields:
                        field.config(state=Tk.DISABLED)
            delivered_bool.trace("w", lambda *args: toggle_delivery_fields())


            # Invoice info entry
            separator = Tk.Frame(editPOwin, height=6, borderwidth=6, relief=Tk.SUNKEN)
            separator.grid(row=19, column=0, columnspan=10, sticky=W+E, padx=5, pady=5)
            invoice_fields = []
            invoiced_bool = Tk.BooleanVar()
            invoiced_bool.set(False)
            Tk.Checkbutton(editPOwin, text=u'輸入發票 \u2696 (捷徑全發)', variable=invoiced_bool).grid(row=20, column=0, columnspan=6)
            Tk.Label(editPOwin, text=u'發票編號').grid(row=21, column=0)
            Tk.Label(editPOwin, text=u'發票日期').grid(row=21, column=3)
            Tk.Label(editPOwin, text=u'發票備註').grid(row=23, column=0)
            entry = Tk.Entry(editPOwin, textvariable=invoice_no)
            entry.grid(row=21, column=1, columnspan=2, sticky=W+E)
            invoice_fields.append(entry)
            b = Tk.Button(editPOwin, textvariable=invoicedate, bg='DarkGoldenrod1')
            b['command'] = lambda tv=invoicedate: date_picker(tv)
            b.grid(row=21, column=4)
            invoicedate.set(datetime.date.today())
            invoice_fields.append(b)
            entry = Tk.Entry(editPOwin, textvariable=invoicenote)
            entry.grid(row=23, column=1, columnspan=6, sticky=W+E)
            invoice_fields.append(entry)

            def toggle_invoice_fields():
                if invoiced_bool.get():
                    for field in invoice_fields:
                        field.config(state=Tk.NORMAL)
                else:
                    for field in invoice_fields:
                        field.config(state=Tk.DISABLED)
            invoiced_bool.trace("w", lambda *args: toggle_invoice_fields())

            toggle_delivery_fields()
            toggle_invoice_fields()
        else: #Load PO
            order_number_str.set(po_rec.orderID)
            seller_str.set(po_rec.seller)
            buyer_str.set(po_rec.buyer)
            orderdate_str.set(po_rec.orderdate)
            duedate_str.set(po_rec.duedate)
            info.order.applytax.set(po_rec.applytax)
            order_note_str.set(po_rec.ordernote)

            Order = info.dmv2.Order
            session = info.dmv2.session
            if po_rec.orderID:
                prodorders = session.query(Order).filter_by(orderID=po_rec.orderID).all()
            else:
                prodorders = [po_rec]

            for i in range(len(prodorders)):
                row = i + 1
                order = prodorders[i]

                pname.append(Tk.StringVar())
                pname[-1].set(order.product.label())
                p_qty.append(Tk.StringVar())
                p_qty[-1].set(order.totalskus)
                p_sku.append(Tk.StringVar())
                p_sku[-1].set(order.product.SKU)
                pcost.append(Tk.StringVar())
                pcost[-1].set(order.price)
                punit.append(Tk.StringVar())
                punit[-1].set(order.product.UM)
                putot.append(Tk.StringVar())
                putot[-1].set(u'')

                p_qty[-1].trace('w', show_total_units)

                Tk.Label(prod_frame, textvariable=pname[-1], anchor=W, bg=u'cyan').grid(row=row, column=0, sticky=W)
                Tk.Entry(prod_frame, textvariable=p_qty[-1], width=8).grid(row=row, column=1)
                Tk.Label(prod_frame, textvariable=p_sku[-1], anchor=W).grid(row=row, column=2, sticky=W)
                Tk.Label(prod_frame, text=u'$', anchor=E).grid(row=row, column=3, sticky=E)
                Tk.Entry(prod_frame, textvariable=pcost[-1], width=8).grid(row=row, column=4)
                Tk.Label(prod_frame, text=u'per').grid(row=row, column=5)
                Tk.Label(prod_frame, textvariable=punit[-1]).grid(row=row, column=6)
                Tk.Label(prod_frame, textvariable=putot[-1], anchor=E).grid(row=row, column=7, sticky=E)
            show_total_units()

            #TODO: Show lists of shipments and invoices. Click to open and view.




        separator = Tk.Frame(editPOwin, height=6, borderwidth=6, relief=Tk.SUNKEN)
        separator.grid(row=100, column=0, columnspan=10, sticky=W+E, padx=5, pady=5)





    separator = Tk.Frame(fp, height=6, borderwidth=6, relief=Tk.SUNKEN)
    separator.grid(row=99, column=0, columnspan=10, sticky=W+E, padx=5, pady=5)

    b = Tix.Button(fp, text=u'創造PO表', command=edit_PO)
    b.grid(row=100, column=0, rowspan=2, sticky=N+S+E+W)
    b.config(bg='SpringGreen2')


    info.order.seller_menu = Tk.OptionMenu(fp, seller_str, None)
    info.order.buyer_menu = Tk.OptionMenu(fp, buyer_str, u'台茂')

    separator = Tk.Frame(fp, height=6, borderwidth=6, relief=Tk.SUNKEN)
    separator.grid(row=1000, column=0, columnspan=10, sticky=W+E, padx=5, pady=5)

    # Refresh is called from the load company method
    #TODO: Refresh after adding a product
    info.method.reload_products_frame = reload_products_frame




    frameProducts.pack(side=TOP, fill=BOTH)
#    frameIn2.pack(side=Tk.TOP, fill=BOTH)
    frameIn.pack(fill=BOTH)



    def create_manifest_form(orders):

        fs = Tix.Toplevel(width=700)
        fs.title(u"New Manifest Form")

        def date_picker():
            _=dp.Calendar(fs, textvariable=shipment_date_str)
            _.grid(row=0, column=0, rowspan=30, columnspan=6, sticky=W+E+N+S)



        # Add order fields
        shipment_date_str = Tk.StringVar()
        shipment_number_str = Tk.StringVar()
        def plate_capitalize():
            #TODO: Detect backspace or deleting and do not fill
            before = shipment_number_str.get()
            if len(before) > 0:
                after = before.upper()
                if before != after:
                    shipment_number_str.set(after)
            before = shipment_truck_str.get()
            if len(before) > 0:
                after = before.upper()
                if before != after:
                    shipment_truck_str.set(after)
                plate_list = info.dmv2.session.query(info.dmv2.Vehicle.id).all()
                plate_list = [p.id for p in plate_list]
                for plate in plate_list:
                    if plate.startswith(after):
                        shipment_truck_str.set(plate)
                        break

        shipment_number_str.trace('w', lambda *args:plate_capitalize())
        shipment_note_str = Tk.StringVar()
        shipment_driver_str = Tk.StringVar()
        shipment_truck_str = Tk.StringVar()
        shipment_truck_str.trace('w', lambda *args:plate_capitalize())

        fi = ttk.Frame(fs, height=6, borderwidth=10, relief=Tk.RAISED)
        separator = Tk.Frame(fi, height=6, borderwidth=6, relief=Tk.SUNKEN)
        separator.grid(row=0, column=0, columnspan=10, sticky=Tk.W+Tk.E, padx=5, pady=5)

    #    Tk.Label(fi, text=u'台茂化工儀器原料行').grid(row=1, column=0)

        Tk.Label(fi, text=u'貨單編號 #').grid(row=11, column=0)
        Tk.Entry(fi, textvariable=shipment_number_str).grid(row=11, column=1, sticky=Tk.W+Tk.E)

        Tk.Label(fi, text=u'  貨單日期').grid(row=11, column=2)
        Tk.Button(fi, textvariable=shipment_date_str, command=date_picker, bg='DarkGoldenrod1').grid(row=11, column=3, sticky=W)

        Tk.Label(fi, text=u'Note 備註').grid(row=12, column=0)
        Tk.Entry(fi, textvariable=shipment_note_str).grid(row=12, column=1, columnspan=10, sticky=Tk.W+Tk.E)

        Tk.Label(fi, text=u'Driver 司機').grid(row=13, column=0)
        Tk.Entry(fi, textvariable=shipment_driver_str).grid(row=13, column=1, sticky=Tk.W+Tk.E)

        Tk.Label(fi, text=u'  槽車號碼').grid(row=13, column=2)
        Tk.Entry(fi, textvariable=shipment_truck_str).grid(row=13, column=3, sticky=Tk.W+Tk.E)

        def submit_manifest():
            #TODO: Check if manifest number already used and confirm to attach to previous
            if shipment_number_str.get() in [u'', None, u'None']:
                okay = tkMessageBox.askokcancel(u'Manifest number warning', u'You did not enter a manifest number (書或編號).\Submit anyway?')
                if not okay:
                    return


            for i, rec in enumerate(orders):
                # SET delivery date.
                ddate = datetime.date(*map(int,shipment_date_str.get().split('-')))

                if qty_SV[i].get() in [None, u'', 0, u'0']:
                    continue
                # Create dictionary for database insert.
                ship_dict = dict(
                    order_id= rec.id,

                    sku_qty= int(qty_SV[i].get()),

                    shipmentdate= ddate, #Same for all

                    shipmentID= shipment_number_str.get(), #Same for all
                    shipmentnote= shipment_note_str.get(), #Same for all
                    driver= shipment_driver_str.get(),
                    truck= shipment_truck_str.get(),
                )
#                print ship_dict
                info.dmv2.append_shipment(rec.id, ship_dict)

                #Add license to database if new
                truck_rec = info.dmv2.session.query(info.dmv2.Vehicle).get(shipment_truck_str.get())
                if truck_rec == None:
                    info.dmv2.session.add(info.dmv2.Vehicle(id=shipment_truck_str.get()))
                    info.dmv2.session.commit()

            info.method.reload_orders(info)
            refresh_order_listbox_all()
            fs.destroy()
            info.method.refresh_manifest_listbox()

        b = Tk.Button(fi, text=u'Submit Manifest (提交)', command=submit_manifest)
        b.grid(row=110, column=1, columnspan=2)
        b.config(bg='SpringGreen2')

        shipment_date_str.set(datetime.date.today())

        separator = Tk.Frame(fi, height=6, borderwidth=6, relief=Tk.SUNKEN)
        separator.grid(row=200, column=0, columnspan=10, sticky=Tk.W+Tk.E, padx=5, pady=5)

        fi.grid(row=0, column=0, columnspan=6, sticky=N+S+E+W)

        # Clean up or delete previous data
        ordered_qty = [rec.totalskus for rec in orders]
        shipped_qty = [rec.qty_shipped() for rec in orders]

        plength = len(orders)
        qty_SV = [Tk.StringVar() for i in range(plength)]
#        allshipped_BV = [Tk.BooleanVar() for i in range(plength)]


        # Fill-in or clear out the desired quantity for a product.
        def match_qty(row):
            tmp = ordered_qty[row]
            dif = tmp - shipped_qty[row]
            if str(dif) != qty_SV[row].get() and dif != 0:
                qty_SV[row].set(dif)
            else:
                # Clear field if the number was already entered (undo auto-entry)
                qty_SV[row].set(u'')
#            w_entryfields[row].focus()
#            w_entryfields[row].icursor(Tk.END)
#            w_entryfields[row].selection_range(0, Tk.END)


#        w_labels_MPNs = []
#        w_entryfields = []
#        w_labels_SKUs = []


        for i, each in enumerate([u'品名',u'這次件數',u'(剩下/要求)']):#,u'全交了?'
            Tk.Label(fs, text=each).grid(row=9,column=i)

        # Add new product rows
        for rid, rec in enumerate(orders):
            bw = Tk.Label(fs, text=rec.product.summary, bg=u'cyan')
            bw.grid(row=rid+10, column=0, sticky=Tk.W+Tk.E)

            ew = Tk.Entry(fs, textvariable=qty_SV[rid], width=8, justify=Tk.CENTER)
            ew.grid(row=rid+10,column=1)
            ew.config(selectbackground=u'LightSkyBlue1', selectforeground=u'black')

            lw = Tk.Label(fs, text=u'( {} / {} )'.format(rec.totalskus-shipped_qty[rid],rec.totalskus), justify=Tk.CENTER)
            lw.grid(row=rid+10,column=2)#, sticky=Tk.W)

            #Fill in remaining qty
            match_qty(rid)

