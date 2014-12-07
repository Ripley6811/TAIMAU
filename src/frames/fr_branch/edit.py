#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Tix
import tkMessageBox


def main(_, br_name):
    """Edit or view a branches information."""
    branch = _.dbm.session.query(_.dbm.Branch).get(br_name)

    flengths = {}
    br_columns = _.dbm.Branch.__table__.columns

    # Get lengths for all string variables
    for key in br_columns.keys():
        try:
            flengths[key] = br_columns[key].type.length
        except AttributeError:
            pass #Skip non string values

    # Create new external window.
    if not _.getExtWin(_, co_name=branch.name,
                       title=u"EDIT"):
        return


    top_bar = Tix.Frame(_.extwin)
    top_bar.pack(side='top', fill='x')

    infoText = Tix.StringVar()
    tl = Tix.Label(top_bar, textvariable=infoText, font=(_.font, 18, 'bold'))
    tl.pack(side='top', fill='x')


    def update_product_info_line():
        try:
            ptext = u'{group}(組) - {name}(分) : {fullname}'
            ptext = ptext.format(**collectSVvalues())
        except KeyError:
#        except ValueError:
            ptext = _.loc(u'(Gold Fields Required!)', 1)

        infoText.set(ptext)

    mainf = Tix.Frame(_.extwin)
    mainf.pack(side='top', fill='x')

    entryfields = [ # (required?, SQL attribute name, Tix.Label, Entry hint)
#        (1, u'name', u'Short Name:', u'2 to 4 character abbreviated branch name.'),
#        (1, u'group', u'Group Code:', u'2 to 4 character name of parent group.'),
        (0, u'fullname', u'Full Name:', u'Full name of branch.'),
        (0, u'english_name', u'English Name:', u'Full English name of branch.'),
        (0, u'tax_id', u'Tax ID:', u'8 digit tax ID (統一編號).'),
        (0, u'phone', u'Phone Number:', u''),
        (0, u'fax', u'Fax Number:', u''),
        (0, u'email', u'Email Address:', u''),
        (0, u'note', u'Note:', u''),
        (0, u'address_office', u'Office Address:', u''),
        (0, u'address_shipping', u'Shipping Address:', u'Location for sending products.'),
        (0, u'address_billing', u'Billing Address:', u''),
        (0, u'address', u'Address (Extra):', u'Additional location.'),
#        (0, u'is_active', u'Current Supplier/Client:', u'(Boolean)'),
    ]
    entrySVars = [(Tix.StringVar(), None) for i in range(len(entryfields))]
    radioSVars = [(u'is_active', Tix.BooleanVar()),
#                  (u'discontinued', Tix.BooleanVar()),
                 ]

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

            # Limit the number of characters typed to database variable limit.
            entrySVars[i][0].set(entrySVars[i][0].get()[:flengths[entryfields[i][1]]])

        update_product_info_line()


    #########################
    ### TEXT ENTRY FIELDS ###
    for row, (req, key, label, entry) in enumerate(entryfields):
        tl = Tix.Label(mainf, textvariable=_.loc(label), font=(_.font, 14))
        tl.grid(row=row, column=0, columnspan=2, sticky='nse')
        if req:
            tl.config(background=u'gold')
        te = Tix.Entry(mainf, textvariable=entrySVars[row][0], width=80, font=(_.font, 14))
        te.grid(row=row, column=2, columnspan=4, sticky='nsew')
        entrySVars[row] = (entrySVars[row][0], te)
        entrySVars[row][0].set(entry)
        entrySVars[row][0].trace('w', lambda a,b,c,tew=te, i=row: validatekey(tew, i))
        te.bind(u'<FocusIn>', lambda e, tew=te: del_hint(tew))
        te.bind(u'<FocusOut>', lambda e, tew=te, i=row: add_hint(tew, i))
        te.config(background=u'moccasin', foreground=hint_color)

    # Set expansion (span) weight. Labels do not expand and entries fill.
    for col in range(2):
        mainf.columnconfigure(col, weight=0)
    for col in range(2,6):
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
    tl = Tix.Label(mainf, textvariable=_.loc(u'Current Supplier/Customer?'), font=(_.font, 14))
    tl.grid(row=row+1, column=0, columnspan=2, sticky='nse')
    trb = Tix.Radiobutton(textvariable=_.loc(u'Yes'),
                    value=True, variable=radioSVars[0][1], **rbopts)
    trb.grid(row=row+1, column=2, columnspan=1, sticky='nsew')
    trb = Tix.Radiobutton(textvariable=_.loc(u'No'),
                    value=False, variable=radioSVars[0][1], **rbopts)
    trb.grid(row=row+1, column=3, columnspan=1, sticky='nsew')


    ###############
    ### BUTTONS ###
    opts = dict(master=mainf, bg=u'lawn green',
                activebackground=u'lime green',
                font=(_.font, 14, 'bold'))
    Tix.Button(textvariable=_.loc(u'Save changes'),
               command=lambda:save_update(), **opts).grid(row=20, column=0, columnspan=6, sticky='nsew')




    def refresh():
        try:
            branch
        except KeyError:
            return

        if branch != None:
            for row, ef in enumerate(entryfields):
                text = branch.__dict__.get(ef[1])
                if text:
                    try:
                        text = str(int(text))
                    except ValueError:
                        pass
                    entrySVars[row][0].set(text.split('{',1)[0])
                else:
                    entrySVars[row][0].set(u'')
                    add_hint(entrySVars[row][1], row)
            for sv in radioSVars:
                boo = bool(branch.__dict__.get(sv[0]))
                if boo == False:
                    sv[1].set(False)
                elif boo == True:
                    sv[1].set(True)
                else:
                    print sv[0], sv[1].get()
                    raise ValueError, u"Branch boolean value error. Value type {}".format(type(boo))

        update_product_info_line()

    def save_update():
        # Check that there is a current product loaded.
        if branch != None:
            # Validate fields
            if validate_fields():
                # If orders already exist, then confirm again to change.
#                nOrders = len(_.curr.product.orders)
                confirm = True
#                if nOrders > 0:
#                    confirm = False
#                    head = _.loc(u'Changing existing records!', 1)
#                    body = _.loc(u'{} orders will be affected.\nContinue with changes?', 1).format(nOrders)
#                    confirm = tkMessageBox.askokcancel(head, body)
                if confirm:
                    query = _.dbm.session.query(_.dbm.Branch)
                    query = query.filter_by(name=branch.name)
                    valdict = collectSVvalues()

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

        _.extwin.destroy()


    def validate_fields():
        '''Assert that required fields have been filled.
        Assert number fields contain numbers.
        Assert short answer fields are not too long.

        Returns boolean type.
        '''
        valdict = collectSVvalues()

        try:
            # Inventory name is required. Other names are not.
            valdict[u'name']
            # Assert "SKU" and "UM" are short words.
            assert(0 < len(valdict[u'name']) <= 8)

            valdict[u'is_active'] = bool(valdict[u'is_active'])
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

        _dict[u'group'] = branch.group
        _dict[u'name'] = branch.name

        return _dict

    refresh()


