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
import frame_order_entry, frame_overview
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
    get_orders_frame(frame, u'Purchases')

def get_sales_frame(frame):
    get_orders_frame(frame, u'Sales')

def get_orders_frame(frame, src):
    # Create info container to manage all Order data
    info = Info()
    info.src = src
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

    #-------
    frame1 = ttk.Frame(frame)
    def manage_companies():
        try:
            if info.co_select.state() == 'normal':
                info.co_select.focus_set()
            return
        except:
            pass

        info.co_select = Tix.Toplevel(width=1200, height=600)
        info.co_select.title(u"公司清單管理")

        grouplist = info.dmv2.cogroups()
        ROWperCOL = 25
        wlist = {}
        for i, group in enumerate(grouplist):
            # Show company group name and additional branches.
            branchlist = [br.name for br in group.branches]
            try:
                branchlist.remove(group.name)
            except ValueError as e:
                print e
            text = u'          {}'.format(group.name)
            if len(branchlist):
                text += u' ({})'.format(u', '.join(branchlist))
            tl = Tix.Label(info.co_select, text=text)
            tl.grid(row=i%ROWperCOL, column=2*(i/ROWperCOL))

            # 'Supplier' and 'Customer' switches.
            # Not using 'Select' label option in order to keep things aligned.
            selectParams = dict(
                radio=False,
                allowzero=True,
                selectedbg=u'cyan',
            )
            tsel = Tix.Select(info.co_select, **selectParams)
            tsel.add(u's', text=u'Supplier')
            tsel.add(u'c', text=u'Customer')
            tsel.grid(row=i%ROWperCOL, column=2*(i/ROWperCOL)+1)

            # Activate buttons according to database records.
            if group.is_supplier:
                tsel.invoke(u's')
            if group.is_customer:
                tsel.invoke(u'c')

            # Add 'Select' widget to widget list
            wlist[group.name] = tsel
            print group.is_supplier,  group.is_customer

        tb = Tix.Button(info.co_select, text=u'提交改變', bg=u'light salmon')
        def submit():
            session = info.dmv2.session
            CG = info.dmv2.CoGroup
            for coname, tsel in wlist.iteritems():
                updates = dict(
                    is_supplier= u's' in tsel['value'],
                    is_customer= u'c' in tsel['value'],
                )
                print updates
                session.query(CG).filter_by(name=coname).update(updates)
                session.commit()
            info.co_select.destroy()
        tb['command'] = submit
        tb.grid(row=100, columnspan=20)



    b = Tk.Button(frame1, text=u"公司清單管理")
    b['command'] = manage_companies
    b.pack(side=Tk.BOTTOM, fill=Tk.X)

    # Set up company listbox on left side of application.
    scrollbar = Tk.Scrollbar(frame1, orient=Tk.VERTICAL)
    info.listbox.companies = Tk.Listbox(frame1, selectmode=Tk.BROWSE,
                         yscrollcommand=scrollbar.set,
                         width=10, font=(info.settings.font, "14"),
                         exportselection=0)
    scrollbar.config(command=info.listbox.companies.yview)

    scrollbar.pack(side=Tk.RIGHT, fill=Tk.Y)
    info.listbox.companies.pack(side=Tk.LEFT, fill=Tk.Y)
    info.listbox.companies.bind("<Double-Button-1>",
                        lambda _: company_listbox_dbl_click(info, True))

    cogroups = dmv2.cogroups()
    if src == u'Sales':
        companies = [cg.name for cg in cogroups if cg.is_customer]
    else:
        companies = [cg.name for cg in cogroups if cg.is_supplier]
    for i, each in enumerate(companies):
        info.listbox.companies.insert(i, each)
        info.listbox.companies.itemconfig(i, bg=u'seashell2',
                                          selectbackground=u'maroon4')

    frame1.pack(side=Tk.LEFT, fill=Tk.Y, padx=2, pady=3)

    #==========================================================================
    # SET UP TABBED SECTIONS
    #==========================================================================
    info.record = {}
    nb = ttk.Notebook(frame)
    #--------------- Overview of database ---------------------
    frame = Tix.Frame(nb)
    frame_overview.create_frame(frame, info)
    nb.add(frame, text=u'概貌', padding=2)
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



def company_listbox_dbl_click(info, grab_index=False):
    '''This function runs when the order list is opened for the first time
    or when it needs to be reloaded to show updates.
    #TODO: Split into two functions: company_listbox_dbl_click() and refreshlists()

    Use info.src for origin of call.

    grab_index = True updates the info.curr_company to list selection.
    grab_index = False (default) uses the company already stored in databook.
    '''
    print 'company_listbox_dbl_click'
    if grab_index:
        info.curr_company = info.listbox.companies.get(Tk.ACTIVE)
    elif not info.curr_company:
        info.curr_company = info.listbox.companies.get(Tk.ACTIVE)

    # Reload orders preloads all records for a selected company into info.order_records
    reload_orders(info)
    refresh_listboxes(info)
    info.method.refresh_po_tree()
    info.method.reload_products_frame()
    info.method.refresh_manifest_listbox()
    info.method.refresh_invoice_listbox()
#    info.method.reload_invoice_frame()



def reload_orders(info):
    '''Create a link to records and corresponding ID's and store in "info".
    '''
    if info.src == u"Sales":
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

