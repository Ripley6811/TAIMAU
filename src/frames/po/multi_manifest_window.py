#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Tix
import tkMessageBox
from datetime import date


def main(_, order, refresh):
    """Displays a window for entering multiple shipments of one item.

    For getting 'caught-up' on processing manifests."""

    # Create new external window.
    if not _.getExtWin(_, co_name=_.curr.cogroup.name,
                       title=u"\u26DF \u26DF \u26DF {}".format(order.product.label())):
        return

    xwin = _.extwin

    """
    http://stackoverflow.com/questions/1450180/how-can-i-change-the-focus-from-one-text-box-to-another-in-python-tkinter
    """
    def focus_next(event):
        event.widget.tk_focusNext().focus()
        return("break")
    def focus_down(event):
        #TODO: Need to skip five widgets.
        event.widget.tk_focusNext()\
                    .tk_focusNext()\
                    .tk_focusNext()\
                    .tk_focusNext()\
                    .tk_focusNext()\
                    .tk_focusNext().focus()
        return("break")
    def focus_up(event):
        #TODO: Need to skip five widgets.
        event.widget.tk_focusPrev()\
                    .tk_focusPrev()\
                    .tk_focusPrev()\
                    .tk_focusPrev()\
                    .tk_focusPrev()\
                    .tk_focusPrev().focus()
        return("break")
    xwin.bind("<Return>", focus_next)
    xwin.bind("<Down>", focus_down)
    xwin.bind("<Up>", focus_up)

    nRecs = 12 # Max records that can be entered at one time.
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
    for i, each in enumerate([u'日期',u'出貨編號',u'件數',u'數量',
                              u'司機',u'車牌',u'備註']):
        tl=Tix.Label(xwin, text=each, **cell_config)
        tl.grid(row=0,column=i, columnspan=1, sticky='nsew')

    cc = dict(
        relief= 'sunken',
        font= (_.font, 18, u'bold',),
        bg= u'wheat', justify='center',
        width= 10,
    )
    for i in range(nRecs):
        dates.append(Tix.StringVar())
        Tix.Entry(xwin, textvariable=dates[i], **cc).grid(row=i+1, column=0, sticky='nsew')
        dates[i].set(u'{0.year}-{0.month}-'.format(date.today()))

        number.append(Tix.StringVar())
        Tix.Entry(xwin, textvariable=number[i], **cc).grid(row=i+1, column=1, sticky='nsew')

        qty.append(Tix.StringVar())
        Tix.Entry(xwin, textvariable=qty[i], **cc).grid(row=i+1, column=2, sticky='nsew')

        units.append(Tix.StringVar())
        Tix.Label(xwin, textvariable=units[i], **cc).grid(row=i+1, column=3, sticky='nsew')
        qty[i].trace('w', lambda a, b, c, index=i: update_units(a, b, index))

        driver.append(Tix.StringVar())
        Tix.Entry(xwin, textvariable=driver[i], **cc).grid(row=i+1, column=4, sticky='nsew')

        truck.append(Tix.StringVar())
        Tix.Entry(xwin, textvariable=truck[i], **cc).grid(row=i+1, column=5, sticky='nsew')
        truck[i].trace('w', lambda a, b, c, index=i: truck[index].set(truck[index].get().upper().replace('-','')[:8]))

        note.append(Tix.StringVar())
        Tix.Entry(xwin, textvariable=note[i], **cc).grid(row=i+1, column=6, sticky='nsew')

    def update_units(a, b, i):
        if _.debug:
            print a, b, i
            print type(i), i
        if qty[i].get().isdigit():
            units[i].set(int(qty[i].get())*order.product.units)
        else:
            units[i].set(0)



    # SUBMIT BUTTON
    tb = Tix.Button(xwin, textvariable=_.loc(u"\u2713 Submit"),
                    bg="lawn green",
                    command=lambda:submit(),
                    activebackground="lime green")
    tb.grid(row=1000, column=0, columnspan=4, sticky='nsew')

    # CANCEL BUTTON
    tb = Tix.Button(xwin, textvariable=_.loc(u"\u26D4 Cancel"),
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
        refresh()
        tkMessageBox.showinfo("Entries saved", "Entries saved to the database.")


