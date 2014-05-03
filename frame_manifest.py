#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
summary

description

:REQUIRES:

:TODO:

:AUTHOR: Ripley6811
:ORGANIZATION: None
:CONTACT: python@boun.cr
:SINCE: Mon Apr 28 13:28:16 2014
:VERSION: 0.1
"""
#===============================================================================
# PROGRAM METADATA
#===============================================================================
__author__ = 'Ripley6811'
__contact__ = 'python@boun.cr'
__copyright__ = ''
__license__ = ''
__date__ = 'Mon Apr 28 13:28:16 2014'
__version__ = '0.1'

#===============================================================================
# IMPORT STATEMENTS
#===============================================================================
import ttk
import Tkinter as Tk
import tkMessageBox
import date_picker as dp
import datetime

#===============================================================================
# METHODS
#===============================================================================

def create_manifest_frame(frame, info):
    info.manifest = info.__class__()
    incoming = info.incoming = False if info.src == 'Sales' else True

    frameIn = ttk.Frame(frame)

    scrollbar2 = Tk.Scrollbar(frameIn, orient=Tk.VERTICAL)
    info.listbox.rec_manifest = Tk.Listbox(frameIn, selectmode=Tk.MULTIPLE,
                         yscrollcommand=scrollbar2.set,
                         font=(info.settings.font, "12"), height=100, exportselection=0)
#    info.listbox.rec_manifest.bind("<Double-Button-1>", lambda _:copyrecord(info,True))
    scrollbar2.config(command=info.listbox.rec_manifest.yview)
    scrollbar2.pack(side=Tk.RIGHT, fill=Tk.Y)
    info.listbox.rec_manifest.pack(side=Tk.TOP, fill=Tk.BOTH)
    # Add right-click popup menu
    orderPopMenu = Tk.Menu(frameIn, tearoff=0)
    def refresh_listbox_item(id, index):
        info.method.refresh_listbox_item(id, index)

#    def toggle_delivered(info):
#        #TODO: Auto enter and attach a shipment (or not?)
#        active_index = info.listbox.rec_manifest.index(Tk.ACTIVE)
#        rec_id = info.order_rec_IDs[active_index]
#        rec = info.dmv2.get_order(rec_id)
##        updates = dict(delivered=False if rec.delivered else True)
##        if u'.0' in rec.deliveryID:
##            updates['deliveryID'] = '{:0>7}'.format(int(float(rec.deliveryID)))
#        info.dmv2.update_order(rec_id, updates)
#        refresh_listbox_item(rec_id, active_index)
#
#
#    def toggle_paid(info):
#        #TODO: Auto enter and attach a payment
#        active_index = info.listbox.rec_manifest.index(Tk.ACTIVE)
#        rec_id = info.order_rec_IDs[active_index]
#        rec = info.dmv2.get_order(rec_id)
#        updates = dict(paid=False if rec.paid else True)
#        info.dmv2.update_order(rec_id, updates)
#        refresh_listbox_item(rec_id, active_index)

    def delete_order(info):
        info.dmv2.delete_order(info.order_rec_IDs[info.listbox.rec_manifest.index(Tk.ACTIVE)])
        info.method.reload_orders(info)
        info.method.refresh_listboxes(info)

#    orderPopMenu.add_command(label=u"編輯 (下劃線的記錄)", command=lambda:copyrecord(info, editmode=True))
#    orderPopMenu.add_command(label=u'切換:已交貨', command=lambda:toggle_delivered(info))
#    orderPopMenu.add_command(label=u'切換:已支付', command=lambda:toggle_paid(info))
    orderPopMenu.add_command(label=u'刪除', command=lambda:delete_order(info))

    def orderoptions(event):
        orderPopMenu.post(event.x_root, event.y_root)
    info.listbox.rec_manifest.bind("<Button-3>", orderoptions)
#    info.listbox.rec_manifest.bind("<F1>", lambda _:toggle_delivered(info))
#    info.listbox.rec_manifest.bind("<F2>", lambda _:toggle_paid(info))
#    info.listbox.rec_manifest.insert(0,*orderlist)






    frameShipment = fs = ttk.Frame(frame)
    def reload_shipment_frame():
        # Clean up or delete previous data
        list_indices = map(int, info.listbox.rec_manifest.curselection())
        info.manifest.order_IDs = [info.order_rec_IDs[i] for i in list_indices]
        info.manifest.order_recs = [info.order_records[i] for i in list_indices]
        info.manifest.ordered_qty = [rec.totalskus for rec in info.manifest.order_recs]
        info.manifest.shipped = [rec.qty_shipped() for rec in info.manifest.order_recs]

        plength = len(list_indices)
        info.manifest.activated = [False] * plength
        info.manifest.qty = [Tk.StringVar() for i in range(plength)]
        info.manifest.allshipped = [Tk.BooleanVar() for i in range(plength)]

#        for i in range(plength):
#            if info.manifest.ordered_qty[i] == info.manifest.shipped[i]:
#                info.manifest.allshipped[i].set(True)

        def show_shipment(i, j):
            print 'show', (i,j)
            query_shipment = info.manifest.order_recs[i].shipments[j]
            display_manifest_for_edit(info, query_shipment)
        def del_shipment(i, j, b0, b1):
            print 'delete', (i,j)
            r = info.manifest.order_recs[i]
            s = r.shipments[j]
            delete = tkMessageBox.askokcancel(u'Delete Shipment?',
                                     u'Confirm to delete shipment of:\n{} {} on {}'
                                     .format(s.sku_qty,r.product.SKU,s.shipmentdate))
            if delete:
                info.dmv2.session.query(info.dmv2.Shipment).filter_by(id=s.id).delete()
                info.dmv2.session.commit()
#                info.dmv2.update_order(r.id, dict(delivered=False))
                b0.config(bg=u'red', state=Tk.DISABLED)
                b1.config(bg=u'gray24', state=Tk.DISABLED)
#                info.dmv2.session.commit()

                redo_indices = list(list_indices)
                info.method.reload_orders(info)
                info.method.refresh_listboxes(info)
#                reset_order_fields()
#                reload_shipment_frame()
                for index in redo_indices:
                    info.listbox.rec_manifest.selection_set(index)
                info.manifest.shipped = [rec.qty_shipped() for rec in info.manifest.order_recs]


        # Fill-in or clear out the desired quantity for a product.
        def match_qty(row):
            tmp = info.manifest.ordered_qty[row]
            dif = tmp - info.manifest.shipped[row]
            if str(dif) != info.manifest.qty[row].get() and dif != 0:
                info.manifest.qty[row].set(dif)
            else:
                # Clear field if the number was already entered (undo auto-entry)
                info.manifest.qty[row].set(u'')
            info.manifest.entryWs[row].focus()
            info.manifest.entryWs[row].icursor(Tk.END)
            info.manifest.entryWs[row].selection_range(0, Tk.END)


        def activate():
            try:
                for row in range(plength):
                    qty = 0
                    try:
                        qty = int(info.manifest.qty[row].get())
                    except:
                        pass

                    activated = True if qty > 0 else False

                    info.manifest.activated[row] = activated
                    info.manifest.buttons[row].config(bg='cyan' if activated else 'slate gray',
                                                    fg='black' if activated else 'snow')
                    if qty + info.manifest.shipped[row] >= info.manifest.ordered_qty[row]:
                        info.manifest.allshipped[row].set(True)
                    else:
                        info.manifest.allshipped[row].set(False)
            except:
                pass

        # Delete previous widgets if they exist.
        try:
            for i in range(len(info.manifest.buttons)):
                info.manifest.buttons.pop().destroy()
                info.manifest.entryWs.pop().destroy()
                info.manifest.totalSKUsLabel.pop().destroy()

            for i in range(len(info.manifest.widgets)):
                info.manifest.widgets.pop().destroy()
        except:
            pass

        info.manifest.buttons = []
        info.manifest.entryWs = []
        info.manifest.totalSKUsLabel = []
        info.manifest.widgets = [] # Holder for all other elements to delete on refresh.

        for i, each in enumerate([u'品名',u'這次件數',u'(剩下/要求)',u'出貨歷史']):#,u'全交了?'
            Tk.Label(fs, text=each).grid(row=0,column=i)

        # Add new product rows
        for row, rec in enumerate(info.manifest.order_recs):
            #TODO: Have button fill in data from last order, i.e. quantity, taxed.
            bw = Tk.Button(fs, text=rec.product.summary, bg=u'slate gray',
#                          command=None)
                          command=lambda i=row:match_qty(i))
            bw.grid(row=row+10, column=0, sticky=Tk.W+Tk.E)
            info.manifest.buttons.append(bw)

            ew = Tk.Entry(fs, textvariable=info.manifest.qty[row], width=8, justify=Tk.CENTER)
            ew.grid(row=row+10,column=1)
            ew.config(selectbackground=u'LightSkyBlue1', selectforeground=u'black')
            info.manifest.entryWs.append(ew)
            info.manifest.qty[row].trace("w", lambda *args:activate())

            lw = Tk.Label(fs, text=u'( {} / {} )'.format(rec.totalskus-info.manifest.shipped[row],rec.totalskus), justify=Tk.CENTER)
            lw.grid(row=row+10,column=2)#, sticky=Tk.W)
            info.manifest.totalSKUsLabel.append(lw)

#            cw = Tk.Checkbutton(fs, text=u'全交了', variable=info.manifest.allshipped[row], command=lambda i=row:adj_skus(i))
#            cw.grid(row=row+10, column=3)#, columnspan=2)
#            info.manifest.widgets.append(cw)


            """#TODO: Add buyer/seller branch switcher/verification. Maybe Payments window is better."""

            """#TODO: Show buttons for previous shipments."""

            for col, ship_rec in enumerate(rec.shipments):
                bw = Tk.Button(fs, text=u'\u26DF {} ({}/{})'.format(
                                            ship_rec.sku_qty,
                                            ship_rec.shipmentdate.month,
                                            ship_rec.shipmentdate.day), bg=u'khaki2',
                              command=lambda i=row, j=col:show_shipment(i,j))
                bw.grid(row=row+10, column=3+col*2, sticky=Tk.W+Tk.E)
                info.manifest.widgets.append(bw)
                bx = Tk.Button(fs, text=u'X', bg=u'red')
                bx.config(command=lambda i=row, j=col, b0=bw, b1=bx:del_shipment(i,j,b0,b1))
                bx.grid(row=row+10, column=4+col*2, sticky=Tk.W)
                info.manifest.widgets.append(bx)

        activate()
    #END: reload_shipment_frame()

    info.listbox.rec_manifest.bind("<ButtonRelease-1>", lambda _:reload_shipment_frame())

    # Add order fields
    shipment_date_str = Tk.StringVar()
    shipment_number_str = Tk.StringVar()
    shipment_note_str = Tk.StringVar()
    shipment_driver_str = Tk.StringVar()
    shipment_truck_str = Tk.StringVar()


    def submit_order():
        #TODO: Check if manifest number already used and confirm to attach to previous
        for i, (include, rec) in enumerate(zip(info.manifest.activated,info.manifest.order_recs)):
            if include:
                # SET delivery date.
                ddate = datetime.date(*map(int,shipment_date_str.get().split('-')))

                # Create dictionary for database insert.
                ship_dict = dict(
                    order_id= rec.id,

                    sku_qty= int(info.manifest.qty[i].get()),

                    shipmentdate= ddate, #Same for all

                    shipmentID= shipment_number_str.get(), #Same for all
                    shipmentnote= shipment_note_str.get(), #Same for all
                    driver= shipment_driver_str.get(),
                    truck= shipment_truck_str.get(),
                )
                print ship_dict
                info.dmv2.append_shipment(rec.id, ship_dict)

#                # Update delivered flag in order if necessary
#                print info.manifest.allshipped[i].get(),
#                delivered = info.manifest.allshipped[i].get()
#                print delivered
#                if delivered:
#                    info.dmv2.update_order(rec.id, dict(delivered=True))
#                    print 'updated'

        if not incoming:
            show_form()
        info.method.reload_orders(info)
        info.method.refresh_listboxes(info)
        reset_order_fields()
        reload_shipment_frame()
    #END: submit_order()

    def show_form():
        pass

    def reset_order_fields():
        for entry in info.manifest.qty:
            entry.set(u'')
        shipment_number_str.set(u'')
        shipment_note_str.set(u'')
        shipment_driver_str.set(u'')
        shipment_truck_str.set(u'')
        shipment_date_str.set(datetime.date.today())

    def date_picker():
        dp.Calendar(fi, textvariable=shipment_date_str).grid(row=100, column=0, rowspan=4,columnspan=3, sticky=Tk.W+Tk.E)


    frameInfo = fi = ttk.Frame(frame, height=6, borderwidth=10, relief=Tk.RAISED)
    separator = Tk.Frame(fi, height=6, borderwidth=6, relief=Tk.SUNKEN)
    separator.grid(row=0, column=0, columnspan=10, sticky=Tk.W+Tk.E, padx=5, pady=5)

#    Tk.Label(fi, text=u'台茂化工儀器原料行').grid(row=1, column=0)

    Tk.Label(fi, text=u'Delivery Date 貨單日期').grid(row=100, column=0)
    Tk.Button(fi, textvariable=shipment_date_str, command=date_picker, bg='DarkGoldenrod1').grid(row=100, column=1)

    Tk.Label(fi, text=u'Delivery \u2116 貨單編號').grid(row=101, column=0)
    Tk.Entry(fi, textvariable=shipment_number_str).grid(row=101, column=1, sticky=Tk.W+Tk.E)

    Tk.Label(fi, text=u'Delivery Note 備註').grid(row=102, column=0)
    Tk.Entry(fi, textvariable=shipment_note_str).grid(row=102, column=1, columnspan=10, sticky=Tk.W+Tk.E)

    Tk.Label(fi, text=u'Driver 司機').grid(row=103, column=0)
    Tk.Entry(fi, textvariable=shipment_driver_str).grid(row=103, column=1, sticky=Tk.W+Tk.E)

    Tk.Label(fi, text=u'Truck 槽車號碼').grid(row=103, column=2)
    Tk.Entry(fi, textvariable=shipment_truck_str).grid(row=103, column=3, sticky=Tk.W+Tk.E)

    b = Tk.Button(fi, text=u'Submit Manifest', command=submit_order)
    b.grid(row=100, column=2)
    b.config(bg='SpringGreen2')

    if not incoming:
        b = Tk.Button(fi, text=u'Preview 出貨單', command=show_form)
        b.grid(row=100, column=3)
        b.config(bg='light salmon')
    shipment_date_str.set(datetime.date.today())

    separator = Tk.Frame(fi, height=6, borderwidth=6, relief=Tk.SUNKEN)
    separator.grid(row=200, column=0, columnspan=10, sticky=Tk.W+Tk.E, padx=5, pady=5)

    # Refresh is called from the load company method
    #TODO: Refresh after adding a product
    info.method.reload_shipment_frame = reload_shipment_frame






    frameShipment.pack(side=Tk.BOTTOM, fill=Tk.BOTH)
    frameInfo.pack(side=Tk.BOTTOM, fill=Tk.BOTH)
#    frameIn2.pack(side=Tk.TOP, fill=Tk.BOTH)
    frameIn.pack(fill=Tk.BOTH)



def display_manifest_for_edit(info, shipment):
    #XXX: There's a chance that the ship_id might repeat, so check matching date as well.
    ship_id = shipment.shipmentID
    ship_date = shipment.shipmentdate
    query_id = shipment.id
    if ship_id in [None,u'None',u'']:
        tkMessageBox.showerror(u'Bad shipment number',u'Manifest number not found.\nShowing sample manifest for one product.')
#        return
        ship_id = u'NONE ENTERED'
        shipmentset = [shipment]
    else:
        shipmentset = info.dmv2.get_entire_shipment(shipment)
    print ship_id, repr(shipmentset)
    orderset = [info.dmv2.get_order(shi.order_id) for shi in shipmentset]

    #TIP: Uncomment below to restrict the popup window to one
#    try:
#        if info.shipmentWin.state() == 'normal':
#            info.shipmentWin.focus_set()
#        return
#    except:
#        pass



    info.shipmentWin = Tk.Toplevel(width=700)
    info.shipmentWin.title(u"Shipment: {}".format(ship_id))

    mani_font = (info.settings.font, "15")



    def submit_changes(info):
        #Check field entries
#        new_prod = dict()
#
#        if not new_prod['inventory_name'] or not new_prod['UM'] or not new_prod['SKU']:
#            return
#
#        try:
#            float(new_prod['units'])
#        except:
#            return
#

        info.shipmentWin.destroy()
#        try:
#            del productSVar['MPN']
#        except:
#            pass
#        info.dmv2.session.query(info.dmv2.Product).filter(info.dmv2.Product.MPN==pID).update(new_prod)
#        info.dmv2.session.commit()
#        if refresh_products_list:
#            refresh_products_list()


    cell_config = dict(
        font= mani_font+(u'bold',),
        bg= u'cornsilk',
        height=2,
    )

    sellertxt = u''
    if info.incoming:
        sellertxt = u'{} ({})'.format(orderset[0].seller, orderset[0].group)
    else:
        sellertxt = u'{}'.format(orderset[0].seller)

    Tk.Label(info.shipmentWin, text=sellertxt, **cell_config).grid(row=0,column=0, columnspan=6, sticky=Tk.W+Tk.E)


    cell_config.update(anchor=Tk.W)

    branch = info.dmv2.get_branch(orderset[0].buyer)

    kehu = u'客戶名稱: {}'.format(branch.name)
    Tk.Label(info.shipmentWin, text=kehu, **cell_config).grid(row=1,column=0, columnspan=2, sticky=Tk.W+Tk.E)

    contactname = branch.contacts[0].name if len(branch.contacts) else u''
    lianluo = u'聯 絡 人: {}'.format(contactname)
    Tk.Label(info.shipmentWin, text=lianluo, **cell_config).grid(row=2,column=0, columnspan=2, sticky=Tk.W+Tk.E)

    contactphone = branch.contacts[0].phone if len(branch.contacts) else branch.phone
    dianhua = u'聯絡電話: {}'.format(contactphone)
    Tk.Label(info.shipmentWin, text=dianhua, **cell_config).grid(row=3,column=0, columnspan=6, sticky=Tk.W+Tk.E)

    shipaddress = branch.address_shipping if branch.address_shipping else branch.address_office
    songhuo = u'送貨地址: {}'.format(shipaddress)
    Tk.Label(info.shipmentWin, text=songhuo, **cell_config).grid(row=4,column=0, columnspan=6, sticky=Tk.W+Tk.E)



    tongyi = u'統一編號: {}'.format(branch.tax_id)
    Tk.Label(info.shipmentWin, text=tongyi, **cell_config).grid(row=1,column=2, columnspan=2, sticky=Tk.W+Tk.E)

    fapiao = u'發票號碼: {}'.format(u'')
    Tk.Label(info.shipmentWin, text=fapiao, **cell_config).grid(row=2,column=2, columnspan=2, sticky=Tk.W+Tk.E)



    riqi = u'貨單日期: {0.year}年 {0.month}月 {0.day}日'.format(shipmentset[0].shipmentdate)
    Tk.Label(info.shipmentWin, text=riqi, **cell_config).grid(row=1,column=4, columnspan=2, sticky=Tk.W+Tk.E)

    huodan = u'貨單編號: {}'.format(ship_id)
    Tk.Label(info.shipmentWin, text=huodan, **cell_config).grid(row=2,column=4, columnspan=2, sticky=Tk.W+Tk.E)


    cell_config = dict(
        font= mani_font,
        bg= u'LightSteelBlue1',
        relief=Tk.RAISED,
    )
    for i, each in enumerate([u'品名',u'規格/包裝',u'件數',u'數量',u'包裝描述',u'出貨資訊']):
        Tk.Label(info.shipmentWin, text=each, **cell_config).grid(row=9,column=i, sticky=Tk.W+Tk.E)


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
    for row, (shipment, order) in enumerate(zip(shipmentset, orderset)):
        config = query_config if shipment.id == query_id else cell_config
#        print shipment
#        print '  ', order
        pinming = u' {} '.format(order.product.product_label if order.product.product_label else order.product.inventory_name)
        guige = u'  {} {} / {}  '.format(order.product.units, order.product.UM, order.product.SKU)
        jianshu = u'  {} {}  '.format(shipment.sku_qty, order.product.UM if order.product.SKU == u'槽車' else order.product.SKU)
        this_units = u'  {} {}  '.format(order.product.units * shipment.sku_qty, order.product.UM)
        Tk.Label(info.shipmentWin, text=pinming, **config).grid(row=10+row,column=0, sticky=Tk.W+Tk.E)
        Tk.Label(info.shipmentWin, text=guige, **config).grid(row=10+row,column=1, sticky=Tk.W+Tk.E)
        Tk.Label(info.shipmentWin, text=jianshu, **config).grid(row=10+row,column=2, sticky=Tk.W+Tk.E)
        Tk.Label(info.shipmentWin, text=this_units, **config).grid(row=10+row,column=3, sticky=Tk.W+Tk.E)
        Tk.Label(info.shipmentWin, bg=u'gray30', fg=u'gray70', text=u'  {}  '.format(order.product.SKUlong)).grid(row=10+row,column=4, sticky=Tk.W+Tk.E)
        Tk.Label(info.shipmentWin, text=u'  {}  '.format(order.ordernote), **config).grid(row=10+row,column=5, sticky=Tk.W+Tk.E)


#    check_no = Tk.StringVar()
#    ttk.Label(info.shipmentWin, text=u'Check number').grid(row=101,column=0)
#    ttk.Entry(info.shipmentWin, textvariable=check_no, width=20).grid(row=101,column=1,columnspan=2)


    Tk.Button(info.shipmentWin, text="Close window", command=lambda:submit_changes(info)).grid(row=103,column=0,columnspan=6)

