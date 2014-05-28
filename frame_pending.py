#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Tkinter as Tk
import ttk
import datetime

import tablet_data_import as tablet


#===============================================================================
# METHODS
#===============================================================================
# Limit all records to the last 90 days (to save lookup and ordering time).
datelimit = datetime.date.today() - datetime.timedelta(90)

def get_pending_frame(frame, dmv2):

    q = dmv2.session.query(dmv2.Order)
    q = q.filter_by(is_sale=False)
    q = q.filter(dmv2.Order.duedate > datelimit)
    q = q.order_by(dmv2.Order.duedate)
    in_query = q

    q = dmv2.session.query(dmv2.Order)#.join("shipments")
    q = q.filter_by(is_sale=True)
    q = q.filter(dmv2.Order.duedate > datelimit)
    q = q.order_by(dmv2.Order.duedate)
    out_query = q

    q = dmv2.session.query(dmv2.Invoice)
    q = q.filter_by(paid=False)
    q = q.order_by(dmv2.Invoice.invoicedate)
    inv_query = q



    def refresh():
        orders = in_query.all()
        deliver_in_listbox.delete(0, 'end')
        invoice_in_listbox.delete(0, 'end')
        pay_in_listbox.delete(0, 'end')
        for order in orders[::-1]:
            if not order.all_shipped():
                txt = u'{0.month:>2}月{0.day:>2}日 : {1}|{2} : {3}{4} {5}'
                txt = txt.format(order.duedate,
                                 order.seller,
                                 order.buyer,
                                 order.totalskus-order.qty_shipped(),
                                 order.product.SKU if order.product.SKU != u'槽車' else order.product.UM,
                                 order.product.summary)
                deliver_in_listbox.insert(0, txt)
            if not order.all_invoiced():
                txt = u'{0.month:>2}月{0.day:>2}日 : {1}|{2} : {3}{4} {5}'
                txt = txt.format(order.duedate,
                                 order.seller,
                                 order.buyer,
                                 order.totalskus-order.qty_invoiced(),
                                 order.product.SKU if order.product.SKU != u'槽車' else order.product.UM,
                                 order.product.summary)
                if order.all_shipped():
                    txt += u'   \u26DF {}'.format(order.shipments[0].shipmentID)
                invoice_in_listbox.insert(0, txt)



        orders = out_query.all()
        deliver_out_listbox.delete(0, 'end')
        invoice_out_listbox.delete(0, 'end')
        pay_out_listbox.delete(0, 'end')
        for order in orders[::-1]:
            if not order.all_shipped():
                txt = u'{0.month:>2}月{0.day:>2}日 : {1}|{2} : {3}{4} {5}'
                txt = txt.format(order.duedate,
                                 order.seller,
                                 order.buyer,
                                 order.totalskus-order.qty_shipped(),
                                 order.product.SKU if order.product.SKU != u'槽車' else order.product.UM,
                                 order.product.summary)
                deliver_out_listbox.insert(0, txt)
            if not order.all_invoiced():
                txt = u'{0.month:>2}月{0.day:>2}日 : {1}|{2} : {3}{4} {5}'
                txt = txt.format(order.duedate,
                                 order.seller,
                                 order.buyer,
                                 order.totalskus-order.qty_invoiced(),
                                 order.product.SKU if order.product.SKU != u'槽車' else order.product.UM,
                                 order.product.summary)
                if order.all_shipped():
                    txt += u'   \u26DF {}'.format(order.shipments[0].shipmentID)
                invoice_out_listbox.insert(0, txt)

        for inv in inv_query.all()[::-1]:
            if inv.items[0].order.is_sale:
                txt = u'{0.month:>2}月{0.day:>2}日 : {1}|{2} : {3} : ${4}'
                txt = txt.format(inv.invoicedate,
                                 inv.items[0].order.seller,
                                 inv.items[0].order.buyer,
                                 inv.invoice_no,
                                 inv.taxtotal())
                pay_out_listbox.insert(0, txt)
            else:
                txt = u'{0.month:>2}月{0.day:>2}日 : {1}|{2} : {3} : ${4}'
                txt = txt.format(inv.invoicedate,
                                 inv.items[0].order.seller,
                                 inv.items[0].order.buyer,
                                 inv.invoice_no,
                                 inv.taxtotal())
                pay_in_listbox.insert(0, txt)
    #
    #==============================================================================
    # SET UP TABBED SECTIONS
    #==============================================================================
    #
    nb = ttk.Notebook(frame)

    refresh_button = Tk.Button(frame, text=u'Refresh Data', command=refresh)
    refresh_button.config(bg=u'gold', activebackground=u'black', activeforeground=u'white')
    refresh_button.pack(side="top", fill='x')

    # Order entry tab
    frame = ttk.Frame(nb)
    nb.add(frame, text=u'要交貨', padding=2)

    Tk.Label(frame, text=u'進貨預期', bg=u'wheat').pack(side="top", fill='x')
    deliver_in_listbox = Tk.Listbox(frame, height=10)
    deliver_in_listbox.pack(side="top",fill="both", expand=True)
    Tk.Label(frame, text=u'出貨預期', bg=u'wheat').pack(side="top", fill='x')
    deliver_out_listbox = Tk.Listbox(frame, height=10)
    deliver_out_listbox.pack(side="top",fill="both", expand=True)

    #---------------------------------------------------------
    frame = ttk.Frame(nb)
    nb.add(frame, text=u'要發票', padding=2)

    Tk.Label(frame, text=u'進貨: 需要發票', bg=u'wheat').pack(side="top", fill='x')
    invoice_in_listbox = Tk.Listbox(frame, height=10)
    invoice_in_listbox.pack(side="top",fill="both", expand=True)
    Tk.Label(frame, text=u'出貨: 需要發票', bg=u'wheat').pack(side="top", fill='x')
    invoice_out_listbox = Tk.Listbox(frame, height=10)
    invoice_out_listbox.pack(side="top",fill="both", expand=True)
    #---------------------------------------------------------------
    frame = ttk.Frame(nb)
    nb.add(frame, text=u'要付錢', padding=2)

    Tk.Label(frame, text=u'進貨: 需要付錢的發票', bg=u'wheat').pack(side="top", fill='x')
    pay_in_listbox = Tk.Listbox(frame, height=10)
    pay_in_listbox.pack(side="top",fill="both", expand=True)
    Tk.Label(frame, text=u'出貨: 需要付錢的發票', bg=u'wheat').pack(side="top", fill='x')
    pay_out_listbox = Tk.Listbox(frame, height=10)
    pay_out_listbox.pack(side="top",fill="both", expand=True)

    nb.pack(side=Tk.RIGHT, fill=Tk.BOTH, expand=Tk.Y, padx=2, pady=3)

    refresh()
    return refresh


def get_tablet_frame(frame, dmv2):


    q = tablet.session.query(tablet.AppRecord)
    q = q.filter_by(recordtype=u'incoming')
    q = q.order_by('date')
#    q = q.limit(100)
    in_query = q

    q = tablet.session.query(tablet.AppRecord)
    q = q.filter_by(recordtype=u'production')
    q = q.order_by('date')
#    q = q.limit(100)
    pro_query = q

    q = tablet.session.query(tablet.AppRecord)
    q = q.filter_by(recordtype=u'outgoing')
    q = q.order_by('date')
#    q = q.limit(100)
    out_query = q

    def refresh():
        try:
            tablet.pull_app_data()
        except:
            pass

        in_recs = in_query.all()
        incoming_listbox.delete(0, 'end')
        pro_recs = pro_query.all()
        production_listbox.delete(0, 'end')
        out_recs = out_query.all()
        outgoing_listbox.delete(0, 'end')

        template = u'{0.month:>2}月{0.day:>2}日 {1.hour:>2}:{1.minute:0>2}  : {2} {3:>5}{4}   {5:<12}   : {6}'
        for rec in in_recs:
            txt = template.format(rec.date,
                             rec.time if rec.time else type('',(),{'hour':0,'minute':0}),
                             rec.lottype,
                             rec.qty,
                             rec.um,
                             rec.product,
                             rec.recordnote)
            incoming_listbox.insert(0, txt)


        for rec in pro_recs:
            txt = template.format(rec.date,
                             rec.time if rec.time else type('',(),{'hour':0,'minute':0}),
                             rec.lottype,
                             rec.qty,
                             rec.um,
                             rec.product,
                             rec.recordnote)
            production_listbox.insert(0, txt)


        for rec in out_recs:
            txt = template.format(rec.date,
                             rec.time if rec.time else type('',(),{'hour':0,'minute':0}),
                             rec.lottype,
                             rec.qty,
                             rec.um,
                             rec.product,
                             rec.recordnote)
            outgoing_listbox.insert(0, txt)



    #==========================================================================
    # SET UP TABBED SECTIONS
    #==========================================================================
    nb = ttk.Notebook(frame)

    refresh_button = Tk.Button(frame, text=u'Refresh Data', command=refresh)
    refresh_button.config(bg=u'gold', activebackground=u'black', activeforeground=u'white')
    refresh_button.pack(side="top", fill='x')

    # Order entry tab
    frame = ttk.Frame(nb)
    nb.add(frame, text=u'進貨表', padding=2)

    incoming_listbox = Tk.Listbox(frame, height=10, font=("NSimSun 12"))
    incoming_listbox.pack(side="top",fill="both", expand=True)
    #---------------------------------------------------------------
    frame = ttk.Frame(nb)
    nb.add(frame, text=u'生產表', padding=2)

    production_listbox = Tk.Listbox(frame, height=10, font=("NSimSun 12"))
    production_listbox.pack(side="top",fill="both", expand=True)
    #---------------------------------------------------------------
    frame = ttk.Frame(nb)
    nb.add(frame, text=u'出貨表', padding=2)

    outgoing_listbox = Tk.Listbox(frame, height=10, font=("NSimSun 12"))
    outgoing_listbox.pack(side="top",fill="both", expand=True)

    nb.pack(side=Tk.RIGHT, fill=Tk.BOTH, expand=Tk.Y, padx=2, pady=3)

    refresh()
    return refresh
