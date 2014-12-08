#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Tix
import tkMessageBox

def main(_):
    '''Sub-frame of product_frame.
    Edit or add products to database.

    NOTE: Product info does not erase when switching companies. This allows
    you to easily add a similar product to another companies product list.

    _ = state information object. See "main.py".
    '''

    _.product_edit = Tix.Frame(_.product_frame)

    top_bar = Tix.Frame(_.product_edit)
    top_bar.pack(side='top', fill='x')

    infoText = Tix.StringVar()
    tl = Tix.Label(top_bar, textvariable=infoText, font=(_.font, 18, 'bold'))
    tl.pack(side='top', fill='x')

    def update_product_info_line():
        try:
            ptext = u'{inventory_name} - {units}{UM} per {SKU}'
            ptext = ptext.format(**collectSVvalues())
        except KeyError:
#        except ValueError:
            ptext = _.loc(u'(Gold Fields Required!)', 1)

        try:
            nOrders = len(_.curr.product.orders)
        except AttributeError:
            nOrders = 0

        text = _.loc(u'{} : {} Order Records', 1).format(ptext, nOrders)
        infoText.set(text)

    mainf = Tix.Frame(_.product_edit)
    mainf.pack(side='top', fill='x')

    entryfields = [ # (required?, SQL attribute name, Tix.Label, Entry hint)
        (1, u'inventory_name', u'Inventory Label:', u'Name used for internal stock keeping.'),
        (0, u'product_label', u'Product Label:', u'Name that the client/supplier wants to see.'),
        (0, u'english_name', u'English Label:', u'English name for the product.'),
        (1, u'SKU', u'SKU (abbrev.):', u'Stock keeping unit. Smallest sale unit like "barrel" or "pallet"'),
        (1, u'units', u'Units per SKU:', u'Amount in kg, L, or gal per container/SKU'),
        (1, u'UM', u'Unit Measure:', u'Smallest measureable size. "kg", "L", "gal", etc.'),
        (0, u'SKUlong', u'SKU Description:', u'SKU longer description. "white 5gal barrel"'),
        (0, u'note', u'Note:', u'Note on production or packaging.'),
        (0, u'ASE_PN', u'(ASE) PN:', u'(ASE) Product Number.'),
        (0, u'ASE_RT', u'(ASE) RT:', u'(ASE) Routing number.'),
#        (0, u'ASE_END', u'(ASE) Last SKU#:', u'(ASE) Last index number used on delivered barrels.'),
        (0, u'curr_price', u'Current Price:', u'Enter a starting price.'),
    ]
    entrySVars = [(Tix.StringVar(), None) for i in range(len(entryfields))]
    radioSVars = [(u'unitpriced', Tix.BooleanVar()),
                  (u'discontinued', Tix.BooleanVar()), ]

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

        update_product_info_line()


    #########################
    ### TEXT ENTRY FIELDS ###
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

    ##########################
    ### RADIOBUTTON FIELDS ###
    rbopts = dict(master=mainf,
                  font=(_.font, 14),
                  indicatoron=False,
                  bg=u'gray40',
                  activebackground=u'gold',
                  selectcolor=u'gold',
                  )
    tl = Tix.Label(mainf, textvariable=_.loc(u'Priced by...:'), font=(_.font, 14))
    tl.grid(row=row+1, column=0, columnspan=2, sticky='nse')
    trb = Tix.Radiobutton(textvariable=_.loc(u'Unit (kg, gal, etc.)'),
                    value=True, variable=radioSVars[0][1], **rbopts)
    trb.grid(row=row+1, column=2, columnspan=2, sticky='nsew')
    trb = Tix.Radiobutton(textvariable=_.loc(u'SKU (barrel, bag, etc.)'),
                    value=False, variable=radioSVars[0][1], **rbopts)
    trb.grid(row=row+1, column=4, columnspan=2, sticky='nsew')

    tl = Tix.Label(mainf, textvariable=_.loc(u'Discontinue?:'), font=(_.font, 14))
    tl.grid(row=row+2, column=0, columnspan=2, sticky='nse')
    trb = Tix.Radiobutton(textvariable=_.loc(u'\u2620 Discontinued'),
                    value=True, variable=radioSVars[1][1], **rbopts)
    trb.grid(row=row+2, column=2, columnspan=2, sticky='nsew')
    trb = Tix.Radiobutton(textvariable=_.loc(u'\u26df Available'),
                    value=False, variable=radioSVars[1][1], **rbopts)
    trb.grid(row=row+2, column=4, columnspan=2, sticky='nsew')

    ###############
    ### BUTTONS ###
    opts = dict(master=mainf, bg=u'lawn green',
                activebackground=u'lime green',
                font=(_.font, 14, 'bold'))
    Tix.Button(textvariable=_.loc(u'Clear fields'),
               command=lambda:clear_fields(), **opts).grid(row=20, column=0)
    Tix.Button(textvariable=_.loc(u'Save changes to product'),
               command=lambda:save_update(), **opts).grid(row=20, column=2)
    Tix.Button(textvariable=_.loc(u'Add to supply list (buy)'),
               command=lambda:save_new_supply(), **opts).grid(row=20, column=4)
    Tix.Button(textvariable=_.loc(u'Add to product list (sell)'),
               command=lambda:save_new_product(), **opts).grid(row=20, column=6)

    def clear_fields():
        '''Clear the reference to the current product in memory and clear
        attribute fields.
        '''
        _.curr.product = None
        _.curr.productSV.set(u'')
        for row, (sv, textset) in enumerate(zip(entrySVars, entryfields)):
            sv[0].set(u'')
            add_hint(sv[1], row)
        for sv in radioSVars:
            sv[1].set(False)



    def refresh():
        try:
            _.curr.product
        except KeyError:
            return

        if _.curr.product != None:
            for row, ef in enumerate(entryfields):
                text = _.curr.product.__dict__.get(ef[1])
                if text:
                    try:
                        text = str(float(text))
                    except ValueError:
                        pass
                    entrySVars[row][0].set(text.split('{',1)[0])
                else:
                    entrySVars[row][0].set(u'')
                    add_hint(entrySVars[row][1], row)
            for sv in radioSVars:
                boo = bool(_.curr.product.__dict__.get(sv[0]))
                if boo == False:
                    sv[1].set(False)
                elif boo == True:
                    sv[1].set(True)
                else:
                    print sv[0], sv[1].get()
                    raise ValueError, u"Product boolean value error. Value type {}".format(type(boo))

        update_product_info_line()

    def save_update():
        # Check that there is a current product loaded.
        if _.curr.product != None and _.curr.productSV.get() != u'':
            # Validate fields
            if validate_fields():
                # If orders already exist, then confirm again to change.
                nOrders = len(_.curr.product.orders)
                confirm = True
                if nOrders > 0:
                    confirm = False
                    head = _.loc(u'Changing existing records!', 1)
                    body = _.loc(u'{} orders will be affected.\nContinue with changes?', 1).format(nOrders)
                    confirm = tkMessageBox.askokcancel(head, body)
                if confirm:
                    query = _.dbm.session.query(_.dbm.Product)
                    query = query.filter_by(MPN=_.curr.productSV.get())
                    valdict = collectSVvalues()
                    # Add back JSON note
                    if u'{' in _.curr.product.note:
                        valdict[u'note'] = valdict.get(u'note', u'') + u'{' + _.curr.product.note.split(u'{',1)[1]
                    query.update(valdict)
                    _.dbm.session.commit()
                else:
                    return
            else:
                tkMessageBox.showwarning(u'Entry error',
                        u'\n'.join([
                            u'Information in "gold" color are required.',
                            u'Check "units" and "current price" are numbers.',
                        ]) )
        else:
            tkMessageBox.showwarning(u'No product is selected.',
                    u'\n'.join([
                        u'Cannot apply updates to product unless',
                        u'it is selected in the menu at the top.',
                    ]) )

    def save_new_supply():
        save_new(True)
    def save_new_product():
        save_new(False)
    def save_new(is_supply):
        # Check that there is a current cogroup loaded.
        if _.curr.cogroup != None and _.curr.cogroupSV.get() != u'':
            # Validate fields
            newDict = validate_fields()
            if newDict:
                newDict['is_supply'] = is_supply
                newDict['cogroup'] = _.curr.cogroup
                newDict['MPN'] = u' '.join([str(len(_.curr.cogroup.products)),
                                            _.curr.cogroup.name,
                                            newDict['inventory_name'],
                                            str(newDict['units']),
                                            newDict['UM'],
                                            newDict['SKU'],
                                            str(newDict['is_supply']),
                                            newDict.get(u'note', u'')])
                if _.debug:
                    print 'METHOD: save_new: newProduct'
                    for key, val in newDict.iteritems():
                        print key, type(val), val
                qprod = _.dbm.session.query(_.dbm.Product)
                print 'MPN!!!', qprod.get(newDict['MPN'])
                if not qprod.get(newDict['MPN']):
                    newProduct = _.dbm.Product(**newDict)
#                    newProduct.MPN = _MPN
                    _.dbm.session.add(newProduct)
                    _.dbm.session.commit()
                    # Load PO HList 'All POs'
                    for each_method in _.refresh:
                        each_method()
                else:
                    tkMessageBox.showwarning(u'Entry error',
                            u'\n'.join([
                                u'A very similar product already exists.',
                                u'Change one of the "gold" fields to make this item unique.',
                                u'Or add a (unique) note.'
                            ]) )
            else:
                tkMessageBox.showwarning(u'Entry error',
                        u'\n'.join([
                            u'Information in "gold" color are required.',
                            u'Check "units" and "current price" are numbers.',
                        ]) )
        else:
            tkMessageBox.showwarning(u'No group is selected.',
                    u'\n'.join([
                        u'Please reselect a company group.',
                    ]) )

    def validate_fields():
        '''Assert that required fields have been filled.
        Assert number fields contain numbers.
        Assert short answer fields are not too long.

        Returns boolean type.
        '''
        valdict = collectSVvalues()

        try:
            # Inventory name is required. Other names are not.
            valdict[u'inventory_name']
            # Assert "SKU" and "UM" are short words.
            assert(0 < len(valdict[u'SKU']) <= 8)
            assert(0 < len(valdict[u'UM']) <= 8)
            # Assert number fields contain numbers
            valdict[u'units'] = float(valdict[u'units'])
            if valdict.get(u'curr_price'): #Optional field
                valdict[u'curr_price'] = float(valdict[u'curr_price'])
            # Assert boolean fields are booleans
            valdict[u'discontinued'] = bool(valdict[u'discontinued'])
            valdict[u'unitpriced'] = bool(valdict[u'unitpriced'])
        except ValueError:
            return False
        except AssertionError:
            return False

        return valdict


    def collectSVvalues():
        '''Collects the entered values from all fields. Ignores fields that
        contain the 'hint' and returns a dictionary of the results.

        Returns dict type.
        '''
        _dict = dict()
        # Get the field values that are not the 'hint' nor blank.
        for txt, svset in zip(entryfields, entrySVars):
            if svset[0].get() not in (txt[-1], u''):
                _dict[txt[1]] = svset[0].get()
            else:
                _dict[txt[1]] = u''
        # Get the radiobutton values.
        for txt, svset in radioSVars:
            _dict[txt] = bool(svset.get())

        if _.debug:
            print 'METHOD: collectSVvalues'
            for key, val in _dict.iteritems():
                print key, val

        return _dict



    _.product_edit.refresh = refresh
    try:
        _.refresh.append(refresh)
    except KeyError:
        _.refresh = [refresh,]

