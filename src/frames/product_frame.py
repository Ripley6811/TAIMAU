#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Tix
import tkMessageBox

import prodf
from utils import settings


def create(_):
    '''

    '''
    _.curr.product = None # Store the SQL object
    _.curr.productSV = Tix.StringVar() # Store the SQL object id ('MPN')


    top_pane = Tix.Frame(_.product_frame)
    top_pane.pack(side='top', fill='x', padx=4, pady=5)
    page_buttons = Tix.Frame(_.product_frame, bg=u'SteelBlue3', pady=4)
    page_buttons.pack(side='top', fill='x', padx=4, pady=5)


    prodf.edit_frame(_)
    prodf.price_frame(_)

    ##############################
    ### View selection buttons ###
    _.prodview = None
    options = dict(variable="pagebuttons2", indicatoron=False,
                   font=(_.font, "14", "bold"), bg="medium purple",
                   selectcolor="plum", padx=50,
                   activebackground="plum")
    tr = Tix.Radiobutton(page_buttons, textvariable=_.loc(u'Product Info/Edit'),
                         command=lambda x=u'edit':change_view(x),
                         value=u'edit', **options)
    tr.grid(row=0, column=0)
    tr.select()
    tr = Tix.Radiobutton(page_buttons, textvariable=_.loc(u'Product Price History'),
                         command=lambda x=u'price':change_view(x),
                         value=u'price', **options)
    tr.grid(row=0, column=1)
    page_buttons.columnconfigure(0,weight=1)
    page_buttons.columnconfigure(1,weight=1)


    def change_view(mode):
        if _.prodview == mode:
            return
        if _.debug:
            print 'VIEW MODE:', mode

        _.prodview = mode

        if mode == u'edit':
            _.product_edit.pack(side='left', fill='both', expand=1)
            _.product_edit.refresh()
        else:
            _.product_edit.pack_forget()

        if mode == u'price':
            _.product_price.pack(side='left', fill='both', expand=1)
            _.product_price.refresh()
        else:
            _.product_price.pack_forget()

    def del_prod(product):
        nRecs = len(product.orders)
        if nRecs == 0:
            _.dbm.session.delete(product)
            _.dbm.session.commit()
            refresh()
        else:
            title = u'Cannot delete a used product record.'
            message = u'This product is connected to {} order{}.'.format(
                        nRecs, u's' if nRecs > 1 else u'')
            message += u'\nAll related orders must be deleted first.'
            tkMessageBox.showerror(title, message)

    def prod_popup(btn, product):
        orderPopMenu = Tix.Menu(btn, tearoff=0)

        def orderoptions(event):
            orderPopMenu.post(event.x_root, event.y_root)
        btn.bind("<Button-3>", orderoptions)

        orderPopMenu.add_command(label=_.loc(u'Delete product',1),
                                 command=lambda x=product: del_prod(x))


    def refresh():

        try:
            while len(top_pane.children) > 0:
                top_pane.children.popitem()[1].destroy()
        except KeyError:
            pass

        def select_product(MPN):
            p = _.dbm.get_product(MPN)
            _.curr.product = p
            _.curr.productSV.set(MPN)
            settings.update(product=MPN)
            _.product_edit.refresh()
            _.product_price.refresh()

        opts = dict(master=top_pane, bg=u'gold4', fg=u'gold', font=(_.font, 14, 'bold'))
        Tix.Label(textvariable=_.loc(u'Supplies We Purchase'), **opts).pack(side='top', fill='x')
        supply_box = Tix.Frame(top_pane)
        supply_box.pack(side='top', fill='x')
        Tix.Label(textvariable=_.loc(u'Products We Sell'), **opts).pack(side='top', fill='x')
        wesell_box = Tix.Frame(top_pane)
        wesell_box.pack(side='top', fill='x')

        product_list = _.curr.cogroup.products
        supply_list = [prod for prod in product_list if prod.is_supply]
        wesell_list = [prod for prod in product_list if not prod.is_supply]

        if _.debug:
            print len(product_list), "products found for current company group."
        TRB = lambda _frame, _text, _val: Tix.Radiobutton(_frame,
                                        text=_text, anchor='w',
                                        variable=_.curr.productSV,
                                        value=_val,
                                        indicatoron=False,
                                      bg="wheat",
                                      activebackground="wheat",
                                      selectcolor="gold")

        row = -1
        cols = 4
        for row, product in enumerate(supply_list):
            _text = u"{}  ({})".format(product.label(), product.specs)
            #TODO: Add Product editing, to be discouraged! Warn!
            #Or just edit names, note and not the numbers related fields
            tb = TRB(supply_box, _text, product.MPN)
            tb['command'] = lambda x=product.MPN:select_product(x)
            if product.discontinued:
                tb.config(bg="gray40", relief="flat")
            tb.grid(row=row/cols, column=row%cols, sticky='ew')

            prod_popup(tb, product)

        for i in (0,1,2,3):
            supply_box.columnconfigure(i,weight=1)


        row = -1
        for row, product in enumerate(wesell_list):
            _text = u"{}  ({})".format(product.label(), product.specs)
            #TODO: Add Product editing, to be discouraged! Warn!
            #Or just edit names, note and not the numbers related fields
            tb = TRB(wesell_box, _text, product.MPN)
            tb['command'] = lambda x=product.MPN:select_product(x)
            if product.discontinued:
                tb.config(bg="gray30", relief="flat")
            tb.grid(row=row/cols, column=row%cols, sticky='ew')

            prod_popup(tb, product)

        for i in (0,1,2,3):
            wesell_box.columnconfigure(i,weight=1)

    try:
        if _.curr.cogroup:
            refresh()
    except KeyError:
        pass

    change_view(u'edit')

    try:
        _.refresh.append(refresh)
    except KeyError:
        _.refresh = [refresh,]