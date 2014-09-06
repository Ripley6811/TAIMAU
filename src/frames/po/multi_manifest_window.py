#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Tix
import tkMessageBox
from utils import date_picker
from datetime import date


def main(_, order):
    """Displays a window for entering multiple shipments of one item.

    For getting 'caught-up' on processing manifests."""


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
    _.extwin.title(u"{} {} {}".format(
                    _.curr.cogroup.name,
                    u"\u26DF \u26DF \u26DF",
                    order.product.label()
                    ))
    _.extwin.focus_set()
    x = _.extwin


    dates = []
    number = []
    qty = []
    units = []
    driver = []
    truck = []
    note = []

    cell_config = dict(
        font= (_.font, 15),
        bg= u'LightSteelBlue1',
        relief='raised',
    )
    for i, each in enumerate([u'日期',u'出貨編號',u'件數',u'數量',u'司機',u'車牌',u'備註']):
        tl=Tix.Label(x, text=each, **cell_config)
        tl.grid(row=0,column=i, columnspan=1, sticky='nsew')

    cc = dict(
        relief= 'sunken',
        font= (_.font, 18, u'bold',),
        bg= u'wheat', justify='center',
        width= 10,
    )
    for i in range(6):
        dates.append(Tix.StringVar())
        Tix.Entry(x, textvariable=dates[i], **cc).grid(row=i+1, column=0, sticky='nsew')
        dates[i].set(date.today())

        number.append(Tix.StringVar())
        Tix.Entry(x, textvariable=number[i], **cc).grid(row=i+1, column=1, sticky='nsew')

        qty.append(Tix.StringVar())
        Tix.Entry(x, textvariable=qty[i], **cc).grid(row=i+1, column=2, sticky='nsew')

        units.append(Tix.StringVar())
        Tix.Label(x, textvariable=units[i], **cc).grid(row=i+1, column=3, sticky='nsew')
        qty[i].trace('w', lambda a, b, c, index=i: update_units(a, b, index))

        driver.append(Tix.StringVar())
        Tix.Entry(x, textvariable=driver[i], **cc).grid(row=i+1, column=4, sticky='nsew')

        truck.append(Tix.StringVar())
        Tix.Entry(x, textvariable=truck[i], **cc).grid(row=i+1, column=5, sticky='nsew')

        note.append(Tix.StringVar())
        Tix.Entry(x, textvariable=note[i], **cc).grid(row=i+1, column=6, sticky='nsew')

    def update_units(a, b, i):
        print a, b, i
        print type(i), i
        units[i].set(int(qty[i].get())*order.product.units)




    # SUBMIT BUTTON
    tb = Tix.Button(x, textvariable=_.loc(u"\u2713 Submit"),
                    bg="lawn green",
                    command=lambda:submit(),
                    activebackground="lime green")
    tb.grid(row=1000, column=0, columnspan=4, sticky='nsew')

    # CANCEL BUTTON
    tb = Tix.Button(x, textvariable=_.loc(u"\u26D4 Cancel"),
                    bg="tomato",
                    command=lambda:exit_win(),
                    activebackground="tomato")
    tb.grid(row=1000, column=4, columnspan=6, sticky='nsew')

    def exit_win():
        _.extwin.destroy()

    def submit():
        '''Submit new shipments to the database.

        #TODO: Check for existing manifest numbers.'''
        for i in range(len(qty)):
            if qty[i].get():
                manifest = _.dbm.Shipment(
                    shipmentdate = date(*[int(a) for a in dates[i].get().split('-')]),
                    shipment_no = number[i].get(),
                    shipmentnote = note[i].get(),
                    driver = driver[i].get(),
                    truck = truck[i].get(),
                )
                item = _.dbm.ShipmentItem(
                    order = order,
                    shipment = manifest,

                    qty = qty[i].get(),
                )
                _.dbm.session.add(item)
        _.dbm.session.commit()

        exit_win()

        tkMessageBox.showinfo("Entries saved", "Entries saved to the database.")


