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
        load_company(cogroup)

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
    top_pane.pack(side=Tix.TOP, fill=Tix.X, padx=2, pady=3)

    # Add branch selection buttons across top
    branchbox = Tix.Frame(top_pane)
    branchbox.pack(side=Tix.TOP, fill=Tix.X)

    # Add center pane for PO listing
    center_pane = Tix.Frame(_.po_frame)
    center_pane.pack(side=Tix.LEFT, fill=Tix.BOTH)

    def load_company(cogroup):
        try:
            branchbox.children.popitem()[1].destroy()
        except KeyError:
            pass
        branchbox_inner = Tix.Frame(branchbox)
        branchbox_inner.pack(side=Tix.TOP, fill=Tix.X)

        options = dict(variable="branchbuttons", indicatoron=False,
                       font=(_.font, "20", "bold"), bg="burlywood",
                       selectcolor="gold",
                       activebackground="gold")
        Tix.Label(branchbox_inner, textvariable=_.loc(u"Branch")).pack(side="left")
        for i, branch in enumerate(cogroup.branches):
            tr = Tix.Radiobutton(branchbox_inner, text=branch.name,
                             value=branch.name,
#                             command=pass,
                             **options)
            tr.pack(side="left")
            if i==0:
                tr.invoke()

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

        _poIDs = []
        _qtyVars = []
        _unitsVars = []
        _discountVars = []
        _multiplier = [] # Convert SKU to units
        _poBs = [] # PO button

#            info.order.entryWs[row].icursor(Tk.END)
#            info.order.entryWs[row].selection_range(0, Tk.END)

        order_list = cogroup.purchases if _.sc_mode == "s" else cogroup.sales
        TB = lambda _text: Tix.Button(pobox, text=_text, anchor='w',
                                      bg="moccasin",
                                      activebackground="moccasin")
        row = 0
        for row, order in enumerate(order_list):
            if not (order.all_shipped() & order.all_invoiced()): # & order.all_paid()
                _poIDs.append(order.id)
                _prod = order.product
                _id = order.orderID if order.orderID else _.loc(u"(NA)", 1)
                _text = u"PO {} : {}".format(_id, _prod.inventory_name)
                #TODO: Button opens PO editing, like price, date, applytax and total qty.
                tb = TB(_text)
#                tb['command'] = pass
                tb.grid(row=row, column=0, sticky='ew')
                _poBs.append(tb)

                # PO remaining QTY
                amt = order.qty_remaining()
                if amt >= 1e9:
                    amt = u'\u221E' # Infinity symbol for unlimited POs.
                _textvar = _.loc(u"(Avail:")
                lw = Tix.Label(pobox, textvariable=_textvar, anchor='w')
                lw.grid(row=row, column=1, sticky='w')
                _sku = _prod.SKU if _prod.SKU != u"槽車" else "kg"
                _text = u'{} {})'.format(amt, _sku)
                lw = Tix.Label(pobox, text=_text, anchor='e')
                lw.grid(row=row, column=2, sticky='e')

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
                        _unitsVars[row].set(u"({}".format(_int))
                    else:
                        _poBs[row].config(bg=u'moccasin')
                        _unitsVars[row].set(u"({}".format(0))
                _qtyVars.append(Tix.StringVar())
                ew = Tix.Entry(pobox, textvariable=_qtyVars[-1], width=7,
                               justify="center", bg=u"moccasin")
                ew.grid(row=row, column=3)
                _qtyVars[-1].trace('w', lambda a,b,c,ew=ew,capamt=amt,row=len(_poIDs)-1: highlight_entry(row,ew,capamt) )

                # SKU
                _text = u'{}'.format(_prod.SKU)
                lw = Tix.Label(pobox, text=_text, anchor='w')
                lw.grid(row=row, column=4, sticky='w')

                # Total units StringVar
                _unitsVars.append(Tix.StringVar())
                _multiplier.append(_prod.units)
                lw = Tix.Label(pobox, textvariable=_unitsVars[-1], anchor='w')
                lw.grid(row=row, column=5, sticky='w')
                _unitsVars[-1].set("(0")
                _text = u' {})'.format(
                    _prod.UM #if _prod.unitpriced else _prod.SKU
                )
                lw = Tix.Label(pobox, text=_text, anchor='w')
                lw.grid(row=row, column=6, sticky='w')

                # Price per sku/unit
                _text = u' ${} per {} '.format(
                    int(_prod.curr_price) if _prod.curr_price.is_integer() else _prod.curr_price,
                    _prod.UM if _prod.unitpriced else _prod.SKU
                )
                lw = Tix.Label(pobox, text=_text)
                lw.grid(row=row, column=7)

                # Discount percentage
                _discountVars.append(Tix.StringVar())
                ew = Tix.Entry(pobox, textvariable=_discountVars[-1], width=7,
                               justify="center", bg=u"moccasin")
                ew.grid(row=row, column=8)
                _discountVars[-1].set(order.discount)
                _discountVars[-1].trace('w', lambda a,b,c,ew=ew,row=len(_poIDs)-1: highlight_entry(row,ew,100) )
                lw = Tix.Label(pobox, textvariable=_.loc(u"% discount"), anchor='w')
                lw.grid(row=row, column=9, sticky='w')


        # Button for adding another product order.
        #TODO: Add command
        tb = Tix.Button(pobox, textvariable=_.loc("+ PO"),
                        bg="lawn green",
                        activebackground="lime green")
        tb.grid(row=row+1, column=0, sticky='ew')
        # Button for submitting new manifest. Goto date selection, etc.
        #TODO: Add command
        if _poIDs:
            tb = Tix.Button(pobox, textvariable=_.loc(u"\u26DF Create Manifest"),
                            bg="lawn green",
                            command=lambda:make_manifest(),
                            activebackground="lime green")
            tb.grid(row=row+1, column=3, columnspan=6, sticky='ew')

        def make_manifest():
            for _id, qtyV, discV in zip(_poIDs, _qtyVars, _discountVars):
                print _id, qtyV.get(), discV.get()



if __name__ == '__main__':
    pass

