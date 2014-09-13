#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Tix
import matplotlib



def main(_):
    '''

    _ = state information object. See "main.py".
    '''

    _.product_edit = Tix.Frame(_.product_frame)

    mainf = Tix.Frame(_.product_edit)
    mainf.pack(side='top', fill='x')

    entryfields = [ # (required?, SQL attribute name, Tix.Label, Entry hint)
        (1, u'inventory_name', u'Inventory Label:', u'Name used for internal stock keeping.'),
        (0, u'product_label', u'Product Label:', u'Name that the client/supplier wants to see.'),
        (0, u'english_name', u'English Label:', u'English name for the product.'),
        (1, u'SKU', u'SKU (abbrev.):', u'Stock keeping unit. Smallest sale unit like "barrel" or "pallet"'),
        (1, u'units', u'Units per SKU:', u'Amount in kg, L, or gal per container/SKU'),
        (1, u'UM', u'Unit Measure:', u'Smallest measureable size. "kg", "L", "gal", etc.'),
        (0, u'SKUlong', u'SKU Description:', u'SKU longer desccription. "white 5gal barrel"'),
        (0, u'note', u'Note:', u'Note on production or packaging.')
    ]
    entrySVars = [(Tix.StringVar(), None) for i in range(len(entryfields))]

    hint_color = u'gray40'
    type_color = u'black'
    def del_hint(tew): #Tix Entry Widget
        if hint_color in tew.config()[u'foreground']:
            tew.delete(0, 'end')

    def add_hint(tew, i): #Tix Entry Widget
        if type_color in tew.config()[u'foreground']:
            if entrySVars[i][0].get() == u'':
                entrySVars[i][0].set(entryfields[i][-1])

    def validatekey(tew, i):
        if entrySVars[i][0].get() == entryfields[i][-1]:
            tew.config(foreground=hint_color, font=(_.font, 14, ""))
        else:
            tew.config(foreground=type_color, font=(_.font, 14, "bold"))




    for row, (req, key, label, entry) in enumerate(entryfields):
        tl = Tix.Label(mainf, textvariable=_.loc(label), font=(_.font, 14))
        tl.grid(row=row, column=0, columnspan=2, sticky='nse')
        if req:
            tl.config(background=u'gold')
        te = Tix.Entry(mainf, textvariable=entrySVars[row][0], font=(_.font, 14))
        te.grid(row=row, column=2, columnspan=10, sticky='nsew')
        entrySVars[row] = (entrySVars[row][0], te)
        entrySVars[row][0].set(entry)
        entrySVars[row][0].trace('w', lambda a,b,c,tew=te, i=row: validatekey(tew, i))
        te.bind(u'<FocusIn>', lambda e, tew=te: del_hint(tew))
        te.bind(u'<FocusOut>', lambda e, tew=te, i=row: add_hint(tew, i))
        te.config(background=u'moccasin', foreground=hint_color)
    for col in range(2):
        mainf.columnconfigure(col, weight=0)
    for col in range(2,12):
        mainf.columnconfigure(col, weight=1)


    ###############
    ### BUTTONS ###
    opts = dict(master=mainf, bg=u'lawn green',
                activebackground=u'lime green',
                font=(_.font, 14, 'bold'))
    Tix.Button(textvariable=_.loc(u'Clear fields'),
               command=lambda:clear_fields(), **opts).grid(row=20, column=0)
    Tix.Button(textvariable=_.loc(u'Save changes to product'), **opts).grid(row=20, column=2)
    Tix.Button(textvariable=_.loc(u'Add to supply list'), **opts).grid(row=20, column=4)
    Tix.Button(textvariable=_.loc(u'Add to product list'), **opts).grid(row=20, column=6)

    def clear_fields():
        for row, (sv, textset) in enumerate(zip(entrySVars, entryfields)):
            sv[0].set(u'')
            add_hint(sv[1], row)


    def refresh():
        try:
            _.curr.product
        except KeyError:
            return

        if _.curr.product != None:
            for row, ef in enumerate(entryfields):
                text = _.curr.product.__dict__.get(ef[1])
                if text:
                    entrySVars[row][0].set(text)
                else:
                    entrySVars[row][0].set(u'')
                    add_hint(entrySVars[row][1], row)



    _.product_edit.refresh = refresh
    try:
        _.refresh.append(refresh)
    except KeyError:
        _.refresh = [refresh,]