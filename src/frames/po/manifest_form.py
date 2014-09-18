#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Tix
import tkMessageBox
import datetime

from utils import date_picker




def main(_, orders=[], qtyVars=[], unitVars=[], numbSVar=None, manifest=None, refresh=None):
    """Displays a window in the appearance of a Taimau shipping manifest.

    "orders" parameter is a list of orders for creating a new manifest.
    "qtyVars" list of Tix.StringVar objects holding the quantities.
    "unitVars" list of Tix.StringVar objects for the discounting.
    Alternatively, a manifest number can be given.
    "manifest" parameter is an existing manifest for viewing/editing."""

    if _.debug:
        print 'In "main" of manifest_window.py.'

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

    _.extwin = Tix.Toplevel(_.parent, width=700)
    _.extwin.title(u"{} {}".format(_.curr.cogroup.name, _.loc(u"\u26DF Create Manifest", asText=True)))
    _.extwin.geometry(u'+{}+{}'.format(_.parent.winfo_rootx()+100, _.parent.winfo_rooty()))
    _.extwin.focus_set()

    main_frame = Tix.Frame(_.extwin)
    main_frame.pack(side='left', fill='both')


    #### VARIABLES FOR RECORD ENTRY ####
    ####################################
    # ShipmentItem
#    _order_id = []
#    _qty = []
#    _lot_start = []
#    _lot_end = []

    # Shipment
    _shipment_no = Tix.StringVar()
    if numbSVar and isinstance(numbSVar, Tix.StringVar):
        _shipment_no = numbSVar
    _destination = Tix.StringVar()
    _driver = Tix.StringVar()
    _truck = Tix.StringVar()
    _truck.trace('w', lambda *args: _truck.set(_truck.get().upper().replace('-','')[:8]))
    _note = Tix.StringVar()

    _date = Tix.StringVar()


    #####################################


    if manifest:
        qtyVars = [Tix.StringVar() for sitem in manifest.items]
        [qtyVars[i].set(sitem.qty) for i, sitem in enumerate(manifest.items)]
        unitVars = [Tix.StringVar() for sitem in manifest.items]
        [unitVars[i].set(sitem.qty*sitem.order.product.units) for i, sitem in enumerate(manifest.items)]
        orders = [item.order for item in manifest.items]
        _shipment_no.set(manifest.shipment_no)
#        _destination = Tix.StringVar()
        _driver.set(manifest.driver)
        _truck.set(manifest.truck)
        _note.set(manifest.shipmentnote)

    order = orders[0]



    cell_config = dict(
        font= (_.font, 16, u'bold'),
        bg= u'cornsilk',
        height= 2,
    )

    seller_name = order.seller
    buyer_name = order.buyer

    kehu = u'客戶名稱: {}'.format(buyer_name)
    tl=Tix.Label(main_frame, text=kehu, **cell_config)
    tl.grid(row=1, column=0, columnspan=4, sticky='nsew')

    try:
        if _.debug:
            print 'In header creation "try" section.'
        branch = ([br for br in order.parent.branches
                    if br.name == buyer_name][0])

        sellertxt = u'{}'.format(seller_name)
        tl=Tix.Label(main_frame, text=sellertxt, **cell_config)
        tl.grid(row=0, column=0, columnspan=8, sticky='nsew')

        cell_config.update(anchor='w')

        contactname = branch.contacts[0].name if len(branch.contacts) else u''
        lianluo = u'聯 絡 人: {}'.format(contactname)
        tl=Tix.Label(main_frame, text=lianluo, **cell_config)
        tl.grid(row=2,column=0, columnspan=4, sticky='nsew')

        contactphone = branch.contacts[0].phone if len(branch.contacts) else branch.phone
        dianhua = u'聯絡電話: {}'.format(contactphone)
        tl=Tix.Label(main_frame, text=dianhua, **cell_config)
        tl.grid(row=3,column=0, columnspan=8, sticky='nsew')

        shipaddress = branch.address_shipping if branch.address_shipping else branch.address_office
        songhuo = u'送貨地址: {}'.format(shipaddress)
        tl=Tix.Label(main_frame, text=songhuo, **cell_config)
        tl.grid(row=4,column=0, columnspan=12, sticky='nsew')

        tongyi = u'統一編號: {}'.format(branch.tax_id)
        tl=Tix.Label(main_frame, text=tongyi, **cell_config)
        tl.grid(row=1,column=4, columnspan=4, sticky='nsew')

        fapiao = u'發票號碼: {}'.format(u'')
        tl=Tix.Label(main_frame, text=fapiao, **cell_config)
        tl.grid(row=2,column=4, columnspan=4, sticky='nsew')
    except Exception:
        if _.debug:
            print 'In header creation "except" section.'
        sellertxt = u'{} ({})'.format(seller_name, order.parent.name)
        tl=Tix.Label(main_frame, text=sellertxt, **cell_config)
        tl.grid(row=0, column=0, columnspan=12, sticky='nsew')
        cell_config.update(anchor='w')

    if manifest:
        b = Tix.Button(main_frame, textvariable=_date, bg='DarkGoldenrod1',
                       font=(_.font, 20))
        b['command'] = lambda curr_date=manifest.shipmentdate: pick_date(curr_date)
        b.grid(row=0, rowspan=3, column=8, columnspan=4, sticky='nsew')

        _date.set(manifest.shipmentdate)

        def pick_date(curr_date):
            cal = date_picker.Calendar(main_frame,
                                       textvariable=_date,
                                       destroy=True,
                                       month=curr_date.month,
                                       year=curr_date.year,
                                       day=curr_date.day)
            cal.grid(row=0, rowspan=3, column=8, columnspan=4, sticky='nsew')
    else:
        cal = date_picker.Calendar(main_frame)
        cal.grid(row=0, rowspan=3, column=8, columnspan=4, sticky='nsew')


    tl=Tix.Label(main_frame, text=u'貨單編號:', **cell_config)
    tl.grid(row=3,column=8, columnspan=2, sticky='ew')
    te = Tix.Entry(main_frame, textvariable=_shipment_no, font=(_.font, 20, 'bold'))
    te.grid(row=3,column=10, columnspan=2, sticky='nsew')

    if _.debug:
        print 'Out of header creation section.'

    cell_config = dict(
        font= (_.font, 15),
        bg= u'LightSteelBlue1',
        relief='raised',
    )
    for i, each in enumerate([u'品名',u'規格/包裝',u'件數',u'數量',u'包裝描述',u'出貨資訊']):
        tl=Tix.Label(main_frame, text=each, **cell_config)
        tl.grid(row=9,column=i*2, columnspan=2, sticky='ew')

    if _.debug:
        print 'Finished table labels'

    cell_config = dict(
        relief= 'sunken',
        font= (_.font, 15, u'bold',),
        bg= u'wheat'
    )

    for row, (order, qSV, uSV) in enumerate(zip(orders, qtyVars, unitVars)):
        if _.debug:
            print row, order.id
#        order = shipment.order
        product = order.product
#        config = query_config if shipment.id == highlight_id else cell_config
        config = cell_config

        pinming = u' {} '.format(product.product_label if product.product_label else product.inventory_name)
        guige = u'  {} {} / {}  '.format(product.units, product.UM, product.SKU)
        if product.SKU == u'槽車':
            guige = u'  槽車  '
        qty = float(qSV.get())
        qty = int(qty) if int(qty)==qty else qty
#        jianshu = u'  {} {}  '.format(qty, product.UM if product.SKU == u'槽車' else product.SKU)
#        units = product.units * qty
#        units = int(units) if int(units)==units else units
        this_units = u'{}  '.format(product.UM)
        Tix.Label(main_frame, text=pinming, **config).grid(row=10+row,column=0, columnspan=2, sticky='ew')
        Tix.Label(main_frame, text=guige, **config).grid(row=10+row,column=2, columnspan=2, sticky='ew')
        Tix.Entry(main_frame, textvariable=qSV, width=8, justify='center',
                  bg=u'PaleTurquoise1', font=(_.font, 15, 'bold'),
                  state=u'disabled' if manifest else u'normal').grid(row=10+row,column=4, columnspan=2, sticky='nsew')
        Tix.Label(main_frame, textvariable=uSV, anchor='e', **config).grid(row=10+row,column=6, columnspan=1, sticky='ew')
        Tix.Label(main_frame, text=this_units, anchor='w', **config).grid(row=10+row,column=7, columnspan=1, sticky='ew')
        Tix.Label(main_frame, bg=u'gray30', fg=u'gray70', text=u'  {}  '.format(product.SKUlong)).grid(row=10+row,column=8, columnspan=2, sticky='ew')
        dispnote = order.ordernote
        if order.orderID:
            dispnote = u'PO#:{} Note:{}'.format(order.orderID, dispnote)
        Tix.Label(main_frame, text=u'  {}  '.format(dispnote), **config).grid(row=10+row,column=10, columnspan=2, sticky='ew')


    sep = Tix.Frame(main_frame, relief='ridge', height=8, bg="LightSteelBlue1")
    sep.grid(row=49, column=0, columnspan=20, sticky='nsew')


    tl=Tix.Label(main_frame, textvariable=_.loc(u'Driver:'), **cell_config)
    tl.grid(row=50, column=0, columnspan=2, sticky='nsew')
    te = Tix.Entry(main_frame, textvariable=_driver, font=(_.font, 20, 'bold'))
    te.grid(row=50, column=2, columnspan=2, sticky='nsew')

    tl=Tix.Label(main_frame, textvariable=_.loc(u'Truck:'), **cell_config)
    tl.grid(row=51, column=0, columnspan=2, sticky='nsew')
    te = Tix.Entry(main_frame, textvariable=_truck, font=(_.font, 20, 'bold'))
    te.grid(row=51, column=2, columnspan=2, sticky='nsew')

    tl=Tix.Label(main_frame, textvariable=_.loc(u'Note:'), **cell_config)
    tl.grid(row=52, column=0, columnspan=2, sticky='nsew')
    te = Tix.Entry(main_frame, textvariable=_note, font=(_.font, 20, 'bold'))
    te.grid(row=52, column=2, columnspan=20, sticky='nsew')







    sep = Tix.Frame(main_frame, relief='ridge', height=8, bg="LightSteelBlue1")
    sep.grid(row=999, column=0, columnspan=20, sticky='nsew')







    # SUBMIT BUTTON
    tb = Tix.Button(main_frame, textvariable=_.loc(u"\u2713 Submit"),
                    bg="lawn green",
                    command=lambda:submit(manifest),
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

    def submit(manifest):
        if manifest == None:
            if cal.selection in (None, u''):
                return
            manifest = _.dbm.existing_shipment(_shipment_no.get(),
                                               cal.selection,
                                               _.curr.cogroup.name)
            if manifest:
                confirm = tkMessageBox.askyesno(u'Manifest number exists.',
                                      u'Add items to existing manifest?')
                if not confirm:
                    _.extwin.focus_set()
                    return
                # Check that adding will not go over five items
                count = len(manifest.items) + len(orders)
                if count > 5:
                    tkMessageBox.showerror(u'Too many to add',
                        u'Additional items will go over the five item limit.\n' +
                        u'Cannot add to existing manifest.')
                    _.extwin.focus_set()
                    return
            if manifest == None:
                manifest = _.dbm.Shipment(
                    shipmentdate = cal.selection,
                    shipment_no = _shipment_no.get().upper(),
                    shipmentnote = _note.get(),
                    driver = _driver.get(),
                    truck = _truck.get().upper().replace('-',''),
                )
            for order, qty in zip(orders, qtyVars):
                item = _.dbm.ShipmentItem(
                    order = order,
                    shipment = manifest,

                    qty = qty.get(),
                )
                _.dbm.session.add(item)
            _.dbm.session.commit()
            for order in orders:
                check_order_qty(order)
        else: #if editing manifest
            manifest.shipmentdate = datetime.date(*[int(z) for z in _date.get().split(u'-')])
            manifest.shipment_no = _shipment_no.get().upper()
            manifest.shipmentnote = _note.get()
            manifest.driver = _driver.get()
            manifest.truck = _truck.get().upper().replace('-','')
            _.dbm.session.commit()


        exit_win()
        if refresh:
            refresh()

    def check_order_qty(order):
        if order.all_shipped():
            head = u'Archive PO?'
            body = u'\n'.join([
                        u'PO {} : {}'.format(order.orderID, order.product.label()),
                        _.loc(u'PO appears to be complete.',1),
                        _.loc(u'All units have shipped.',1),
                        _.loc(u'Archive this PO?',1)])
            confirm = tkMessageBox.askyesno(head, body)

            if confirm:
                _.dbm.update_order(order.id, dict(is_open=False))








































if __name__ == '__main__':
    main()