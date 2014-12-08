#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
summary

Improvements over previous version include:
- "state" object (single underscore) that maintains and passes session info
between all modules.
- Translation module for registering StringVars and easily switch languages.
- "settings" that are saved and loaded from file using the json package.

:REQUIRES:
    - Database using TM2014_tables_v3.py
    - FPDF for create PDF files.


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
# Show full path to this file location.
print os.path.abspath(__file__)
# Change working directory one level up when running this module.
if __name__ == '__main__':
    os.chdir(os.pardir)
# Make a "data" folder for storing default database.
if not os.path.exists('data'):
    os.mkdir('data')
# Make a "png" folder for images used in PDF reports.
if not os.path.exists('png'):
    os.mkdir('png')

import datetime
import tkMessageBox
import tkFileDialog
import ttk
import tkFont
import xlwt
import Tix
#import analytics

import db_tools.db_manager as dbm
from pdf_tools import activity_report, product_QC_report
import frames.po_frame
import frames.product_frame
from utils.translate_term import localize, setLang
from utils import settings, check_for_update
#===============================================================================
# METHODS
#===============================================================================

# Container for passing state parameters
Info = type('struct', (), {})
Info = type('adict', (dict,), {'__getattr__': dict.__getitem__, '__setattr__': dict.__setitem__})
#NOTE: Create another internal Info type like this: var = Info(); var.x = type(var)()

# Alternatively can be created this way
class adict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


class TaimauApp(Tix.Tk):
    '''Main application.
    '''

    def __init__(self, parent, debug=False):

        Tix.Tk.__init__(self, parent)

        self.parent = parent
        self.option_add("*Font", "PMingLiU 13")
        ttk.Style().configure('.', font=tkFont.Font(family="PMingLiU", size=13))
        self.tk_setPalette(
                background=u'AntiqueWhite1',
                foreground=u'black',
                selectColor='white',
                activeForeground='black',
                selectBackground='black',
                selectForeground='yellow',
                disabledForeground='gray',
        )


        _ = Info()
        _.parent = self
        _.debug = debug # For console messages and English GUI
        _.font = u"NSimSun"
        _.loc = localize # Translation to Chinese
        _.dbm = dbm.db_manager() # Database API methods
        _.curr = Info() # For storage current company, list ID's, etc.
        _.getExtWin = getExtWin
        self._ = _


        # SET LANGUAGE SELECTION
        self.lang_select = Tix.StringVar()
        def switch_language(*args):
            new_lang = self.lang_select.get()
            settings.update(language=new_lang)
            setLang(new_lang)
        self.lang_select.trace_variable('w', switch_language)
        self.lang_select.set(settings.load().get(u'language', u'English'))


        # SET AUTO UPDATE OPTION
        self.auto_update_check = Tix.BooleanVar()
        self.auto_update_check.set(settings.load().get(u'auto_update_check', True))
        def switch_auto_update(*args):
            new_bool = not settings.load()[u'auto_update_check']
            settings.update(auto_update_check=new_bool)
        self.auto_update_check.trace_variable('w', switch_auto_update)



        #
        # SET UP MENU BAR
        #
        menubar = Tix.Menu(self)

        # FILE MENU OPTIONS: LOAD, SAVE, EXIT...
        filemenu = Tix.Menu(menubar, tearoff=0)
#        filemenu.add_command(label=_.loc(u"Change Database", 1), command=self.change_db)
        filemenu.add_command(label=_.loc(u"Exit", 1), command=self.endsession)
        menubar.add_cascade(label=_.loc(u"Main", 1), menu=filemenu)

        # REPORT MENU OPTIONS
        reportmenu = Tix.Menu(menubar, tearoff=0)
        reportmenu.add_command(label=u"Change location for saving reports",
                               command=set_report_location)
        reportmenu.add_command(label=u"Activity Report (PDF)",
                               command=lambda:activity_report.main(_))
        reportmenu.add_command(label=u"ASE Product QC (PDF)",
                               command=lambda:product_QC_report.main(_))
        reportmenu.add_command(label=u"Save client shipments to Excel (6 months).",
                               command=lambda:sales_shipments_to_excel(_))
        reportmenu.add_command(label=u"Save incoming shipments to Excel (6 months).",
                               command=lambda:purchases_shipments_to_excel(_))
        reportmenu.add_command(label=u"Save all products to Excel file.",
                               command=lambda:save_products_to_excel(_))

        reportmenu.add_command(label=u"Save all static data to an Excel file.",
                               command=lambda:staticDB2excel(_))
        reportmenu.add_command(label=u"Save all active data to an Excel file.",
                               command=lambda:activeDB2excel(_))

#        reportmenu.add_command(label="Report3", command=None, state=Tk.DISABLED)
#        reportmenu.add_command(label="Report4", command=None, state=Tk.DISABLED)
        menubar.add_cascade(label=_.loc(u"Reports", 1), menu=reportmenu)


        # FONT MENU OPTIONS
#        def setFont():
#            self.option_add("*Font", fontsize.get())
#        fontmenu = Tix.Menu(menubar, tearoff=0)
#        fontsize = Tix.StringVar()
#        fontmenu.add_radiobutton(label=u'Verdana 12', variable=fontsize,
#                                 command=setFont, value=u'Verdana 12')
#        fontmenu.add_radiobutton(label=u'PMingLiU 13', variable=fontsize,
#                                 command=setFont, value=u'PMingLiU 13')
#        fontmenu.add_radiobutton(label=u'NSimSun 13', variable=fontsize,
#                                 command=setFont, value=u'NSimSun 13')
#        menubar.add_cascade(label=_.loc(u"Font", 1), menu=fontmenu)
#        fontsize.set(u'NSimSun 13')
#        setFont()

        # SETTINGS MENU OPTIONS
        settingsmenu = Tix.Menu(menubar, tearoff=0)
        lang_menu = Tix.Menu(settingsmenu, tearoff=0)
        settingsmenu.add_cascade(label=_.loc(u"Language", 1), menu=lang_menu)
        update_menu = Tix.Menu(settingsmenu, tearoff=0)
        settingsmenu.add_cascade(label=_.loc(u"Update", 1), menu=update_menu)
        lang_menu.add_radiobutton(label=u'繁體中文', variable=self.lang_select,
            value=u'Chinese',
            selectcolor=u'black')
        lang_menu.add_radiobutton(label=u'English', variable=self.lang_select,
            value=u'English',
            selectcolor=u'black')
        update_menu.add_command(label=_.loc(u"Check for update", 1), command=self.version_update)
        update_menu.add_separator()
        update_menu.add_checkbutton(label=_.loc(u'Auto check for updates',1),
            onvalue=True, offvalue=False, variable=self.auto_update_check,
            selectcolor=u'black')
        settingsmenu.add_separator()
        settingsmenu.add_command(label=_.loc(u'PO List Ordering', 1),
            command=lambda: setPOorder(_))
        menubar.add_cascade(label=_.loc(u"Settings", 1), menu=settingsmenu)



        # HELP MENU OPTIONS
        helpmenu = Tix.Menu(menubar, tearoff=0)
        helpmenu.add_command(label=_.loc(u"About", 1), command=about)
        menubar.add_cascade(label=_.loc(u"Help", 1), menu=helpmenu)

        #
        menubar.add_separator()
        menubar.add_separator()
        menubar.add_command(label=u'DATABASE={}'.format(_.dbm.dbpath),
                            background=u'LightSkyBlue1')
        self.menubar = menubar


        # SET AND SHOW MENU
        self.config(menu=menubar)
        try:
            self.geometry(settings.load()['geometry'])
        except KeyError:
            #Default geometry
            self.geometry('1240x800')


        # SET MAIN NOTEBOOK
        nb = ttk.Notebook()
        #---------- Add PO (main) frame
        #XXX: merging Purchases & Sales frames to PO frame in version 0.3
        _.po_frame = ttk.Frame(nb)
        frames.po_frame.create(_)
        nb.add(_.po_frame, text='PO')
        #---------- Add Product frame
        _.product_frame = ttk.Frame(nb)
        frames.product_frame.create(_)
        nb.add(_.product_frame, text=_.loc(u'Products',1))
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
        nb.pack(side='right', fill='both', expand='y', padx=2, pady=3)

        if self.auto_update_check.get():
            check_for_update.update(self._, settings, silent=True)


    def endsession(self):
        settings.update(geometry=self.geometry())
        self._.dbm.session.close()
        self._.parent.destroy()
        del self._
        self.quit()

    def change_db(self):
        #self._.curr.cogroup = None

        self._.dbm.change_db()
        try:
            for ref in self._.refresh:
                ref()
        except:
            print("'refresh()' method not found in state object.")

        # TODO: Bug in update. Suddenly not working...
        self.menubar.entryconfig(8, label=u'DATABASE={}'.format(self._.dbm.dbpath))


    def version_update(self):
        check_for_update.update(self._, settings)


def getExtWin(_, co_name=u'', title=u'', width=700, destroy=False):
    '''Create new external window or "set focus" if one is already open.

    See if an external window is open already. If window is not associated
    with the currently selected company in the main window, then destroy it
    and create a new external window. Otherwise set focus on window for user
    to see it and exit. This allows the number of external windows to be
    limited to one (as long as they all use the "_.extwin" reference).

    Company association is set by putting the CoGroup (Company Group) name
    in the title of the external window.

    Set 'destroy' to True to unconditionally close any open external window
    and create a new one.

    Returns reference to a new window (also accessible by "_.extwin") or
    "False" if a new window is not created.
    '''
    #### LIMIT EXTERNAL WINDOW TO ONE ####
    try:
        if _.extwin.state() == 'normal' and not destroy:
            if _.curr.cogroup.name in _.extwin.title():
                # Focus existing frame and return
                _.extwin.focus_set()
                return False
    except KeyError:
        # Continue with frame creation
        pass
    except Tix.TclError:
        pass

    #### CREATE NEW EXTERNAL WINDOW ####
    # Destroy existing frame and make new one
    try:
        _.extwin.destroy()
    except KeyError:
        pass
    _.extwin = Tix.Toplevel(_.parent, width=width)
    # Add title string
    if co_name:
        title = u'{}: {}'.format(co_name, title)
    _.extwin.title(title)
    # Place new window over main window
    xoffset = _.parent.winfo_rootx()+100
    yoffset = _.parent.winfo_rooty()
    _.extwin.geometry(u'+{}+{}'.format(xoffset, yoffset))
    # Set focus and return
    _.extwin.focus_set()
    return _.extwin



def setPOorder(_):
    cogroup = _.curr.cogroup
    order_list = cogroup.openpurchases if _.sc_mode == "s" else cogroup.opensales

    if not getExtWin(_, co_name=cogroup.name, title=u'PO ordering'):
        return

    ordering = []
    for row, order in enumerate(order_list):
        ordering.append(Tix.StringVar())

        options = ___ = dict(master=_.extwin)
        ___['font'] = (_.font, 14)
        ___['text'] = u'{}:{} {}'.format(order.orderID,
                      order.product.name, order.product.specs)
        Tix.Label(**options).grid(row=row, column=0, sticky='w')

        options = ___ = dict(master=_.extwin)
        ___['bg'] = u'moccasin'
        ___['font'] = (_.font, 14)
        ___['width'] = 5
        ___['textvariable'] = ordering[-1]
        Tix.Entry(**options).grid(row=row, column=1, sticky='w')

    options = ___ = dict(master=_.extwin)
    ___['bg'] = u'lawn green'
    ___['font'] = (_.font, 16, 'bold')
    ___['textvariable'] = _.loc(u"\u2713 Submit")
    ___['command'] = lambda *args: submit(ordering)
    Tix.Button(**options).grid(row=101, column=0)

    options = ___ = dict(master=_.extwin)
    ___['bg'] = u'tomato'
    ___['font'] = (_.font, 16, 'bold')
    ___['textvariable'] = _.loc(u'Clear')
    ___['command'] = lambda *args: [sv.set(u'') for sv in ordering]
    Tix.Button(**options).grid(row=101, column=1)

    # Get existing ordering if defined previously.
    po_order = settings.load().get('po_order', {})
    nset = po_order.get(cogroup.name, None)
    if nset:
        for val, sv in zip(nset, ordering):
            sv.set(str(val))

    def submit(ordering):
        try:
            unused = range(1,100)
            # Convert entries to integers or None.
            ordering = [int(sv.get()) if sv.get().isdigit() else None for sv in ordering]
            # Removed used integers from the unused list.
            [unused.remove(val) for val in ordering if isinstance(val, int)]
            # Fill in blank (None) entries with unused integers.
            ordering = [unused.pop(0) if val == None else val for val in ordering]
            # Save ordering.
            po_order[cogroup.name] = ordering
            settings.update(po_order = po_order)

            _.extwin.destroy()
        except ValueError:
            pass



def set_report_location():
    FILE_OPTS = dict(
        title = u'PDF save location.',
        initialdir = os.path.expanduser('~') + '/Desktop/',
        mustexist = True
    )
    if settings.load().get(u'pdfpath'):
        FILE_OPTS['initialdir'] = settings.load()[u'pdfpath']

    outdir = os.path.normpath(tkFileDialog.askdirectory(**FILE_OPTS))

    settings.update(pdfpath=outdir)


def sales_shipments_to_excel(_):
    save_shipments_to_excel(_, is_sale=True)


def purchases_shipments_to_excel(_):
    save_shipments_to_excel(_, is_sale=False)


def save_shipments_to_excel(_, is_sale=None, days=180):
    '''Save all activity in the last half-year to Excel.
    Order by delivery date.

    #TODO: Add first page with everyone combined
    #TODO: Make columns for every parameter and add header
    '''
    wb = xlwt.Workbook()
    cogroups = _.dbm.cogroups()
    cutoff = datetime.date.today() - datetime.timedelta(days)

    style = xlwt.XFStyle()
    style.num_format_str = '"$"#,##0.00_);("$"#,##'

    for group in cogroups:
        query = _.dbm.session.query(_.dbm.Order)
        query = query.filter_by(group=group.name, is_sale=is_sale)
        query = query.filter(_.dbm.Order.duedate > cutoff)
        orders = query.order_by(_.dbm.Order.duedate).all()

        if orders:
            #Make sheet with cogroup name
            ws = wb.add_sheet(group.name)
        else:
            continue
        row = 0
        for order in orders:
            for shipmentitem in order.shipments:
                ws.write(row, 0, str(shipmentitem.shipment.shipmentdate))
                ws.write(row, 1, unicode(order.seller))
                ws.write(row, 2, '->')
                ws.write(row, 3, unicode(order.buyer))
                ws.write(row, 4, unicode(order.product.name))
                qty = shipmentitem.qty
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

def save_products_to_excel(_):
    '''Save all products to Excel.
    #TODO: Line between companies'''
    wb = xlwt.Workbook()

    style = xlwt.XFStyle()
    style.num_format_str = '"$"#,##0.00_);("$"#,##'
    def_style = xlwt.XFStyle()


    query = _.dbm.session.query(_.dbm.Product)
    recs = query.order_by(_.dbm.Product.group).all()

    ws = wb.add_sheet(u'Products')

    headers = _.dbm.Product.__table__.columns.keys()

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

def staticDB2excel(_):
    '''Export entire database to an Excel file.'''
    wb = xlwt.Workbook()

    tables = {
        u'Product': _.dbm.Product,
        u'CoGroup': _.dbm.CoGroup,
        u'Branch': _.dbm.Branch,
        u'Contact': _.dbm.Contact,
        u'Stock': _.dbm.Stock,
        u'Vehicle': _.dbm.Vehicle,
    }

    for key, val in tables.iteritems():
        query = _.dbm.session.query(val)
        recs = query.all()

        ws = wb.add_sheet(key)

        headers = val.__table__.columns.keys()

        row = 0
        for col, head in enumerate(headers):
            ws.write(row, col, head)
        for rec in recs:
            row += 1
            for col, head in enumerate(headers):

                ws.write(row, col, rec.__dict__[head])


    filename = u'TAIMAU_DB_Static.xls'

    base = os.getcwd()
    path = os.path.join(base, filename)
    wb.save(path)
    os.system('start "'+ base + '" ' + filename)

def activeDB2excel(_):
    '''Export entire database to an Excel file.'''
    wb = xlwt.Workbook()

    tables = {
        u'Order': _.dbm.Order,
        u'Shipment': _.dbm.Shipment,
        u'ShipmentItem': _.dbm.ShipmentItem,
        u'Invoice': _.dbm.Invoice,
        u'InvoiceItem': _.dbm.InvoiceItem,
    }

    for key, val in tables.iteritems():
        query = _.dbm.session.query(val)
        recs = query.all()

        ws = wb.add_sheet(key)

        headers = val.__table__.columns.keys()

        row = 0
        for col, head in enumerate(headers):
            ws.write(row, col, head)
        for rec in recs:
            row += 1
            for col, head in enumerate(headers):

                ws.write(row, col, rec.__dict__[head])


    filename = u'TAIMAU_DB_Active.xls'

    base = os.getcwd()
    path = os.path.join(base, filename)
    wb.save(path)
    os.system('start "'+ base + '" ' + filename)

def about():
    '''Display program author and date.'''
    tkMessageBox.showinfo('About', '台茂化工資料庫\nWritten by Jay W Johnson\n2014')




if __name__ == '__main__':
    app = TaimauApp(None, debug=False)
    app.title('Taimau')
    app.mainloop()

