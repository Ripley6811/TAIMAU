#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
summary

description

:REQUIRES:
    - Database using TM2014_tables_v2.py
    - gdata (Google API) for pulling Android app data.

:TODO:


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
import datetime
import Tkinter as Tk
import tkMessageBox
import ttk
import tkFont
import frame_company_editor
import frame_payment
import frame_order_entry
import frame_manifest
import frame_pending
import db_manager_v2 as dmv2
import xlwt
import Tix
import analytics

print os.getcwd()
#===============================================================================
# METHODS
#===============================================================================

# Container for passing state parameters
# Separate into current record, product
Info = type('struct', (), {})


class TaimauApp(Tix.Tk):
    '''Main application.
    '''
    run_location = os.getcwd()


    def __init__(self, parent):

        Tix.Tk.__init__(self, parent)
#        self.wm_title('woot')
        self.parent = parent
        self.option_add("*Font", "PMingLiU 13")
        ttk.Style().configure('.', font=tkFont.Font(family="PMingLiU", size=-12))

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
        reportmenu.add_command(label="Save client shipments to Excel (6 months).", command=sales_shipments_to_excel)
        reportmenu.add_command(label="Save incoming shipments to Excel (6 months).", command=purchases_shipments_to_excel)
        reportmenu.add_command(label="Save all products to Excel file.", command=save_products_to_excel)
        reportmenu.add_command(label="Report3", command=None, state=Tk.DISABLED)
        reportmenu.add_command(label="Report4", command=None, state=Tk.DISABLED)
        menubar.add_cascade(label=u"報告", menu=reportmenu)


#        # FONT MENU OPTIONS
        def setFont():
            self.option_add("*Font", fontsize.get())
        fontmenu = Tk.Menu(menubar, tearoff=0)
        fontsize = Tk.StringVar()
        fontmenu.add_radiobutton(label=u'Verdana 12', variable=fontsize,
                                 command=setFont, value=u'Verdana 12')
        fontmenu.add_radiobutton(label=u'PMingLiU 13', variable=fontsize,
                                 command=setFont, value=u'PMingLiU 13')
        fontmenu.add_radiobutton(label=u'NSimSun 13', variable=fontsize,
                                 command=setFont, value=u'NSimSun 13')
        menubar.add_cascade(label=u"Font", menu=fontmenu)
#        fontsize.set(u'NSimSun 13')
#        setFont()


        # HELP MENU OPTIONS
        helpmenu = Tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label=u"關於", command=about)
        menubar.add_cascade(label="Help", menu=helpmenu)


        # SET AND SHOW MENU
        self.config(menu=menubar)
        self.geometry('1200x740')


        # SET MAIN NOTEBOOK
        nb = ttk.Notebook()
        #---------- Add Purchases frame
        frame = ttk.Frame(nb)
        get_purchases_frame(frame)
        nb.add(frame, text='Purchases', underline=0)
        #---------- Add Sales frame
        frame = ttk.Frame(nb)
        get_sales_frame(frame)
        nb.add(frame, text='Sales', underline=0)
        #---------- Add Pending info frame
        frame = ttk.Frame(nb)
        frame_pending.get_pending_frame(frame, dmv2)
        nb.add(frame, text='Pending', underline=2)
        #TODO:---------- Add In-Out Records info frame
        frame = ttk.Frame(nb)
        frame_pending.get_tablet_frame(frame, dmv2)
        nb.add(frame, text='Tablet Data', underline=0)
        #TODO:---------- Add Company data edit frame
        frame = ttk.Frame(nb)
        frame_company_editor.get_company_editor(frame, dmv2)
        nb.add(frame, text='Catalog', underline=0)
        #TODO:---------- Add Warehouse management frame


        #--------- Set arrangement of notebook frames
        nb.pack(side=Tk.RIGHT, fill=Tk.BOTH, expand=Tk.Y, padx=2, pady=3)


    def endsession(self):
        self.quit()


def sales_shipments_to_excel():
    save_shipments_to_excel(is_sale=True)

def purchases_shipments_to_excel():
    save_shipments_to_excel(is_sale=False)

def save_shipments_to_excel(is_sale=None):
    '''Save all activity in the last half-year to Excel.
    Order by delivery date.
    '''
    wb = xlwt.Workbook()
    cogroups = dmv2.cogroups()
    cutoff = datetime.date.today() - datetime.timedelta(180)

    style = xlwt.XFStyle()
    style.num_format_str = '"$"#,##0.00_);("$"#,##'

    for group in cogroups:
        query = dmv2.session.query(dmv2.Order)
        query = query.filter_by(group=group.name, is_sale=is_sale)
        query = query.filter(dmv2.Order.duedate > cutoff)
        orders = query.order_by(dmv2.Order.duedate).all()

        if orders:
            #Make sheet with cogroup name
            ws = wb.add_sheet(group.name)
        else:
            continue
        row = 0
        for order in orders:
            for shipment in order.shipments:
                ws.write(row, 0, str(shipment.shipmentdate))
                ws.write(row, 1, unicode(order.seller))
                ws.write(row, 2, '->')
                ws.write(row, 3, unicode(order.buyer))
                ws.write(row, 4, unicode(order.product.summary))
                qty = shipment.sku_qty
                sku = order.product.SKU
                if order.product.unitpriced or sku == u'槽車':
                    qty *= order.product.units
                    sku = order.product.UM
                ws.write(row, 5, qty)
                ws.write(row, 6, sku)
                ws.write(row, 7, order.price, style)
                ws.write(row, 8, u'\u214C {}'.format(sku))
                ws.write(row, 9, qty*order.price, style)
                row += 1
            ws.col(0).width = 3000
            ws.col(2).width = 700
            ws.col(4).width = 8000
            ws.col(7).width = 3000
            ws.col(9).width = 3000


    filename = 'OUTPUT.xls'
    if is_sale:
        filename = 'SALES_ACTIVITY.xls'
    else:
        filename = 'PURCHASES_ACTIVITY.xls'

    base = os.getcwd()
    path = os.path.join(base, filename)
    wb.save(path)
    os.system('start "'+ base + '" ' + filename)

def save_products_to_excel():
    '''Save all products to Excel.'''
    wb = xlwt.Workbook()

    style = xlwt.XFStyle()
    style.num_format_str = '"$"#,##0.00_);("$"#,##'
    def_style = xlwt.XFStyle()


    query = dmv2.session.query(dmv2.Product)
    recs = query.order_by(dmv2.Product.group).all()

    ws = wb.add_sheet(u'Products')

    headers = [u'group', u'product_label', u'inventory_name', u'curr_price',
               u'english_name', u'units', u'UM', u'SKU',
               u'SKUlong', u'unitpriced', u'ASE_PN',
               u'note', u'is_supply', u'discontinued',
               ]
    row = 0
    for col, head in enumerate(headers):
        ws.write(row, col, head)
    for rec in recs:
        row += 1
        for col, head in enumerate(headers):

            ws.write(row, col, rec.__dict__[head], style
                                                    if head == u'curr_price'
                                                    else def_style)
#        ws.col(0).width = 3000
#        ws.col(2).width = 700
#        ws.col(4).width = 8000
#        ws.col(7).width = 3000
#        ws.col(9).width = 3000


    filename = 'PRODUCTS.xls'

    base = os.getcwd()
    path = os.path.join(base, filename)
    wb.save(path)
    os.system('start "'+ base + '" ' + filename)



def save_co_text():
    '''Saves orders from one company to a text file.'''
    tmpwin = Tk.Toplevel(width=700)
    tmpwin.title(u"Pick company group to export")

    cogroups = dmv2.cogroups()

    co_lb = Tk.Listbox(tmpwin, width=30, height=30)
    co_lb.grid()

    for co in cogroups:
        br_list = [br.name for br in co.branches]
        co_lb.insert(0, u'{0.name} ({1})'.format(co, u', '.join(br_list)))



def get_purchases_frame(frame):
    # Create info container to manage all Purchases data
    info = Info()
    info.src = "Purchases"
    info.curr_company = None
    info.edit_ID = None
    info.listbox = Info()
    info.button = Info()
    info.method = Info()
    info.settings = Info()
    info.settings.font = "NSimSun"#"PMingLiU"
#    info.dm = dm
    info.dmv2 = dmv2
    info.method.reload_orders = reload_orders
    info.method.refresh_listboxes = refresh_listboxes
    info.method.format_order_summary = format_order_summary
#    info.method.convert_date = convert_date

    #-------
    frame1 = ttk.Frame(frame)
    def showall_companies():
        info.listbox.companies.delete(0, Tk.END)
        for i, each in enumerate(dmv2.cogroup_names()):
            info.listbox.companies.insert(i, each)
            info.listbox.companies.itemconfig(i, bg=u'white',
                                              selectbackground=u'SlateBlue4')

    b = Tk.Button(frame1, text="Show All", command=lambda: showall_companies())
    b.pack(side=Tk.BOTTOM, fill=Tk.X)
    scrollbar = Tk.Scrollbar(frame1, orient=Tk.VERTICAL)
    info.listbox.companies = Tk.Listbox(frame1, selectmode=Tk.BROWSE,
                         yscrollcommand=scrollbar.set,
                         width=10, font=(info.settings.font, "14"),
                         exportselection=0)
    scrollbar.config(command=info.listbox.companies.yview)
#        scrollbar.grid(row=0,column=0, sticky=Tk.N+Tk.S)
#        info.listbox.companies.grid(row=0,column=1,sticky=Tk.N+Tk.S)
    scrollbar.pack(side=Tk.RIGHT, fill=Tk.Y)
    info.listbox.companies.pack(side=Tk.LEFT, fill=Tk.Y)
    info.listbox.companies.bind("<Double-Button-1>",
                                lambda _: loadcompany(info, True))


#    info.listbox.companies.insert(0,*dmv2.company_list_from_purchases())
    for i, each in enumerate(dmv2.company_list_from_purchases()):
        info.listbox.companies.insert(i, each)
        info.listbox.companies.itemconfig(i, bg=u'seashell2',
                                          selectbackground=u'maroon4')

    frame1.pack(side=Tk.LEFT, fill=Tk.Y, padx=2, pady=3)

    #
    #==========================================================================
    # SET UP TABBED SECTIONS
    #==========================================================================
    #
    info.record = {}
    nb = ttk.Notebook(frame)
    #--------------- Order entry tab -----------------------
    frame = ttk.Frame(nb)
    frame_order_entry.make_order_entry_frame(frame, info)
    nb.add(frame, text=u'訂單 (造出貨單)', padding=2)

    #------------------ Manifest tab ----------------------------
    frame = ttk.Frame(nb)
    frame_manifest.create_manifest_frame(frame, info)
    nb.add(frame, text=u'出貨單 (造發票)', padding=2)
    #------------------ Invoice tab -----------------------------
    frame = ttk.Frame(nb)
    frame_payment.set_invoice_frame(frame, info)
    nb.add(frame, text=u'發票 (已支付?)', padding=2)
    #------------------ Pack notebook ----------------------------
    nb.pack(side=Tk.RIGHT, fill=Tk.BOTH, expand=Tk.Y, padx=2, pady=3)


def format_order_summary(record):
    prodtmp = record.product.product_label, record.product.inventory_name
    if prodtmp[0] and prodtmp[0] != prodtmp[1]:
        prodtmp = u'{} (台茂:{})'.format(*prodtmp)
    else:
        prodtmp = prodtmp[1]
    tmp = u''
#            tmp += u'\u25C6' if val['delivered'] else u'\u25C7'
    #PO icon and PO number if available
    po_no_txt = (record.orderID.strip() if record.orderID
                                        else '({})'.format(record.id))
    tmp += u"{0:<14}".format(po_no_txt)

    #Shipping icon and manifest number if available
    tmp += u'\u26DF' if len(record.shipments) > 0 else u'\u25C7'
    tmp += (u'*{:<3}'.format(len(record.shipments)) if record.shipments
                                                    else u'    ')
#    man_no_txt = record.shipments[0].shipmentID[:11].strip()[-9:] if record.shipments else u''
#    tmp += u"{0:<10}".format(man_no_txt)

    #Invoice paid icon and invoice number if available
    tmp += u'\u265B' if record.all_paid() else u'\u25C7'
    tmp += (u'*{:<3}'.format(len(record.invoices)) if record.invoices
                                                    else u'    ')
#    inv_no_txt = record.invoices[0].invoice_no[:10].strip() if record.invoices else u''
#    tmp += u"{0:<12}".format(inv_no_txt if u'random' not in inv_no_txt else u'')

#    print type(record), record.__dict__.keys()
    if record.all_shipped():
        try:
            tmp += (u"到期:{0.month:>2}月{0.day:>2}日".format(
                record.shipments[0].shipmentdate)#.replace(' ','  ')
            )
        except:
            tmp += u"到期:  月  日   年"#.replace(' ','  ')
    else:
        try:
            tmp += (u"訂單日:{0.month:>2}月{0.day:>2}日".format(
                record.orderdate)#.replace(' ','  ')
            )
        except:
            tmp += u'  None Entered'
    try:
        tmp += u" \u273F {0}\u2794{1} \u273F {9:>6}{3:>5}{5} {2:<14} @ ${7} \u214C {8}".format(
            record.seller,#.split()[0],
            record.buyer,#.split()[0],
            prodtmp,
            record.totalskus,
            int(record.totalunits),
            record.product.UM if record.product.SKU == u'槽車' else record.product.SKU,
            int(record.totalunits),
            int(record.price) if float(record.price).is_integer() else record.price,
            record.product.UM if record.product.unitpriced else record.product.SKU,
            u'{}/'.format(record.qty_remaining()),
            )
    except:
        pass

    return tmp



def loadcompany(info, grab_index=False):
    '''This function runs when the order list is opened for the first time
    or when it needs to be reloaded to show updates.
    #TODO: Split into two functions: loadcompany() and refreshlists()

    Use info.src for origin of call.

    grab_index = True updates the info.curr_company to list selection.
    grab_index = False (default) uses the company already stored in databook.
    '''
    print 'LOADCOMPANY'
    if grab_index:
        info.curr_company = info.listbox.companies.get(Tk.ACTIVE)
    elif not info.curr_company:
        info.curr_company = info.listbox.companies.get(Tk.ACTIVE)

    # Reload orders preloads all records for a selected company into info.order_records
    reload_orders(info)
    refresh_listboxes(info)
    info.method.reload_products_frame()
    info.method.refresh_manifest_listbox()
    info.method.refresh_invoice_listbox()
#    info.method.reload_invoice_frame()



def reload_orders(info):
    '''Create a link to records and corresponding ID's and store in "info".
    '''
    if info.src == "Sales":
        info.order_records = dmv2.sales(group=info.curr_company)[::-1]
        info.order_rec_IDs = [rec.id for rec in info.order_records]
    else:
        info.order_records = dmv2.purchases(group=info.curr_company)[::-1]
        info.order_rec_IDs = [rec.id for rec in info.order_records]


def refresh_listboxes(info):
    '''Refresh the record lists for each frame.
    #TODO: Split up and put in their respective modules.
    '''
    # Add previous orders to order listbox
    info.listbox.rec_orders.delete(0, Tk.END)
#    info.listbox.rec_manifest.delete(0, Tk.END)
#    info.listbox.rec_invoices.delete(0, Tk.END)

    # List of order summaries
    tmp = [rec.listbox_summary() for rec in info.order_records]

    #TODO: Different colors for different products. Not necessary...
    for i, each in enumerate(tmp):
        info.listbox.rec_orders.insert(i, each)
        info.listbox.rec_orders.itemconfig(i, bg=u'lavender',
                                           selectbackground=u'dark orchid')





def get_sales_frame(frame):
    # Create info container to manage all Sales data
    info = Info()
    info.src = "Sales"
    info.curr_company = None
    info.edit_ID = None
    info.listbox = Info()
    info.button = Info()
    info.method = Info()
    info.settings = Info()
    info.settings.font = "NSimSun"#"PMingLiU"
#    info.dm = dm
    info.dmv2 = dmv2
    info.method.refresh_listboxes = refresh_listboxes
    info.method.format_order_summary = format_order_summary
#    info.method.convert_date = convert_date
    info.method.reload_orders = reload_orders

    #-------
    frame1 = ttk.Frame(frame)
    def showall_companies():
        info.listbox.companies.delete(0, Tk.END)
        for i, each in enumerate(dmv2.cogroup_names()):
            info.listbox.companies.insert(i, each)
            info.listbox.companies.itemconfig(i, bg=u'white',
                                              selectbackground=u'SlateBlue4')

    b = Tk.Button(frame1, text="Show All", command=lambda: showall_companies())
    b.pack(side=Tk.BOTTOM, fill=Tk.X)
    scrollbar = Tk.Scrollbar(frame1, orient=Tk.VERTICAL)
    info.listbox.companies = Tk.Listbox(frame1, selectmode=Tk.BROWSE,
                                         yscrollcommand=scrollbar.set,
                                         width=10,
                                         font=(info.settings.font, "14"),
                                         exportselection=0)
    scrollbar.config(command=info.listbox.companies.yview)
#        scrollbar.grid(row=0,column=0, sticky=Tk.N+Tk.S)
#        info.listbox.companies.grid(row=0,column=1,sticky=Tk.N+Tk.S)
    scrollbar.pack(side=Tk.RIGHT, fill=Tk.Y)
    info.listbox.companies.pack(side=Tk.LEFT, fill=Tk.Y)
    info.listbox.companies.bind("<Double-Button-1>", lambda _: loadcompany(info, True))
#    info.listbox.companies.insert(0,*dmv2.company_list_from_sales())
    for i, each in enumerate(dmv2.company_list_from_sales()):
        info.listbox.companies.insert(i, each)
        info.listbox.companies.itemconfig(i, bg=u'CadetBlue1', selectbackground=u'SlateBlue4')
    frame1.pack(side=Tk.LEFT, fill=Tk.Y, padx=2, pady=3)

    #
    #==============================================================================
    # SET UP TABBED SECTIONS
    #==============================================================================
    #
    info.record = {}
    nb = ttk.Notebook(frame)
    #--------------- Order entry tab -----------------------
    frame = ttk.Frame(nb)
    frame_order_entry.make_order_entry_frame(frame, info)
    nb.add(frame, text=u'訂單 (造出貨單)', padding=2)
    #------------------ Manifest tab ----------------------------
    frame = ttk.Frame(nb)
    frame_manifest.create_manifest_frame(frame, info)
    nb.add(frame, text=u'出貨單 (造發票)', padding=2)
    #------------------ Invoice tab -----------------------------
    frame = ttk.Frame(nb)
    frame_payment.set_invoice_frame(frame, info)
    nb.add(frame, text=u'發票 (已支付?)', padding=2)
    #------------------ Pack notebook ----------------------------
    nb.pack(side=Tk.RIGHT, fill=Tk.BOTH, expand=Tk.Y, padx=2, pady=3)


    #==============================================================================
    # DATABASE ANALYSIS
    #==============================================================================
    # Calculate if ASE quotas will go over in the next order
    analytics.ASE_analysis(info)



def hello():
    '''Filler function.'''
    print("It works")
    tkMessageBox.showinfo('About', 'This is about nothing')

def about():
    '''Display program author and date.'''
    tkMessageBox.showinfo('About', '台茂化工\nWritten by Jay W Johnson\n2014')




if __name__ == '__main__':
    app = TaimauApp(None)
    app.title('Taimau')
    app.mainloop()

