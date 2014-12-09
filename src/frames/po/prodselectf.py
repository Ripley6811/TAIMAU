#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Tix
import tkMessageBox

from utils import settings


def main(_):
    """List products for creating orders.

    Enter prices and order amounts and save as a multiple shipment order (added
    to open PO list) or a one time order."""

    frame = Tix.Frame(_.po_frame)

    # Register validation methods to this frame.
    def is_float(val):
        try:
            float(val)
        except:
            return True if val == '' else False
        return True

    vcmd_float = frame.register(lambda x: is_float(x))
    vcmd_int = frame.register(lambda x: x.isdigit())


    def refresh():
        try:
            while True:
                frame.children.popitem()[1].destroy()
        except KeyError:
            pass

        cog = None # Current cogroup
        scm = None # Current 's' or 'c' mode (supplier or customer view)
        _priceSV = [] # Store stringvar for entered prices
        _qtySV = [] # Store stringvar for entered quantity
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
        prodrecs = query.all()

        # Set default options for all widgets.
        OPTS = dict(master=frame, justify="center", font=(_.font, 12, 'bold'))
        # Set entry widget defaults


        Eopts = dict(width=6, bg=u"moccasin",
                     validate='key', **OPTS)


        for row, PR in zip(rows, prodrecs):
            col = 0
            PrU = PR.UM if PR.unitpriced else PR.SKU

            # Product name and specs
            lw = Tix.Label(text=PR.name, **OPTS)
            lw.grid(row=row, column=col, sticky='nsw'); col += 1
            lw = Tix.Label(text=PR.specs, padx=10, **OPTS)
            lw.grid(row=row, column=col, sticky='nsw'); col += 1

            # Price entry
            _priceSV.append(Tix.StringVar())
            _priceSV[-1].set(PR.price)
            ew = Tix.Entry(textvariable=_priceSV[-1],
                           validatecommand=(vcmd_float, '%P'), **Eopts)
            ew.grid(row=row, column=col); col += 1

            # TWD per sku/unit
            lw = Tix.Label(text=u'TWD/{}'.format(PrU), padx=10, **OPTS)
            lw.grid(row=row, column=col, sticky='nsw'); col += 1

            # Number of units entry
            _qtySV.append(Tix.StringVar())
            ew = Tix.Entry(textvariable=_qtySV[-1],
                           validatecommand=(vcmd_int, '%S'), **Eopts)
            ew.grid(row=row, column=col); col += 1

            # Show SKU after quantity number
            lw = Tix.Label(text=PR.SKU, padx=10, **OPTS)
            lw.grid(row=row, column=col, sticky='nsw'); col += 1










    _.prodselectf = frame
    _.prodselectf.refresh = refresh

    try:
        _.refresh.append(refresh)
    except KeyError:
        _.refresh = [refresh,]

    return frame









