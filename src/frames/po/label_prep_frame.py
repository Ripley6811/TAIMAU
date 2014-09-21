#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Methods for preparing and printing barrel labels with the TSC TTP-243E Plus
printer.

description

:REQUIRES:

:TODO:


"""
import Tix
import tkMessageBox
import datetime

from utils import print_labels


def main(_, shipmentItemID):

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

    _.extwin = Tix.Toplevel(_.parent)
    _.extwin.title(u"{} {}".format(_.curr.cogroup.name, _.loc(u"+ PO", asText=True)))
    _.extwin.geometry(u'+{}+{}'.format(_.parent.winfo_rootx()+100, _.parent.winfo_rooty()))
    _.extwin.focus_set()


    ship_rec = _.dbm.session.query(_.dbm.ShipmentItem).get(shipmentItemID)
    print repr(ship_rec)
    prod_rec = ship_rec.order.product
    print repr(prod_rec)



#    set_data = {}
    # Replace with 'lot', 'lot_start', 'lot_end', 'rt_no'

    # Set fields according to the "last use" data in Product.note field.
    # Then replace with data from Shipment.note field if it exists.
    if prod_rec.json():
        ASE_data = prod_rec.json()
        print 'JSON from product:', ASE_data
    else:
        ASE_data = {u'current_lot':u'', u'Expiration':u''}
#    try:
#        set_data = json.loads(shnote[shnote.index('{'):])
#    except:
#        pass

    svDOM = Tix.StringVar()
    svEXP = Tix.StringVar()


    ase_no = Tix.StringVar()
    if ship_rec.lot:
        ase_no.set(ship_rec.lot)
        print 'lot from ship_rec', ship_rec.lot
    else:
        print 'adding default current_lot number'
        ase_no.set(ASE_data.get(u'current_lot', u''))



    rt_no = Tix.StringVar()
    if ship_rec.rt_no:
        rt_no.set(ship_rec.rt_no)
    else:
        today = datetime.date.today()
        date_dic = {
            u'year' : str(today.year)[-1],
            u'month' : today.month,
            u'day' : today.day,
        }
        if date_dic['month'] == 10:
            date_dic['month'] = 'A'
        elif date_dic['month'] == 11:
            date_dic['month'] = 'B'
        elif date_dic['month'] == 12:
            date_dic['month'] = 'C'
        rt_no_text = u'{year}{month}{day:0>2}'.format(**date_dic)
        try:
            rt_no.set(u'{}{}'.format(rt_no_text, prod_rec.ASE_RT[4:]))
        except:
            rt_no.set(rt_no_text)


    exp_m = Tix.StringVar()
    exp_m.set(ASE_data.get(u'Expiration', u'12'))


    pF = Tix.StringVar()
    pL = Tix.StringVar()
    ase_no_group = Tix.StringVar()
    start_no = Tix.StringVar()

    Tix.Label(_.extwin, text=u'Date').grid(row=0,column=0)
    Tix.Label(_.extwin, text=u'Qty').grid(row=0,column=1)
    Tix.Label(_.extwin, text=u'Lot No').grid(row=0,column=2)
    Tix.Label(_.extwin, text=u'範圍').grid(row=0,column=3)
    Tix.Label(_.extwin, text=u'起始號碼').grid(row=0,column=4)
    Tix.Label(_.extwin, text=u'RT No').grid(row=0,column=5)
    Tix.Label(_.extwin, text=u'過期 (#月)').grid(row=0,column=6)
#    Tix.Label(_.extwin, text=u'開始號碼 (可略)').grid(row=0,column=4)
#    Tix.Label(_.extwin, text=u'停住號碼 (可略)').grid(row=0,column=5)

#    Tix.Entry(_.extwin, textvariable=pF).grid(row=10,column=4)
#    Tix.Entry(_.extwin, textvariable=pL).grid(row=10,column=5)

#        Tix.Label(info.labelWin, text=u'Start').grid(row=0,column=2)

    query = _.dbm.session.query(_.dbm.ShipmentItem)
    query = query.join(_.dbm.Shipment)
    query = query.order_by(_.dbm.Shipment.shipmentdate.desc())
    query = query.join(_.dbm.Order)
    query = query.filter_by(MPN=prod_rec.MPN)
    for i, hrec in enumerate(query.all()[:8][::-1]):
        if hrec.id == ship_rec.id:
            opts = dict(master=_.extwin, relief='sunken',
                        bg='moccasin', font=(_.font, 14, 'bold'))
            gopts = dict(row=i+1, sticky='nsew')
            Tix.Label(text=ship_rec.shipment.shipmentdate,  **opts).grid(column=0, **gopts)
            Tix.Label(text=ship_rec.qty, width=5,                    **opts).grid(column=1, **gopts)
            Tix.Label(textvariable=ase_no_group, width=12, anchor='w', **opts).grid(column=3, **gopts)
            opts = dict(master=_.extwin, bg='white', font=(_.font, 14, 'bold'))
            Tix.Entry(textvariable=ase_no, justify='right', width=12, **opts).grid(column=2, **gopts)
            Tix.Entry(textvariable=start_no, width=7,                **opts).grid(column=4, **gopts)
            Tix.Entry(textvariable=rt_no, justify='center', width=13, **opts).grid(column=5, **gopts)
            Tix.Entry(textvariable=exp_m, justify='center', width=7, **opts).grid(column=6, **gopts)
        else:
            opts = dict(master=_.extwin, relief='sunken', font=(_.font, 14))
            gopts = dict(row=i+1, sticky='nsew')
            Tix.Label(text=hrec.shipment.shipmentdate, **opts).grid(column=0, **gopts)
            Tix.Label(text=hrec.qty, **opts).grid(column=1, **gopts)
            Tix.Label(text=hrec.lot, anchor='e', **opts).grid(column=2, **gopts)
            Tix.Label(text=u'{:0>4}-{:0>4}'.format(hrec.lot_start, hrec.lot_end) if hrec.lot_start else u'', anchor='w', **opts).grid(column=3, **gopts)
            Tix.Label(text=hrec.lot_start, anchor='w', **opts).grid(column=4, **gopts)
            Tix.Label(text=hrec.rt_no, **opts).grid(column=5, **gopts)
            Tix.Label(text=hrec.order.product.json().get('Expiration',u'Unknown'), **opts).grid(column=6, **gopts)

    def set_group_nos(*args):
        # Set to the numbers recorded in shipment if any.
        if ship_rec.lot_start:
            start_no.set(ship_rec.lot_start)
            ase_no_group.set(u'{:0>4}-{:0>4}'.format(ship_rec.lot_start, ship_rec.lot_end))
            return
        # Otherwise create new set numbers.
        last_no = 0
        # If same lot continuation, pull last unit number.
        try:
            if ase_no.get() == ASE_data.get(u'current_lot', None):
                last_no = int(prod_rec.ASE_END)
        except ValueError:
            pass
        except TypeError:
            pass

        start_no.set(last_no + 1)
        begin = last_no + 1
        endno = last_no + ship_rec.qty
        ase_no_group.set(u'{:0>4}-{:0>4}'.format(begin, endno))

    def set_start(*args):
        # Ensure only uppercase letters and numbers are in entry field
        check_text = u''.join([ea for ea in ase_no.get().upper() if ea.isalnum()])
        if check_text != ase_no.get():
            ase_no.set(check_text)

        if ase_no.get() == ASE_data.get(u'current_lot', None):
            start_no.set( prod_rec.ASE_END + 1 )
        else:
            start_no.set( 1 )


    def set_range(*args):
        # Ensure only numbers are in entry field
        check_text = u''.join([ea for ea in start_no.get() if ea.isdigit()])
        if check_text != start_no.get():
            start_no.set(check_text)

        if start_no.get(): # Excludes blank entry
            begin = ship_rec.lot_start = int(start_no.get())
            endno = ship_rec.lot_end = begin + ship_rec.qty - 1
            ase_no_group.set(u'{:0>4}-{:0>4}'.format(begin, endno))

    start_no.trace('w', set_range)

    ase_no.trace('w', set_start)

    def set_rt(*args):
        # Ensure only uppercase letters and numbers are in entry field
        check_text = u''.join([ea for ea in rt_no.get().upper() if ea.isalnum()])
        if check_text != rt_no.get():
            rt_no.set(check_text)
        update_print_preview(*args)

    rt_no.trace('w', set_rt)

#    print_text = Tix.Text(_.extwin, width=30, height=10, font=(_.font, 14))
#    print_text.grid(row=9,column=0,columnspan=5, sticky='nsew')

    opts = dict(master=_.extwin, bg='moccasin', anchor='w')
    gopts = dict(sticky='ew')
    Tix.Label(text=u'Material name:', **opts).grid(row=11, column=0, **gopts)
    Tix.Label(text=u'P/N:', **opts).grid(row=12, column=0, **gopts)
    Tix.Label(text=u'LOT NO:', **opts).grid(row=13, column=0, **gopts)
    Tix.Label(text=u'Min Pkg No:', **opts).grid(row=14, column=0, **gopts)
    Tix.Label(text=u"Q'TY:", **opts).grid(row=15, column=0, **gopts)
    Tix.Label(text=u'Exp Date:', **opts).grid(row=16, column=0, **gopts)
    Tix.Label(text=u'DOM:', **opts).grid(row=17, column=0, **gopts)
    Tix.Label(text=u'RT NO:', **opts).grid(row=18, column=0, **gopts)

    Tix.Label(textvariable=ase_no, **opts).grid(row=14, column=1)
    Tix.Label(textvariable=ase_no_group, **opts).grid(row=14, column=2, **gopts)
    gopts = dict(sticky='ew', columnspan=2)
    Tix.Label(text=prod_rec.name, **opts).grid(row=11, column=1, **gopts)
    Tix.Label(text=prod_rec.ASE_PN, **opts).grid(row=12, column=1, **gopts)
    Tix.Label(textvariable=ase_no, **opts).grid(row=13, column=1, **gopts)
    Tix.Label(text=ship_rec.qty, **opts).grid(row=15, column=1, **gopts)
    Tix.Label(textvariable=svEXP, **opts).grid(row=16, column=1, **gopts)
    Tix.Label(textvariable=svDOM, **opts).grid(row=17, column=1, **gopts)
    Tix.Label(textvariable=rt_no, **opts).grid(row=18, column=1, **gopts)

    vals = type('Vals',(),{})()
    def update_print_preview(*args):
        vals.name = prod_rec.product_label
        if not vals.name:
            vals.name = prod_rec.inventory_name
        vals.PN = prod_rec.ASE_PN
        vals.LOT = ase_no.get()
        vals.LOT_err = u'' if len(vals.LOT) == 9 else u' (Error! Check Lot# length)'
        vals.ASE = ase_no.get() + ase_no_group.get()
        vals.ASE_err = u'' if len(vals.ASE) == 18 else u' (Error! Check range length "####-####")'
        vals.QTY = ship_rec.qty
        vals.EXP = "dddddddd"
        pdate = vals.LOT[1:7]
        try:
            dateDOM = datetime.date(2000+int(pdate[:2]), int(pdate[2:4]), int(pdate[4:6]))
            vals.DOM = "{d.year:04}{d.month:02}{d.day:02}".format(d=dateDOM)
        except:
            vals.DOM = u'Date is out of range!'
        vals.RT = rt_no.get()
        vals.RT_err = u'' if len(vals.RT) == 10 else u' (Error! Check RT# length)'
        try:
            Exp = int(exp_m.get())
            #dateDelta = datetime.timedelta((365/12)*Exp)
            ''' # The following is for an exact expiration date
            vals.DOM = "{0:04}{1:02}{2:02}".format(dateDOM.year, dateDOM.month, dateDOM.day)
            dateEXP = dateDOM + dateDelta
            vals.EXP = "{0:04}{1:02}{2:02}".format(dateEXP.year, dateEXP.month, dateEXP.day)
            '''
            inc_year = False
            if int((dateDOM.month-1 + Exp) / 12):
                inc_year = True
            vals.EXP = "{0:04}{1:02}{2:02}".format(
                    (dateDOM.year + int((dateDOM.month-1 + Exp) / 12)) if inc_year else dateDOM.year,
                    int((dateDOM.month-1 + Exp) % 12)+1,
                    dateDOM.day)
            svEXP.set(vals.EXP)
            svDOM.set(vals.DOM)
        except:
            pass#raw_input('Error converting expiration date. Using "dddddddd"\nHIT ENTER TO CONTINUE...')


#        text = u"Material name: {v.name}\nPN:   {v.PN}\nLOT NO:  {v.LOT}{v.LOT_err}\nMin Pkg No:  {v.ASE}{v.ASE_err}\nQ'TY:  {v.QTY}\nExp Date:  {v.EXP}\nDOM:  {v.DOM}\nRT NO:   {v.RT}{v.RT_err}".format(v=vals)
#        print_text.delete(1.0,"end")
#        print_text.insert("end",text)


        if vals.RT_err or vals.LOT_err or vals.ASE_err:
            pb.config(state="disabled")
            pb2.config(state="disabled")
        else:
            pb.config(state="normal")
            pb2.config(state="normal")

    ase_no_group.trace('w', update_print_preview)
    exp_m.trace('w', update_print_preview)


    def submit_print_request(DM=False):
        print u'{}{}'.format(ase_no.get(), ase_no_group.get())
#        ASE_data[u'ASE No'] = ase_no.get()
        ASE_data[u'current_lot'] = ase_no.get()
#        ASE_data[u'RT No'] = rt_no.get()
        ASE_data[u'Expiration'] = int(exp_m.get())

#        ship_xnote = {
#        }

        product = _.dbm.session.query(_.dbm.Product).get(prod_rec.MPN)
        product.json(ASE_data) #
        product.ASE_RT = rt_no.get()
        product.ASE_END = map(int, ase_no_group.get().split("-"))[-1]
        shipmentItem = _.dbm.session.query(_.dbm.ShipmentItem).get(ship_rec.id)
        shipmentItem.lot = ase_no.get()
        if start_no.get():
            shipmentItem.lot_start = int(start_no.get())
            shipmentItem.lot_end = int(start_no.get()) + shipmentItem.qty - 1
        shipmentItem.rt_no = rt_no.get()
        _.dbm.session.commit()

        _.extwin.destroy()

        #TODO: Actually print labels
        begin,endno = map(int, ase_no_group.get().split("-"))
        if pF.get().isdigit():
            begin = int(pF.get())
        if pL.get().isdigit():
            endno = int(pL.get())
        if print_labels.tsc == None:
            tkMessageBox.showerror(u'Printer not found', u'Printer could not be found.\nCheck that printer is installed and functioning.')
            return
        for i in range(begin,endno+1):
            ASE = u"{0}{1:04}".format(vals.LOT, i)
            try:
                if DM:
                    print_labels.TM_DMlabel(vals.name, vals.PN, vals.LOT, ASE,
                         vals.QTY, vals.EXP, vals.DOM, vals.RT)
                else:
                    print_labels.TM_label(vals.name, vals.PN, vals.LOT, ASE,
                         vals.QTY, vals.EXP, vals.DOM, vals.RT)
            except Exception as e:
                print u'Failed to print:', ASE, e

    pb = Tix.Button(_.extwin, text=u'Print Barcode Labels', command=submit_print_request,
                    bg=u'lawn green', activebackground=u'lime green')
    pb.grid(row=100, column=0, columnspan=3, sticky='nsew')
    pb2 = Tix.Button(_.extwin, text=u'Print Datamatrix Labels', command=lambda:submit_print_request(DM=True),
                    bg=u'lawn green', activebackground=u'lime green')
    pb2.grid(row=100, column=3, columnspan=3, sticky='nsew')

    set_group_nos()
    update_print_preview()



