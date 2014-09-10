#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
summary

Improvements over previous version include:
- "_state" object that maintains and passes session info between all modules.
- Translation module for registering StringVars and easily switch languages.
- "settings" that are saved and loaded from file using the json package.

:REQUIRES:
    - Database using TM2014_tables_v2.py
    - gdata (Google API) for pulling Android app data.

:TODO:


:AUTHOR: Jay W Johnson
:ORGANIZATION: Taimau Chemicals
:CONTACT: python@boun.cr
:SINCE: Sun Mar 02 15:14:32 2014
:VERSION: 0.3
"""
#===============================================================================
# PROGRAM METADATA
#===============================================================================
__author__ = 'Jay W Johnson'
__contact__ = 'python@boun.cr'
__copyright__ = ''
__license__ = ''
__date__ = 'Sun Mar 02 15:14:32 2014'
__version__ = '0.3'

#===============================================================================
# IMPORT STATEMENTS
#===============================================================================
import os  # os.walk(basedir) FOR GETTING DIR STRUCTURE
import datetime
import Tkinter as Tk
import tkMessageBox
import tkFileDialog
import ttk
import tkFont
import xlwt
import Tix
#import analytics

import db_tools.db_manager as dbm
from pdf_tools import activity_report
import frames.po_frame
from utils.translate_term import localize, setLang
from utils import settings
print 'CWD:', os.getcwd()
#===============================================================================
# METHODS
#===============================================================================

# Container for passing state parameters
# Separate into current record, product
Info = type('struct', (), {})

Info = type('adict', (dict,), {'__getattr__': dict.__getitem__, '__setattr__': dict.__setitem__})


class adict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


class TaimauApp(Tix.Tk):
    '''Main application.
    '''
    run_location = os.getcwd()

    def __init__(self, parent, debug=False):

        Tix.Tk.__init__(self, parent)

        self.parent = parent
        self.option_add("*Font", "PMingLiU 13")
        ttk.Style().configure('.', font=tkFont.Font(family="PMingLiU", size=-12))


        _state = Info()
        _state.debug = debug # For console messages and English GUI
        _state.font = u"NSimSun"
        _state.loc = localize # Translation to Chinese
        _state.dbm = dbm.db_manager() # Database API methods
        _state.curr = Info() # For storage current company, list ID's, etc.
        self._ = _state


        #
        # SET UP MENU BAR
        #
        menubar = Tk.Menu(self)

        # FILE MENU OPTIONS: LOAD, SAVE, EXIT...
        filemenu = Tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label=_state.dbm.dbpath, state='disabled')
        filemenu.add_separator()
        filemenu.add_command(label=_state.loc(u"Change Database", 1), command=self.change_db)
        filemenu.add_separator()
        filemenu.add_command(label=_state.loc(u"Exit", 1), command=self.endsession)
        menubar.add_cascade(label=_state.loc(u"File", 1), menu=filemenu)
        filemenu.entryconfig(0, background=u'pale goldenrod', foreground=u'black')
        self.filemenu = filemenu

        # REPORT MENU OPTIONS
        reportmenu = Tk.Menu(menubar, tearoff=0)
        reportmenu.add_command(label="Change location for saving reports",
                               command=set_report_location)
        reportmenu.add_command(label="Activity Report (PDF)",
                               command=lambda:activity_report.main(_state))
        reportmenu.add_command(label="Save client shipments to Excel (6 months).",
                               command=sales_shipments_to_excel)
        reportmenu.add_command(label="Save incoming shipments to Excel (6 months).",
                               command=purchases_shipments_to_excel)
        reportmenu.add_command(label="Save all products to Excel file.",
                               command=save_products_to_excel)
#        reportmenu.add_command(label="Report3", command=None, state=Tk.DISABLED)
#        reportmenu.add_command(label="Report4", command=None, state=Tk.DISABLED)
        menubar.add_cascade(label=_state.loc(u"Reports", 1), menu=reportmenu)


        # FONT MENU OPTIONS
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
        menubar.add_cascade(label=_state.loc(u"Font", 1), menu=fontmenu)
#        fontsize.set(u'NSimSun 13')
#        setFont()

        # SETTINGS MENU OPTIONS
        settingsmenu = Tk.Menu(menubar, tearoff=0)
        settingsmenu.add_radiobutton(label=u'Chinese', variable='lang_select',
            command=lambda: setLang(u"Chinese"), value=u'Chinese')
        settingsmenu.add_radiobutton(label=u'English', variable='lang_select',
            command=lambda: setLang(u"English"), value=u'English')
        menubar.add_cascade(label=_state.loc(u"Settings", 1), menu=settingsmenu)

        # HELP MENU OPTIONS
        helpmenu = Tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label=_state.loc(u"About", 1), command=about)
        menubar.add_cascade(label=_state.loc(u"Help", 1), menu=helpmenu)


        # SET AND SHOW MENU
        self.config(menu=menubar)
        self.geometry('1200x740')


        # SET MAIN NOTEBOOK
        nb = ttk.Notebook()
        #---------- Add PO (main) frame
        #XXX: merging Purchases & Sales frames to PO frame in version 0.3
        _state.po_frame = ttk.Frame(nb)
        frames.po_frame.create(_state)
        nb.add(_state.po_frame, text='PO', underline=0)
        #---------- Add Sales frame
#        frame = ttk.Frame(nb)
#        get_sales_frame(frame)
#        nb.add(frame, text='Sales', underline=0)
        #---------- Add Pending info frame
#        frame = ttk.Frame(nb)
#        frame_pending.get_pending_frame(frame, dmv2)
#        nb.add(frame, text='Pending', underline=2)
        #TODO:---------- Add In-Out Records info frame
#        frame = ttk.Frame(nb)
#        frame_pending.get_tablet_frame(frame, dmv2)
#        nb.add(frame, text='Tablet Data', underline=0)
        #TODO:---------- Add Company data edit frame
#        frame = ttk.Frame(nb)
#        frame_company_editor.get_company_editor(frame, dmv2)
#        nb.add(frame, text='Catalog', underline=0)
        #TODO:---------- Add Warehouse management frame


        #--------- Set arrangement of notebook frames
        nb.pack(side=Tk.RIGHT, fill=Tk.BOTH, expand=Tk.Y, padx=2, pady=3)


    def endsession(self):
        self.quit()

    def change_db(self):
        self._.dbm.change_db()
        try:
            self._.refresh()
        except:
            print("'refresh()' method not found in state object.")

        self.filemenu.entryconfig(0, label=self._.dbm.dbpath)



def set_report_location():
    FILE_OPTS = dict(
        title = u'PDF save location.',
        initialdir = os.path.expanduser('~') + '/Desktop/',
        mustexist = True
    )
    if settings.load().get(u'pdfpath'):
        FILE_OPTS['initialdir'] = settings.load()[u'pdfpath']

    outdir = tkFileDialog.askdirectory(**FILE_OPTS)

    settings.update(pdfpath=outdir)


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




def about():
    '''Display program author and date.'''
    tkMessageBox.showinfo('About', '台茂化工\nWritten by Jay W Johnson\n2014')




if __name__ == '__main__':
    app = TaimauApp(None, debug=True)
    app.title('Taimau')
    app.mainloop()

