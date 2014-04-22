#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
summary

description

:REQUIRES:
    - At least a *.xlsx file from the Google Drive master copy. *.xls are the
      edited database files created by this program.

:TODO: - Create applet for updating a companies information
    - Delete option for order records
    - Refactor and maybe try more lambda
    - Ensure the MPN is unique before adding.
    - Backup the order database.
    - Add reload database option to menus (for after editing excel)
    - Add various reports
    - Expected delivery date is first important date
    - Add transaction entered date (so that incorrect user dates are not lost)
    - Check that entered dates are close to current date and confirm if not
        To prevent wrong years when only month and day is entered.
    - Allow user to enter only month and day for dates
    - "File" add option to output database as Excel file
    - "File" add option to replace database from Excel file (backup old database for quick reversal)
    - Fix adding new products and make sure transactions enter correctly
    - Create an edit button that brings up a pop-up window showing old values and
        spaces for new values. Also a delete button (this way the delete is harder to get to
        and also confirm before delete)
    - Base "Open Orders" window on the manifest and "Not Paid" window on receipt formats.
    - "Submit" and "Clear" fields buttons or "Update" and "Cancel" buttons.
    - Show only company names that have entries. Add "show all" button to show a complete
        list of companies to choose from.
    - Add top level tab for 'pending' to see all undelivered and unpaid orders.
    - Add alternate record view for orders. Show latest of each product.


:AUTHOR: Jay W Johnson
:ORGANIZATION: Taimau Chemicals
:CONTACT: python@boun.cr
:SINCE: Sun Mar 02 15:14:32 2014
:VERSION: 0.2
"""
#===============================================================================
# PROGRAM METADATA
#===============================================================================
__author__ = 'Jay W Johnson'
__contact__ = 'python@boun.cr'
__copyright__ = ''
__license__ = ''
__date__ = 'Sun Mar 02 15:14:32 2014'
__version__ = '0.2'

#===============================================================================
# IMPORT STATEMENTS
#===============================================================================
import os  # os.walk(basedir) FOR GETTING DIR STRUCTURE
from tkFileDialog import askopenfilename, askopenfile
#from collections import namedtuple
import datetime
#import tables_company_data as tables
import Tkinter as Tk
import tkMessageBox
import ttk
import tkFont
#import google_spreadsheet as gs
import database_management as dm
import frame_company_editor

#===============================================================================
# METHODS
#===============================================================================

class Taimau_app(Tk.Tk):
    run_location = os.getcwd()



    def __init__(self, parent):

        Tk.Tk.__init__(self, parent)
#        self.wm_title('woot')
        self.parent = parent
        self.option_add("*Font", "Verdana 13")
        s = ttk.Style()
        s.configure('.', font=tkFont.Font(family="Verdana", size=-12))


        #
        # SET UP MENU BAR
        #

        menubar = Tk.Menu(self)


        # FILE MENU OPTIONS: LOAD, SAVE, EXIT...
        filemenu = Tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=None, state=Tk.DISABLED)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.endsession)
        menubar.add_cascade(label="File", menu=filemenu)



        # REPORT MENU OPTIONS
        reportmenu = Tk.Menu(menubar, tearoff=0)
        reportmenu.add_command(label="Report1", command=None, state=Tk.DISABLED)
        reportmenu.add_command(label="Report2", command=None, state=Tk.DISABLED)
        reportmenu.add_command(label="Report3", command=None, state=Tk.DISABLED)
        reportmenu.add_command(label="Report4", command=None, state=Tk.DISABLED)
        menubar.add_cascade(label=u"報告", menu=reportmenu)


#        # FONT MENU OPTIONS
#        def setFont():
#            self.option_add("*Font", fontsize.get())
#        fontmenu = Tk.Menu(menubar, tearoff=0)
#        fontsize = Tk.StringVar()
#        fontmenu.add_radiobutton(label="12", command=setFont, value='Verdana 12')
#        fontmenu.add_radiobutton(label="13", command=setFont, value='Verdana 13')
#        fontmenu.add_radiobutton(label="14", command=setFont, value='Verdana 14')
#        menubar.add_cascade(label=u"Font", menu=fontmenu)
#        fontsize.set('Verdana 12')


        # HELP MENU OPTIONS
        helpmenu = Tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label=u"關於", command=about)
        menubar.add_cascade(label="Help", menu=helpmenu)


        # SET AND SHOW MENU
        self.config(menu=menubar)
        self.geometry('1020x720')


#        mainframe = ttk.Frame(self)

        nb = ttk.Notebook()

        #TODO:---------- Add Purchases frame

        frame = ttk.Frame(nb)

        get_purchases_frame(frame)

        nb.add(frame, text='Purchases', underline=0)

#        nb.pack(side=Tk.RIGHT, fill=Tk.BOTH, expand=Tk.Y, padx=2, pady=3)

        #---------- Add Sales frame

        frame = ttk.Frame(nb)

        get_sales_frame(frame)

        nb.add(frame, text='Sales', underline=0)

#        nb.pack(side=Tk.RIGHT, fill=Tk.BOTH, expand=Tk.Y, padx=2, pady=3)

        #TODO:---------- Add Pending info frame

        frame = ttk.Frame(nb)

#        get_purchases_frame(frame)

        nb.add(frame, text='Pending', underline=2, state=Tk.DISABLED)

#        nb.pack(side=Tk.RIGHT, fill=Tk.BOTH, expand=Tk.Y, padx=2, pady=3)

        #TODO:---------- Add Company data edit frame

        frame = ttk.Frame(nb)

        frame_company_editor.get_company_editor(frame, dm)

        nb.add(frame, text='Catalog', underline=0)

#        nb.pack(side=Tk.RIGHT, fill=Tk.BOTH, expand=Tk.Y, padx=2, pady=3)


        #TODO:---------- Add Warehouse management frame
#        frame = ttk.Frame(nb)
#
#        txt = Tk.Text(frame, wrap=Tk.WORD, width=40, height=10)
#        vscroll = ttk.Scrollbar(frame, orient=Tk.VERTICAL, command=txt.yview)
#        txt['yscroll'] = vscroll.set
#        vscroll.pack(side=Tk.RIGHT, fill=Tk.Y)
#        txt.pack(fill=Tk.BOTH, expand=Tk.Y)
#
#        # add to notebook (underline = index for short-cut character)
#        nb.add(frame, text='Warehouse', underline=0)

        #--------- Set arrangement of notebook frames

        nb.pack(side=Tk.RIGHT, fill=Tk.BOTH, expand=Tk.Y, padx=2, pady=3)






    def endsession(self):
        self.quit()


def get_purchases_frame(frame):
    info = Info()
    info.src = "Purchases"
    info.curr_company = None
    info.edit_ID = None
    info.listbox = Info()
    info.button = Info()
    info.method = Info()


    #-------
    frame1 = ttk.Frame(frame)
    def showall_companies():
        info.listbox.companies.delete(0,Tk.END)
        info.listbox.companies.insert(0,*dm.company_list())

    b = Tk.Button(frame1, text="Show All", command=lambda:showall_companies())
    b.pack(side=Tk.BOTTOM, fill=Tk.X)
    scrollbar = Tk.Scrollbar(frame1, orient=Tk.VERTICAL)
    info.listbox.companies = Tk.Listbox(frame1, selectmode=Tk.BROWSE,
                         yscrollcommand=scrollbar.set,
                         width=8, font=("Verdana", "14"), exportselection=0)
    scrollbar.config(command=info.listbox.companies.yview)
#        scrollbar.grid(row=0,column=0, sticky=Tk.N+Tk.S)
#        info.listbox.companies.grid(row=0,column=1,sticky=Tk.N+Tk.S)
    scrollbar.pack(side=Tk.RIGHT, fill=Tk.Y)
    info.listbox.companies.pack(side=Tk.LEFT, fill=Tk.Y)
    info.listbox.companies.bind("<Double-Button-1>", lambda _:loadcompany(info,True))
    info.listbox.companies.insert(0,*dm.company_list_from_purchases())
    frame1.pack(side=Tk.LEFT, fill=Tk.Y, padx=2, pady=3)

    #
    #==============================================================================
    # SET UP TABBED SECTIONS
    #==============================================================================
    #
    info.record = {}
    nb = ttk.Notebook(frame)

    # Order entry tab
    frame = ttk.Frame(nb)

    orderlist = []


    frameIn = ttk.Frame(frame)
    b = Tk.Button(frameIn, text=u"編輯紀錄",
            command=lambda:copyrecord(info,True))
    b.pack(side=Tk.BOTTOM, fill=Tk.X)
#    b = Tk.Button(frameIn, text=u"編輯 (下劃線的記錄)",
#            command=lambda:copyrecord(info,True))
#    b.pack(side=Tk.BOTTOM, fill=Tk.X)
    scrollbar2 = Tk.Scrollbar(frameIn, orient=Tk.VERTICAL)
    info.listbox.rec_orders = Tk.Listbox(frameIn, selectmode=Tk.BROWSE,
                         yscrollcommand=scrollbar2.set,
                         font=("Verdana", "12"), height=100, exportselection=0)

    info.listbox.rec_orders.bind("<ButtonRelease-1>", lambda _:copyrecord(info,False))
#    info.listbox.rec_orders.bind("<Double-Button-1>", lambda _:copyrecord(info,True))
    scrollbar2.config(command=info.listbox.rec_orders.yview)
    scrollbar2.pack(side=Tk.RIGHT, fill=Tk.Y)
    info.listbox.rec_orders.pack(side=Tk.TOP, fill=Tk.BOTH)
    # Add right-click popup menu
    orderPopMenu = Tk.Menu(frame, tearoff=0)
    def refresh_listbox_item(id, index):
        recvals = dm.get_record(id, True)
        info.listbox.rec_orders.delete(index)
        info.listbox.rec_manifest.delete(index)
        info.listbox.rec_orders.insert(index, format_order_summary(recvals))
        info.listbox.rec_manifest.insert(index, format_order_summary(recvals))
        info.listbox.rec_orders.select_set(index)
        info.listbox.rec_orders.activate(index)

    def toggle_delivered(info):
        active_index = info.listbox.rec_orders.index(Tk.ACTIVE)
        rec_id = info.orderIDs[active_index]
        rec = dm.get_record(rec_id, incoming=True)
        updates = dict(delivered=False if rec['delivered'] else True)
        if u'.0' in rec['deliveryID']:
            updates['deliveryID'] = '{:0>7}'.format(int(float(rec['deliveryID'])))
        dm.update_purchase(rec_id, updates)
        refresh_listbox_item(rec_id, active_index)


    def toggle_paid(info):
        active_index = info.listbox.rec_orders.index(Tk.ACTIVE)
        rec_id = info.orderIDs[active_index]
        rec = dm.get_record(rec_id, incoming=True)
        updates = dict(paid=False if rec['paid'] else True)
        dm.update_purchase(rec_id, updates)
        refresh_listbox_item(rec_id, active_index)

    def delete_order(info):
        dm.delete_purchase(info.orderIDs[info.listbox.rec_orders.index(Tk.ACTIVE)])
        loadcompany(info)

    orderPopMenu.add_command(label=u"編輯 (下劃線的記錄)", command=lambda:copyrecord(info, editmode=True))
    orderPopMenu.add_command(label=u'切換:已交貨', command=lambda:toggle_delivered(info))
    orderPopMenu.add_command(label=u'切換:已支付', command=lambda:toggle_paid(info))
    orderPopMenu.add_command(label=u'刪除', command=lambda:delete_order(info))

    def orderoptions(event):
        orderPopMenu.post(event.x_root, event.y_root)
    info.listbox.rec_orders.bind("<Button-3>", orderoptions)
    info.listbox.rec_orders.bind("<F1>", lambda _:toggle_delivered(info))
    info.listbox.rec_orders.bind("<F2>", lambda _:toggle_paid(info))
    info.listbox.rec_orders.insert(0,*orderlist)



    frameIn2 = ttk.Frame(frame)

    r = 0 # Row placement
    info.record['parentcompany'] = Tk.StringVar()
    info.record['sellercompany'] = Tk.StringVar()
    info.branch_listpicker = Tk.OptionMenu(frameIn2, info.record['sellercompany'], '')
    info.branch_listpicker.grid(row=r, column=0, columnspan=2, sticky=Tk.W+Tk.E)
    info.branch_listpicker.configure(font=('Impact', 22))
    ttk.Label(frameIn2, text=u"\u21DB").grid(row=0, column=2) # '=>' arrow sign
    info.record['buyingcompany'] = Tk.StringVar()
    buycom = Tk.OptionMenu(frameIn2, info.record['buyingcompany'], u'台茂', u'富茂', u'永茂')
    info.record['buyingcompany'].set(u'台茂')
    buycom.grid(row=r, column=3, columnspan=2, sticky=Tk.W+Tk.E)
    buycom.configure(font=('Impact', 22))

    info.record['mpn'] = Tk.StringVar()


    def updateProduct():
        subcom_options = dm.get_product_summary(info.record['parentcompany'].get().encode('utf8'), incoming=True)
        if info.product_info.get() == u">>增加產品<<":
            # Auto prompt new product addition
            frame_company_editor.addProductWindow(info, dm, group_id=info.record['parentcompany'].get())
            return
        index = subcom_options.index(info.product_info.get())
        proddict = dm.get_products(info.record['parentcompany'].get(), incoming=True)[index]
        info.record['price'].set(0) #TODO: Change this to search for last price
        info.record['unitssku'].set(proddict.units)
        info.record['unitmeasurement'].set(proddict.UM)
        info.record['skudescription'].set(proddict.SKU)
        info.record['mpn'].set(proddict.MPN)
        info.product_info.set(subcom_options[index])
        if proddict.SKUpricing:
            info.priceby.set('SKU')
        else:
            info.priceby.set(proddict.UM)
        productnote.set(proddict.note)
        updateUnits() # Update calculations
    info.method.updateProduct = updateProduct



    r += 1

    ttk.Label(frameIn2, text=u"品名").grid(row=r,column=0)
    info.product_info = Tk.StringVar()
    info.product_info.trace("w", lambda name, index, mode, sv=info.product_info: updateProduct())
    info.record['productname'] = Tk.StringVar()
    info.record['unitssku'] = Tk.DoubleVar()
    info.record['unitmeasurement'] = Tk.StringVar()
    info.record['skudescription'] = Tk.StringVar()
    info.product_list = Tk.OptionMenu(frameIn2, info.product_info, '')
    info.product_list.grid(row=r, column=1, columnspan=4, sticky=Tk.W+Tk.E)

#    r += 1
#    ttk.Label(frameIn2, text=u"產品備註").grid(row=r,column=0)
    productnote = Tk.StringVar()
#    ttk.Label(frameIn2, textvariable=productnote).grid(row=r,column=1, columnspan=4)

    def updateUnits():
        if not info.record["price"].get():
            return
        try:
            info.record["totalskus"].set(int(info.record["totalskus"].get()))
        except:
            return
        info.record["totalunits"].set(info.record["totalskus"].get() * info.record["unitssku"].get())
        if info.priceby.get() == "SKU":
            info.record["pretaxtotal"].set(int(round(float(info.record["price"].get()) * float(info.record["totalskus"].get()))))
        else:
            info.record["pretaxtotal"].set(int(round(float(info.record["price"].get()) * float(info.record["totalunits"].get()))))
        if info.record["applytax"].get():
            taxamount.set(int(round(float(info.record["pretaxtotal"].get()) * 0.05)))
            info.record["totalcharge"].set(int(float(taxamount.get()) + float(info.record["pretaxtotal"].get())))
        else:
            taxamount.set(0)
            info.record["totalcharge"].set(info.record["pretaxtotal"].get())

    r += 1
    ttk.Label(frameIn2, text=u"單價").grid(row=r,column=0)
    info.record["price"] = Tk.StringVar()
    info.record["price"].trace("w", lambda name, index, mode, sv=info.record["price"]: updateUnits())
    priceField = ttk.Entry(frameIn2, textvariable=info.record["price"], width=8)
    priceField.grid(row=r, column=1, sticky=Tk.W)
    ttk.Label(frameIn2, text="/").grid(row=r,column=2)
    info.priceby = Tk.StringVar()
    unskulbl = ttk.Label(frameIn2, textvariable=info.priceby)
    unskulbl.grid(row=r,column=3, sticky=Tk.W)

    r += 1
    #TODO: Change to ttk.combobox filled with previously used values
    #XXX: Requires scanning through all orders
    ttk.Label(frameIn2, text=u"數量").grid(row=r,column=0)
    info.record["totalskus"] = Tk.IntVar()
    info.record["totalskus"].trace("w", lambda name, index, mode, sv=info.record["totalskus"]: updateUnits())
    ttk.Entry(frameIn2, textvariable=info.record["totalskus"], width=8)\
            .grid(row=r,column=1, columnspan=2, sticky=Tk.W)
#    ttk.Label(frameIn2, text=u"SKUs \u2248").grid(row=r,column=3, sticky=Tk.W)
    ttk.Label(frameIn2, textvariable=info.record['skudescription']).grid(row=r,column=2, sticky=Tk.W)
    info.record["totalunits"] = Tk.DoubleVar()
    ttk.Label(frameIn2, textvariable=info.record["totalunits"])\
            .grid(row=r,column=3, sticky=Tk.E)
    ttk.Label(frameIn2, textvariable=info.record["unitmeasurement"]).grid(row=r,column=4, sticky=Tk.W)
    info.record["totalunits"].set(0.0)

    r += 1
    r += 1
    ttk.Label(frameIn2, text=u"稅前總額").grid(row=r,column=0)
    info.record["pretaxtotal"] = Tk.IntVar()
    ttk.Label(frameIn2, textvariable=info.record["pretaxtotal"], justify=Tk.RIGHT)\
            .grid(row=r,column=1, sticky=Tk.E)
    ttk.Label(frameIn2, text=u"TWD").grid(row=r,column=3, sticky=Tk.W)

    r += 1
    ttk.Label(frameIn2, text=u"稅率").grid(row=r,column=0)
    info.record["applytax"] = Tk.BooleanVar()
    info.record["applytax"].trace("w", lambda name, index, mode, sv=info.record["applytax"]: updateUnits())
    taxamount = Tk.StringVar() # Calculated for user to see and not store
    ttk.Label(frameIn2, textvariable=taxamount, justify=Tk.RIGHT)\
            .grid(row=r,column=1, sticky=Tk.E)
    Tk.Checkbutton(frameIn2, text=u'适用税率 (5%)', variable=info.record["applytax"],
                   onvalue=True, offvalue=False).grid(row=r, column=3, sticky=Tk.W)
    info.record["applytax"].set(True)

    r += 1
    ttk.Separator(frameIn2, orient=Tk.HORIZONTAL).grid(row=r, column=1, sticky=Tk.W+Tk.E)

    r += 1
    ttk.Label(frameIn2, text=u"合計").grid(row=r,column=0)
    info.record["totalcharge"] = Tk.IntVar()
    info.record["totalcharge"].trace("w", lambda name, index, mode, sv=info.record["totalcharge"]: updateUnits())
    ttk.Label(frameIn2, textvariable=info.record["totalcharge"], justify=Tk.RIGHT)\
            .grid(row=r,column=1, sticky=Tk.E)
    ttk.Label(frameIn2, text=u"TWD").grid(row=r,column=3, sticky=Tk.W)



    ttk.Separator(frameIn2, orient=Tk.VERTICAL)\
            .grid(row=0, column=9, rowspan=20, sticky=Tk.N+Tk.S)

    for label in ['ordernote','orderID','deliverynote','deliveryID','paymentnote','paymentID']:
        info.record[label] = Tk.StringVar()

    ttk.Label(frameIn2, text=u"預定交貨日").grid(row=0,column=10, sticky=Tk.W)
    info.record['orderdate'] = Tk.StringVar()
    Tk.Entry(frameIn2, textvariable=info.record['orderdate'], width=12)\
            .grid(row=0, column=11, columnspan=1, sticky=Tk.W+Tk.E)


    ttk.Button(frameIn2, text=u'今天', command=lambda:info.record['orderdate'].set(datetime.date.today().strftime("%m/%d/%Y")))\
            .grid(row=0,column=12)

    ttk.Label(frameIn2, text=u"訂單號碼")\
            .grid(row=1, column=10, sticky=Tk.W)
    Tk.Entry(frameIn2, textvariable=info.record['orderID'])\
            .grid(row=1, column=11, columnspan=2, sticky=Tk.W+Tk.E)
    ttk.Button(frameIn2, text=u'\u226A刪除', command=lambda: info.record['orderID'].set(''))\
            .grid(row=1,column=13)
    ttk.Label(frameIn2, text=u"訂貨備註")\
            .grid(row=2, column=10, sticky=Tk.W)
#    Tk.Entry(frameIn2, textvariable=info.record['ordernote'], width=30)\
#            .grid(row=2, column=11, columnspan=4, sticky=Tk.W)
    info.orderNote = Tk.Text(frameIn2, width=30, height=2)
    info.orderNote.grid(row=2, column=11, rowspan=2, columnspan=3, sticky=Tk.W+Tk.E)

    ttk.Button(frameIn2, text=u'刪除\u226B', command=lambda: info.orderNote.delete(1.0,Tk.END))\
            .grid(row=3,column=10)
#    Tk.Label(frameIn2, textvariable=info.record['ordernote'], anchor=Tk.N+Tk.W, relief=Tk.RIDGE, width=40, wraplength=400, justify=Tk.LEFT)\
#            .grid(row=3, column=10, rowspan=1, columnspan=5, sticky=Tk.W+Tk.N+Tk.S)


    ttk.Button(frameIn2, text=u'明天', command=lambda:info.record['orderdate'].set((datetime.date.today() + datetime.timedelta(days=1)).strftime("%m/%d/%Y")))\
            .grid(row=0,column=13)

    ttk.Separator(frameIn2, orient=Tk.HORIZONTAL)\
        .grid(row=4, column=10, columnspan=4, sticky=Tk.W+Tk.E)

    ttk.Label(frameIn2, text=u"交貨日期").grid(row=5,column=10, sticky=Tk.W)
    info.record['deliverydate'] = Tk.StringVar()
    Tk.Entry(frameIn2, textvariable=info.record['deliverydate'], width=12)\
            .grid(row=5, column=11, columnspan=1, sticky=Tk.W+Tk.E)



    ttk.Button(frameIn2, text=u'今天', command=lambda:info.record['deliverydate'].set(datetime.date.today().strftime("%m/%d/%Y")))\
            .grid(row=5,column=12)

    info.record["delivered"] = Tk.BooleanVar()
    Tk.Checkbutton(frameIn2, text=u'已交', variable=info.record["delivered"],
                   onvalue=True, offvalue=False).grid(row=5, column=13, sticky=Tk.W)
    info.record["delivered"].set(0)

    ttk.Label(frameIn2, text=u"貨單編號")\
            .grid(row=6, column=10, sticky=Tk.W)
    Tk.Entry(frameIn2, textvariable=info.record['deliveryID'])\
            .grid(row=6, column=11, columnspan=2, sticky=Tk.W+Tk.E)
    ttk.Button(frameIn2, text=u'\u226A刪除', command=lambda: info.record['deliveryID'].set(''))\
            .grid(row=6, column=13)
    ttk.Label(frameIn2, text=u"交貨備註")\
            .grid(row=7, column=10, sticky=Tk.W)
    info.deliveryNote = Tk.Text(frameIn2, width=30, height=2)
    info.deliveryNote.grid(row=7, column=11, rowspan=2, columnspan=3, sticky=Tk.W+Tk.E)
    ttk.Button(frameIn2, text=u'刪除\u226B', command=lambda: info.deliveryNote.delete(1.0,Tk.END))\
            .grid(row=8, column=10)


    def submitentry(info):
        newentry = {}
        for key, strvar in info.record.iteritems():
            if 'date' in key:
                strdate = strvar.get()
                # Try different separators until one produces a list of len 2 or 3
                for sep in [None,'/','-','\\']:
                    if 2 <= len(strdate.split(sep)) <=3:
                        strdate = strdate.split(sep)
                        break
                try:
                    # If len three, assume date is given last, if two then use closest year
                    if len(strdate) == 3:
                        newentry[key] = datetime.date(int(strdate[2]),int(strdate[0]),int(strdate[1]))
                    else:
                        dnow = datetime.date.today()
                        dates = [datetime.date(dnow.year+x,int(strdate[0]),int(strdate[1])) for x in [-1,0,1]]
                        diff = [abs((x-dnow).days) for x in dates]
                        newentry[key] = dates[diff.index(min(diff))]
                except:
                    pass
            else:
                try:
                    newentry[key] = strvar.get()
                except:
                    print key
                    try:
                        newentry[key] = False if strvar.get() == "None" else True
                    except:
                        newentry[key] = False
        newentry['recorddate'] = datetime.datetime.now()
        newentry['ordernote'] = info.orderNote.get(1.0, Tk.END).strip()
        newentry['deliverynote'] = info.deliveryNote.get(1.0, Tk.END).strip()
#        newentry['mpn'] = info.product_info.get()
        newentry['paid'] = False
        # Make 'order date' and 'delivery date' the same if one is missing.
        if not newentry.get('orderdate'):
            newentry['orderdate'] = newentry.get('deliverydate')
        elif not newentry.get('deliverydate'):
            newentry['deliverydate'] = newentry.get('orderdate')
        if newentry.get('price') and newentry.get('orderdate') and newentry.get('mpn'):
            if info.edit_ID:
                dm.update_purchase(info.edit_ID, newentry)
                info.button.submit.config(state = Tk.NORMAL)
#                but_clear.config(state = Tk.NORMAL)
                info.button.update.config(state = Tk.DISABLED)
#                but_cancel.config(state = Tk.DISABLED)
                active_index = info.listbox.rec_orders.index(Tk.ACTIVE)
                refresh_listbox_item(info.edit_ID, active_index)
                info.edit_ID = None
            else:
                dm.insert_purchase(newentry)

                loadcompany(info)
        else:
            tkMessageBox.showinfo('還沒填好', '檢查:\n品名\n單價\n交貨日期')

    def cancel_entry(info):
        info.edit_ID = None
        info.button.submit.config(state = Tk.NORMAL)
        info.button.update.config(state = Tk.DISABLED)
        info.record['deliverydate'].set('')
        info.record['orderdate'].set('')
        info.record["totalskus"].set(0)
        info.record['delivered'].set(False)


    r += 1
    ttk.Separator(frameIn2, orient=Tk.HORIZONTAL)\
        .grid(row=r, column=1, sticky=Tk.W+Tk.E)
    r += 1
    ttk.Separator(frameIn2, orient=Tk.HORIZONTAL)\
        .grid(row=r, column=1, sticky=Tk.W+Tk.E)

    r += 20
    info.button.update = ttk.Button(frameIn2, text='UPDATE', underline=0, state=Tk.DISABLED, command=lambda:submitentry(info))
    info.button.update.grid(row=r, column=0, columnspan=20, sticky=Tk.W+Tk.E)
    r += 1
    but_cancel = ttk.Button(frameIn2, text='CANCEL', underline=0, state=Tk.ACTIVE, command=lambda:cancel_entry(info))
    but_cancel.grid(row=r, column=0, columnspan=20, sticky=Tk.W+Tk.E)
    r += 1
    info.button.submit = ttk.Button(frameIn2, text='SUBMIT NEW', underline=0, command=lambda:submitentry(info))
    info.button.submit.grid(row=r, column=0, columnspan=20, sticky=Tk.W+Tk.E)
#    but_clear = ttk.Button(frameIn2, text='CLEAR', underline=0, command=lambda:cancel_entry(info))
#    but_clear.grid(row=r, column=10, columnspan=5, sticky=Tk.W+Tk.E)

    frameIn2.pack(side=Tk.BOTTOM, fill=Tk.BOTH)
    frameIn.pack(fill=Tk.BOTH)


    nb.add(frame, text=u'訂單', padding=2)

#    nb.pack(side=Tk.RIGHT, fill=Tk.BOTH, expand=Tk.Y, padx=2, pady=3)



    #---------------------------------------------------------
    frame = ttk.Frame(nb)

    frameInTop = ttk.Frame(frame)
    scrollbarComp = Tk.Scrollbar(frameInTop, orient=Tk.VERTICAL)
    info.listbox.branches = Tk.Listbox(frameInTop, selectmode=Tk.BROWSE,
                         yscrollcommand=scrollbarComp.set,
                         font=("Verdana", "11"), height=5, exportselection=0)
    scrollbarComp.config(command=info.listbox.branches.yview)
    scrollbarComp.pack(side=Tk.RIGHT, fill=Tk.Y)
    info.listbox.branches.pack(side=Tk.TOP, fill=Tk.X)

    frameInTop.pack(side=Tk.TOP, fill=Tk.X)


#    nb.pack(side=Tk.RIGHT, fill=Tk.BOTH, expand=Tk.Y, padx=2, pady=3)

    #XXX: Scroll list with only items that have not been shipped
    #XXX: Show amount ordered but leave space for amount actually shipped
    #XXX: Able to add manifest number to all selected at once.


    def editrecord2(info):
        nb.select(0)
        print 'list', info.listbox.rec_manifest.index(Tk.ACTIVE), map(int, info.listbox.rec_manifest.curselection())
#        info.listbox.rec_orders.activate(map(int, info.listbox.rec_manifest.curselection())[0])
        info.listbox.rec_orders.activate(info.listbox.rec_manifest.index(Tk.ACTIVE))
        copyrecord(info, True)


    def createManifest(info):
        # Put company information in 'txt' box
        info.cotxt.config(state=Tk.NORMAL)
        info.cotxt.delete(1.0,Tk.END)
        co_info = dm.get_branches(info.curr_company.encode('utf8'))[info.listbox.branches.index(Tk.ACTIVE)]
        print 'co-info', co_info

        info.cotxt.insert(Tk.END, u'客戶名稱:{}\t\t統一編號:{}\n聯絡人:{}\t\t發票號碼:{}\n聯絡電話:{}\n送貨地址:{}'.format(
            co_info.id,
            co_info.tax_id,
            co_info.contact,
            '',
            co_info.phone,
            co_info.address_shipping if co_info.address_shipping else co_info.address_office,
        ))
        info.cotxt.config(state=Tk.DISABLED)

        info.manifestprods = [dm.get_purchases(info.curr_company)[x] for x in map(int, info.listbox.rec_manifest.curselection())]
        mani_txt = [u'', u'', u'', u'', u'']
        for rec in info.manifestprods:
            pr = dm.get_product_data(rec['mpn'])
            units = int(float(pr.units)) if float(pr.units).is_integer() else pr.units
            guige = u'{} {}/{}'.format(units,pr.UM,pr.SKU)
            if pr.SKU.strip() == u'槽車':
                guige = u'~ kg/槽車'
            totalunits = int(float(rec['totalunits'])) if float(rec['totalunits']).is_integer() else rec['totalunits']
            mani_txt[0] += u'{}\n'.format(pr.product_label)
            mani_txt[1] += u'{}\n'.format(guige)
            mani_txt[2] += u'{}\n'.format(rec.totalskus)
            mani_txt[3] += u'{}\n'.format(totalunits)
            mani_txt[4] += u'-{}\n'.format(rec.deliverynote)
#        mani_txt = mani_txt.replace(u' ',u'\u2003')
        for i in range(5):
            info.prodtxt[i].config(state=Tk.NORMAL)
            info.prodtxt[i].delete(1.0,Tk.END)
            info.prodtxt[i].insert(Tk.END, mani_txt[i], 'a' if i in [1,2,3] else None)
            info.prodtxt[i].config(state=Tk.DISABLED)


    frameIn = ttk.Frame(frame)
#    b = Tk.Button(frameIn, text="作為模板 (Copy to new entry)",
#            command=copyrecord)
#    b.pack(side=Tk.BOTTOM, fill=Tk.X)
#    b = Tk.Button(frameIn, text="Edit/Delete",
#            command=lambda:copyrecord(True))
#    b.pack(side=Tk.BOTTOM, fill=Tk.X)
    b = Tk.Button(frameIn, text=u"創造出貨單",
            command=lambda:createManifest(info))
    b.pack(side=Tk.BOTTOM, fill=Tk.X)
    scrollbar3 = Tk.Scrollbar(frameIn, orient=Tk.VERTICAL)
    info.listbox.rec_manifest = Tk.Listbox(frameIn, selectmode=Tk.MULTIPLE,
                         yscrollcommand=scrollbar3.set,
                         font=("Verdana", "12"), height=10, exportselection=0)
    scrollbar3.config(command=info.listbox.rec_manifest.yview)
    scrollbar3.pack(side=Tk.RIGHT, fill=Tk.Y)
    info.listbox.rec_manifest.pack(side=Tk.TOP, fill=Tk.X)
#    b = Tk.Button(frameIn, text="編輯 (下劃線的記錄)",
#            command=editrecord2)
#    b.pack(side=Tk.BOTTOM, fill=Tk.X)


    orderPopMenu2 = Tk.Menu(frameIn, tearoff=0)
    orderPopMenu2.add_command(label=u"編輯 (下劃線的記錄)", command=lambda:editrecord2(info))
    def orderoptions2(event):
        orderPopMenu2.post(event.x_root, event.y_root)
    info.listbox.rec_manifest.bind("<Button-3>", orderoptions2)

    frameIn.pack(side=Tk.TOP, fill=Tk.X)


    frameIn2 = ttk.Frame(frame)
    r = 0

    info.cotxt = Tk.Text(frameIn2, wrap=Tk.WORD, width=40, height=5, state=Tk.DISABLED)
    info.cotxt.grid(row=0,rowspan=5,column=0,columnspan=4, sticky=Tk.W)#
    labels = [u'品名', u'規格/包裝', u'件數', u'數量', u'運貨備註']
    info.prodtxt = []
    for i in range(5):
        adj = (0,2) if i==0 else (1,1)
        w = 10 if i in [1,2,3] else 22
        print adj
        ttk.Label(frameIn2, text=labels[i]).grid(row=5, column=i+adj[0], columnspan=adj[1])
        info.prodtxt.append(Tk.Text(frameIn2, wrap=Tk.WORD, width=w, height=6))
        info.prodtxt[i].grid(row=6,column=i+adj[0],columnspan=adj[1], sticky=Tk.W+Tk.E)#, font=("Courier", "12")
        info.prodtxt[i].config(state=Tk.DISABLED)
        info.prodtxt[i].tag_config('a', justify=Tk.RIGHT)

    ttk.Label(frameIn2, text=u"貨單日期:").grid(row=0,column=4)
    ttk.Label(frameIn2, text=u"貨單編號:").grid(row=1,column=4)
    company_data = Tk.StringVar()
    ttk.Label(frameIn2, textvariable=company_data).grid(row=0,column=5)
    new_delivery_date = Tk.StringVar()
    new_delivery_ID = Tk.StringVar()
    Tk.Entry(frameIn2, textvariable=new_delivery_date)\
            .grid(row=0, column=5, columnspan=2, sticky=Tk.W+Tk.E)
    Tk.Entry(frameIn2, textvariable=new_delivery_ID)\
            .grid(row=1, column=5, columnspan=2, sticky=Tk.W+Tk.E)

    def submitmanifest(info):
        update_dic = dict(delivered=True, deliveryID=new_delivery_ID.get())

        strdate = new_delivery_date.get()
        for sep in [None,'/','-','\\']:
            if 1 < len(strdate.split(sep)) < 4:
                strdate = strdate.split(sep)
                break
        try:
            if len(strdate) == 3:
                update_dic['deliverydate'] = datetime.date(int(strdate[2]),int(strdate[0]),int(strdate[1]))
            else:
                dnow = datetime.date.today()
                dates = [datetime.date(dnow.year+x,int(strdate[0]),int(strdate[1])) for x in [-1,0,1]]
                diff = [abs((x-dnow).days) for x in dates]
                update_dic['deliverydate'] = dates[diff.index(min(diff))]
        except:
            return
        # Send updates to SQL database
        [dm.update_purchase(mp['id'], update_dic) for mp in info.manifestprods]

        loadcompany(info)



    mani_submit = ttk.Button(frameIn2, text=u'提交出貨單 (變更日期與編號)', command=lambda:submitmanifest(info))
    mani_submit.grid(row=2, column=4, columnspan=3, sticky=Tk.W+Tk.E)


    frameIn2.pack(side=Tk.TOP, fill=Tk.X)


    # add to notebook (underline = index for short-cut character)
    nb.add(frame, text=u'出貨單', padding=2, state=Tk.NORMAL)




    #---------------------------------------------------------------
    frame = ttk.Frame(nb)

    txt2 = Tk.Text(frame, wrap=Tk.WORD, width=40, height=10)
    vscroll = ttk.Scrollbar(frame, orient=Tk.VERTICAL, command=txt2.yview)
    txt2['yscroll'] = vscroll.set
    vscroll.pack(side=Tk.RIGHT, fill=Tk.Y)
    txt2.pack(fill=Tk.BOTH, expand=Tk.Y)

    # add to notebook (underline = index for short-cut character)
    nb.add(frame, text=u'發票', padding=2, state=Tk.DISABLED)

    nb.pack(side=Tk.RIGHT, fill=Tk.BOTH, expand=Tk.Y, padx=2, pady=3)


def format_order_summary(val):
    prodtmp = dm.get_product(val['mpn'])
    if prodtmp[0] and prodtmp[0] != prodtmp[1]:
        prodtmp = u'{} (台茂:{})'.format(*prodtmp)
    else:
        prodtmp = prodtmp[1]
    tmp = u''
#            tmp += u'\u25C6' if val['delivered'] else u'\u25C7'
    tmp += u'\u26DF' if val['delivered'] else u'\u25C7'
    tmp += u'\u265B' if val['paid'] else u'\u25C7'
    if val['delivered']:
        if val['deliverydate']:
            tmp += (u"到期:{:>2}月{:>2}日{}年 \u273F ".format(
                val['deliverydate'].month,
                val['deliverydate'].day,
                val['deliverydate'].year).replace(' ','  ')
            )
        else:
            tmp += u"到期:  月  日   年 \u273F ".replace(' ','  ')
    else:
        try:
            tmp += (u"預期:{:>2}月{:>2}日{}年 \u273F ".format(
                val['orderdate'].month,
                val['orderdate'].day,
                val['orderdate'].year).replace(' ','  ')
            )
        except:
            tmp += u'  None Entered  \u273F '
    try:
        tmp += u"{0}\u2794{1} \u273F   {2}  \u223C {3}*{4}{5}={6} \u25CA ${7}".format(
            val['sellercompany'],#.split()[0],
            val['buyingcompany'],#.split()[0],
            prodtmp,
            val['totalskus'],
            int(int(val['totalunits'])/int(val['totalskus'])),
            u'u',
            int(val['totalunits']),
            int(val['price']) if float(val['price']).is_integer() else val['price'],
            val['mpn'])
    except:
        pass
    if val['deliveryID']:
        tmp += u"  貨單編號:{0}".format(
            val['deliveryID']
        )
    return tmp



def loadcompany(info, grab_index=False):
    '''This function runs when the order list is opened for the first time
    or when it needs to be reloaded to show updates.

    Use info.src for origin of call.

    grab_index = True updates the info.curr_company to list selection.
    grab_index = False (default) uses the company already stored in databook.
    '''
    if grab_index:
        info.curr_company = info.listbox.companies.get(Tk.ACTIVE)
    elif not info.curr_company:
        info.curr_company = info.listbox.companies.get(Tk.ACTIVE)

    info.cotxt.config(state=Tk.NORMAL)
    info.cotxt.delete(1.0, Tk.END)
    info.cotxt.config(state=Tk.DISABLED)
    for i in range(4):
        info.prodtxt[i].config(state=Tk.NORMAL)
        info.prodtxt[i].delete(1.0, Tk.END)
        info.prodtxt[i].config(state=Tk.DISABLED)


    info.orderIDs=[]

    # Add previous orders to order listbox
    info.listbox.rec_orders.delete(0,Tk.END)
    info.listbox.rec_manifest.delete(0,Tk.END)

    reclist = []
    if info.src == "Sales":
        reclist = dm.get_sales(info.curr_company)
    else:
        reclist = dm.get_purchases(info.curr_company)



    for i,val in enumerate(reclist):
        print 'val.id =', type(val.id), val.id
#            orderListIDs.append( val['id'] )
        info.orderIDs.append( val['id'] )
#            print info.orderIDs
#        prodtmp = dm.get_product(val['mpn'])
#        if prodtmp[0] and prodtmp[0] != prodtmp[1]:
#            prodtmp = u'{} (台茂:{})'.format(*prodtmp)
#        else:
#            prodtmp = prodtmp[1]
#        tmp = u''
##            tmp += u'\u25C6' if val['delivered'] else u'\u25C7'
#        tmp += u'\u26DF' if val['delivered'] else u'\u25C7'
#        tmp += u'\u265B' if val['paid'] else u'\u25C7'
#        if val['delivered']:
#            if val['deliverydate']:
#                tmp += (u"到期:{:>2}月{:>2}日{}年 \u273F ".format(
#                    val['deliverydate'].month,
#                    val['deliverydate'].day,
#                    val['deliverydate'].year).replace(' ','  ')
#                )
#            else:
#                tmp += u"到期:  月  日   年 \u273F ".replace(' ','  ')
#        else:
#            try:
#                tmp += (u"預期:{:>2}月{:>2}日{}年 \u273F ".format(
#                    val['orderdate'].month,
#                    val['orderdate'].day,
#                    val['orderdate'].year).replace(' ','  ')
#                )
#            except:
#                tmp += u'  None Entered  \u273F '
#        try:
#            tmp += u"{0}\u2794{1} \u273F   {2}  \u223C {3}*{4}{5}={6} \u25CA ${7}".format(
#                val['sellercompany'],#.split()[0],
#                val['buyingcompany'],#.split()[0],
#                prodtmp,
#                val['totalskus'],
#                int(int(val['totalunits'])/int(val['totalskus'])),
#                u'u',
#                int(val['totalunits']),
#                int(val['price']) if float(val['price']).is_integer() else val['price'],
#                val['mpn'])
#        except:
#            pass
#        if val['deliveryID']:
#            tmp += u"  貨單編號:{0}".format(
#                val['deliveryID']
#            )
        tmp = format_order_summary(val)

        info.listbox.rec_orders.insert(i,tmp)
        info.listbox.rec_manifest.insert(i,tmp)
    info.listbox.rec_orders.selection_set(Tk.END)
    info.listbox.rec_orders.see(Tk.END)
    info.listbox.rec_orders.activate(Tk.END)

#        info.listbox.rec_manifest.selection_set(Tk.END)
    info.listbox.rec_manifest.see(Tk.END)
#        info.listbox.rec_manifest.activate(Tk.END)

    info.listbox.branches.delete(0,Tk.END)
    [info.listbox.branches.insert(i,compsum) for i, compsum in enumerate(dm.get_branch_numbers(info.curr_company.encode('utf8')))]


    info.record['parentcompany'].set(info.curr_company)

    prod_options = dm.get_product_summary(info.curr_company.encode('utf8'),
                                          incoming = False if info.src=="Sales" else True)+[">>增加產品<<"]

    m = info.product_list.children['menu']
    m.delete(0,Tk.END)
    for opt in prod_options:
        m.add_command(label=opt, command=Tk._setit(info.product_info, opt))

    #Setting 'info.product_info' triggers update of GUI product information
    info.product_info.set(prod_options[0])

    # Display company branches in a dropdown menu
    subcom_options = dm.get_branch_summary(info.curr_company.encode('utf8'))
    m = info.branch_listpicker.children['menu']
    m.delete(0,Tk.END)
    if info.src == "Sales":
        for opt in subcom_options:
            m.add_command(label=opt, command=Tk._setit(info.record['buyingcompany'], opt))
        info.record['buyingcompany'].set(info.record['parentcompany'].get())
    else:
        for opt in subcom_options:
            m.add_command(label=opt, command=Tk._setit(info.record['sellercompany'], opt))
        info.record['sellercompany'].set(info.record['parentcompany'].get())

#        updateProduct() # Called when info.product_info changes
    info.record['orderdate'].set('')
    info.record['deliverydate'].set('')

    if info.listbox.rec_orders.size():
        copyrecord(info,False)


def copyrecord(info, editmode = False):
    incoming = False if info.src == "Sales" else True
    selected = int(info.listbox.rec_orders.curselection()[0])

    copydata = dm.get_record(info.orderIDs[selected], incoming=incoming)
    copydata = dict(zip(copydata.keys(), copydata.values()))

    #XXX: Switch buttons based on editing mode
    if editmode:
        info.button.submit.config(state = Tk.DISABLED)
#            but_clear.config(state = Tk.DISABLED)
        info.button.update.config(state = Tk.NORMAL)
#            but_cancel.config(state = Tk.NORMAL)
        info.edit_ID = copydata['id']
    else:
        info.button.submit.config(state = Tk.NORMAL)
#            but_clear.config(state = Tk.NORMAL)
        info.button.update.config(state = Tk.DISABLED)
#            but_cancel.config(state = Tk.DISABLED)
        info.edit_ID = None
    for key, val in copydata.iteritems():
        if key in info.record:
            info.record[key].set(val)
    # Fill in SKU count with Unit count if it doesn't exist
    try:
        info.record["totalskus"].set(copydata["totalskus"])
        info.record["totalskus"].get()
    except:
        info.record["totalskus"].set(copydata["totalunits"])

    info.record["applytax"].set(copydata["applytax"])

    prodInfo = dm.get_product_data(copydata["mpn"])

    if prodInfo:
        info.product_info.set(dm.formatrec(prodInfo))
        info.method.updateProduct()
    else:
        tkMessageBox.showerror("Product Not Found","Could not find this product in the listing.\nCheck the product listing and manually set the product name.")

    if not editmode:
        if info.record.get('orderdate'):
            info.record['orderdate'].set('')
        if info.record.get('deliverydate'):
            info.record['deliverydate'].set('')
        info.record['delivered'].set(False)
    else:
        try:
            info.record['orderdate'].set(copydata['orderdate'].strftime("%m/%d/%Y"))
        except:
            pass
        try:
            info.record['deliverydate'].set(copydata['deliverydate'].strftime("%m/%d/%Y"))
        except:
            pass
    info.record['price'].set(copydata['price'])

    info.orderNote.delete(1.0, Tk.END)
    info.orderNote.insert(Tk.END, copydata['ordernote'])
    info.deliveryNote.delete(1.0, Tk.END)
    info.deliveryNote.insert(Tk.END, copydata['deliverynote'])

class Info(object):
    # Container for passing state parameters
    # Separate into current record, product
    pass

def get_sales_frame(frame):
    info = Info()
    info.src = "Sales"
    info.curr_company = None
    info.edit_ID = None
    info.listbox = Info()
    info.button = Info()
    info.method = Info()


    #-------
    frame1 = ttk.Frame(frame)
    def showall_companies():
        info.listbox.companies.delete(0,Tk.END)
        info.listbox.companies.insert(0,*dm.company_list())

    b = Tk.Button(frame1, text="Show All", command=lambda:showall_companies())
    b.pack(side=Tk.BOTTOM, fill=Tk.X)
    scrollbar = Tk.Scrollbar(frame1, orient=Tk.VERTICAL)
    info.listbox.companies = Tk.Listbox(frame1, selectmode=Tk.BROWSE,
                         yscrollcommand=scrollbar.set,
                         width=8, font=("Verdana", "14"), exportselection=0)
    scrollbar.config(command=info.listbox.companies.yview)
#        scrollbar.grid(row=0,column=0, sticky=Tk.N+Tk.S)
#        info.listbox.companies.grid(row=0,column=1,sticky=Tk.N+Tk.S)
    scrollbar.pack(side=Tk.RIGHT, fill=Tk.Y)
    info.listbox.companies.pack(side=Tk.LEFT, fill=Tk.Y)
    info.listbox.companies.bind("<Double-Button-1>", lambda _:loadcompany(info,True))
    info.listbox.companies.insert(0,*dm.company_list_from_sales())
    frame1.pack(side=Tk.LEFT, fill=Tk.Y, padx=2, pady=3)

    #
    #==============================================================================
    # SET UP TABBED SECTIONS
    #==============================================================================
    #
    info.record = {}
    nb = ttk.Notebook(frame)

    # Order entry tab
    frame = ttk.Frame(nb)

    orderlist = []

#    def editrecord(rec_id):
#        global prodWin
#        prodWin = Tk.Toplevel(width=500)
#        rec = dm.get_record(rec_id)
##        prodWin.title(rec['parentcompany'] + u" : Edit")
#        prodWin.title(repr(rec.keys()))
##        print repr(companyName),
#
#
#        for each in rec:
#            print each
#        r = 0
#        mpntext = Tk.StringVar()
#        mpntext.set('')
#        ttk.Label(prodWin, text=u'MPN:').grid(row=r,column=0)
#        ttk.Entry(prodWin, text=u'MPN:').grid(row=r,column=0)
#        prodName = ttk.Label(prodWin, textvariable=mpntext, width=20)
#        prodName.grid(row=r,column=1, columnspan=2)
#        r += 1
#        prodName = Tk.StringVar()
#        prodName.trace('w',lambda name, index, mode:updateMPN())
#        ttk.Label(prodWin, text=u'Product:產品名稱(客戶)').grid(row=r,column=0)
#        ttk.Entry(prodWin, textvariable=prodName, width=20)\
#            .grid(row=r,column=1, columnspan=2)


    frameIn = ttk.Frame(frame)
    b = Tk.Button(frameIn, text=u"編輯紀錄",
            command=lambda:copyrecord(info,True))
    b.pack(side=Tk.BOTTOM, fill=Tk.X)
#    b = Tk.Button(frameIn, text=u"編輯 (下劃線的記錄)",
#            command=lambda:copyrecord(info,True))
#    b.pack(side=Tk.BOTTOM, fill=Tk.X)
    scrollbar2 = Tk.Scrollbar(frameIn, orient=Tk.VERTICAL)
    info.listbox.rec_orders = Tk.Listbox(frameIn, selectmode=Tk.BROWSE,
                         yscrollcommand=scrollbar2.set,
                         font=("Verdana", "12"), height=100, exportselection=0)

    info.listbox.rec_orders.bind("<ButtonRelease-1>", lambda _:copyrecord(info,False))
#    info.listbox.rec_orders.bind("<Double-Button-1>", lambda _:copyrecord(info,True))
    scrollbar2.config(command=info.listbox.rec_orders.yview)
    scrollbar2.pack(side=Tk.RIGHT, fill=Tk.Y)
    info.listbox.rec_orders.pack(side=Tk.TOP, fill=Tk.X)
    # Add right-click popup menu
    orderPopMenu = Tk.Menu(frame, tearoff=0)
    def refresh_listbox_item(id, index):
        recvals = dm.get_record(id, False)
        info.listbox.rec_orders.delete(index)
        info.listbox.rec_manifest.delete(index)
        info.listbox.rec_orders.insert(index, format_order_summary(recvals))
        info.listbox.rec_manifest.insert(index, format_order_summary(recvals))
        info.listbox.rec_orders.select_set(index)
        info.listbox.rec_orders.activate(index)

    def toggle_delivered(info):
        active_index = info.listbox.rec_orders.index(Tk.ACTIVE)
        rec_id = info.orderIDs[active_index]
        rec = dm.get_record(rec_id)
        updates = dict(delivered=False if rec['delivered'] else True)
        if u'.0' in rec['deliveryID']:
            updates['deliveryID'] = '{:0>7}'.format(int(float(rec['deliveryID'])))
        dm.update_sale(rec_id, updates)
        refresh_listbox_item(rec_id, active_index)
#        loadcompany(info)
#        info.listbox.rec_orders.select_clear(info.listbox.rec_orders.index(Tk.ACTIVE))
#        info.listbox.rec_orders.select_set(active_index)
#        info.listbox.rec_orders.activate(active_index)


    def toggle_paid(info):
        active_index = info.listbox.rec_orders.index(Tk.ACTIVE)
        rec_id = info.orderIDs[active_index]
        rec = dm.get_record(rec_id)
        updates = dict(paid=False if rec['paid'] else True)
        dm.update_sale(rec_id, updates)
        refresh_listbox_item(rec_id, active_index)
#        loadcompany(info)
#        info.listbox.rec_orders.select_clear(info.listbox.rec_orders.index(Tk.ACTIVE))
#        info.listbox.rec_orders.select_set(active_index)
#        info.listbox.rec_orders.activate(active_index)

    def delete_order(info):
        dm.delete_sale(info.orderIDs[info.listbox.rec_orders.index(Tk.ACTIVE)])
        loadcompany(info)

    orderPopMenu.add_command(label=u"編輯 (下劃線的記錄)", command=lambda:copyrecord(info, editmode=True))
    orderPopMenu.add_command(label=u'切換:已交貨', command=lambda:toggle_delivered(info))
    orderPopMenu.add_command(label=u'切換:已支付', command=lambda:toggle_paid(info))
    orderPopMenu.add_command(label=u'刪除', command=lambda:delete_order(info))

    def orderoptions(event):
        orderPopMenu.post(event.x_root, event.y_root)
    info.listbox.rec_orders.bind("<Button-3>", orderoptions)
    info.listbox.rec_orders.bind("<F1>", lambda _:toggle_delivered(info))
    info.listbox.rec_orders.bind("<F2>", lambda _:toggle_paid(info))
    info.listbox.rec_orders.insert(0,*orderlist)


    frameIn2 = ttk.Frame(frame)

    r = 0 # Row placement
#    ttk.Label(frameIn2, text=u'台茂', font=("Verdana", "15")).grid(row=r, column=0)
    info.record['parentcompany'] = Tk.StringVar()
#    parcom = ttk.Label(frameIn2, textvariable=info.record['parentcompany'], font=("Verdana", "15"))
#    parcom.grid(row=r, column=4)
    info.record['buyingcompany'] = Tk.StringVar()
    info.branch_listpicker = Tk.OptionMenu(frameIn2, info.record['buyingcompany'], '')
    info.branch_listpicker.grid(row=r, column=3, columnspan=2, sticky=Tk.W+Tk.E)
    info.branch_listpicker.configure(font=('Impact', 22))
    ttk.Label(frameIn2, text=u"\u21DB").grid(row=0, column=2) # '=>' arrow sign
    info.record['sellercompany'] = Tk.StringVar()
    buycom = Tk.OptionMenu(frameIn2, info.record['sellercompany'], u'台茂', u'富茂', u'永茂')
    info.record['sellercompany'].set(u'台茂')
    buycom.grid(row=r, column=0, columnspan=2, sticky=Tk.W+Tk.E)
    buycom.configure(font=('Impact', 22))

    info.record['mpn'] = Tk.StringVar()


    def updateProduct():
        subcom_options = dm.get_product_summary(info.record['parentcompany'].get().encode('utf8'))
        if info.product_info.get() == u">>增加產品<<":
            # Auto prompt new product addition
            frame_company_editor.addProductWindow(info, dm, group_id=info.record['parentcompany'].get())
            return
        index = subcom_options.index(info.product_info.get())
        proddict = dm.get_products(info.record['parentcompany'].get())[index]
        info.record['price'].set(0) #TODO: Change this to search for last price
        info.record['unitssku'].set(proddict.units)
        info.record['unitmeasurement'].set(proddict.UM)
        info.record['skudescription'].set(proddict.SKU)
        info.record['mpn'].set(proddict.MPN)
        info.product_info.set(subcom_options[index])
        if proddict.SKUpricing:
            info.priceby.set('SKU')
        else:
            info.priceby.set(proddict.UM)
        productnote.set(proddict.note)
        updateUnits() # Update calculations
    info.method.updateProduct = updateProduct



    r += 1

    ttk.Label(frameIn2, text=u"品名").grid(row=r,column=0)
    info.product_info = Tk.StringVar()
    info.product_info.trace("w", lambda name, index, mode, sv=info.product_info: updateProduct())
    info.record['productname'] = Tk.StringVar()
    info.record['unitssku'] = Tk.DoubleVar()
    info.record['unitmeasurement'] = Tk.StringVar()
    info.record['skudescription'] = Tk.StringVar()
    info.product_list = Tk.OptionMenu(frameIn2, info.product_info, '')
    info.product_list.grid(row=r, column=1, columnspan=4, sticky=Tk.W+Tk.E)

#    r += 1
#    ttk.Label(frameIn2, text=u"產品備註").grid(row=r,column=0)
    productnote = Tk.StringVar()
#    ttk.Label(frameIn2, textvariable=productnote).grid(row=r,column=1, columnspan=4)

    def updateUnits():
        if not info.record["price"].get():
            return
        try:
            info.record["totalskus"].set(int(info.record["totalskus"].get()))
        except:
            return
        info.record["totalunits"].set(info.record["totalskus"].get() * info.record["unitssku"].get())
        if info.priceby.get() == "SKU":
            info.record["pretaxtotal"].set(int(round(float(info.record["price"].get()) * float(info.record["totalskus"].get()))))
        else:
            info.record["pretaxtotal"].set(int(round(float(info.record["price"].get()) * float(info.record["totalunits"].get()))))
        if info.record["applytax"].get():
            taxamount.set(int(round(float(info.record["pretaxtotal"].get()) * 0.05)))
            info.record["totalcharge"].set(int(float(taxamount.get()) + float(info.record["pretaxtotal"].get())))
        else:
            taxamount.set(0)
            info.record["totalcharge"].set(info.record["pretaxtotal"].get())

    r += 1
    ttk.Label(frameIn2, text=u"單價").grid(row=r,column=0)
    info.record["price"] = Tk.StringVar()
    info.record["price"].trace("w", lambda name, index, mode, sv=info.record["price"]: updateUnits())
    priceField = ttk.Entry(frameIn2, textvariable=info.record["price"], width=8)
    priceField.grid(row=r, column=1, sticky=Tk.W)
    ttk.Label(frameIn2, text="/").grid(row=r,column=2)
    info.priceby = Tk.StringVar()
    unskulbl = ttk.Label(frameIn2, textvariable=info.priceby)
    unskulbl.grid(row=r,column=3, sticky=Tk.W)

    r += 1
    #TODO: Change to ttk.combobox filled with previously used values
    #XXX: Requires scanning through all orders
    ttk.Label(frameIn2, text=u"數量").grid(row=r,column=0)
    info.record["totalskus"] = Tk.IntVar()
    info.record["totalskus"].trace("w", lambda name, index, mode, sv=info.record["totalskus"]: updateUnits())
    ttk.Entry(frameIn2, textvariable=info.record["totalskus"], width=8)\
            .grid(row=r,column=1, columnspan=2, sticky=Tk.W)
#    ttk.Label(frameIn2, text=u"SKUs \u2248").grid(row=r,column=3, sticky=Tk.W)
    ttk.Label(frameIn2, textvariable=info.record['skudescription']).grid(row=r,column=2, sticky=Tk.W)
    info.record["totalunits"] = Tk.DoubleVar()
    ttk.Label(frameIn2, textvariable=info.record["totalunits"])\
            .grid(row=r,column=3, sticky=Tk.E)
    ttk.Label(frameIn2, textvariable=info.record["unitmeasurement"]).grid(row=r,column=4, sticky=Tk.W)
    info.record["totalunits"].set(0.0)

    r += 1
    r += 1
    ttk.Label(frameIn2, text=u"稅前總額").grid(row=r,column=0)
    info.record["pretaxtotal"] = Tk.IntVar()
    ttk.Label(frameIn2, textvariable=info.record["pretaxtotal"], justify=Tk.RIGHT)\
            .grid(row=r,column=1, sticky=Tk.E)
    ttk.Label(frameIn2, text=u"TWD").grid(row=r,column=3, sticky=Tk.W)

    r += 1
    ttk.Label(frameIn2, text=u"稅率").grid(row=r,column=0)
    info.record["applytax"] = Tk.BooleanVar()
    info.record["applytax"].trace("w", lambda name, index, mode, sv=info.record["applytax"]: updateUnits())
    taxamount = Tk.StringVar() # Calculated for user to see and not store
    ttk.Label(frameIn2, textvariable=taxamount, justify=Tk.RIGHT)\
            .grid(row=r,column=1, sticky=Tk.E)
    Tk.Checkbutton(frameIn2, text=u'适用税率 (5%)', variable=info.record["applytax"],
                   onvalue=True, offvalue=False).grid(row=r, column=3, sticky=Tk.W)
    info.record["applytax"].set(True)

    r += 1
    ttk.Separator(frameIn2, orient=Tk.HORIZONTAL).grid(row=r, column=1, sticky=Tk.W+Tk.E)

    r += 1
    ttk.Label(frameIn2, text=u"合計").grid(row=r,column=0)
    info.record["totalcharge"] = Tk.IntVar()
    info.record["totalcharge"].trace("w", lambda name, index, mode, sv=info.record["totalcharge"]: updateUnits())
    ttk.Label(frameIn2, textvariable=info.record["totalcharge"], justify=Tk.RIGHT)\
            .grid(row=r,column=1, sticky=Tk.E)
    ttk.Label(frameIn2, text=u"TWD").grid(row=r,column=3, sticky=Tk.W)



    ttk.Separator(frameIn2, orient=Tk.VERTICAL)\
            .grid(row=0, column=9, rowspan=20, sticky=Tk.N+Tk.S)

    for label in ['ordernote','orderID','deliverynote','deliveryID','paymentnote','paymentID']:
        info.record[label] = Tk.StringVar()

    ttk.Label(frameIn2, text=u"預定交貨日").grid(row=0,column=10, sticky=Tk.W)
    info.record['orderdate'] = Tk.StringVar()
    Tk.Entry(frameIn2, textvariable=info.record['orderdate'], width=12)\
            .grid(row=0, column=11, columnspan=1, sticky=Tk.W+Tk.E)


    ttk.Button(frameIn2, text=u'今天', command=lambda:info.record['orderdate'].set(datetime.date.today().strftime("%m/%d/%Y")))\
            .grid(row=0,column=12)

    ttk.Label(frameIn2, text=u"訂單號碼")\
            .grid(row=1, column=10, sticky=Tk.W)
    Tk.Entry(frameIn2, textvariable=info.record['orderID'])\
            .grid(row=1, column=11, columnspan=2, sticky=Tk.W+Tk.E)
    ttk.Button(frameIn2, text=u'\u226A刪除', command=lambda: info.record['orderID'].set(''))\
            .grid(row=1,column=13)
    ttk.Label(frameIn2, text=u"訂貨備註")\
            .grid(row=2, column=10, sticky=Tk.W)
#    Tk.Entry(frameIn2, textvariable=info.record['ordernote'], width=30)\
#            .grid(row=2, column=11, columnspan=4, sticky=Tk.W)
    info.orderNote = Tk.Text(frameIn2, width=30, height=2)
    info.orderNote.grid(row=2, column=11, rowspan=2, columnspan=3, sticky=Tk.W+Tk.E)

    ttk.Button(frameIn2, text=u'刪除\u226B', command=lambda: info.orderNote.delete(1.0,Tk.END))\
            .grid(row=3,column=10)
#    Tk.Label(frameIn2, textvariable=info.record['ordernote'], anchor=Tk.N+Tk.W, relief=Tk.RIDGE, width=40, wraplength=400, justify=Tk.LEFT)\
#            .grid(row=3, column=10, rowspan=1, columnspan=5, sticky=Tk.W+Tk.N+Tk.S)


    ttk.Button(frameIn2, text=u'明天', command=lambda:info.record['orderdate'].set((datetime.date.today() + datetime.timedelta(days=1)).strftime("%m/%d/%Y")))\
            .grid(row=0,column=13)

    ttk.Separator(frameIn2, orient=Tk.HORIZONTAL)\
        .grid(row=4, column=10, columnspan=4, sticky=Tk.W+Tk.E)

    ttk.Label(frameIn2, text=u"交貨日期").grid(row=5,column=10, sticky=Tk.W)
    info.record['deliverydate'] = Tk.StringVar()
    Tk.Entry(frameIn2, textvariable=info.record['deliverydate'], width=12)\
            .grid(row=5, column=11, columnspan=1, sticky=Tk.W+Tk.E)



    ttk.Button(frameIn2, text=u'今天', command=lambda:info.record['deliverydate'].set(datetime.date.today().strftime("%m/%d/%Y")))\
            .grid(row=5,column=12)

    info.record["delivered"] = Tk.BooleanVar()
    Tk.Checkbutton(frameIn2, text=u'已交', variable=info.record["delivered"],
                   onvalue=True, offvalue=False).grid(row=5, column=13, sticky=Tk.W)
    info.record["delivered"].set(0)

    ttk.Label(frameIn2, text=u"貨單編號")\
            .grid(row=6, column=10, sticky=Tk.W)
    Tk.Entry(frameIn2, textvariable=info.record['deliveryID'])\
            .grid(row=6, column=11, columnspan=2, sticky=Tk.W+Tk.E)
    ttk.Button(frameIn2, text=u'\u226A刪除', command=lambda: info.record['deliveryID'].set(''))\
            .grid(row=6, column=13)
    ttk.Label(frameIn2, text=u"交貨備註")\
            .grid(row=7, column=10, sticky=Tk.W)
    info.deliveryNote = Tk.Text(frameIn2, width=30, height=2)
    info.deliveryNote.grid(row=7, column=11, rowspan=2, columnspan=3, sticky=Tk.W+Tk.E)
    ttk.Button(frameIn2, text=u'刪除\u226B', command=lambda: info.deliveryNote.delete(1.0,Tk.END))\
            .grid(row=8, column=10)


    def submitentry(info):
        newentry = {}
        for key, strvar in info.record.iteritems():
            if 'date' in key:
                strdate = strvar.get()
                # Try different separators until one produces a list of len 2 or 3
                for sep in [None,'/','-','\\']:
                    if 2 <= len(strdate.split(sep)) <=3:
                        strdate = strdate.split(sep)
                        break
                try:
                    # If len three, assume date is given last, if two then use closest year
                    if len(strdate) == 3:
                        newentry[key] = datetime.date(int(strdate[2]),int(strdate[0]),int(strdate[1]))
                    else:
                        dnow = datetime.date.today()
                        dates = [datetime.date(dnow.year+x,int(strdate[0]),int(strdate[1])) for x in [-1,0,1]]
                        diff = [abs((x-dnow).days) for x in dates]
                        newentry[key] = dates[diff.index(min(diff))]
                except:
                    pass
            else:
                try:
                    newentry[key] = strvar.get()
                except:
                    print key
                    try:
                        newentry[key] = False if strvar.get() == "None" else True
                    except:
                        newentry[key] = False

        newentry['recorddate'] = datetime.datetime.now()
        newentry['ordernote'] = info.orderNote.get(1.0, Tk.END).strip()
        newentry['deliverynote'] = info.deliveryNote.get(1.0, Tk.END).strip()
#        newentry['mpn'] = info.product_info.get()
        newentry['paid'] = False
        # Make 'order date' and 'delivery date' the same if one is missing.
        if not newentry.get('orderdate'):
            newentry['orderdate'] = newentry.get('deliverydate')
        elif not newentry.get('deliverydate'):
            newentry['deliverydate'] = newentry.get('orderdate')
        if newentry.get('price') and newentry.get('orderdate') and newentry.get('mpn'):
            if info.edit_ID:
                dm.update_sale(info.edit_ID, newentry)
                active_index = info.listbox.rec_orders.index(Tk.ACTIVE)
                refresh_listbox_item(info.edit_ID, active_index)
            else:
                dm.insert_sale(newentry)

                loadcompany(info)

        else:
            tkMessageBox.showinfo('還沒填好', '檢查:\n品名\n單價\n交貨日期')

    def cancel_entry(info):
        info.edit_ID = None
        info.button.submit.config(state = Tk.NORMAL)
        info.button.update.config(state = Tk.DISABLED)
        info.record['deliverydate'].set('')
        info.record['orderdate'].set('')
        info.record["totalskus"].set(0)
        info.record['delivered'].set(False)


    r += 1
    ttk.Separator(frameIn2, orient=Tk.HORIZONTAL)\
        .grid(row=r, column=1, sticky=Tk.W+Tk.E)
    r += 1
    ttk.Separator(frameIn2, orient=Tk.HORIZONTAL)\
        .grid(row=r, column=1, sticky=Tk.W+Tk.E)

    r += 20
    info.button.update = ttk.Button(frameIn2, text='UPDATE', underline=0, state=Tk.DISABLED, command=lambda:submitentry(info))
    info.button.update.grid(row=r, column=0, columnspan=20, sticky=Tk.W+Tk.E)
    r += 1
    but_cancel = ttk.Button(frameIn2, text='CANCEL', underline=0, state=Tk.ACTIVE, command=lambda:cancel_entry(info))
    but_cancel.grid(row=r, column=0, columnspan=20, sticky=Tk.W+Tk.E)
    r += 1
    info.button.submit = ttk.Button(frameIn2, text='SUBMIT NEW', underline=0, command=lambda:submitentry(info))
    info.button.submit.grid(row=r, column=0, columnspan=20, sticky=Tk.W+Tk.E)
#    but_clear = ttk.Button(frameIn2, text='CLEAR', underline=0, command=lambda:cancel_entry(info))
#    but_clear.grid(row=r, column=10, columnspan=5, sticky=Tk.W+Tk.E)

    frameIn2.pack(side=Tk.BOTTOM, fill=Tk.BOTH)
    frameIn.pack(fill=Tk.BOTH)



    nb.add(frame, text=u'訂單', padding=2)

#    nb.pack(side=Tk.RIGHT, fill=Tk.BOTH, expand=Tk.Y, padx=2, pady=3)



    #---------------------------------------------------------
    frame = ttk.Frame(nb)

    frameInTop = ttk.Frame(frame)
    scrollbarComp = Tk.Scrollbar(frameInTop, orient=Tk.VERTICAL)
    info.listbox.branches = Tk.Listbox(frameInTop, selectmode=Tk.BROWSE,
                         yscrollcommand=scrollbarComp.set,
                         font=("Verdana", "11"), height=5, exportselection=0)
    scrollbarComp.config(command=info.listbox.branches.yview)
    scrollbarComp.pack(side=Tk.RIGHT, fill=Tk.Y)
    info.listbox.branches.pack(side=Tk.TOP, fill=Tk.X)

    frameInTop.pack(side=Tk.TOP, fill=Tk.X)


#    nb.pack(side=Tk.RIGHT, fill=Tk.BOTH, expand=Tk.Y, padx=2, pady=3)

    #XXX: Scroll list with only items that have not been shipped
    #XXX: Show amount ordered but leave space for amount actually shipped
    #XXX: Able to add manifest number to all selected at once.


    def editrecord2(info):
        nb.select(0)
        print 'list', info.listbox.rec_manifest.index(Tk.ACTIVE), map(int, info.listbox.rec_manifest.curselection())
#        info.listbox.rec_orders.activate(map(int, info.listbox.rec_manifest.curselection())[0])
        info.listbox.rec_orders.activate(info.listbox.rec_manifest.index(Tk.ACTIVE))
        copyrecord(info, True)


    def createManifest(info):
        # Put company information in 'txt' box
        info.cotxt.config(state=Tk.NORMAL)
        info.cotxt.delete(1.0,Tk.END)
        co_info = dm.get_branches(info.curr_company.encode('utf8'))[info.listbox.branches.index(Tk.ACTIVE)]
        print 'co-info', co_info

        info.cotxt.insert(Tk.END, u'客戶名稱:{}\t\t統一編號:{}\n聯絡人:{}\t\t發票號碼:{}\n聯絡電話:{}\n送貨地址:{}'.format(
            co_info.id,
            co_info.tax_id,
            co_info.contact,
            '',
            co_info.phone,
            co_info.address_shipping if co_info.address_shipping else co_info.address_office,
        ))
        info.cotxt.config(state=Tk.DISABLED)

        info.manifestprods = [dm.get_sales(info.curr_company)[x] for x in map(int, info.listbox.rec_manifest.curselection())]
        mani_txt = [u'', u'', u'', u'', u'']
        for rec in info.manifestprods:
            pr = dm.get_product_data(rec['mpn'])
            units = int(float(pr.units)) if float(pr.units).is_integer() else pr.units
            guige = u'{} {}/{}'.format(units,pr.UM,pr.SKU)
            if pr.SKU.strip() == u'槽車':
                guige = u'~ kg/槽車'
            totalunits = int(float(rec['totalunits'])) if float(rec['totalunits']).is_integer() else rec['totalunits']
            mani_txt[0] += u'{}\n'.format(pr.product_label)
            mani_txt[1] += u'{}\n'.format(guige)
            mani_txt[2] += u'{}\n'.format(rec.totalskus)
            mani_txt[3] += u'{}\n'.format(totalunits)
            mani_txt[4] += u'-{}\n'.format(rec.deliverynote)
#        mani_txt = mani_txt.replace(u' ',u'\u2003')
        for i in range(5):
            info.prodtxt[i].config(state=Tk.NORMAL)
            info.prodtxt[i].delete(1.0,Tk.END)
            info.prodtxt[i].insert(Tk.END, mani_txt[i], 'a' if i in [1,2,3] else None)
            info.prodtxt[i].config(state=Tk.DISABLED)


    frameIn = ttk.Frame(frame)
#    b = Tk.Button(frameIn, text="作為模板 (Copy to new entry)",
#            command=copyrecord)
#    b.pack(side=Tk.BOTTOM, fill=Tk.X)
#    b = Tk.Button(frameIn, text="Edit/Delete",
#            command=lambda:copyrecord(True))
#    b.pack(side=Tk.BOTTOM, fill=Tk.X)
    b = Tk.Button(frameIn, text=u"創造出貨單",
            command=lambda:createManifest(info))
    b.pack(side=Tk.BOTTOM, fill=Tk.X)
    scrollbar3 = Tk.Scrollbar(frameIn, orient=Tk.VERTICAL)
    info.listbox.rec_manifest = Tk.Listbox(frameIn, selectmode=Tk.MULTIPLE,
                         yscrollcommand=scrollbar3.set,
                         font=("Verdana", "12"), height=10, exportselection=0)
    scrollbar3.config(command=info.listbox.rec_manifest.yview)
    scrollbar3.pack(side=Tk.RIGHT, fill=Tk.Y)
    info.listbox.rec_manifest.pack(side=Tk.TOP, fill=Tk.X)
#    b = Tk.Button(frameIn, text="編輯 (下劃線的記錄)",
#            command=editrecord2)
#    b.pack(side=Tk.BOTTOM, fill=Tk.X)


    orderPopMenu2 = Tk.Menu(frameIn, tearoff=0)
    orderPopMenu2.add_command(label=u"編輯 (下劃線的記錄)", command=lambda:editrecord2(info))
    def orderoptions2(event):
        orderPopMenu2.post(event.x_root, event.y_root)
    info.listbox.rec_manifest.bind("<Button-3>", orderoptions2)

    frameIn.pack(side=Tk.TOP, fill=Tk.X)


    frameIn2 = ttk.Frame(frame)
    r = 0

    info.cotxt = Tk.Text(frameIn2, wrap=Tk.WORD, width=40, height=5, state=Tk.DISABLED)
    info.cotxt.grid(row=0,rowspan=5,column=0,columnspan=4, sticky=Tk.W)#
    labels = [u'品名', u'規格/包裝', u'件數', u'數量', u'運貨備註']
    info.prodtxt = []
    for i in range(5):
        adj = (0,2) if i==0 else (1,1)
        w = 10 if i in [1,2,3] else 22
        print adj
        ttk.Label(frameIn2, text=labels[i]).grid(row=5, column=i+adj[0], columnspan=adj[1])
        info.prodtxt.append(Tk.Text(frameIn2, wrap=Tk.WORD, width=w, height=6))
        info.prodtxt[i].grid(row=6,column=i+adj[0],columnspan=adj[1], sticky=Tk.W+Tk.E)#, font=("Courier", "12")
        info.prodtxt[i].config(state=Tk.DISABLED)
        info.prodtxt[i].tag_config('a', justify=Tk.RIGHT)

    ttk.Label(frameIn2, text=u"貨單日期:").grid(row=0,column=4)
    ttk.Label(frameIn2, text=u"貨單編號:").grid(row=1,column=4)
    company_data = Tk.StringVar()
    ttk.Label(frameIn2, textvariable=company_data).grid(row=0,column=5)
    new_delivery_date = Tk.StringVar()
    new_delivery_ID = Tk.StringVar()
    Tk.Entry(frameIn2, textvariable=new_delivery_date)\
            .grid(row=0, column=5, columnspan=2, sticky=Tk.W+Tk.E)
    Tk.Entry(frameIn2, textvariable=new_delivery_ID)\
            .grid(row=1, column=5, columnspan=2, sticky=Tk.W+Tk.E)

    def submitmanifest(info):
        update_dic = dict(delivered=True, deliveryID=new_delivery_ID.get())

        strdate = new_delivery_date.get()
        for sep in [None,'/','-','\\']:
            if 1 < len(strdate.split(sep)) < 4:
                strdate = strdate.split(sep)
                break
        try:
            if len(strdate) == 3:
                update_dic['deliverydate'] = datetime.date(int(strdate[2]),int(strdate[0]),int(strdate[1]))
            else:
                dnow = datetime.date.today()
                dates = [datetime.date(dnow.year+x,int(strdate[0]),int(strdate[1])) for x in [-1,0,1]]
                diff = [abs((x-dnow).days) for x in dates]
                update_dic['deliverydate'] = dates[diff.index(min(diff))]
        except:
            return
        # Send updates to SQL database
        [dm.update_sale(mp['id'], update_dic) for mp in info.manifestprods]

        loadcompany(info)



    mani_submit = ttk.Button(frameIn2, text=u'提交出貨單 (變更日期與編號)', command=lambda:submitmanifest(info))
    mani_submit.grid(row=2, column=4, columnspan=3, sticky=Tk.W+Tk.E)


    frameIn2.pack(side=Tk.TOP, fill=Tk.X)


    # add to notebook (underline = index for short-cut character)
    nb.add(frame, text=u'出貨單', padding=2, state=Tk.NORMAL)




    #---------------------------------------------------------------
    frame = ttk.Frame(nb)

    txt2 = Tk.Text(frame, wrap=Tk.WORD, width=40, height=10)
    vscroll = ttk.Scrollbar(frame, orient=Tk.VERTICAL, command=txt2.yview)
    txt2['yscroll'] = vscroll.set
    vscroll.pack(side=Tk.RIGHT, fill=Tk.Y)
    txt2.pack(fill=Tk.BOTH, expand=Tk.Y)

    # add to notebook (underline = index for short-cut character)
    nb.add(frame, text=u'發票', padding=2, state=Tk.DISABLED)

    nb.pack(side=Tk.RIGHT, fill=Tk.BOTH, expand=Tk.Y, padx=2, pady=3)


def hello():
    print("It works")
    tkMessageBox.showinfo('About', 'This is about nothing')

def about():
    tkMessageBox.showinfo('About', '台茂化工\nWritten by Jay W Johnson\n2014')


def convert_date(adate):
    '''Converts a formatted string to a datetime.date object or from date to str
    depending on input.'''
    if isinstance(adate,str):
        for sep in [None,'/','-','\\']:
            if 2 <= len(adate.split(sep)) <= 3:
                adate = adate.split(sep)
                break
        if len(adate) == 3:
            update_dic['deliverydate'] = datetime.date(int(adate[2]),int(adate[0]),int(adate[1]))
        else:
            # Find the closest year
            dnow = datetime.date.today()
            dates = [datetime.date(dnow.year+x,int(adate[0]),int(adate[1])) for x in [-1,0,1]]
            diff = [abs((x-dnow).days) for x in dates]
            update_dic['deliverydate'] = dates[diff.index(min(diff))]


        strdate = adate
        # Try different separators until one produces a list of len 2 or 3
        for sep in [None,'/','-','\\']:
            if 2 <= len(adate.split(sep)) <=3:
                strdate = adate.split(sep)
                break
        try:
            # If len three, assume date is given last, if two then use closest year
            if len(strdate) == 3:
                return datetime.date(int(strdate[2]),int(strdate[0]),int(strdate[1]))
            else:
                dnow = datetime.date.today()
                dates = [datetime.date(dnow.year+x,int(strdate[0]),int(strdate[1])) for x in [-1,0,1]]
                diff = [abs((x-dnow).days) for x in dates]
                return dates[diff.index(min(diff))]
        except:
            pass
    elif isinstance(adate,datetime.date):
        return


if __name__ == '__main__':
    app = Taimau_app(None)
    app.title('Taimau')
    app.mainloop()

