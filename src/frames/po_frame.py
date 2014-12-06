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
import fr_branch
from utils import settings

#===============================================================================
# METHODS
#===============================================================================



#===============================================================================
# MAIN METHOD AND TESTING AREA
#===============================================================================
def create(_):
    """Creates the main purchase and sale window in the supplied frame."""
    _.curr.cogroup = None # Store the current SQL CoGroup object
    _.curr.cogroupSV = Tix.StringVar() # Store the current CoGroup id ('name')
    _.curr.branchSV = Tix.StringVar() # Store the current Branch id ('name')
    _.edit_ID = None
    _.listbox = type(_)()
    _.poF = type(_)()
#    _state.settings.font = "NSimSun"#"PMingLiU"



    #### Set up left pane containing company names ####
    ###################################################
    left_pane = Tix.Frame(_.parent, width=260)
    left_pane.pack_propagate(0)
    left_pane.pack(side='left', fill='y', padx=2, pady=3)


    # Set up mode switching buttons: Purchases, Sales
    def sc_switch(mode):
        _.sc_mode = mode
        settings.update(sc_mode=mode)

        # Ensure button is selected when invoked.
        if mode == 'c':
            cmodeRB.select()
        else:
            smodeRB.select()

#        for each_butt in _.cog_butts:
#            if "{}:0".format(mode) not in each_butt["value"]:
#                each_butt.configure(bg='burlywood')
#            else:
#                each_butt.configure(bg='NavajoWhite4')
        try:
            load_company()
        except NameError:
            pass # Pass on initialization.
    _.sc_switch = sc_switch

    # Mode here refers to supplier or customer records.
    modebox = Tix.Frame(left_pane)
    modebox.pack(side=Tix.TOP, fill=Tix.X)
    options = dict(variable="modebuttons", indicatoron=False,
                   bg="NavajoWhite4", font=(_.font, "15", "bold"),
                   selectcolor="light sky blue",
                   activebackground="light sky blue")
    smodeRB = Tix.Radiobutton(modebox, value="s", textvariable=_.loc("Supplier"),
                         command=lambda:sc_switch("s"), **options)
    smodeRB.pack(side=Tix.LEFT, expand=True, fill=Tix.X)
    cmodeRB = Tix.Radiobutton(modebox, value="c", textvariable=_.loc("Customer"),
                         command=lambda:sc_switch("c"), **options)
    cmodeRB.pack(side=Tix.RIGHT, expand=True, fill=Tix.X)


    # Set up company switching buttons
    def select_cogroup(cog_name):
        _.curr.cogroupSV.set(cog_name)
        cogroup = _.dbm.get_cogroup(cog_name)
        _.curr.cogroup = cogroup
        settings.update(cogroup=cogroup.name)
        if _.debug:
            print(cogroup)
        load_company()



    if _.debug:
        print len(_.dbm.cogroups()), "company groups in database loaded."



    def refresh_colist():
        try:
            _.colist.destroy()
        except KeyError:
            pass

        colist_frame = _.colist = Tix.Frame(left_pane)
        colist_frame.pack(side='left', fill='both', expand=1)

        tree = Tix.Tree(colist_frame, options='hlist.width 20')
        tree.pack(expand=1, fill='both', side='top')
        tree['opencmd'] = lambda dir=None, w=tree: opendir(w, dir)
        tree.hlist['separator'] = '~' # Default is gray
        tree.hlist.column_width(0, chars=35)

        '''Show_branch fires after the opendir method runs'''
        def show_branch(e):
            path = tree.hlist.info_selection()[0]
#            opendir(tree, path, load=True)
            select_cogroup(path)
            tree.hlist.selection_set(path)
        tree.hlist.bind('<Double-ButtonRelease-1>', show_branch)

        tds = lambda anchor, bg: Tix.DisplayStyle(
            anchor=anchor,
            bg=bg,
            itemtype='text',
            refwindow=tree.hlist,
            font=_.font
        )

        tree.hlist.delete_all()
        for cog in _.dbm.cogroups():
            tree.hlist.add(cog.name,
                           text=cog.name + _.loc(u" (group)", 1),
                           itemtype=Tix.TEXT,
                           style=tds('w', u'gold') )
            tree.setmode(cog.name, 'open')

    def opendir(tree, path, load=False):
        if _.debug:
            print 'HList path:', path
        path = tree.hlist.info_selection()[0]
        for each in tree.hlist.info_children(''):
            tree.close(each)
            for subeach in tree.hlist.info_children(each):
                tree.hlist.hide_entry(subeach)
            tree.setmode(each, 'open')
        entries = tree.hlist.info_children(path)
#        if load:
        if entries: # Show previously loaded entries
            for entry in entries:
                tree.hlist.show_entry(entry)

        else:
            for br in _.dbm.get_cogroup(path).branches:
                hid = path.decode("utf8")+u'~'+br.name
                tree.hlist.add(hid,
                               text=br.fullname if br.fullname else br.name,
                               itemtype=Tix.TEXT)



        """
        options = dict(variable="companybuttons", indicatoron=False,
                       font=(_.font, "12", "bold"), bg="burlywood",
                       selectcolor="gold",
                       activebackground="gold")

        cog_butts = _.cog_butts = []
        i = 0 # Counter for row placement.
        cols = 4 # Number of columns for company names.
        # Order the company groups by number of branches.
        ord_cogs = [(len(cog.branches), cog) for cog in _.dbm.cogroups()]
        ord_cogs = sorted(ord_cogs)[::-1]
        ord_cogs = [tup[1] for tup in ord_cogs]
        for i, cog in enumerate(ord_cogs):
            text = u'\n'.join([br.name for br in cog.branches])
            nPOs = _.dbm.active_POs(cog.name) # number of (Purchase, Sale) POs
            if _.debug:
                text += u'\n{}'.format(nPOs)
            tr = Tix.Radiobutton(colist_frame, text=text,
                                 value=u"s:{}c:{} {}".format(nPOs[0],
                                                           nPOs[1],
                                                           cog.name),
                                 command=lambda x=cog.name:select_cogroup(x),
                                 **options)
            #TODO: color by supplier/client
            tr.grid(row=i/cols,column=i%cols, sticky=u'nsew')
            cog_butts.append(tr)
        else:
            # Increment one more to add the "+" button.
            i += 1
        tr = Tix.Button(colist_frame, text=u"+",
                        command=lambda *args:fr_branch.add_new(_),
                        font=(_.font, "12", "bold"), bg="lawn green",
                        activebackground="lime green")
        tr.grid(row=i/cols,column=i%cols, sticky='ew')

        """

    _.refresh_colist = refresh_colist
    _.refresh_colist()




    #### Set up right pane containing company info and POs ####
    ###########################################################
    top_pane = Tix.Frame(_.po_frame)
    top_pane.pack(side='top', fill='x', padx=4, pady=5)

    # Add branch selection buttons across top
    branchbox = Tix.Frame(top_pane)
    branchbox.pack(side='top', fill=Tix.X)

    #### PAGE BUTTONS: PO, MANIFEST, INVOICE, ALL PO ####
    #####################################################
    page_buttons = Tix.Frame(top_pane, bg=u'SteelBlue3', pady=4)
    page_buttons.pack(side='top', fill='x', expand=True)

    options = dict(variable="pagebuttons", indicatoron=False,
                   font=(_.font, "16", "bold"), bg="medium purple",
                   selectcolor="plum", padx=40,
                   activebackground="plum")
    tr = Tix.Radiobutton(page_buttons, textvariable=_.loc(u'Active POs'),
                    command=lambda x='po new':change_view(x),
                    value='po new', **options)
    tr.grid(row=0, column=0)
    tr.select()
    _.view_mode = 'po new'
    tr = Tix.Radiobutton(page_buttons, textvariable=_.loc(u'Manifests & Invoices'),
                    command=lambda x='shipped':change_view(x),
                    value='shipped', **options)
    tr.grid(row=0, column=1)
    tr = Tix.Radiobutton(page_buttons, textvariable=_.loc(u'All POs'),
                    command=lambda x='po all':change_view(x),
                    value='po all', **options)
    tr.grid(row=0, column=2)
    page_buttons.columnconfigure(0,weight=1)
    page_buttons.columnconfigure(1,weight=1)
    page_buttons.columnconfigure(2,weight=1)

    po.all_frame(_)
    po.mi_frame(_)

    def change_view(mode):
        if _.view_mode == mode:
            return
        if _.debug:
            print 'VIEW MODE:', mode

        _.view_mode = mode

        if mode == 'po new':
            _.po_center.pack(side='left', fill='both', expand=1)
        else:
            _.po_center.pack_forget()

        if mode == 'po all':
            _.all_frame.pack(side='left', fill='both', expand=1)
            _.all_frame.refresh()
        else:
            _.all_frame.pack_forget()

        if mode == 'shipped':
            _.mi_frame.pack(side='left', fill='both', expand=1)
            _.mi_frame.refresh()
        else:
            _.mi_frame.pack_forget()



    # Add center pane for PO listing
    center_pane = _.po_center = Tix.Frame(_.po_frame)
    center_pane.pack(side=Tix.LEFT, fill=Tix.BOTH, expand=1)

    def branch_edit(name):
        fr_branch.edit(_, name)

    def load_company():
        try:
            cogroup = _.curr.cogroup
        except KeyError:
            return # Group not selected yet
        if cogroup == None or cogroup == u'':
            return
        try:
            branchbox.children.popitem()[1].destroy()
        except KeyError:
            pass
        branchbox_inner = Tix.Frame(branchbox)
        branchbox_inner.pack(side=Tix.TOP, fill=Tix.X)

        options = dict(variable=_.curr.branchSV, indicatoron=False,
                       font=(_.font, "20", "bold"), bg="burlywood",
                       selectcolor="gold",
                       activebackground="gold")
        Tix.Label(branchbox_inner, textvariable=_.loc(u"Branch")).pack(side="left")
        branch_info = Tix.StringVar()
        def set_branch_info():
            branch = _.dbm.get_branch(_.curr.branchSV.get())
            text = u'\u2116 {} : {}'.format(branch.tax_id, branch.fullname)
            text += u'\n\u260E {}'.format(branch.phone)
            if branch.fax:
                text += u'  \u213B {}'.format(branch.fax)
            text += u'\n\u2709 {}'.format(branch.email)
            branch_info.set(text)
        _.curr.branchSV.trace('w', lambda a,b,c,: set_branch_info())
        for i, branch in enumerate(cogroup.branches):
            tr = Tix.Radiobutton(branchbox_inner, text=branch.name,
                                 value=branch.name, **options)
            tr.pack(side="left", fill='y')
            if i==0:
                tr.invoke()
            tr.bind('<Double-Button-1>', lambda e, bn=branch.name: branch_edit(bn))
        Tix.Label(branchbox_inner, textvariable=branch_info, justify='left',
                  font=(_.font, 14, 'bold')).pack(side='left')


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
        def fill_qty(i, amount):
            _qtyVars[i].set(amount)

        order_list = cogroup.purchases if _.sc_mode == "s" else cogroup.sales
        TB = lambda _text, **kwargs: Tix.Button(pobox, text=_text, anchor='w',
                                      bg="moccasin", font=(_.font, 13, 'bold'),
                                      activebackground="moccasin", **kwargs)

        # Retrieve user designated PO ordering if it exists.
        minlen = 100
        rows = settings.load().get('po_order', {}).get(cogroup.name, range(minlen))
        # Increase 'rows' length in case more PO's are added.
        if len(rows) < minlen:
            rows = rows + range(max(rows)+1, max(rows)+minlen-len(rows))
        # Place PO (purchase orders) in the designated 'rows' ordering.
        for row, order in zip(rows, order_list):
            if order.is_open:
                activeOrders.append(order)
                _poIDs.append(order.id)
                _prod = order.product
                if _.debug:
                    print 'PRODUCT TYPE:', type(_prod)
                assert isinstance(_prod, _.dbm.Product), u"Product not attached to order."


                # PO start date
                _text=u'{d.month}月{d.day}日'.format(d=order.orderdate)
                lw = Tix.Label(pobox, text=_text, font=(_.font, 11, 'bold'))
                lw.grid(row=row*2, column=0)


                _id = order.orderID if order.orderID else None
                if _id:
                    _text = u'PO {:<10}:'.format(_id)
                else:
                    _text = u''
                _text += u"{}".format(_prod.label())
                tb = TB(_text)
                tb['command'] = lambda o=order: po.edit(_,o,load_company)
                tb.grid(row=row*2, column=1, sticky='nsew')
                _poBs.append(tb)

                # Price per sku/unit
                _Ptext = u' ${}/{} '.format(
                    int(order.price) if order.price.is_integer() else order.price,
                    _prod.UM if _prod.unitpriced else _prod.SKU
                )
#                lw = Tix.Label(pobox, text=_text)
#                lw.grid(row=row*2, column=8)

                _text=u'{}:{}'.format(_prod.specs, _Ptext)
                lw = Tix.Label(pobox, text=_text, padx=10, font=("PMingLiU", 13, 'bold'))
                lw.grid(row=row*2, column=2, sticky='w')


                if order.ordernote:
                    lw = Tix.Label(pobox, textvariable=_.loc(u'NOTE:'),
                                   bg='coral', font=(_.font, 9))
                    lw.grid(row=row*2+1, column=0, sticky='ew')
                    lw = Tix.Label(pobox, text=order.ordernote, anchor='w',
                                   bg='lavender', font=(_.font, 9))
                    lw.grid(row=row*2+1, column=1, columnspan=10, sticky='ew')


                # PO remaining QTY
                amt = order.qty_remaining()
                if amt >= 1e9:
                    amt = u'\u221E' # Infinity symbol for unlimited POs.
                _textvar = _.loc(u"(Avail:")
                lw = Tix.Label(pobox, textvariable=_textvar, anchor='w')
                lw.grid(row=row*2, column=3, sticky='ew')
                _sku = _prod.SKU if _prod.SKU != u"槽車" else "kg"
                _textvar2 = Tix.StringVar()
                _text = u'{} {})'.format(amt, _sku)
                _textvar2.set(_text)
                _btext = u'{} {})'.format(amt * _prod.units if isinstance(amt, int) else amt, _prod.UM)
                lw.bind('<Button-1>', lambda e, sv=_textvar2, a=_text, b=_btext: \
                        sv.set(b if sv.get() == a else a))
                lw2 = Tix.Label(pobox, textvariable=_textvar2, anchor='e')
                lw2.grid(row=row*2, column=4, sticky='ew')
                lw2.bind('<Double-Button-1>', lambda e, a=amt, i=len(_qtyVars): fill_qty(i,a))

                # If PO remainder is zero. Make red.
                if order.all_shipped():
                    lw.config(bg=u'tomato')
                    lw2.config(bg=u'tomato')

                # Multiple entry option button
                tb = Tix.Button(pobox, text=u'\u26DF \u26DF',
                                font=(_.font, 11), bg="lawn green",
                                activebackground="lime green")
                tb['command'] = lambda o=order: po.add_many(_,o,load_company)
                tb.grid(row=row*2, column=5, sticky='nsew')

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
                ew.grid(row=row*2, column=6)
                _qtyVars[-1].trace('w', lambda a,b,c,ew=ew,capamt=amt,row=len(_poIDs)-1: highlight_entry(row,ew,capamt) )

                # SKU
                _text = u'{}:'.format(_prod.SKU)
                lw = Tix.Label(pobox, text=_text, anchor='w')
                lw.grid(row=row*2, column=7, sticky='w')

                # Total units StringVar
                _unitsVars.append(Tix.StringVar())
                _multiplier.append(_prod.units)
                lw = Tix.Label(pobox, textvariable=_unitsVars[-1],
                               anchor='e', bg=u'LightGoldenrod1')
                lw.grid(row=row*2, column=8, sticky='e')
                _unitsVars[-1].set("0")
                _text = u' {}'.format(
                    _prod.UM #if _prod.unitpriced else _prod.SKU
                )
                lw = Tix.Label(pobox, text=_text,
                               anchor='w', bg=u'LightGoldenrod1')
                lw.grid(row=row*2, column=9, sticky='w')

                # Discount percentage
#                _discountVars.append(Tix.StringVar())
#                ew = Tix.Entry(pobox, textvariable=_discountVars[-1], width=7,
#                               justify="center", bg=u"moccasin")
#                ew.grid(row=row*2, column=9)
#                _discountVars[-1].set(order.discount)
#                _discountVars[-1].trace('w', lambda a,b,c,ew=ew,row=len(_poIDs)-1: highlight_entry(row,ew,100) )
#                lw = Tix.Label(pobox, textvariable=_.loc(u"% discount"), anchor='w')
#                lw.grid(row=row*2, column=10, sticky='w')




        # Button for adding another product order.
        #TODO: Add command
        tb = Tix.Button(pobox, textvariable=_.loc("+ PO"),
                        bg="lawn green",
                        command=lambda:po.new(_, load_company),
                        activebackground="lime green")
        tb.grid(row=1000, column=1, sticky='ew')

        # Button for submitting new manifest. Goto date selection, etc.
        #TODO: Add command
        numbSVar = Tix.StringVar()
        if _poIDs:
            tl = Tix.Label(pobox, textvariable=_.loc(u'Manifest #:'))
            tl.grid(row=1000, column=2, columnspan=2, sticky='e')
            te = Tix.Entry(pobox, textvariable=numbSVar, width=9,
                               justify="center", bg=u"moccasin")
            te.grid(row=1000, column=4, columnspan=2, sticky='ew')
            tb = Tix.Button(pobox, textvariable=_.loc(u"\u26DF Create Manifest"),
                            bg="lawn green",
                            command=lambda:make_manifest(),
                            activebackground="lime green")
            tb.grid(row=1000, column=6, columnspan=5, sticky='ew')

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
                            refresh=load_company,
                            numbSVar = numbSVar)


        # Load PO HList 'All POs'
        for each_method in _.refresh:
            each_method()


    # Load cogroup and mode from previous session.
    js = settings.load()
    if js.get('sc_mode'):
        try:
            _.curr.cogroup = _.dbm.get_cogroup(js.get('cogroup'))
            _.curr.cogroupSV.set(_.curr.cogroup.name)
            for key, val in _.colist.children.iteritems():
                try:
                    if _.curr.cogroup.name in val['value']:
                        if _.debug:
                            print _.curr.cogroup, val['value']
                            print _.colist.children[key]
                        _.colist.children[key].select()
                except:
                    pass
        except TypeError:
            pass

        if js['sc_mode'] == 'c':
            cmodeRB.invoke()
        else:
            smodeRB.invoke()
    else:
        # Set "Supplier" button as active
        smodeRB.invoke()
    del js


if __name__ == '__main__':
    pass

