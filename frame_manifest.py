#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ttk
import Tkinter as Tk
from Tkinter import BOTTOM, TOP,  W, E, N, S, X
import tkMessageBox
import date_picker as dp
import datetime
import json
import print_labels as label_maker
from TM_forms import manifest_form
import Tix

#===============================================================================
# METHODS
#===============================================================================

def create_manifest_frame(frame, info):
    info.manifest = info.__class__()
    incoming = info.incoming = False if info.src == 'Sales' else True

    frameIn = ttk.Frame(frame)

    info.manifest.filterterm_SV = Tk.StringVar()

    tle = Tix.LabelEntry(frameIn, label=u'Filter:')
    tle.entry.configure(textvariable=info.manifest.filterterm_SV)
    tle.pack(side=TOP, fill=X)

    create_invoice_button = Tk.Button(frameIn, text=u'\u2696 創造發票 \u2696',
                                       bg=u'light salmon')
    create_invoice_button.pack(side=BOTTOM, fill=X)
    scrollbar2 = Tk.Scrollbar(frameIn, orient=Tk.VERTICAL)
    info.listbox.rec_manifest = Tk.Listbox(frameIn, selectmode=Tk.EXTENDED,
                         yscrollcommand=scrollbar2.set,
                         font=(info.settings.font, "12"), height=100, exportselection=0)
#    info.listbox.rec_manifest.bind("<Double-Button-1>", lambda _:copyrecord(info,True))
    scrollbar2.config(command=info.listbox.rec_manifest.yview)
    scrollbar2.pack(side=Tk.RIGHT, fill=Tk.Y)
    info.listbox.rec_manifest.pack(side=Tk.TOP, fill=Tk.BOTH)


    def create_invoice():
        indices = map(int, info.listbox.rec_manifest.curselection())
        so_tuples = [info.manifest.shipment_recs[i] for i in indices]

        create_invoice_form(so_tuples)


    create_invoice_button['command'] = create_invoice

    def refresh_manifest_listbox():
        '''Refresh the record lists for each frame.
        #TODO: Split up and put in their respective modules.
        '''
        # Add previous orders to order listbox
        info.listbox.rec_manifest.delete(0, Tk.END)

        # List of order summaries
        query = info.dmv2.session.query
        Shipment = info.dmv2.Shipment
        Order = info.dmv2.Order
        one_year = datetime.date.today() - datetime.timedelta(366)
        shipment_recs = query(Shipment, Order).join('order')\
                        .filter_by(group = info.curr_company)\
                        .filter(Shipment.shipmentdate > one_year)\
                        .order_by(Shipment.shipmentdate.desc()).all()
        info.manifest.shipment_recs = shipment_recs

        tmp = [rec[0].listbox_summary() for rec in shipment_recs]

        #TODO: Different colors for different products. Not necessary...
        for i, each in enumerate(tmp):
            shipped_color = dict(bg=u'SlateGray4', fg=u'gray79',
                                 selectbackground=u'tomato',
                                 selectforeground=u'black')
            no_ship_color = dict(bg=u'pale green', selectbackground=u'yellow',
                                 selectforeground=u'black')
            info.listbox.rec_manifest.insert(i, each)
            ins_colors = shipped_color if shipment_recs[i][1].all_paid() else no_ship_color
            info.listbox.rec_manifest.itemconfig(i, ins_colors)
    info.method.refresh_manifest_listbox = refresh_manifest_listbox

    def apply_list_filter(*args):
        lb = info.listbox.rec_manifest # Temp short name
        ft = info.manifest.filterterm_SV.get() # Temp short name
        for i in range(lb.size()):
            if ft in lb.get(i):
                lb.itemconfig(i, fg=u'black')
            else:
                lb.itemconfig(i, fg=u'gray72')

    info.manifest.filterterm_SV.trace('w',apply_list_filter)

    info.listbox.rec_manifest.bind("<Double-Button-1>", lambda _: display_manifest_for_edit(info))


    # Add right-click popup menu
    orderPopMenu = Tk.Menu(frameIn, tearoff=0)
    def delete_order(info):
        shiprec, _ = info.manifest.shipment_recs[info.listbox.rec_manifest.index(Tk.ACTIVE)]
        info.dmv2.session.query(info.dmv2.Shipment).filter_by(id=shiprec.id).delete()
        info.dmv2.session.commit()
        info.method.reload_orders(info)
        info.method.refresh_listboxes(info)
        info.method.refresh_manifest_listbox()
#        info.method.refresh_invoice_listbox()


    orderPopMenu.add_command(label=u'刪除', command=lambda: delete_order(info))

    def orderoptions(event):
        orderPopMenu.post(event.x_root, event.y_root)
    info.listbox.rec_manifest.bind("<Button-3>", orderoptions)



    frameIn.pack(fill=Tk.BOTH)

    def create_invoice_form(so_tuples):
        fi = Tix.Toplevel(width=700)
        fi.title(u"New Invoice Form")

        def date_picker():
            _=dp.Calendar(fi, textvariable=invoice_date_str)
            _.grid(row=0, column=0, rowspan=30, columnspan=6, sticky=W+E+N+S)

        def set_inv_number():
            try:
                if len(invoice_number_str.get()) <= 6 and u'[' not in seller_str.get():
                    code = info.invoices.codes.get(seller_str.get(), None)
                    if code != None:
                        invoice_number_str.set(code)
                    else:
                        query = info.dmv2.session.query(info.dmv2.Invoice) \
                                            .filter_by(seller=seller_str.get()) \
                                            .order_by('invoicedate')
                        invoiceset = query.all()[::-1]

                        for inv in invoiceset:
                            if inv.invoice_no[:2].isalpha():
                                invoice_number_str.set(inv.invoice_no[:6])
                                key = seller_str.get()
                                info.invoices.codes[key] = inv.invoice_no[:6]
                                break
            except:
                pass


        def inv_capitalize():
            #TODO: Auto-fill with plate by matching first letters.
            before = invoice_check_str.get()
            after = before.upper()
            if before != after:
                invoice_check_str.set(after)
            before = invoice_number_str.get()
            after = before.upper()
            if before != after:
                invoice_number_str.set(after)
        # Add order fields
        invoice_date_str = Tk.StringVar()
        invoice_number_str = Tk.StringVar()
        invoice_number_str.trace('w', lambda *args:inv_capitalize())
        invoice_note_str = Tk.StringVar()
        invoice_check_str = Tk.StringVar()
        invoice_check_str.trace('w', lambda *args:inv_capitalize())
        seller_str = Tk.StringVar()
        seller_str.trace('w', lambda *args:set_inv_number())
        buyer_str = Tk.StringVar()


        def submit_order():
            #TODO: Check if invoice number already used and confirm to attach to previous
            if u'[' in seller_str.get():
                tkMessageBox.showerror(u'Multiple sellers selected.', u'Please select one supplier for this invoice.')
                return
            if u'[' in buyer_str.get():
                tkMessageBox.showerror(u'Multiple buyers selected.', u'Please select one client for this invoice.')
                return

            if len(invoice_number_str.get()) <=2:
                okay = tkMessageBox.askokcancel(u'Invoice number warning', u'You did not enter an invoice number (發票號碼).\Submit anyway?')
                if not okay:
                    return

            for i, (srec, rec) in enumerate(so_tuples):
                # SET delivery date.
                idate = datetime.date(*map(int,invoice_date_str.get().split('-')))

                # Create dictionary for database insert.
                inv_dict = dict(
                    invoice_no= invoice_number_str.get(), #Same for all
                    seller= seller_str.get(),
                    buyer= buyer_str.get(),


                    invoicedate= idate, #Same for all

                    invoicenote= invoice_note_str.get(), #Same for all
#                    truck= invoice_truck_str.get(),
                )
                item_dict = dict(
                    invoice_no= invoice_number_str.get(), #Same for all

                    order_id= rec.id,

                    sku_qty= int(qty_SV[i].get()),
                )

                if len(invoice_number_str.get()) > 2:
                    key = seller_str.get()
                    info.invoices.codes[key]=invoice_number_str.get()[:2]

                # If check number is entered then update payment fields.
                if invoice_check_str.get():
                    inv_dict['check_no'] = invoice_check_str.get()
                    inv_dict['paid'] = True
                    #TODO: Allow user entry of date
                    inv_dict['paydate'] = datetime.date.today()


#                print inv_dict
                info.dmv2.append_invoice_item(inv_dict, item_dict)



            info.method.reload_orders(info)
            info.method.refresh_listboxes(info)
            info.method.refresh_manifest_listbox()
            info.method.refresh_invoice_listbox()
            fi.destroy()
        #END: submit_order()

        plength = len(so_tuples)
        qty_SV = [Tk.StringVar() for i in range(plength)]

#        fi = ttk.Frame(frame, height=6, borderwidth=10, relief=Tk.RAISED)
        separator = Tk.Frame(fi, height=6, borderwidth=6, relief=Tk.SUNKEN)
        separator.grid(row=0, column=0, columnspan=10, sticky=Tk.W+Tk.E, padx=5, pady=5)


        Tk.Label(fi, text=u'> \u26DF > \u26DF > \u26DF >').grid(row=90, column=0, columnspan=10)
        seller_menu = Tk.OptionMenu(fi, seller_str, None)
        seller_menu.grid(row=90, column=0, columnspan=2)
        seller_menu.config(bg=u'DarkOrchid4', fg=u'white')
        buyer_menu = Tk.OptionMenu(fi, buyer_str, u'台茂')
        buyer_menu.grid(row=90, column=2, columnspan=2)
        buyer_menu.config(bg=u'DarkOrchid4', fg=u'white')

        if info.incoming:
            seller_opts = [b.name for b in info.dmv2.branches(info.curr_company)]
            buyer_opts = [u'台茂',u'富茂',u'永茂']
        else:
            seller_opts = [u'台茂',u'富茂',u'永茂']
            buyer_opts = [b.name for b in info.dmv2.branches(info.curr_company)]
        smenu = seller_menu['menu']
        smenu.delete(0,Tk.END)
        bmenu = buyer_menu['menu']
        bmenu.delete(0,Tk.END)
        [smenu.add_command(label=choice, command=Tk._setit(seller_str, choice)) for choice in seller_opts]
        [bmenu.add_command(label=choice, command=Tk._setit(buyer_str, choice)) for choice in buyer_opts]
        try:
            seller_str.set(seller_opts[0])
            buyer_str.set(buyer_opts[0])
        except IndexError:
            tkMessageBox.showwarning(u'Company not in catalog.', u'Add this company to the catalog\nto avoid future errors.')


        Tk.Label(fi, text=u'發票日期').grid(row=1, column=2)
        Tk.Button(fi, textvariable=invoice_date_str, command=date_picker, bg='DarkGoldenrod1').grid(row=1, column=3)

        Tk.Label(fi, text=u'發票編號').grid(row=1, column=0)
        Tk.Entry(fi, textvariable=invoice_number_str).grid(row=1, column=1, sticky=Tk.W+Tk.E)

        Tk.Label(fi, text=u'Note 備註').grid(row=2, column=0)
        Tk.Entry(fi, textvariable=invoice_note_str).grid(row=2, column=1, columnspan=10, sticky=Tk.W+Tk.E)

        Tk.Label(fi, text=u'Check \u2116').grid(row=3, column=0)
        Tk.Entry(fi, textvariable=invoice_check_str).grid(row=3, column=1, sticky=Tk.W+Tk.E)

        separator = Tk.Frame(fi, height=6, borderwidth=6, relief=Tk.SUNKEN)
        separator.grid(row=6, column=0, columnspan=10, sticky=Tk.W+Tk.E, padx=5, pady=5)

        b = Tk.Button(fi, text=u'Submit Invoice (提交)', command=submit_order)
        b.grid(row=200, column=1, columnspan=2)
        b.config(bg='SpringGreen2')


        fi_items = Tk.Frame(fi)
        rowsize = "12"
        font = (info.settings.font, rowsize)
        for i, each in enumerate([u'品名',u'這次SKUs',u'剩下/总量(總額)']):#,u'全交了?'
            Tk.Label(fi_items, text=each, font=font).grid(row=0,column=i)

        for row, (rec, order) in enumerate(so_tuples):
            #TODO: Have button fill in data from last order, i.e. quantity, taxed.
            bw = Tk.Label(fi_items, text=order.product.summary, bg=u'cyan', font=font, anchor=W)
            bw.grid(row=row+10, column=0, sticky=W+E)

            ew = Tk.Entry(fi_items, textvariable=qty_SV[row], font=font, width=8, justify=Tk.CENTER)
            ew.grid(row=row+10,column=1)
            ew.config(selectbackground=u'LightSkyBlue1', selectforeground=u'black')
            qty_SV[row].set(rec.sku_qty)

            qty_to_invoice = order.qty_shipped()-order.qty_invoiced()
            text=u'{} / {} (${})'.format(qty_to_invoice,
                                         order.totalskus,
                                         order.qty_quote(qty_to_invoice))
            lw = Tk.Label(fi_items, font=font, text=text, justify=Tk.CENTER)
            lw.grid(row=row+10,column=2)#, sticky=Tk.W)
        fi_items.grid(row=100, column=0, columnspan=10)
        invoice_date_str.set(datetime.date.today())



def display_manifest_for_edit(info, shipment=None):
    #XXX: There's a chance that the ship_id might repeat, so check matching date as well.
    lindex = info.listbox.rec_manifest.index(Tk.ACTIVE)
    if not shipment:
        shipment = info.manifest.shipment_recs[lindex][0] #tuple(Shipment, Order)
    ship_id = shipment.shipmentID
#    ship_date = shipment.shipmentdate
#    query_id = shipment.id
    if ship_id in [None,u'None',u'']:
        tkMessageBox.showerror(u'Bad shipment number',u'Manifest number not found.\nShowing sample manifest for one product.')
#        return
        ship_id = u'NONE ENTERED'
        shipmentset = [shipment]
    else:
        shipmentset = info.dmv2.get_entire_shipment(shipment)
    print ship_id, repr(shipmentset)
    orderset = [info.dmv2.get_order(shi.order_id) for shi in shipmentset]

    #TIP: Uncomment below to restrict the popup window to one
#    try:
#        if info.shipmentWin.state() == 'normal':
#            info.shipmentWin.focus_set()
#        return
#    except:
#        pass



    info.shipmentWin = Tk.Toplevel(width=700)
    info.shipmentWin.title(u"Shipment: {}".format(ship_id))

    mani_font = (info.settings.font, "15")

    def print_labels(id):

        try:
            if info.labelWin.state() == 'normal':
                info.labelWin.focus_set()
            return
        except:
            pass


#        print id
        ship_rec = info.dmv2.session.query(info.dmv2.Shipment).get(id)
        prod_rec = ship_rec.order.product
#        print prod_rec

        info.labelWin = Tk.Toplevel(width=400)
        info.labelWin.title(u"Label: {}".format(ship_rec.id))



        ASE_data = {u'ASE No':u'', u'RT No':u'', u'Last No':0,u'Expiration':u''}
        set_data = {}
        pnote = prod_rec.note
        shnote = ship_rec.note

        # Set fields according to the "last use" data in Product.note field.
        # Then replace with data from Shipment.note field if it exists.
        try:
            ASE_data = json.loads(pnote[pnote.index('{'):])
        except:
            pass
        try:
            set_data = json.loads(shnote[shnote.index('{'):])
        except:
            pass


        ase_no = Tk.StringVar()
        try:
            ase_no.set(ASE_data[u'ASE No'])
        except:
            pass
        try:
            if set_data:
                ase_no.set(set_data[u'ASE No'])
        except:
            pass

        rt_no = Tk.StringVar()
        date_dic = {
            u'year' : str(ship_rec.shipmentdate.year)[-1],
            u'month' : ship_rec.shipmentdate.month,
            u'day' : ship_rec.shipmentdate.day,
        }
        if date_dic['month'] == 10:
            date_dic['month'] = 'A'
        elif date_dic['month'] == 11:
            date_dic['month'] = 'B'
        elif date_dic['month'] == 12:
            date_dic['month'] = 'C'
        rt_no_text = u'{0[year]}{0[month]}{0[day]:0>2}'.format(date_dic)
        try:
            rt_no.set(u'{}{}'.format(rt_no_text,ASE_data[u'RT No'][4:]))
        except:
            rt_no.set(rt_no_text)
        try:
            rt_no.set(set_data[u'RT No'])
        except:
            pass

        exp_m = Tk.StringVar()
        try:
            exp_m.set(ASE_data[u'Expiration'])
        except:
            pass
        try:
            exp_m.set(set_data[u'Expiration'])
        except:
            pass


        pF = Tk.StringVar()
        pL = Tk.StringVar()

        Tk.Label(info.labelWin, text=u'Lot No / 範圍').grid(row=0,column=0)
        Tk.Entry(info.labelWin, textvariable=ase_no).grid(row=0,column=1)
        Tk.Label(info.labelWin, text=u'RT No').grid(row=1,column=0)
        Tk.Entry(info.labelWin, textvariable=rt_no).grid(row=1,column=1)
        Tk.Label(info.labelWin, text=u'過期 (##月)').grid(row=2,column=0)
        Tk.Entry(info.labelWin, textvariable=exp_m).grid(row=2,column=1)
        Tk.Label(info.labelWin, text=u'開始號碼 (可略)').grid(row=3,column=0)
        Tk.Entry(info.labelWin, textvariable=pF).grid(row=3,column=1)
        Tk.Label(info.labelWin, text=u'停住號碼 (可略)').grid(row=4,column=0)
        Tk.Entry(info.labelWin, textvariable=pL).grid(row=4,column=1)

        ase_no_group = Tk.StringVar()
#        Tk.Label(info.labelWin, text=u'Start').grid(row=0,column=2)
        Tk.Entry(info.labelWin, textvariable=ase_no_group).grid(row=0,column=2)

        def set_group_nos(*args):
            # Set to the numbers recorded in shipment if any.
            try:
                if set_data[u'Set #s']:
                    ase_no_group.set(set_data[u'Set #s'])
                    return
            except:
                pass
            # Otherwise create new set numbers.
            last_no = 0
            try:
                if ase_no.get() == ASE_data[u'ASE No']:
                    last_no = ASE_data[u'Last No']
            except:
                pass
            begin = last_no + 1
            endno = last_no + ship_rec.sku_qty
            ase_no_group.set(u'{:0>4}-{:0>4}'.format(begin, endno))


        ase_no.trace('w', set_group_nos)

        print_text = Tk.Text(info.labelWin, width=30, height=8, font=mani_font)
        print_text.grid(row=9,column=0,columnspan=5)

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
            vals.QTY = ship_rec.sku_qty
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
            except:
                pass#raw_input('Error converting expiration date. Using "dddddddd"\nHIT ENTER TO CONTINUE...')


            text = u'品名: {v.name}\nPN:   {v.PN}\nLOT:  {v.LOT}{v.LOT_err}\nASE:  {v.ASE}{v.ASE_err}\nQTY:  {v.QTY}\nEXP:  {v.EXP}\nDOM:  {v.DOM}\nRT:   {v.RT}{v.RT_err}'.format(v=vals)
            print_text.delete(1.0,"end")
            print_text.insert("end",text)


            if vals.RT_err or vals.LOT_err or vals.ASE_err:
                pb.config(state="disabled")
            else:
                pb.config(state="normal")

        ase_no_group.trace('w', update_print_preview)
        exp_m.trace('w', update_print_preview)
        rt_no.trace('w', update_print_preview)



        def submit_print_request():
            print u'{}{}'.format(ase_no.get(), ase_no_group.get())
            ASE_data[u'ASE No'] = ase_no.get()
            ASE_data[u'Last No'] = int(ase_no_group.get()[-4:])
            ASE_data[u'RT No'] = rt_no.get()
            ASE_data[u'Expiration'] = int(exp_m.get())
            try:
                new_pnote = u'{}{}'.format(pnote[:pnote.index('{')],json.dumps(ASE_data))
            except ValueError:
                new_pnote = u'{}{}'.format(pnote,json.dumps(ASE_data))
            ship_xnote = {
                u'ASE No': ASE_data[u'ASE No'],
                u'RT No': ASE_data[u'RT No'],
                u'Set #s': ase_no_group.get(),
                u'Expiration': int(exp_m.get()),
            }
            info.dmv2.session.query(info.dmv2.Product).filter_by(MPN=prod_rec.MPN).update({u'note':new_pnote, u'summary':prod_rec.summary})
            info.dmv2.session.query(info.dmv2.Shipment).filter_by(id=ship_rec.id).update({u'note':json.dumps(ship_xnote)})
            info.dmv2.session.commit()

            info.labelWin.destroy()

            #TODO: Actually print labels
            begin,endno = map(int, ase_no_group.get().split("-"))
            if pF.get().isdigit():
                begin = int(pF.get())
            if pL.get().isdigit():
                endno = int(pL.get())
            for i in range(begin,endno+1):
                ASE = u"{0}{1:04}".format(vals.LOT, i)
                try:
                    label_maker.TM_label(vals.name, vals.PN, vals.LOT, ASE,
                             vals.QTY, vals.EXP, vals.DOM, vals.RT)
                except Exception as e:
                    print u'Failed to print:', ASE, e

        pb = Tk.Button(info.labelWin, text=u'PRINT', command=submit_print_request)
        pb.grid(row=10,column=0,columnspan=5)

        set_group_nos()
        update_print_preview()



    def submit_changes(info):
        #Check field entries

        info.shipmentWin.destroy()


    if info.src == 'Sales':
        for row, (shipment, order) in enumerate(zip(shipmentset, orderset)):
            b_text = u'Print Labels for {}'.format(shipment.order.product.label())
            b = Tk.Button(info.shipmentWin, text=b_text)
            b['command'] = lambda x=shipment.id: print_labels(x)
            b.grid(row=10+row, column=1, columnspan=4, sticky=Tk.W+Tk.E)

    b = Tk.Button(info.shipmentWin, text="Close window")
    b['command'] = lambda: submit_changes(info)
    b.grid(row=103,column=0,columnspan=6)


    info.testwin = Tk.Frame(info.shipmentWin)
    manifest_form(info.testwin, shipmentset)
    info.testwin.grid(row=0, column=0, columnspan=10)
#    mf.pack()

