#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Tkinter as Tk
import tkMessageBox
import ttk
import tkFont
import datetime
import frame_company_editor
import locale
import date_picker as dp
locale.setlocale(locale.LC_ALL, '')

def make_order_entry_frame(frame, info):
    info.order = info.__class__()
    incoming = False if info.src == 'Sales' else True
    frameIn = ttk.Frame(frame)
    b = Tk.Button(frameIn, text=u"編輯紀錄",
                  command=lambda:edit_order(info), bg=u'light salmon')
    b.pack(side=Tk.BOTTOM, fill=Tk.X)
#    b = Tk.Button(frameIn, text=u"編輯 (下劃線的記錄)",
#            command=lambda:copyrecord(info,True))
#    b.pack(side=Tk.BOTTOM, fill=Tk.X)
    scrollbar2 = Tk.Scrollbar(frameIn, orient=Tk.VERTICAL)
    info.listbox.rec_orders = Tk.Listbox(frameIn, selectmode=Tk.BROWSE,
                         yscrollcommand=scrollbar2.set,
                         font=(info.settings.font, "12"), height=100, exportselection=0)

#    info.listbox.rec_orders.bind("<ButtonRelease-1>", lambda _:set_info_rec(info))
#    info.listbox.rec_orders.bind("<Double-Button-1>", lambda _:copyrecord(info,True))
    scrollbar2.config(command=info.listbox.rec_orders.yview)
    scrollbar2.pack(side=Tk.RIGHT, fill=Tk.Y)
    info.listbox.rec_orders.pack(side=Tk.TOP, fill=Tk.BOTH)
    # Add right-click popup menu
    orderPopMenu = Tk.Menu(frameIn, tearoff=0)
    def refresh_listbox_item(id, index):
        #TODO: Refactor this and the list refresh in main to be consistent.
        recvals = info.dmv2.get_order(id)
        info.listbox.rec_orders.delete(index)
        info.listbox.rec_manifest.delete(index)
        info.listbox.rec_orders.insert(index, info.method.format_order_summary(recvals))
        info.listbox.rec_manifest.insert(index, info.method.format_order_summary(recvals))
        info.listbox.rec_orders.select_clear(0, Tk.END)
        info.listbox.rec_orders.select_set(index)
        info.listbox.rec_orders.activate(index)
        info.listbox.rec_manifest.select_set(index)
        info.listbox.rec_manifest.activate(index)

        no_ship_color = dict(bg=u'lavender', selectbackground=u'dark orchid')
        shipped_color = dict(bg=u'DarkOliveGreen1', selectbackground=u'firebrick1')
        insert_colors =  shipped_color if info.order_records[index].all_shipped() else no_ship_color
        info.listbox.rec_manifest.itemconfig(index, insert_colors)
        info.listbox.rec_orders.itemconfig(index, insert_colors)

    info.method.refresh_listbox_item = refresh_listbox_item

#    def toggle_delivered(info):
#        #TODO: Auto enter and attach a shipment
#        active_index = info.listbox.rec_orders.index(Tk.ACTIVE)
#        rec_id = info.order_rec_IDs[active_index]
#        rec = info.dmv2.get_order(rec_id)
#        updates = dict(delivered=False if rec.delivered else True)
##        if u'.0' in rec.deliveryID:
##            updates['deliveryID'] = '{:0>7}'.format(int(float(rec.deliveryID)))
#        info.dmv2.update_order(rec_id, updates)
#        refresh_listbox_item(rec_id, active_index)
#
#
#    def toggle_paid(info):
#        #TODO: Auto enter and attach a payment
#        active_index = info.listbox.rec_orders.index(Tk.ACTIVE)
#        rec_id = info.order_rec_IDs[active_index]
#        rec = info.dmv2.get_order(rec_id)
#        updates = dict(paid=False if rec.paid else True)
#        info.dmv2.update_order(rec_id, updates)
#        refresh_listbox_item(rec_id, active_index)

    def delete_order(info):
        info.dmv2.delete_order(info.order_rec_IDs[info.listbox.rec_orders.index(Tk.ACTIVE)])
        info.method.reload_orders(info)
        info.method.refresh_listboxes(info)

#    orderPopMenu.add_command(label=u"編輯 (下劃線的記錄)", command=lambda:copyrecord(info, editmode=True))
#    orderPopMenu.add_command(label=u'切換:已交貨', command=lambda:toggle_delivered(info))
#    orderPopMenu.add_command(label=u'切換:已支付', command=lambda:toggle_paid(info))
    orderPopMenu.add_command(label=u'刪除', command=lambda:delete_order(info))

    def orderoptions(event):
        orderPopMenu.post(event.x_root, event.y_root)
    info.listbox.rec_orders.bind("<Button-3>", orderoptions)
#    info.listbox.rec_orders.bind("<F1>", lambda _:toggle_delivered(info))
#    info.listbox.rec_orders.bind("<F2>", lambda _:toggle_paid(info))
#    info.listbox.rec_orders.insert(0,*orderlist)






    frameProducts = fp = ttk.Frame(frame)
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
        info.order.applytax.trace("w", lambda *args:activate())
        info.order.recent_orders = []
        for rec in info.order.products:
            info.order.recent_orders.append(
                        info.dmv2.get_product_recent_order(rec.MPN, update=True))


        if info.incoming:
            seller_opts = [b.name for b in info.dmv2.branches(info.curr_company)]
            buyer_opts = [u'台茂',u'富茂',u'永茂']
        else:
            seller_opts = [u'台茂',u'富茂',u'永茂']
            buyer_opts = [b.name for b in info.dmv2.branches(info.curr_company)]
        smenu = info.order.seller_menu['menu']
        smenu.delete(0,Tk.END)
        bmenu = info.order.buyer_menu['menu']
        bmenu.delete(0,Tk.END)
        [smenu.add_command(label=choice, command=Tk._setit(seller_str, choice)) for choice in seller_opts]
        [bmenu.add_command(label=choice, command=Tk._setit(buyer_str, choice)) for choice in buyer_opts]
        try:
            seller_str.set(seller_opts[0])
            buyer_str.set(buyer_opts[0])
        except IndexError:
            tkMessageBox.showwarning(u'Company not in catalog.', u'Add this company to the catalog\nto avoid future errors.')


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
                    except:
                        pass #info.order.qty[row].set(u'')
                    try:
                        price = float(info.order.price[row].get())
                    except:
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
                    info.order.subtotal[row].set(locale.currency( x, grouping=True ))
                    subtax = x*0.05 if info.order.applytax.get() else 0.0
                    info.order.taxed[row].set(locale.currency( subtax, grouping=True ))
                    info.order.total[row].set(locale.currency( x+subtax, grouping=True ))
                subtotal.set(locale.currency( st, grouping=True ))
                subtax = st*0.05 if info.order.applytax.get() else 0.0
                tax_amt.set(locale.currency( subtax, grouping=True ))
                totalcharge.set(locale.currency( st+subtax, grouping=True ))


                for i in range(plength):
                    if info.order.activated[i] == True and info.order.recent_orders[i] != None:
                        seller_str.set(info.order.recent_orders[i].seller)
                        buyer_str.set(info.order.recent_orders[i].buyer)
                        break

            except:
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
        except:
            pass
        info.order.buttons = []
        info.order.entryWs = []
        info.order.labelSubtotal = []
        info.order.labelTaxed = []
        info.order.labelTotal = []
        info.order.widgets = [] # Holder for all other elements to delete on refresh.


        # Add new product rows
        for row, product in enumerate(info.order.products):
            #TODO: Have button fill in data from last order, i.e. quantity, taxed.
            bw = Tk.Button(fp, text=product.summary, bg='grey',
                           command=lambda i=row:match_qty(i))
            bw.grid(row=row, column=0, sticky=Tk.W+Tk.E)
            info.order.buttons.append(bw)

            ew = Tk.Entry(fp, textvariable=info.order.qty[row], width=8, justify=Tk.CENTER)
            ew.grid(row=row,column=1)
            ew.config(selectbackground=u'LightSkyBlue1', selectforeground=u'black')
            ew.config(highlightcolor=u'cyan', highlightthickness=4)
            info.order.entryWs.append(ew)
            info.order.qty[row].trace("w", lambda *args:activate())

            lw = Tk.Label(fp, text=u'{} @ $'.format(product.SKU), width=8, justify=Tk.RIGHT)
            lw.grid(row=row,column=2)
            info.order.widgets.append(lw)

            ew = Tk.Entry(fp, textvariable=info.order.price[row], width=8)
            ew.grid(row=row,column=3)
            info.order.widgets.append(ew)
            info.order.price[row].set(product.curr_price)
            info.order.price[row].trace("w", lambda *args:activate())
#            info.order.price[row].set(product.curr_price)

            txt = u'per {}'.format(product.UM if product.unitpriced else product.SKU)
            lw = Tk.Label(fp, text=txt, width=8)
            lw.grid(row=row,column=4)
            info.order.widgets.append(lw)

            lw = Tk.Label(fp, textvariable=info.order.subtotal[row], width=12)
            lw.grid(row=row,column=5)
            info.order.labelSubtotal.append(lw)

            lw = Tk.Label(fp, textvariable=info.order.taxed[row], width=12)
            lw.grid(row=row,column=6)
            info.order.labelTaxed.append(lw)

            lw = Tk.Label(fp, textvariable=info.order.total[row], width=12)
            lw.grid(row=row,column=7)
            info.order.labelTotal.append(lw)
        info.order.applytax.set(True)
    #END: reload_products_frame()

    # Add order fields
    subtotal = Tk.StringVar()
    tax_amt = Tk.StringVar()
    totalcharge = Tk.StringVar()
    order_duedate_str = Tk.StringVar()
    order_date_label = Tk.StringVar()
    order_number_str = Tk.StringVar()
    order_number_label = Tk.StringVar()
    order_delivered_bool = Tk.BooleanVar()
    order_note_str = Tk.StringVar()
    order_note_label = Tk.StringVar()
    shipment_driver_str = Tk.StringVar()
    shipment_truck_str = Tk.StringVar()
    Tk.Label(fp, text=u'Subtotal').grid(row=100, column=5)
    Tk.Label(fp, textvariable=subtotal).grid(row=101, column=5)
    Tk.Button(fp, text=u'Tax (?)', command=toggle_tax_all, bg='violet').grid(row=100, column=6)
    Tk.Label(fp, textvariable=tax_amt).grid(row=101, column=6)
    Tk.Label(fp, text=u'Total').grid(row=100, column=7)
    Tk.Label(fp, textvariable=totalcharge).grid(row=101, column=7)

    def submit_order():
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
                seller= seller_str.get()
                buyer= buyer_str.get()

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
        info.method.refresh_listboxes(info)
        reset_order_fields()
#        toggle_delivery_labels() #TIP: Can change this to adding a trace on the BoolenVar.
    #END: submit_order()


    def reset_order_fields():
        for entry in info.order.qty:
            entry.set(u'')
        order_number_str.set(u'')
        order_note_str.set(u'')
#        order_delivered_bool.set(False)
#        order_duedate_str.set(datetime.date.today())

    def date_picker():
        dp.Calendar(fp, textvariable=order_duedate_str).grid(row=100, column=0, rowspan=3,columnspan=3, sticky=Tk.W+Tk.E)

    def toggle_delivery_labels():
        if order_delivered_bool.get():
            order_date_label.set(u'Delivery Date')
            order_note_label.set(u'Delivery Note')
            order_number_label.set(u'Delivery Number')
            driver_field.config(state=Tk.NORMAL)
            truck_field.config(state=Tk.NORMAL)
        else:
            order_date_label.set(u'Due Date')
            order_note_label.set(u'Order Note')
            order_number_label.set(u'Order Number')
            driver_field.config(state=Tk.DISABLED)
            truck_field.config(state=Tk.DISABLED)


    seller_str = Tk.StringVar()
    buyer_str = Tk.StringVar()


    Tk.Label(fp, text=u'>>>>>>>>>>').grid(row=100, column=3, columnspan=2)
    info.order.seller_menu = Tk.OptionMenu(fp, seller_str, None)
    info.order.seller_menu.grid(row=100, column=3)
    info.order.seller_menu.config(bg=u'DarkOrchid4', fg=u'white')
    info.order.buyer_menu = Tk.OptionMenu(fp, buyer_str, u'台茂')
    info.order.buyer_menu.grid(row=100, column=4)
    info.order.buyer_menu.config(bg=u'DarkOrchid4', fg=u'white')

    Tk.Label(fp, textvariable=order_date_label).grid(row=100, column=0)
    order_date_label.set(u'Due Date')
    Tk.Button(fp, textvariable=order_duedate_str, command=date_picker, bg='DarkGoldenrod1').grid(row=100, column=1)
    Tk.Label(fp, textvariable=order_number_label).grid(row=101, column=0)
    order_number_label.set(u'Order Number')
    Tk.Entry(fp, textvariable=order_number_str).grid(row=101, column=1, columnspan=2, sticky=Tk.W+Tk.E)
    Tk.Label(fp, textvariable=order_note_label).grid(row=102, column=0)
    order_note_label.set(u'Order Note')
    Tk.Entry(fp, textvariable=order_note_str).grid(row=102, column=1, columnspan=7, sticky=Tk.W+Tk.E)
    Tk.Checkbutton(fp, text=u'已交\u26DF', variable=order_delivered_bool).grid(row=100, column=2)#, columnspan=2)
    order_delivered_bool.trace("w", lambda *args:toggle_delivery_labels())
    b = Tk.Button(fp, text=u'Submit Order', command=submit_order)
    b.grid(row=101, column=3, columnspan=2)
    b.config(bg='SpringGreen2')
    order_duedate_str.set(datetime.date.today())

    Tk.Label(fp, text=u'Driver 司機').grid(row=103, column=0)
    driver_field = Tk.Entry(fp, textvariable=shipment_driver_str, state=Tk.DISABLED)
    driver_field.grid(row=103, column=1, columnspan=2, sticky=Tk.W+Tk.E)

    Tk.Label(fp, text=u'Truck 槽車號碼').grid(row=103, column=3)
    truck_field = Tk.Entry(fp, textvariable=shipment_truck_str, state=Tk.DISABLED)
    truck_field.grid(row=103, column=4, columnspan=2, sticky=Tk.W+Tk.E)

    separator = Tk.Frame(fp, height=6, borderwidth=6, relief=Tk.SUNKEN)
    separator.grid(row=1000, column=0, columnspan=10, sticky=Tk.W+Tk.E, padx=5, pady=5)

    # Refresh is called from the load company method
    #TODO: Refresh after adding a product
    info.method.reload_products_frame = reload_products_frame





    frameProducts.pack(side=Tk.TOP, fill=Tk.BOTH)
#    frameIn2.pack(side=Tk.TOP, fill=Tk.BOTH)
    frameIn.pack(fill=Tk.BOTH)



def edit_order(info):
    try:
        if info.editWin.state() == 'normal':
            info.editWin.focus_set()
        return
    except:
        pass

    selected_index = info.listbox.rec_orders.index(Tk.ACTIVE)
    order_id = info.order_rec_IDs[selected_index]
    record = info.dmv2.get_order(order_id)
    excluded = [u'MPN',u'id',u'group',u'recorddate',u'discount',u'note',u'is_sale',u'date']

    info.editWin = Tk.Toplevel(width=700)
    info.editWin.title(u"Edit:({}) {}".format(order_id,record.product.product_label))

    orderSVar = dict()

    def date_picker(row, var):
        dp.Calendar(info.editWin, textvariable=var).grid(row=row, column=1, rowspan=3,columnspan=3, sticky=Tk.W+Tk.E)


    fields = info.dmv2.Order.__table__.c.keys()
    fields = [(key, repr(info.dmv2.Order.__table__.c[key].type)) for key in fields]

    def update_order(info,orderSVar):
        #Check field entries
        updates = dict([(key,orderSVar[key].get()) for key in orderSVar])

        is_confirmed = tkMessageBox.askokcancel('Confirm update',
            u'Your changes are not verified\nand could cause an error.\nSubmit changes to this order?')
        if is_confirmed:
            info.editWin.destroy()
            # Make sure particular fields are deleted before update.
            for key in excluded:
                try:
                    del updates[key]
                except:
                    pass
            # Remove blank and None fields.
            for key in updates.keys():
                if updates[key] in [None, u'None', u'']:
                    del updates[key]
            # Convert strings to Date object if a date field.
            for key in updates.keys():
                if u'date' in key:
                    updates[key] = datetime.date(*map(int,updates[key].split('-')))

            info.dmv2.update_order(record.id, updates)
            info.method.refresh_listbox_item(order_id, selected_index)
        else:
            info.editWin.focus_set()


    for i, field in enumerate(fields):
        if field[0] in excluded:
            continue
        ttk.Label(info.editWin, text=field[0]).grid(row=i,column=0)
        if field[1].startswith("Bool"):
            orderSVar[field[0]] = Tk.BooleanVar()
            Tk.Radiobutton(info.editWin, text="True", variable=orderSVar[field[0]], value=True)\
                    .grid(row=i,column=1)
            Tk.Radiobutton(info.editWin, text="False", variable=orderSVar[field[0]], value=False)\
                    .grid(row=i,column=2)
        elif 'date' in field[0]:
            orderSVar[field[0]] = Tk.StringVar()
            Tk.Button(info.editWin, textvariable=orderSVar[field[0]], command=lambda row=i, var=orderSVar[field[0]]:date_picker(row,var), bg='DarkGoldenrod1').grid(row=i,column=1,columnspan=2)
        else:
            orderSVar[field[0]] = Tk.StringVar()
            ttk.Entry(info.editWin, textvariable=orderSVar[field[0]], width=20).grid(row=i,column=1,columnspan=2)
        # Set values from record.
        orderSVar[field[0]].set(record.__dict__[field[0]])


    Tk.Button(info.editWin, text="Update Order", command=lambda:update_order(info,orderSVar)).grid(row=99,column=0,columnspan=3)

