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
:SINCE: Tue Aug 26 19:02:13 2014
:VERSION: 0.1
"""
#===============================================================================
# PROGRAM METADATA
#===============================================================================
__author__ = 'Ripley6811'
__contact__ = 'python@boun.cr'
__copyright__ = ''
__license__ = ''
__date__ = 'Tue Aug 26 19:02:13 2014'
__version__ = '0.1'

#===============================================================================
# IMPORT STATEMENTS
#===============================================================================
import Tix
import tkMessageBox
import po #package

#===============================================================================
# METHODS
#===============================================================================



#===============================================================================
# MAIN METHOD AND TESTING AREA
#===============================================================================
def create(_):
    """Creates the main purchase and sale window in the supplied frame."""
    _.curr_company = None
    _.edit_ID = None
    _.listbox = type(_)()
    _.poF = type(_)()
#    _state.settings.font = "NSimSun"#"PMingLiU"



    #### Set up left pane containing company names ####
    ###################################################
    left_pane = Tix.Frame(_.po_frame)
    left_pane.pack(side=Tix.LEFT, fill=Tix.Y, padx=2, pady=3)


    # Set up mode switching buttons: Purchases, Sales
    def sc_switch(mode):
        print mode
        _.sc_mode = mode
        for each_butt in cog_butts:
            if "{}1".format(mode) in each_butt["value"]:
                each_butt.configure(bg='burlywood')
            else:
                each_butt.configure(bg='NavajoWhite4')
        try:
            load_company()
        except NameError:
            pass # Pass on initialization.

    modebox = Tix.Frame(left_pane)
    modebox.pack(side=Tix.TOP, fill=Tix.X)
    options = dict(variable="modebuttons", indicatoron=False,
                   bg="NavajoWhite4", font=(_.font, "15", "bold"),
                   selectcolor="light sky blue",
                   activebackground="light sky blue")
    srb = Tix.Radiobutton(modebox, value="s", textvariable=_.loc("Supplier"),
                         command=lambda:sc_switch("s"), **options)
    srb.pack(side=Tix.LEFT, expand=True, fill=Tix.X)
    tr = Tix.Radiobutton(modebox, value="c", textvariable=_.loc("Customer"),
                         command=lambda:sc_switch("c"), **options)
    tr.pack(side=Tix.RIGHT, expand=True, fill=Tix.X)


    # Set up company switching buttons
    def select_cogroup(cogroup):
        _.curr.cogroup = cogroup
        if _.debug: print(cogroup)
        load_company()

    def add_cogroup():
        #TODO: Ability to add a new company group
        # Use the currently selected cogroup button "+" to add to list
        print("TODO: Add method to add a new company group!")


    cogroups = _.dbm.cogroups()
    if _.debug:
        print len(cogroups), "company groups in database loaded."

    colist_frame = Tix.Frame(left_pane)
    colist_frame.pack(side=Tix.LEFT, fill=Tix.BOTH)
    options = dict(variable="companybuttons", indicatoron=False,
                   font=(_.font, "12", "bold"), bg="burlywood",
                   selectcolor="gold",
                   activebackground="gold")

    cog_butts = []
    i = 0
    for i, cog in enumerate(cogroups):
        tr = Tix.Radiobutton(colist_frame, text=cog.name,
                             value=u"s{}c{} {}".format(int(cog.is_supplier)
                                                      ,int(cog.is_customer)
                                                      ,cog.name),
                             command=lambda x=cog:select_cogroup(x),
                             **options)
        #TODO: color by supplier/client
        tr.grid(row=i/4,column=i%4, sticky=Tix.W+Tix.E)
        cog_butts.append(tr)
    else:
        # Increment one more to add the "+" button.
        i += 1
    tr = Tix.Button(colist_frame, text=u"+",
                    command=add_cogroup,
                    font=(_.font, "12", "bold"), bg="lawn green",
                    activebackground="lime green")
    tr.grid(row=i/4,column=i%4, sticky='ew')

    # Set "Supplier" button as active
    srb.invoke()





    #### Set up right pane containing company info and POs ####
    ###########################################################
    top_pane = Tix.Frame(_.po_frame)
    top_pane.pack(side='top', fill='x', padx=4, pady=5)

    # Add branch selection buttons across top
    branchbox = Tix.Frame(top_pane)
    branchbox.pack(side='top', fill=Tix.X)

    #### PAGE BUTTONS: PO, MANIFEST, INVOICE, ALL PO ####
    #####################################################
    page_buttons = Tix.Frame(top_pane)
    page_buttons.pack(side='top', fill='x', expand=True)

    options = dict(variable="pagebuttons", indicatoron=False,
                   font=(_.font, "14", "bold"), bg="medium purple",
                   selectcolor="plum", padx=40,
                   activebackground="plum")
    tr = Tix.Radiobutton(page_buttons, textvariable=_.loc(u'Active POs'),
                    command=lambda x='po new':change_view(x),
                    value='po new', **options)
    tr.pack(side='left', fill='x')
    tr.select()
    _.view_mode = 'po new'
    tr = Tix.Radiobutton(page_buttons, textvariable=_.loc(u'Manifests & Invoices'),
                    command=lambda x='shipped':change_view(x),
                    value='shipped', **options)
    tr.pack(side='left', fill='x')
    tr = Tix.Radiobutton(page_buttons, textvariable=_.loc(u'All POs'),
                    command=lambda x='po all':change_view(x),
                    value='po all', **options)
    tr.pack(side='left', fill='x')

    po.all_frame(_)
    po.mi_frame(_)

    def change_view(mode):
        if _.view_mode == mode:
            return
        print 'view:', mode

        _.view_mode = mode

        if mode == 'po new':
            _.po_center.pack(side='left', fill='both', expand=1)
        else:
            _.po_center.pack_forget()
        if mode == 'po all':
            _.all_frame.pack(side='left', fill='both', expand=1)
            _.all_frame_refresh()
        else:
            _.all_frame.pack_forget()
        if mode == 'shipped':
            _.mi_frame.pack(side='left', fill='both', expand=1)
            _.mi_frame_refresh()
        else:
            _.mi_frame.pack_forget()



    # Add center pane for PO listing
    center_pane = _.po_center = Tix.Frame(_.po_frame)
    center_pane.pack(side=Tix.LEFT, fill=Tix.BOTH)

    def load_company():
        try:
            cogroup = _.curr.cogroup
        except AttributeError:
            return # Group not selected yet
        if cogroup == None or cogroup == u'':
            return
        try:
            branchbox.children.popitem()[1].destroy()
        except KeyError:
            pass
        branchbox_inner = Tix.Frame(branchbox)
        branchbox_inner.pack(side=Tix.TOP, fill=Tix.X)

        _.curr.branch = Tix.StringVar()
        options = dict(variable=_.curr.branch, indicatoron=False,
                       font=(_.font, "20", "bold"), bg="burlywood",
                       selectcolor="gold",
                       activebackground="gold")
        Tix.Label(branchbox_inner, textvariable=_.loc(u"Branch")).pack(side="left")
        branch_info = Tix.StringVar()
        def set_branch_info():
            branch = _.dbm.get_branch(_.curr.branch.get())
            text = u'\u260E {}\n\u213B {}\n\u2709 {}'.format(branch.phone, branch.fax, branch.email)
            branch_info.set(text)
        _.curr.branch.trace('w', lambda a,b,c,: set_branch_info())
        for i, branch in enumerate(cogroup.branches):
            tr = Tix.Radiobutton(branchbox_inner, text=branch.name,
                                 value=branch.name, **options)
            tr.pack(side="left")
            if i==0:
                tr.invoke()
        Tix.Label(branchbox_inner, textvariable=branch_info, justify='left')\
            .pack(side='left')


        #TODO: Load entry fields with company info for viewing/editing
        #TODO: Buttons for switching supplier/customer booleans



        #### Display open purchase orders that can ship ####
        ####################################################

        try:
            center_pane.children.popitem()[1].destroy()
        except KeyError:
            pass
        pobox = Tix.Frame(center_pane)
        pobox.pack(side=Tix.TOP, fill=Tix.X)

        activeOrders = []
        _poIDs = []
        _qtyVars = []
        _unitsVars = []
        _discountVars = []
        _multiplier = [] # Convert SKU to units
        _poBs = [] # PO button

#            info.order.entryWs[row].icursor(Tk.END)
#            info.order.entryWs[row].selection_range(0, Tk.END)

        order_list = cogroup.purchases if _.sc_mode == "s" else cogroup.sales
        TB = lambda _text, **kwargs: Tix.Button(pobox, text=_text, anchor='w',
                                      bg="moccasin",
                                      activebackground="moccasin", **kwargs)
        row = 0
        for row, order in enumerate(order_list):
            if order.is_open:
                activeOrders.append(order)
                _poIDs.append(order.id)
                _prod = order.product
                print type(_prod)
                assert isinstance(_prod, _.dbm.Product), u"Product not attached to order."
                _id = order.orderID if order.orderID else _.loc(u"(NA)", 1)
                _text = u"PO {} : {} ({})".format(_id, _prod.label(), _prod.specs)
                #TODO: Button opens PO editing, like price, date, applytax and total qty.
                tb = TB(_text)
                tb['command'] = lambda o=order: po.edit(_,o,load_company)
                tb.grid(row=row*2, rowspan=2, column=0, sticky='nsew')
                _poBs.append(tb)

                if order.ordernote:
                    lw = Tix.Label(pobox, textvariable=_.loc(u'NOTE:'),
                                   bg='coral', font=(_.font, 9))
                    lw.grid(row=row*2+1, column=1, sticky='ew')
                    lw = Tix.Label(pobox, text=order.ordernote, anchor='w',
                                   bg='lavender', font=(_.font, 9))
                    lw.grid(row=row*2+1, column=2, columnspan=10, sticky='ew')

                # Multiple entry option button
                tb = Tix.Button(pobox, text=u'\u26DF \u26DF',
                                font=(_.font, 11), bg="lawn green",
                                activebackground="lime green")
                tb['command'] = lambda o=order: po.add_many(_,o,load_company)
                tb.grid(row=row*2, column=1, sticky='nsew')

                # PO remaining QTY
                amt = order.qty_remaining()
                if amt >= 1e9:
                    amt = u'\u221E' # Infinity symbol for unlimited POs.
                _textvar = _.loc(u"(Avail:")
                lw = Tix.Label(pobox, textvariable=_textvar, anchor='w')
                lw.grid(row=row*2, column=2, sticky='w')
                _sku = _prod.SKU if _prod.SKU != u"槽車" else "kg"
                _text = u'{} {})'.format(amt, _sku)
                lw = Tix.Label(pobox, text=_text, anchor='e')
                lw.grid(row=row*2, column=3, sticky='e')



                # QTY entry field
                def highlight_entry(row, widget, capamt=100):
                    if _.debug:
                        print "row=",row, " widget=",widget, " capamt=",capamt
                    # Check if entry is a number and doesn't exceed PO max.
                    if widget.get():
                        if widget.get().isdigit() and int(widget.get()) <= capamt:
                            widget.config(bg=u'PaleTurquoise1')
                        else:
                            widget.config(bg=u'IndianRed1')
                    else:
                        widget.config(bg=u'moccasin')
                    # Fill in total units reference and color the PO button
                    if _qtyVars[row].get().isdigit():
                        _int = int(_qtyVars[row].get())*_multiplier[row]
                        _poBs[row].config(bg=u'PaleTurquoise1')
                        if _int.is_integer():
                            _int = int(_int)
                        _unitsVars[row].set(u"{}".format(_int))
                    else:
                        _poBs[row].config(bg=u'moccasin')
                        _unitsVars[row].set(u"{}".format(0))
                _qtyVars.append(Tix.StringVar())
                ew = Tix.Entry(pobox, textvariable=_qtyVars[-1], width=7,
                               justify="center", bg=u"moccasin")
                ew.grid(row=row*2, column=4)
                _qtyVars[-1].trace('w', lambda a,b,c,ew=ew,capamt=amt,row=len(_poIDs)-1: highlight_entry(row,ew,capamt) )

                # SKU
                _text = u'{}:'.format(_prod.SKU)
                lw = Tix.Label(pobox, text=_text, anchor='w')
                lw.grid(row=row*2, column=5, sticky='w')

                # Total units StringVar
                _unitsVars.append(Tix.StringVar())
                _multiplier.append(_prod.units)
                lw = Tix.Label(pobox, textvariable=_unitsVars[-1],
                               anchor='e', bg=u'LightGoldenrod1')
                lw.grid(row=row*2, column=6, sticky='e')
                _unitsVars[-1].set("0")
                _text = u' {}'.format(
                    _prod.UM #if _prod.unitpriced else _prod.SKU
                )
                lw = Tix.Label(pobox, text=_text,
                               anchor='w', bg=u'LightGoldenrod1')
                lw.grid(row=row*2, column=7, sticky='w')

                # Price per sku/unit
                _text = u' ${} per {} '.format(
                    int(order.price) if order.price.is_integer() else order.price,
                    _prod.UM if _prod.unitpriced else _prod.SKU
                )
                lw = Tix.Label(pobox, text=_text)
                lw.grid(row=row*2, column=8)

                # Discount percentage
                _discountVars.append(Tix.StringVar())
                ew = Tix.Entry(pobox, textvariable=_discountVars[-1], width=7,
                               justify="center", bg=u"moccasin")
                ew.grid(row=row*2, column=9)
                _discountVars[-1].set(order.discount)
                _discountVars[-1].trace('w', lambda a,b,c,ew=ew,row=len(_poIDs)-1: highlight_entry(row,ew,100) )
                lw = Tix.Label(pobox, textvariable=_.loc(u"% discount"), anchor='w')
                lw.grid(row=row*2, column=10, sticky='w')


                # PO start date
                lw = Tix.Label(pobox, text=u'({})'.format(order.orderdate),
                               font=(_.font, 10))
                lw.grid(row=row*2, column=11)


        # Button for adding another product order.
        #TODO: Add command
        tb = Tix.Button(pobox, textvariable=_.loc("+ PO"),
                        bg="lawn green",
                        command=lambda:po.new(_, load_company),
                        activebackground="lime green")
        tb.grid(row=row*2+2, column=0, sticky='ew')

        # Button for submitting new manifest. Goto date selection, etc.
        #TODO: Add command
        if _poIDs:
            tb = Tix.Button(pobox, textvariable=_.loc(u"\u26DF Create Manifest"),
                            bg="lawn green",
                            command=lambda:make_manifest(),
                            activebackground="lime green")
            tb.grid(row=row*2+2, column=4, columnspan=6, sticky='ew')

        def make_manifest():
            manifest_list = [(a, b, c) for a,b,c in
                             zip(activeOrders, _qtyVars, _unitsVars) if b.get()]
            if _.debug:
                print manifest_list
            if len(manifest_list) > 5:
                tkMessageBox.showwarning(_.loc(u"Maximum exceeded",True),
                        _.loc(u"Only a maximum of five items allowed.",True))
                return
            if len(manifest_list) < 1:
                return

            po.manifest(_, orders=[a for a,b,c in manifest_list],
                           qtyVars=[b for a,b,c in manifest_list],
                           unitVars=[c for a,b,c in manifest_list],
                            refresh=load_company)

        # Load PO HList 'All POs'
        _.all_frame_refresh()
        _.mi_frame_refresh()

    _.refresh = load_company

if __name__ == '__main__':
    pass

