#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Tix
from utils import date_picker


def main(_, order, refresh):
    """PO editing window"""

    #### USE THIS TO INTEGRATE FRAME INTO MAIN WINDOW ####
#    repack_info = _.po_center.pack_info()
#    _.po_center.pack_forget() # .pack(**repack_info)
#    center_pane = Tix.Frame(_.po_frame)
#    center_pane.pack(side='left', fill='both')


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
    _.extwin.title(u"{}: {}".format(_.curr.cogroup.name, _.loc(u"Edit PO", asText=True)))
    _.extwin.focus_set()

    center_pane = Tix.Frame(_.extwin)
    center_pane.pack(side='left', fill='both')


    #### VARIABLES FOR RECORD ENTRY ####
    ####################################
    _pname = Tix.StringVar()
    _ponumber = Tix.StringVar()
    _qty = Tix.StringVar()
    _price = Tix.StringVar()
    _note = Tix.StringVar()
    _tax = Tix.BooleanVar()




    sep = Tix.Frame(center_pane, relief='ridge', height=8, bg="gray")
    sep.pack(side='top', fill='x')


    pogrid = Tix.Frame(center_pane)
    pogrid.pack(side='top')
    ### DATE SELECTION ###
    # Order date: preselect today
    tl = Tix.Label(pogrid, textvariable=_.loc(u"Date of PO"))
    tl.grid(row=0, column=2, columnspan=2)
    cal = date_picker.Calendar(pogrid,
                               month=order.orderdate.month,
                               year=order.orderdate.year,
                               day=order.orderdate.day)
    cal.grid(row=1, rowspan=6, column=2, columnspan=2)

    # Due date: nothing preselected (omit this?)


    ### SHOW PRODUCT ###
    le = Tix.LabelEntry(pogrid, labelside='left')
    le.label.configure(textvariable=_.loc(u"Product"), anchor='center')
    le.entry.configure(textvariable=_pname, width=26)
    _pname.set(order.product.label())
    le.entry.configure(state='disabled')
    le.grid(row=0, rowspan=1, column=0, columnspan=2, sticky='w')

    ### PO NUMBER ###
    le = Tix.LabelEntry(pogrid, labelside='left')
    le.label.configure(textvariable=_.loc(u"PO #"), anchor='center')
    le.entry.configure(textvariable=_ponumber, width=26)
    _ponumber.set(order.orderID)
    le.grid(row=1, rowspan=1, column=0, columnspan=2, sticky='w')

    ### PO QTY ###
    le = Tix.LabelEntry(pogrid, labelside='left')
    le.label.configure(textvariable=_.loc(u"Qty"), anchor='center')
    le.entry.configure(textvariable=_qty, width=20)
    _qty.set(u"\u221E" if order.qty >= 1e9 else order.qty)
    le.grid(row=2, rowspan=1, column=0, columnspan=1, sticky='w')
    tcb = Tix.Button(pogrid, text=u'\u221E', bg='plum')
    tcb['command'] = lambda w=le: _qty.set(u"\u221E")
    tcb.grid(row=2, column=1, sticky='w')

    ### PRICE PER SKU ###
    le = Tix.LabelEntry(pogrid, labelside='left')
    le.label.configure(textvariable=_.loc(u"Price"), anchor='center')
    le.entry.configure(textvariable=_price, width=26)
    _price.set(order.price)
#    le.entry.configure(state='disabled')
    le.grid(row=3, rowspan=1, column=0, columnspan=2, sticky='w')

    ### TAX OPTION ###
    tcb = Tix.Checkbutton(pogrid, textvariable=_.loc(u"Apply tax?"),
                          bg='PaleGreen1', variable=_tax)
    _tax.set(order.applytax)
#    tcb.config(state='disabled')
    tcb.grid(row=4, column=0, columnspan=2)


    ### Co. branches, buyer/seller ###
    match_names = [order.seller, order.buyer]
    br = Tix.Select(pogrid, allowzero=False, radio=True, selectedbg=u'gold')
    br.label.config(textvariable=_.loc(u"Branch"))
    for branch in _.curr.cogroup.branches:
        br.add(branch.name.lower(), text=branch.name)
        if branch.name in match_names:
            br['value'] = branch.name.lower()
    br.grid(row=5, column=0, columnspan=2)

    tm = Tix.Select(pogrid, allowzero=False, radio=True, selectedbg=u'gold')
    tm.label.config(textvariable=_.loc(u"Taimau"))
    for branch in _.dbm.get_cogroup(u"台茂").branches:
        tm.add(branch.name.lower(), text=branch.name)
        if branch.name in match_names:
            tm['value'] = branch.name.lower()
    tm.grid(row=6, column=0, columnspan=2)

    ### PO NOTE ###
    le = Tix.LabelEntry(pogrid, labelside='left')
    le.label.configure(textvariable=_.loc(u"Note"), anchor='center')
    le.entry.configure(textvariable=_note, width=26)
    _note.set(order.ordernote)
    le.grid(row=50, rowspan=1, column=0, columnspan=10, sticky='ew')


    sep = Tix.Frame(pogrid, relief='ridge', height=8, bg="gray")
    sep.grid(row=90, column=0, columnspan=10, sticky='ew')


    # Button for archiving PO
    tb = Tix.Button(pogrid, textvariable=_.loc(u"\u2620 Archive this PO \u2620"),
                    bg="orange red",
                    command=lambda:inactivate_po(),
                    activebackground="orange red")
    tb.grid(row=99, column=2, columnspan=2, sticky='ew')

    # Button for submitting new PO
    tb = Tix.Button(pogrid, textvariable=_.loc(u"\u2692 Update Product Order (PO)"),
                    bg="lawn green",
                    command=lambda:make_po(),
                    activebackground="lime green")
    tb.grid(row=99, rowspan=2, column=0, columnspan=2, sticky='nsew')

    # Button for cancelling
    tb = Tix.Button(pogrid, textvariable=_.loc(u"\u26D4 Cancel"),
                    bg="tomato",
                    command=lambda:exit_win(),
                    activebackground="tomato")
    tb.grid(row=100, column=2, columnspan=2, sticky='ew')


    def make_po():
        if check_fields() == False:
            return
        ins = dict(qty=_qty.get(),
                   price=_price.get(),
                   orderID=_ponumber.get(),
                   ordernote=_note.get(),
                   applytax=_tax.get())
        if _qty.get() == u"\u221E":
            ins['qty'] = 1e10
        if tm['value'] != u'' and br['value'] != u'':
            ins['seller'] = tm['value'] if _.sc_mode == 'c' else br['value'].upper()
            ins['buyer'] = tm['value'] if _.sc_mode == 's' else br['value'].upper()
        if cal.selection:
            ins['orderdate'] = cal.selection

        if _.debug:
            print ins

        _.dbm.update_order(order.id, ins)

        exit_win()



    def exit_win():
        _.extwin.destroy()

#        # Repack PO list frame if swapping with PO creator
#        _.po_center.pack(**repack_info)

        refresh()


    def inactivate_po():
        _.dbm.update_order(order.id, dict(is_open=False))

        exit_win()



    def check_fields():
        if not _price.get().replace('.','',1).isdigit():
            return False
        if _qty.get() != u"\u221E" and not _qty.get().isdigit():
            return False
        if not tm['value']:
            return False
        if not br['value']:
            return False
        return True



if __name__ == '__main__':
    main()