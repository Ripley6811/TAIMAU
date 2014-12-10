#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Tix
import tkMessageBox

from utils import settings, date_picker


def main(_):
    """List products for creating orders.

    Enter prices and order amounts and save as a multiple shipment order (added
    to open PO list) or a one time order."""

    frame = Tix.Frame(_.po_frame)
    prodf = Tix.Frame(frame)
    prodf.pack(side='left', anchor='n')
    #XXX: Or use grid with column weighting

    # Register validation methods to this frame.
    prefix = u'$'
    def is_float(val):
        try:
            float(val[1:])
        except:
            return True if val == prefix else False
        return True

    vcmd_float = frame.register(lambda x: is_float(x))
    vcmd_int = frame.register(lambda x: x.isdigit())

    prodrecs = []
    _priceSV = [] # Store stringvar for entered prices
    _qtySV = [] # Store stringvar for entered quantity

    font = (_.font, 12, 'bold')

    def refresh():
        try:
            while True:
                prodf.children.popitem()[1].destroy()
        except KeyError:
            pass

        prodrecs.__delslice__(0,1000) # Store product records
        _priceSV.__delslice__(0,1000) # Store stringvar for entered prices
        _qtySV.__delslice__(0,1000) # Store stringvar for entered quantity
        cog = None # Current cogroup
        scm = None # Current 's' or 'c' mode (supplier or customer view)
        try:
            cog = _.curr.cogroup
            scm = _.sc_mode
        except KeyError:
            return

        # Retrieve user designated PO ordering if it exists.
        minlen = 100
        rows = settings.load().get(scm, {}).get(cog.name, range(minlen))
        # Increase 'rows' length in case more prod are added.
        #XXX: Possibly unnecessary. Refresh if new products added.
        if len(rows) < minlen:
            rows = rows + range(max(rows)+1, max(rows)+minlen-len(rows))

        query = _.dbm.session.query(_.dbm.Product)
        query = query.filter_by(group = cog.name)
        query = query.filter_by(discontinued = False)
        query = query.filter_by(is_supply=True if scm == u's' else False)
        query = query.order_by('inventory_name')
        [prodrecs.append(p) for p in query.all()]

        # Set default options for all widgets.
        OPTS = dict(master=prodf, justify="right")#, font=font)
        # Set entry widget defaults
        Eopts = dict(width=8, bg=u"moccasin", validate='key', **OPTS)


        for row, PR in zip(rows, prodrecs):
            col = 0
            PrU = PR.UM if PR.unitpriced else PR.SKU

            # Product name and specs
            lw = Tix.Label(text=PR.name, **OPTS)
            lw.grid(row=row, column=col, sticky='nsw'); col += 1
            lw = Tix.Label(text=PR.specs, padx=20, **OPTS)
            lw.grid(row=row, column=col, sticky='nsw'); col += 1

            # Price entry
            _priceSV.append(Tix.StringVar())
            _priceSV[-1].set(u'{}{}'.format(prefix, PR.price))
            ew = Tix.Entry(textvariable=_priceSV[-1],
                           validatecommand=(vcmd_float, '%P'), **Eopts)
            ew.grid(row=row, column=col); col += 1

            # TWD per sku/unit
            lw = Tix.Label(text=u'/{}'.format(PrU), padx=10, **OPTS)
            lw.grid(row=row, column=col, sticky='nsw'); col += 1

            # Number of units entry
            _qtySV.append(Tix.StringVar())
            ew = Tix.Entry(textvariable=_qtySV[-1],
                           validatecommand=(vcmd_int, '%S'), **Eopts)
            ew.grid(row=row, column=col); col += 1

            # Show SKU after quantity number
            lw = Tix.Label(text=PR.SKU, padx=10, **OPTS)
            lw.grid(row=row, column=col, sticky='nsw'); col += 1


    # Form creation panel. Make different types of POs.
    formf = Tix.Frame(frame)
    formf.pack(side='top', anchor='n')

    longPOf = Tix.Frame(formf)
    longPOf.pack(side='top')
    shortPOf = Tix.Frame(formf)
    shortPOf.pack(side='top')

    ponSV = Tix.StringVar() # PO number
    manSV = Tix.StringVar() # Manifest number

    #TODO: Add Taimau branch selection

    # Order date: preselect today
    tl = Tix.Label(longPOf, textvariable=_.loc(u"Date of order/shipment"))
    tl.grid(row=0, columnspan=2)
    cal = date_picker.Calendar(longPOf)
    cal.grid(row=1, columnspan=2)

    Tix.Label(longPOf, textvariable=_.loc(u'Order (PO) #:'), pady=10)\
        .grid(row=2, column=0, sticky='nsew')
    ponEntry = Tix.Entry(longPOf, textvariable=ponSV, bg=u"moccasin")
    ponEntry.grid(row=2, column=1, sticky='ew')

    Tix.Label(longPOf, textvariable=_.loc(u'Manifest #:'), pady=10)\
        .grid(row=3, column=0, sticky='nsew')
    ponEntry = Tix.Entry(longPOf, textvariable=manSV, bg=u"moccasin")
    ponEntry.grid(row=3, column=1, sticky='ew')

    def createOrder(PROD, PRICE, QTY, is_open=True):
        '''
        PROD : string Product object MPN identifier
        PRICE : float
        QTY : integer
        '''
        PRICE = float(PRICE.replace('$',''))
        QTY = int(QTY)
        ins = dict(MPN=PROD,
                       qty=QTY,
                       price=PRICE,
                       orderID=ponSV.get().upper(),
                       orderdate=cal.selection,
                       is_open=is_open,
                       ordernote=u'', #TODO:
                       applytax=True) #TODO:
        ins['is_sale'] = True if _.sc_mode == 'c' else False
        ins['is_purchase'] = True if _.sc_mode == 's' else False
        ins['group'] = _.curr.cogroup.name
        ins['seller'] = u'台茂' if _.sc_mode == 'c' else _.curr.branchSV.get()
        ins['buyer'] = u'台茂' if _.sc_mode == 's' else _.curr.branchSV.get()

        if _.debug:
            print ins

        return _.dbm.Order(**ins)

    def createShipmentItem(order, manifest, QTY):
        '''
        new_order : Order object
        manifest : Shipment object
        QTY : integer
        '''
        QTY = int(QTY)
        return _.dbm.ShipmentItem(
            order = order,
            shipment = manifest,
            qty = QTY,
        )

    def submitPO(*args):
        '''Add new POs for each item with user defined quantities.'''
        if confirm_entries():
            for PROD, PRICE, QTY in zip(prodrecs, _priceSV, _qtySV):
                if QTY.get().isdigit() and len(PRICE.get()) > 1:
                    new_order = createOrder(PROD.MPN, PRICE.get(), QTY.get())

                    _.dbm.session.add(new_order)
            _.dbm.session.commit()
            refresh()
            try:
                for ref in _.refresh:
                    ref()
            except AttributeError:
                pass

    def submitMF(*args):
        '''Add new POs and manifest for all items with defined quantities.
        Set POs as inactive (single-use).'''
        if len([1 for Q in _qtySV if Q.get().isdigit()]) > 5 and _.sc_mode == 'c':
            title = u'Too many items.'
            message = u'Each manifest can only have five items.'
            tkMessageBox.showerror(title, message)
            return
        if confirm_entries():
            manifest = _.dbm.existing_shipment(manSV.get(),
                                               cal.selection,
                                               _.curr.cogroup.name)
            if not manifest:
                manifest = _.dbm.Shipment(
                    shipmentdate = cal.selection,
                    shipment_no = manSV.get().upper(),
#                    shipmentnote = ,
#                    driver = ,
#                    truck = ,
                )

            for PROD, PRICE, QTY in zip(prodrecs, _priceSV, _qtySV):
                if QTY.get().isdigit() and len(PRICE.get()) > 1:
                    new_order = createOrder(PROD.MPN, PRICE.get(), QTY.get(), is_open=False)
                    item = createShipmentItem(new_order, manifest, QTY.get())
                    _.dbm.session.add(item)
            _.dbm.session.commit()
            try:
                for ref in _.refresh:
                    ref()
            except AttributeError:
                pass

    Tix.Button(longPOf, textvariable=_.loc(u"\u2692 Create Product Order (PO)"),
               pady=12, bg=u'lawngreen', command=submitPO).grid(row=4, columnspan=2)

    Tix.Button(longPOf, textvariable=_.loc(u"\u26DF Create Manifest"),
               pady=12, bg=u'lawngreen', command=submitMF).grid(row=5, columnspan=2)

    def confirm_entries():
        title = u'Confirm entries'
        message = _.loc(u'Verify these entries:',1)
        message += u'\n\n日期 : {}'.format(cal.selection)
        message += u'\n分司 : {}'.format(_.curr.branchSV.get())
        message += u'\n訂單#: {}'.format(ponSV.get())
        message += u'\n出貨#: {}'.format(manSV.get())
        for PROD, PRICE, QTY in zip(prodrecs, _priceSV, _qtySV):
            if len(QTY.get()) > 0:
                message += u'\n\t{}{}   {}  @  {}/{}'.format(
                    QTY.get(), PROD.UM if PROD.SKU==u'槽車' else PROD.SKU,
                    PROD.name,
                    PRICE.get(), PROD.PrMeas,
                )

        return tkMessageBox.askokcancel(title, message)


    _.prodselectf = frame
    _.prodselectf.refresh = refresh

    try:
        _.refresh.append(refresh)
    except KeyError:
        _.refresh = [refresh,]

    return frame









