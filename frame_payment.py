#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Tkinter as Tk
import tkMessageBox
import ttk
import tkFont


def format_pay_info(record, product):
    ddate = record.deliverydate if record.deliverydate else record.orderdate
    txt = u''
    txt += u'\u2691' if record.paymentID else u'\u2690'
    txt += u'\u2611' if record.paid else u'\u2610'
    txt += u'\u269A' if record.applytax else u'  '
    txt += u'  {}\u2794{}'.format(record.sellercompany, record.buyingcompany)
    txt += u'  {}/{}/{}'.format(ddate.year,ddate.month,ddate.day)
    txt += u'  {}'.format(product.inventory_name)
    txt += u'  ${}'.format(record.totalcharge)
    txt += u'  \u2116 {}'.format(record.paymentID)
    return txt
    
    
def set_payment_frame(frame, info):
    def refresh_frame(info):
        refresh_payment_list(info)
        refresh_info_box(info)
    info.method.refresh_pay_frame = refresh_frame

    def refresh_info_box(info):
        info.txt2.delete(1.0, Tk.END)
        info.txt2.tag_config("err", background="red", foreground="white")
        incoming = False if info.src == 'Sales' else True
        indexes = info.listbox.rec_paylist.curselection()
        IDs = [info.listbox.rec_paylist_IDs[i] for i in map(int,indexes)]
        print IDs
        txt = u''
        txt += u'Record IDs:{}\n'.format(repr(IDs))
        total = 0
        payIDs = set()
        paySellers = set()
        payBuyers = set()
        count = 0
        counttaxed = 0
        for id in IDs:
            rec = info.dm.get_record(id, incoming)
            total += int(rec.totalcharge)
            payIDs.add(rec.paymentID)
            paySellers.add(rec.sellercompany)
            payBuyers.add(rec.buyingcompany)
            count += 1
            if rec.applytax:
                counttaxed += 1
        payIDs = payIDs.pop() if len(payIDs) == 1 else u'[{}]'.format(u', '.join(payIDs))
        paySellers = paySellers.pop() if len(paySellers) == 1 else u'[{}]'.format(u', '.join(paySellers))
        payBuyers = payBuyers.pop() if len(payBuyers) == 1 else u'[{}]'.format(u', '.join(payBuyers))
        info.txt2.insert(Tk.END, u'Payment ID(s):')
        info.txt2.insert(Tk.END, u'{}'.format(payIDs), 'err' if u'[' in payIDs else '')
        info.txt2.insert(Tk.END, u'\nSeller ID(s):')
        info.txt2.insert(Tk.END, u'{}'.format(paySellers), 'err' if u'[' in paySellers else '')
        info.txt2.insert(Tk.END, u'\nBuyer ID(s):')
        info.txt2.insert(Tk.END, u'{}'.format(payBuyers), 'err' if u'[' in payBuyers else '')
        info.txt2.insert(Tk.END, u'\n\nTaxed items(\u269A): {}/{}'.format(counttaxed,count))
        info.txt2.insert(Tk.END, u'\nTotal charge: ${}'.format(total))
        #info.txt2.insert(Tk.END, txt, "err")
        
    def refresh_payment_list(info, refresh_index=[]):
        bgcolors = ['cyan','#9CF','#FCA','#AFC','#CCF']
        payColor = {'':'white'}
        if not isinstance(refresh_index, list):
            raise TypeError, "'refresh_index' should be an empty list or list of indices."
            return
        group_id = info.curr_company
        incoming = False if info.src == 'Sales' else True
        if len(refresh_index) > 0:
            for index in refresh_index:
                rec = dm.get_record(info.listbox.rec_paylist_IDs[index], incoming)
                prod = info.dm.get_product_data(rec.mpn)
                info.listbox.rec_paylist.delete(index)
                info.listbox.rec_paylist.insert(index, format_pay_info(rec, prod))
        else: #Refresh all
            info.listbox.rec_paylist.delete(0,Tk.END)
            reclist = info.dm.get_purchases(group_id) if incoming else info.dm.get_sales(group_id)
            # Maybe reverse it to put newest at the top            reclist = reclist[::-1]
            info.listbox.rec_paylist_IDs = [r.id for r in reclist]
            for i, r in enumerate(reclist):
                payID = r.paymentID
                prod = info.dm.get_product_data(r.mpn)
                info.listbox.rec_paylist.insert(i, format_pay_info(r, prod))
                if payID not in payColor:
                    #Assign a background color
                    payColor[payID] = bgcolors[0]
                    #Rotate color list
                    bgcolors = bgcolors[1:] + bgcolors[:1]
                sbg = 'red' if payID else None
                info.listbox.rec_paylist.itemconfig(i, bg=payColor[payID], selectbackground=sbg)
                info.listbox.rec_paylist.see(Tk.END)
    
    def edit_payment_group(info):
        try:
            if info.tempWindow.state() == 'normal':
                info.tempWindow.focus_set()
            return
        except:
            pass
        incoming = False if info.src == 'Sales' else True
        indexes = info.listbox.rec_paylist.curselection()
        IDs = [info.listbox.rec_paylist_IDs[i] for i in map(int,indexes)]
        payIDs = set()
        paySellers = set()
        payBuyers = set()
        taxedList = []
        for id in IDs:
            rec = info.dm.get_record(id, incoming)
            payIDs.add(rec.paymentID)
            paySellers.add(rec.sellercompany)
            payBuyers.add(rec.buyingcompany)
            taxedList.append(rec.applytax)
        payIDs = payIDs.pop() if len(payIDs) == 1 else u'[{}]'.format(u', '.join(payIDs))
        paySellers = paySellers.pop() if len(paySellers) == 1 else u'[{}]'.format(u', '.join(paySellers))
        payBuyers = payBuyers.pop() if len(payBuyers) == 1 else u'[{}]'.format(u', '.join(payBuyers))
        
        def submit_changes(info):
            is_confirmed = tkMessageBox.askokcancel('Confirm Data', 
                u'''Please confirm the group and branch ID names.''')
            
            if is_confirmed: 
                info.tempWindow.destroy()
                updates = dict(
                    paymentID=info.new_pay_id.get(),
                    sellercompany=info.new_seller.get(),
                    buyingcompany=info.new_buyer.get(),
                    applytax=info.applytax.get()
                )
                IDs = [info.listbox.rec_paylist_IDs[i] for i in map(int,indexes)]
                if incoming:
                    for id in IDs:
                        info.dm.update_purchase(id, updates)
                else:
                    for id in IDs:
                        info.dm.update_sale(id, updates)
                info.method.refresh_pay_frame(info)
            else:
                info.tempWindow.focus_set()
        
        info.tempWindow = Tk.Toplevel(width=500)
        info.tempWindow.title("Enter a payment ID")
        info.new_seller = Tk.StringVar()
        info.new_buyer = Tk.StringVar()
        info.new_pay_id = Tk.StringVar()
        
        ttk.Label(info.tempWindow, text=u"Seller").grid(row=0, column=0)
        ttk.Entry(info.tempWindow, textvariable=info.new_seller, width=20).grid(row=0, column=1)
        ttk.Label(info.tempWindow, text=u"Buyer").grid(row=1, column=0)
        ttk.Entry(info.tempWindow, textvariable=info.new_buyer, width=20).grid(row=1, column=1)
        ttk.Label(info.tempWindow, text=u"Payment ID").grid(row=2, column=0)
        ttk.Entry(info.tempWindow, textvariable=info.new_pay_id, width=20).grid(row=2, column=1)
        
        info.applytax = Tk.BooleanVar()
        Tk.Radiobutton(info.tempWindow, text="Tax", variable=info.applytax, value=True)\
                .grid(row=3,column=0)
        Tk.Radiobutton(info.tempWindow, text="No-Tax", variable=info.applytax, value=False)\
                .grid(row=3,column=1)
        
        info.new_seller.set(paySellers)
        info.new_buyer.set(payBuyers)
        info.new_pay_id.set(payIDs)
        info.applytax.set(True if True in taxedList else False)
        
        Tk.Button(info.tempWindow, text="Submit changes", command=lambda:submit_changes(info)).grid(row=4, column=0, columnspan=2)
        info.tempWindow.focus_set()
    
    
    info.txt2 = Tk.Text(frame, wrap=Tk.WORD, width=40, height=10)
    vscroll = ttk.Scrollbar(frame, orient=Tk.VERTICAL, command=info.txt2.yview)
    info.txt2['yscroll'] = vscroll.set
    vscroll.pack(side=Tk.RIGHT, fill=Tk.Y)
    info.txt2.pack(fill=Tk.BOTH, expand=Tk.Y)
    
    
    b = Tk.Button(frame, text=u"編輯上面所選擇", command=lambda:edit_payment_group(info))
    b.pack(side=Tk.BOTTOM, fill=Tk.X)
    scrollbar3 = Tk.Scrollbar(frame, orient=Tk.VERTICAL)
    info.listbox.rec_paylist = Tk.Listbox(frame, selectmode=Tk.MULTIPLE,
                         yscrollcommand=scrollbar3.set,
                         font=("Verdana", "14"), height=100, exportselection=0)
    info.listbox.rec_paylist.bind("<ButtonRelease-1>", lambda _:refresh_info_box(info))
    scrollbar3.config(command=info.listbox.rec_paylist.yview)
    scrollbar3.pack(side=Tk.RIGHT, fill=Tk.Y)
    info.listbox.rec_paylist.pack(side=Tk.TOP, fill=Tk.BOTH)
    
    refresh_payment_list(info)