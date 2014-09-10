#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Tix
from utils import date_picker


def main(_, refresh):
    """Window for adding a new purchase order (PO)."""

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
    _.extwin.title(u"{} {}".format(_.curr.cogroup.name, _.loc(u"+ PO", asText=True)))
    _.extwin.focus_set()

    center_pane = Tix.Frame(_.extwin)
    center_pane.pack(side='left', fill='both')


    #### VARIABLES FOR RECORD ENTRY ####
    ####################################
    _prodMPN = Tix.StringVar()
    _ponumber = Tix.StringVar()
    _qty = Tix.StringVar()
    _price = Tix.StringVar()
    _note = Tix.StringVar()
    _tax = Tix.BooleanVar()
    _prodMPN.trace('w', lambda a,b,c: _price.set(_.dbm.get_product_price(_prodMPN.get(), True)))


    #### Display products that can be ordered ####
    ##############################################


    tl = Tix.Label(center_pane, textvariable=_.loc(u"Select one product"))
    tl.pack(side='top')

    product_list = _.curr.cogroup.products
    if _.debug:
        print len(product_list), "products found for current company group."
    pobox = Tix.Frame(center_pane)
    pobox.pack(side='top', fill='x')
    TRB = lambda _text, _val: Tix.Radiobutton(pobox, text=_text, anchor='w',
                                        variable=_prodMPN,
                                        value=_val,
                                        indicatoron=False,
                                  bg="PaleTurquoise1",
                                  activebackground="PaleTurquoise1",
                                  selectcolor="gold")
    row = 0
    cols = 3
    for row, product in enumerate(product_list):
        _text = u"{}  ({})".format(product.label(), product.specs)
        #TODO: Add Product editing, to be discouraged! Warn!
        #Or just edit names, note and not the numbers related fields
        tb = TRB(_text, product.MPN)
        if product.discontinued:
            tb.config(state="disabled", bg="slate gray", relief="flat")
#                tb['command'] = pass
        tb.grid(row=row/cols, column=row%cols, sticky='ew')
#        _pBs.append(tb)

        #TODO: Product note as popup balloon
    #TODO: Add command for adding a product
    tb = Tix.Button(pobox, textvariable=_.loc(u"+ product"),
                    bg="lawn green",
#                    command=lambda:po.new(_),
                    activebackground="lime green")
    row += 1
    tb.grid(row=row/cols, column=row%cols, sticky='ew')



    sep = Tix.Frame(center_pane, relief='ridge', height=8, bg="gray")
    sep.pack(side='top', fill='x')


    pogrid = Tix.Frame(center_pane)
    pogrid.pack(side='top')
    ### DATE SELECTION ###
    # Order date: preselect today
    tl = Tix.Label(pogrid, textvariable=_.loc(u"Date of PO"))
    tl.grid(row=0, column=2, columnspan=2)
    cal = date_picker.Calendar(pogrid)
    cal.grid(row=1, rowspan=6, column=2, columnspan=2)

    # Due date: nothing preselected (omit this?)


    ### PO NUMBER ###
    le = Tix.LabelEntry(pogrid, labelside='left')
    le.label.configure(textvariable=_.loc(u"PO #"), anchor='center')
    le.entry.configure(textvariable=_ponumber, width=26)
    le.grid(row=1, rowspan=1, column=0, columnspan=2, sticky='w')

    ### PO QTY ###
    le = Tix.LabelEntry(pogrid, labelside='left')
    le.label.configure(textvariable=_.loc(u"Qty"), anchor='center')
    le.entry.configure(textvariable=_qty, width=20)
    le.grid(row=2, rowspan=1, column=0, columnspan=1, sticky='w')
    tcb = Tix.Button(pogrid, text=u'\u221E', bg='plum')
    tcb['command'] = lambda w=le: _qty.set(u"\u221E")
    tcb.grid(row=2, column=1, sticky='w')

    ### PRICE PER SKU ###
    le = Tix.LabelEntry(pogrid, labelside='left')
    le.label.configure(textvariable=_.loc(u"Price"), anchor='center')
    le.entry.configure(textvariable=_price, width=26)
    le.grid(row=3, rowspan=1, column=0, columnspan=2, sticky='w')

    ### TAX OPTION ###
    tcb = Tix.Checkbutton(pogrid, textvariable=_.loc(u"Apply tax?"),
                          bg='PaleGreen1', variable=_tax)
    tcb.invoke()
    tcb.grid(row=4, column=0, columnspan=2)


    ### Co. branches, buyer/seller ###
    br = Tix.Select(pogrid, allowzero=False, radio=True, selectedbg=u'gold')
    br.label.config(textvariable=_.loc(u"Branch"))
    for branch in _.curr.cogroup.branches:
        br.add(branch.name.lower(), text=branch.name)
    br.grid(row=5, column=0, columnspan=2)

    tm = Tix.Select(pogrid, allowzero=False, radio=True, selectedbg=u'gold')
    tm.label.config(textvariable=_.loc(u"Taimau"))
    for branch in _.dbm.get_cogroup(u"台茂").branches:
        tm.add(branch.name.lower(), text=branch.name)
    tm.grid(row=6, column=0, columnspan=2)

    ### PO NOTE ###
    le = Tix.LabelEntry(pogrid, labelside='left')
    le.label.configure(textvariable=_.loc(u"Note"), anchor='center')
    le.entry.configure(textvariable=_note, width=26)
    le.grid(row=50, rowspan=1, column=0, columnspan=10, sticky='ew')


    sep = Tix.Frame(pogrid, relief='ridge', height=8, bg="gray")
    sep.grid(row=99, column=0, columnspan=10, sticky='ew')


    # Button for submitting new PO
    tb = Tix.Button(pogrid, textvariable=_.loc(u"\u2692 Create Product Order (PO)"),
                    bg="lawn green",
                    command=lambda:make_po(),
                    activebackground="lime green")
    tb.grid(row=100, column=0, columnspan=2, sticky='ew')

    # Button for submitting new PO
    tb = Tix.Button(pogrid, textvariable=_.loc(u"\u26D4 Cancel"),
                    bg="tomato",
                    command=lambda:exit_win(),
                    activebackground="tomato")
    tb.grid(row=100, column=2, columnspan=2, sticky='ew')


    def make_po():
        #TODO: Select button values must be lower case, need to work around.
        if check_fields() == False:
            return
        ins = dict(MPN=_prodMPN.get(),
                       qty=_qty.get(),
                       price=_price.get(),
                       orderID=_ponumber.get(),
                       orderdate=cal.selection,
                       ordernote=_note.get(),
                       applytax=_tax.get())
        if _qty.get() == u"\u221E":
            ins['qty'] = 1e10
        ins['is_sale'] = True if _.sc_mode == 'c' else False
        ins['is_purchase'] = True if _.sc_mode == 's' else False
        ins['group'] = _.curr.cogroup.name
        ins['seller'] = tm['value'] if _.sc_mode == 'c' else br['value'].upper()
        ins['buyer'] = tm['value'] if _.sc_mode == 's' else br['value'].upper()

        if _.debug:
            print ins

        _.dbm.insert_order(ins)

        exit_win()



    def exit_win():
        _.extwin.destroy()

#        # Repack PO list frame if swapping with PO creator
#        _.po_center.pack(**repack_info)

        refresh()



    def check_fields():
        if not _prodMPN.get():
            return False
        if _qty.get() != u"\u221E" and not _qty.get().isdigit():
            return False
        if not _price.get().replace('.','',1).isdigit():
            return False
        if not cal.selection:
            return False
        if not tm['value']:
            return False
        if not br['value']:
            return False
        return True



if __name__ == '__main__':
    main()