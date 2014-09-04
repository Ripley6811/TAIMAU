#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Tix
from utils import date_picker



def main(_, items=None, manifest_no=None):
    """Displays a window in the appearance of a Taimau shipping manifest.

    "Items" parameter is a list of order ids and quantities for creating a
    new manifest.
    "id" parameter is the id of an existing manifest for viewing/editing."""


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

    _.extwin = Tix.Toplevel(width=700)
    _.extwin.title(u"{} {}".format(_.curr.cogroup.name, _.loc(u"\u26DF Create Manifest", asText=True)))

    center_pane = Tix.Frame(_.extwin)
    center_pane.pack(side='left', fill='both')


    #### VARIABLES FOR RECORD ENTRY ####
    ####################################
    # ShipmentItem
    _order_id = []
    _qty = []
    _lot_start = []
    _lot_end = []

    # Shipment
    _shipment_no = Tix.StringVar()
    _destination = Tix.StringVar()
    _driver = Tix.StringVar()
    _truck = Tix.StringVar()
    _note = Tix.StringVar()


    #####################################
    qtys = []
    units = []
    orders = []
    order = None
    if items:
        poIDs = []
        qtys = []
        [poIDs.append(a) for a,b,c in items]
        [qtys.append(b) for a,b,c in items]
        [units.append(c) for a,b,c in items]
        orders = [_.dbm.get_order(poid) for poid in poIDs]
        order = orders[0]
    elif manifest_no:
        manifest = _.dbm.get_manifest(manifest_no)
        qtys = [sitem.qty for sitem in manifest.items]
        orders = [item.order for item in manifest.items]
        order = orders[0]
    else:
        _.extwin.destroy()
        return
    print 'items', items, [b for a,b,c in items]

    for i in range(len(qtys)):
        print i, qtys
        _qty.append(qtys[i])



    cell_config = dict(
        font= (_.font, 15, u'bold'),
        bg= u'cornsilk',
        height= 2,
    )

    seller_name = order.seller
    buyer_name = order.buyer

    kehu = u'客戶名稱: {}'.format(buyer_name)
    tl=Tix.Label(center_pane, text=kehu, **cell_config)
    tl.grid(row=1, column=0, columnspan=4, sticky='ew')

    try:
        branch = ([br for br in order.parent.branches
                    if br.name == buyer_name][0])

        sellertxt = u'{}'.format(seller_name)
        tl=Tix.Label(center_pane, text=sellertxt, **cell_config)
        tl.grid(row=0, column=0, columnspan=12, sticky='ew')

        cell_config.update(anchor='w')

        contactname = branch.contacts[0].name if len(branch.contacts) else u''
        lianluo = u'聯 絡 人: {}'.format(contactname)
        tl=Tix.Label(center_pane, text=lianluo, **cell_config)
        tl.grid(row=2,column=0, columnspan=4, sticky='ew')

        contactphone = branch.contacts[0].phone if len(branch.contacts) else branch.phone
        dianhua = u'聯絡電話: {}'.format(contactphone)
        tl=Tix.Label(center_pane, text=dianhua, **cell_config)
        tl.grid(row=3,column=0, columnspan=8, sticky='ew')

        shipaddress = branch.address_shipping if branch.address_shipping else branch.address_office
        songhuo = u'送貨地址: {}'.format(shipaddress)
        tl=Tix.Label(center_pane, text=songhuo, **cell_config)
        tl.grid(row=4,column=0, columnspan=12, sticky='ew')

        tongyi = u'統一編號: {}'.format(branch.tax_id)
        tl=Tix.Label(center_pane, text=tongyi, **cell_config)
        tl.grid(row=1,column=4, columnspan=4, sticky='ew')

        fapiao = u'發票號碼: {}'.format(u'')
        tl=Tix.Label(center_pane, text=fapiao, **cell_config)
        tl.grid(row=2,column=4, columnspan=4, sticky='ew')
    except Exception:
        sellertxt = u'{} ({})'.format(seller_name, order.parent.name)
        tl=Tix.Label(center_pane, text=sellertxt, **cell_config)
        tl.grid(row=0, column=0, columnspan=12, sticky='ew')
        cell_config.update(anchor='w')



    cal = date_picker.Calendar(center_pane)
    cal.grid(row=0, rowspan=3, column=8, columnspan=4, sticky='ew')
#    riqi = u'貨單日期: {0.year}年 {0.month}月 {0.day}日'.format(order.shipments[0].shipmentdate)
#    tl=Tix.Label(center_pane, text=riqi, **cell_config)
#    tl.grid(row=1,column=4, columnspan=2, sticky='ew')

    tl=Tix.Label(center_pane, text=u'貨單編號:', **cell_config)
    tl.grid(row=3,column=8, columnspan=2, sticky='ew')
    te = Tix.Entry(center_pane, textvariable=_shipment_no)
    te.grid(row=3,column=10, columnspan=2, sticky='ew')


    cell_config = dict(
        font= (_.font, 15),
        bg= u'LightSteelBlue1',
        relief='raised',
    )
    for i, each in enumerate([u'品名',u'規格/包裝',u'件數',u'數量',u'包裝描述',u'出貨資訊']):
        tl=Tix.Label(center_pane, text=each, **cell_config)
        tl.grid(row=9,column=i*2, columnspan=2, sticky='ew')


    cell_config = dict(
        relief= 'sunken',
        font= (_.font, 15, u'bold',),
        bg= u'wheat'
    )
    query_config = dict(
        relief= 'sunken',
        font= (_.font, 15, u'bold',),
        bg= u'yellow'
    )
    print len(orders), len(_qty), _qty
    for row, (order, qSV, uSV) in enumerate(zip(orders, qtys, units)):
        if _.debug:
            print row, order
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
        jianshu = u'  {} {}  '.format(qty, product.UM if product.SKU == u'槽車' else product.SKU)
        units = product.units * qty
        units = int(units) if int(units)==units else units
        this_units = u'{}  '.format(product.UM)
        Tix.Label(center_pane, text=pinming, **config).grid(row=10+row,column=0, columnspan=2, sticky='ew')
        Tix.Label(center_pane, text=guige, **config).grid(row=10+row,column=2, columnspan=2, sticky='ew')
        Tix.Entry(center_pane, textvariable=qSV, width=5, justify='center').grid(row=10+row,column=4, columnspan=2, sticky='ew')
        Tix.Label(center_pane, textvariable=uSV, anchor='e', **config).grid(row=10+row,column=6, columnspan=1, sticky='ew')
        Tix.Label(center_pane, text=this_units, anchor='w', **config).grid(row=10+row,column=7, columnspan=1, sticky='ew')
        Tix.Label(center_pane, bg=u'gray30', fg=u'gray70', text=u'  {}  '.format(product.SKUlong)).grid(row=10+row,column=8, columnspan=2, sticky='ew')
        dispnote = order.ordernote
        if order.orderID:
            dispnote = u'PO#:{} Note:{}'.format(order.orderID, dispnote)
        Tix.Label(center_pane, text=u'  {}  '.format(dispnote), **config).grid(row=10+row,column=10, columnspan=2, sticky='ew')





















































if __name__ == '__main__':
    main()