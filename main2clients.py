#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
summary

description

:REQUIRES:
    - Database using TM2014_tables_v2.py

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

    ## Things to fix or do after refactoring ##
    - Change manifest to create partial orders and work with Shipment db table.
    - Change invoice page to manage partial payments and pre-payments with Payment db table.
    - Rewrite order placement tab to be simpler and use the correct data fields.
    - Right click option on company to open Company/Branch information.


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
#from tkFileDialog import askopenfilename, askopenfile
#from collections import namedtuple
import datetime
#import tables_company_data as tables
import Tkinter as Tk
import tkMessageBox
import ttk
import tkFont
#import google_spreadsheet as gs
#import database_management as dm
import frame_company_editor
import frame_payment
import frame_order_entry
import frame_manifest
import db_manager_v2 as dmv2

#===============================================================================
# METHODS
#===============================================================================

# Container for passing state parameters
# Separate into current record, product
class Info(object):
    def __init__(self, **attrs):
        for key, value in attrs.iteritems():
            if isinstance(value, dict):
                attrs[key] = Info(**value)
        self.__dict__.update(attrs)


class Taimau_app(Tk.Tk):
    run_location = os.getcwd()



    def __init__(self, parent):

        Tk.Tk.__init__(self, parent)
#        self.wm_title('woot')
        self.parent = parent
        self.option_add("*Font", "PMingLiU 13")
        s = ttk.Style()
        s.configure('.', font=tkFont.Font(family="PMingLiU", size=-12))


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

        frame_company_editor.get_company_editor(frame, dmv2)

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
    # Create info container to manage all Purchases data
    info = Info()
    info.src = "Purchases"
    info.curr_company = None
    info.edit_ID = None
    info.listbox = Info()
    info.button = Info()
    info.method = Info()
    info.settings = Info()
    info.settings.font = "PMingLiU"
#    info.dm = dm
    info.dmv2 = dmv2
    info.method.reload_orders = reload_orders
    info.method.refresh_listboxes = refresh_listboxes
    info.method.format_order_summary = format_order_summary
    info.method.convert_date = convert_date


    #-------
    frame1 = ttk.Frame(frame)
    scrollbar = Tk.Scrollbar(frame1, orient=Tk.VERTICAL)
    info.listbox.companies = Tk.Listbox(frame1, selectmode=Tk.BROWSE,
                         yscrollcommand=scrollbar.set,
                         width=10, font=(info.settings.font, "14"), exportselection=0)
    scrollbar.config(command=info.listbox.companies.yview)
#        scrollbar.grid(row=0,column=0, sticky=Tk.N+Tk.S)
#        info.listbox.companies.grid(row=0,column=1,sticky=Tk.N+Tk.S)
    scrollbar.pack(side=Tk.RIGHT, fill=Tk.Y)
    info.listbox.companies.pack(side=Tk.LEFT, fill=Tk.Y)
    info.listbox.companies.bind("<Double-Button-1>", lambda _:loadcompany(info,True))


#    info.listbox.companies.insert(0,*dmv2.company_list_from_purchases())
    for i,each in enumerate(dmv2.company_list_from_purchases()):
        info.listbox.companies.insert(i,each)
        info.listbox.companies.itemconfig(i, bg=u'seashell2', selectbackground=u'maroon4')

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
    nb.add(frame, text=u'訂單', padding=2)

    #------------------ Manifest tab ----------------------------
    frame = ttk.Frame(nb)
    frame_manifest.create_manifest_frame(frame, info)
    nb.add(frame, text=u'出貨單', padding=2, state=Tk.NORMAL)
    #------------------ Invoice tab -----------------------------
    frame = ttk.Frame(nb)
    frame_payment.set_invoice_frame(frame, info)
    nb.add(frame, text=u'發票', padding=2)
#    #------------------ Payment tab -----------------------------
#    frame = ttk.Frame(nb)
#    frame_payment.set_invoice_frame(frame, info)
#    nb.add(frame, text=u'發票', padding=2)
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
    tmp += u'\u26DF' if record.all_shipped() else u'\u25C7'
    tmp += u'\u265B' if record.all_paid() else u'\u25C7'
#    print type(record), record.__dict__.keys()
    if record.all_shipped():
        try:
            tmp += (u"到期:{:>2}月{:>2}日{}年".format(
                record.shipments[0].shipmentdate.month,
                record.shipments[0].shipmentdate.day,
                record.shipments[0].shipmentdate.year).replace(' ','  ')
            )
        except:
            tmp += u"到期:  月  日   年".replace(' ','  ')
    else:
        try:
            tmp += (u"預期:{:>2}月{:>2}日{}年".format(
                record.duedate.month,
                record.duedate.day,
                record.duedate.year).replace(' ','  ')
            )
        except:
            tmp += u'  None Entered'
    try:
        tmp += u" \u273F  {2}  \u273F {0}\u2794{1} \u273F  {3} ({4} {5}) \u25CA ${7}".format(
            record.seller,#.split()[0],
            record.buyer,#.split()[0],
            prodtmp,
            record.totalskus,
            int(record.totalunits),
            record.product.UM,
            int(record.totalunits),
            int(record.price) if float(record.price).is_integer() else record.price,
            record.MPN)
    except:
        pass
    if record.shipments:
        tmp += u"  貨單編號:{0}".format(
            record.shipments[0].shipmentID
        )
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
    info.method.reload_shipment_frame()
    info.method.reload_invoice_frame()



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
    info.listbox.rec_orders.delete(0,Tk.END)
    info.listbox.rec_manifest.delete(0,Tk.END)
    info.listbox.rec_invoices.delete(0,Tk.END)

    # List of order summaries
    tmp = [format_order_summary(rec) for rec in info.order_records]

    #TODO: Different colors for different products. Not necessary...
    for i, each in enumerate(tmp):
        info.listbox.rec_orders.insert(i,each)
        info.listbox.rec_orders.itemconfig(i, bg=u'lavender', selectbackground=u'dark orchid')
        shipped_color = dict(bg=u'SlateGray4', fg=u'gray79', selectbackground=u'tomato', selectforeground=u'black')
        no_ship_color = dict(bg=u'pale green', selectbackground=u'yellow', selectforeground=u'black')
        info.listbox.rec_manifest.insert(i,each)
        ins_colors = shipped_color if info.order_records[i].all_shipped() else no_ship_color
        info.listbox.rec_manifest.itemconfig(i, ins_colors)

        invoiced_color = dict(bg=u'SlateGray4', fg=u'gray79', selectbackground=u'tomato', selectforeground=u'black')
        no_ship_color = dict(bg=u'pale green', selectbackground=u'yellow', selectforeground=u'black')
        info.listbox.rec_invoices.insert(i,each)
        ins_colors = invoiced_color if info.order_records[i].all_invoiced() else no_ship_color
        info.listbox.rec_invoices.itemconfig(i, ins_colors)
#    info.listbox.rec_orders.selection_set(Tk.END)
#    info.listbox.rec_orders.see(Tk.END)
#    info.listbox.rec_orders.activate(Tk.END)
#
##        info.listbox.rec_manifest.selection_set(Tk.END)
#    info.listbox.rec_manifest.see(Tk.END)
#        info.listbox.rec_manifest.activate(Tk.END)

#    info.listbox.branches.delete(0,Tk.END)
#    [info.listbox.branches.insert(i,compsum) for i, compsum in enumerate(dmv2.get_branch_numbers(info.curr_company.encode('utf8')))]

#    info.method.reload_invoice_frame()



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
    info.settings.font = "PMingLiU"
#    info.dm = dm
    info.dmv2 = dmv2
    info.method.refresh_listboxes = refresh_listboxes
    info.method.format_order_summary = format_order_summary
    info.method.convert_date = convert_date
    info.method.reload_orders = reload_orders


    #-------
    frame1 = ttk.Frame(frame)
#    def showall_companies():
#        info.listbox.companies.delete(0,Tk.END)
#        for i,each in enumerate(dmv2.cogroup_names()):
#            info.listbox.companies.insert(i,each)
#            info.listbox.companies.itemconfig(i, bg=u'SkyBlue2', selectbackground=u'SlateBlue4')

#    b = Tk.Button(frame1, text="Show All", command=lambda:showall_companies())
#    b.pack(side=Tk.BOTTOM, fill=Tk.X)
    scrollbar = Tk.Scrollbar(frame1, orient=Tk.VERTICAL)
    info.listbox.companies = Tk.Listbox(frame1, selectmode=Tk.BROWSE,
                         yscrollcommand=scrollbar.set,
                         width=10, font=(info.settings.font, "14"), exportselection=0)
    scrollbar.config(command=info.listbox.companies.yview)
#        scrollbar.grid(row=0,column=0, sticky=Tk.N+Tk.S)
#        info.listbox.companies.grid(row=0,column=1,sticky=Tk.N+Tk.S)
    scrollbar.pack(side=Tk.RIGHT, fill=Tk.Y)
    info.listbox.companies.pack(side=Tk.LEFT, fill=Tk.Y)
    info.listbox.companies.bind("<Double-Button-1>", lambda _:loadcompany(info,True))
#    info.listbox.companies.insert(0,*dmv2.company_list_from_sales())
    for i,each in enumerate(dmv2.company_list_from_sales()):
        info.listbox.companies.insert(i,each)
        info.listbox.companies.itemconfig(i, bg=u'CadetBlue1', selectbackground=u'SlateBlue4')
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
    frame_order_entry.make_order_entry_frame(frame, info)
    nb.add(frame, text=u'訂單', padding=2)
    #---------------------------------------------------------
    frame = ttk.Frame(nb)
    frame_manifest.create_manifest_frame(frame, info)
    nb.add(frame, text=u'出貨單', padding=2, state=Tk.NORMAL)
    #---------------------------------------------------------------
    frame = ttk.Frame(nb)
    nb.add(frame, text=u'發票', padding=2)
    frame_payment.set_invoice_frame(frame, info)

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
        #Convert datetime object to string
        return u'{}/{}/{}'.format(adate.month,adate.day,adate.year)


if __name__ == '__main__':
    app = Taimau_app(None)
    app.title('Taimau')
    app.mainloop()

