#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
summary

description

:REQUIRES:
    - PyFPDF ("C:\Python\easy_install fpdf")

:TODO:

:AUTHOR: Ripley6811
:ORGANIZATION: None
:CONTACT: python@boun.cr
:SINCE: Sat Jun 07 08:17:53 2014
:VERSION: 0.1
"""

import Tix
from Tix import E, W, TOP, END, X, Y, EXTENDED, LEFT, ACTIVE, CENTER
import pandas as pd
import fpdf
import tkFileDialog, tkMessageBox
import os
import date_picker as dp
import datetime as dt
import product_qc_pdf as qcpdf

def create_frame(frame, info):
    top = Tix.Frame(frame)
    top.pack(side=TOP, fill=X)
    text = Tix.Text(top, height=8)
    text.pack(side=LEFT, fill=Y)

    Tix.Button(top, text=u'創造PDF: Transactions in Date Range',
               command=lambda: checklist_pdf()).pack(fill=X)
    Tix.Button(top, text=u'(ASE)創造PDF: Product Test Report',
               command=lambda: product_analysis_pdf()).pack(fill=X)
    Tix.Button(top, text=u'3').pack(fill=X)
    Tix.Button(top, text=u'4').pack(fill=X)

    def product_analysis_pdf():
        # Currently aimed at producing product testing results for ASE
        # products but could change it to work for any product in the
        # future.
        #
        pdfwin = Tix.Toplevel(width=700)
        pdfwin.title(u"New Product Analysis Report")


        company_w = Tix.Select(pdfwin, label=u'公司',
                               radio=True, orientation=Tix.VERTICAL)
        company_w.add(u'台茂化工儀器原料行', text=u'台茂化工儀器原料行')
        company_w.invoke(u'台茂化工儀器原料行')
        company_w.add(u'富茂工業原料行', text=u'富茂工業原料行')
        company_w.add(u'永茂企業行', text=u'永茂企業行')
        company_w.grid(row=0, column=0, columnspan=3, sticky=W+E)

        pname_SV = Tix.StringVar()
#        pname_SV.trace('w', lambda: autofill())
        product_w = Tix.ComboBox(pdfwin, label=u'品名', dropdown=True,
                                 editable=False,
                                 variable=pname_SV, command=lambda *args: autofill())
#        product_w.entry.configure(textvariable=pname_SV)
        ASE = info.dmv2.session.query(info.dmv2.CoGroup).get(u'ASE')
        MPN_list = []
        for ea in ASE.products:
            product_w.insert(END, ea.label())
            MPN_list.append(ea.MPN)
        product_w.grid(row=1, column=0, columnspan=3, sticky=W+E)
#        ASE_w = Tix.LabelEntry(pdfwin, label=u'料號')
#        ASE_w.grid(row=2, column=0, sticky=W+E)
        lot_w = Tix.LabelEntry(pdfwin, label=u'批號')
        lot_w.grid(row=3, column=0, columnspan=3, sticky=W+E)
        qty_w = Tix.LabelEntry(pdfwin, label=u'數量')
        qty_w.grid(row=4, column=0, columnspan=3, sticky=W+E)
        tester_w = Tix.LabelEntry(pdfwin, label=u'取樣人員')
        tester_w.grid(row=5, column=0, columnspan=3, sticky=W+E)
        gridlabels = [u'檢 驗 項 目', u'規 格', u'檢 驗 結 果']
        for i in range(3):
            Tix.Label(pdfwin, text=gridlabels[i]).grid(row=6, column=i)

        egrid = []
        for i in range(8):
            egrid.append([])
            for j in range(3):
                egrid[i].append(Tix.Entry(pdfwin, justify=CENTER))
                egrid[i][j].grid(row=i+10, column=j)


        # Restore previous entries for a particular product
        def autofill():
            # Retrieve product record.
            MPN = MPN_list[product_w.slistbox.listbox.index(ACTIVE)]
            p_rec = info.dmv2.get_product(MPN)
            _ = p_rec.json()
            if not _:
                return
            if _.get('amount'):
                qty_w.entry.delete(0, END)
                qty_w.entry.insert(0, _['amount'])
            if _.get('tester'):
                tester_w.entry.delete(0, END)
                tester_w.entry.insert(0, _['tester'])
            if _.get('lot_no'):
                lot_w.entry.delete(0, END)
                lot_w.entry.insert(0, _['lot_no'])
            if _.get('test_params'):
                tp = _['test_params']
                for i in range(len(egrid)):
                    for j in range(len(egrid[0])):
                        egrid[i][j].delete(0, END)
                        egrid[i][j].insert(0, tp[i][j])


        submit_w = Tix.Button(pdfwin, text=u'提交')
        submit_w['command'] = lambda: submit()
        submit_w.grid(row=50, column=0, columnspan=3)

        def submit():
            # Convert matrix of entry widgets into matrix of values.
            for i in range(8):
                for j in range(3):
                    egrid[i][j] = egrid[i][j].get()
            # Retrieve product record.
            MPN = MPN_list[product_w.slistbox.listbox.index(ACTIVE)]
            p_rec = info.dmv2.get_product(MPN)
            info.dmv2.session.commit()
            # Create dictioinary of values to pass to pdf writing method.
            _ = dict(
                company=company_w['value'],
                product=p_rec.label(),
                ASE_pn=p_rec.ASE_PN,
                lot_no=lot_w.entry.get(),
                amount=qty_w.entry.get(),
                tester=tester_w.entry.get(),

                test_params=egrid,
            )

            qcpdf.create_qc_pdf(**_)

            # Save options as JSON in product database record.
            del _['company']
            del _['product']
            del _['ASE_pn']
            # Update previous json
            p_rec.json(_)
            info.dmv2.session.commit()

            pdfwin.destroy()



    def checklist_pdf():
        pdfwin = Tix.Toplevel(width=700)
        pdfwin.title(u"New Purchase Order (PO) Form")

        startdate = Tix.StringVar()
        enddate = Tix.StringVar()

        def date_picker(tvar=None):
            cal = dp.Calendar(pdfwin, textvariable=tvar)
            cal.grid(row=0, column=0, rowspan=3, columnspan=3, sticky=W+E)

        Tix.Label(pdfwin, text=u'Start date').grid(row=0, column=0)
        b = Tix.Button(pdfwin, textvariable=startdate, bg='DarkGoldenrod1')
        b['command'] = lambda tv=startdate: date_picker(tv)
        b.grid(row=0, column=1)
        startdate.set(dt.date.today().replace(day=1))

        Tix.Label(pdfwin, text=u'End date').grid(row=1, column=0)
        b = Tix.Button(pdfwin, textvariable=enddate, bg='DarkGoldenrod1')
        b['command'] = lambda tv=enddate: date_picker(tv)
        b.grid(row=1, column=1)
        for day in range(31,26,-1):
            try:
                enddate.set(dt.date.today().replace(day=day))
                break
            except ValueError:
                continue

        tb = Tix.Button(pdfwin, text=u'Submit', bg=u'light salmon')
        tb['command'] = lambda: submit()
        tb.grid(row=2, column=0, columnspan=2, sticky=W+E)

        def submit(separate_products=False):
            #TODO: Add option to order by product and date and give totals.
            #TODO: Add client branch column

            # Retrieve shipment data within date range
            session = info.dmv2.session
            Order = info.dmv2.Order
            Shipment = info.dmv2.Shipment
            sdate = dt.date(*map(int,startdate.get().split('-')))
            edate = dt.date(*map(int,enddate.get().split('-')))

            q = session.query(Shipment).filter(Shipment.shipmentdate >= sdate)
            q = q.filter(Shipment.shipmentdate <= edate)
            q = q.order_by(Shipment.shipmentdate)
            q = q.join(Order).filter_by(group=info.curr_company, is_sale=True)
            q = q.all()

            # Create Pandas DataFrame for analysis (if needed)
            df = pd.DataFrame()
            df[u'日期'] = [rec.shipmentdate for rec in q]
            df[u'出貨單號'] = [rec.shipmentID for rec in q]
            df[u'品名'] = [rec.order.product.label() for rec in q]
            df[u'數量'] = [rec.sku_qty*(rec.order.product.units if rec.order.product.unitpriced else 1) for rec in q]
            df[u'單位'] = [rec.order.product.SKUlabel() for rec in q]
            df[u'SKU']  = [u'({} {})'.format(rec.sku_qty,rec.order.product.SKU) if (rec.order.product.unitpriced and rec.order.product.SKU != u'槽車') else u'' for rec in q]
            df[u'單價'] = [rec.order.price for rec in q]
            df[u'總價'] = [u'{:,}'.format(rec.order.qty_quote(rec.sku_qty)) for rec in q]
            sub_amt = sum([rec.order.qty_quote(rec.sku_qty) for rec in q])
            print df

            # PDF class and settings
            font = r'C:\Windows\Fonts\simfang.ttf'
#            font = r'C:\Windows\Fonts\simkai.ttf'
            font = r'C:\Windows\Fonts\simhei.ttf'
            x =     [ 10, 36, 62,102,122,136,154,174]
            w =     [ 26, 26, 40, 20, 16, 18, 20, 24]
            align = ['C','C','L','R','L','C','R','R']
            class myPDF(fpdf.FPDF):
                def header(self):
                    self.image(u'TaimauChemicals.png', 25, 5)
                    self.add_font(u'SimHei', 'B', font, uni=True) # Only .ttf and not .ttc
                    self.set_font(u'SimHei', 'B', 16)
                    self.set_xy(25, 25)
                    self.cell(40, 10, u'台茂化工儀器原料行', align='L')

                    # Client name
                    self.set_font(u'SimHei', 'B', 12)
                    self.set_xy(100, 14)
                    self.cell(40, 8, u'客戶名稱: {}'.format(info.curr_company))

                    # Time period
                    self.set_xy(100, 20)
                    self.cell(50, 8, u'日期區間: {} : {}'.format(sdate, edate))

                    # Write a separation line
                    FPDF.set_line_width(0.3)
                    FPDF.line(10, 40, 200, 40)

                    # Write column header
                    for col, key in enumerate(df.keys()):
                        FPDF.set_xy(x[col], 42)
                        FPDF.cell(w[col], 5, txt=key, align='C')
                    # Write a separation line
                    FPDF.set_line_width(0.1)
                    FPDF.line(10, 48, 200, 48)

                    # Set starting position for data.
                    self.set_y(50)
                def footer(self):
                    self.set_font(u'SimHei', 'B', 10)
                    self.set_xy(0, -12)
                    self.cell(0, 10, txt=u'Page {}'.format(self.page), align='C')

            # Create PDF
            FPDF = myPDF('P','mm','A4')
            FPDF.alias_nb_pages()
            FPDF.add_font('SimHei', '', font, uni=True) # Only .ttf and not .ttc
            FPDF.set_font('SimHei', '', 12)
            FPDF.add_page() # Adding a page also creates a page break from last page

            # Write data row by row
            for row in range(len(q)):
                for col, key in enumerate(df.keys()):
                    txt = unicode(df[key][row])
                    FPDF.set_x(x[col])
                    FPDF.cell(w[col], 6, txt=txt, align=align[col])
                FPDF.ln()
            FPDF.set_line_width(0.1)
            FPDF.line(10, FPDF.get_y()+1, 200, FPDF.get_y()+1)
            FPDF.line(10, FPDF.get_y()+3, 200, FPDF.get_y()+3)
            FPDF.ln()
            FPDF.set_x(x[5])
            FPDF.cell(w[5], 6, txt=u'合 計:', align=align[5])
            FPDF.set_x(x[7])
            FPDF.cell(w[7], 6, txt=u'{:,}'.format(sub_amt), align=align[7])
            FPDF.ln()
            FPDF.set_x(x[5])
            FPDF.cell(w[5], 6, txt=u'稅 捐:', align=align[5])
            FPDF.set_x(x[7])
            tax_amt = int(round(sub_amt * 0.05))
            FPDF.cell(w[7], 6, txt=u'{:,}'.format(tax_amt), align=align[7])
            FPDF.ln()
            FPDF.set_x(x[5])
            FPDF.cell(w[5], 6, txt=u'總 計:', align=align[5])
            FPDF.set_x(x[7])
            tot_amt = int(sub_amt + tax_amt)
            FPDF.cell(w[7], 6, txt=u'{:,}'.format(tot_amt), align=align[7])




            FILE_OPTS = dict(
                parent = frame,
                title = u'PDF name and location.',
                defaultextension = '.pdf',
                initialdir = os.path.expanduser('~') + '/Desktop/',
                initialfile = u'{}_Summary_{}_{}'.format(info.curr_company,
                                                         str(sdate),
                                                         str(edate)),
            )
            pdfwin.destroy()

            outfile = tkFileDialog.asksaveasfilename(**FILE_OPTS)
            if outfile and not os.path.exists(outfile):
                FPDF.output(name=outfile)
            else:
                tkMessageBox.showinfo(u'',u'Canceled PDF creation.')




    midbar = Tix.Frame(frame)
    midbar.pack(side=TOP, fill=X)

    editPO = Tix.Button(midbar, text=u"編輯紀錄", bg=u'light salmon')
    editPO.pack(side=LEFT, fill=X)
    makeManifest = Tix.Button(midbar, text=u"創造出貨表", bg=u'light salmon')
    makeManifest.pack(side=LEFT, fill=X)

    def show_selection():
#        print tree.hlist.cget('value')
        print tree.hlist.info_selection()
        print tree.hlist.item_configure('5774', 0)
    editPO['command'] = show_selection

    # Headers and (column number, col width)
    H = {
        u'No.'  : (0, 18),
        u'Date' : (1, 12),
        u'品名' : (2, 24),
        u'數量' : (3, 10),
        u'單位' : (4, 8),
        u'價格' : (5, 10),
        u'總價' : (6, 14),
        u'全出貨' : (7, 6),
        u'全發票' : (8, 6),
        u'PAID' : (9, 6),
        u''     : (10, 10)
    }
    tree = Tix.Tree(frame, options='columns {}'.format(len(H)), height=1000)
    tree.pack(expand=1, fill=Tix.BOTH, side=Tix.TOP)
    tree['opencmd'] = lambda dir=None, w=tree: opendir(w, dir)
    tree.hlist['header'] = True
    tree.hlist['separator'] = '~' # Default is gray
    tree.hlist['background'] = 'white' # Default is gray
    tree.hlist['selectforeground'] = 'white' # Default is gray
    tree.hlist['selectmode'] = EXTENDED # Select multiple items
    tree.hlist['indent'] = 14 # Adjust indentation of children
    tree.hlist['wideselect'] = 1 # Color selection from end to end
    tree.hlist['font'] = info.settings.font
    params = dict(
        itemtype=Tix.TEXT,
        refwindow=tree.hlist,
        font=info.settings.font,
    )
    styleRorder = Tix.DisplayStyle(anchor=Tix.E, bg=u'white', **params)
    styleCorder = Tix.DisplayStyle(anchor=Tix.CENTER, bg=u'white', **params)
    styleLorder = Tix.DisplayStyle(anchor=Tix.W, bg=u'white', **params)
    styleRship = Tix.DisplayStyle(anchor=Tix.E, bg=u'honeydew2', **params)
    styleCship = Tix.DisplayStyle(anchor=Tix.CENTER, bg=u'honeydew2', **params)
    styleLship = Tix.DisplayStyle(anchor=Tix.W, bg=u'honeydew2', **params)
    styleRinv = Tix.DisplayStyle(anchor=Tix.E, bg=u'PeachPuff2', **params)
    styleCinv = Tix.DisplayStyle(anchor=Tix.CENTER, bg=u'PeachPuff2', **params)
    styleLinv = Tix.DisplayStyle(anchor=Tix.W, bg=u'PeachPuff2', **params)
    for key, (col, width) in H.iteritems():
        tree.hlist.header_create(col, text=key, headerbackground='cyan')
        tree.hlist.column_width(col, chars=width)

    # Add orders from current company selection.
    def refresh_po_tree():
        text.delete(0.0, END)
        for branch in info.dmv2.branches(info.curr_company):
            text.insert(END, u'{0.name}  {0.phone}\n'.format(branch))

        tree.hlist.delete_all()
        for rec in info.order_records:
            hid = str(rec.id)
            tree.hlist.add(hid, itemtype=Tix.TEXT, text=rec.orderID)
            tree.hlist.item_create(hid, col=H[u'Date'][0], text=rec.orderdate, itemtype=Tix.TEXT, style=styleCorder)
            tree.hlist.item_create(hid, col=H[u'品名'][0], text=rec.product.label())
            tree.hlist.item_create(hid, col=H[u'數量'][0], text=rec.totalskus, itemtype=Tix.TEXT, style=styleRorder)
            tree.hlist.item_create(hid, col=H[u'單位'][0], text=rec.product.UM)
            tree.hlist.item_create(hid, col=H[u'價格'][0], text=rec.price, itemtype=Tix.TEXT, style=styleRorder)
            tree.hlist.item_create(hid, col=H[u'總價'][0], text=u'{:,}'.format(int(round(rec.subtotal))), itemtype=Tix.TEXT, style=styleRorder)
            if rec.all_shipped():
                tree.hlist.item_create(hid, col=H[u'全出貨'][0], text=u'\u2713', itemtype=Tix.TEXT, style=styleCorder)
            if rec.all_invoiced():
                tree.hlist.item_create(hid, col=H[u'全發票'][0], text=u'\u2713', itemtype=Tix.TEXT, style=styleCorder)
            if rec.all_paid():
                tree.hlist.item_create(hid, col=H[u'PAID'][0], text=u'\u2713', itemtype=Tix.TEXT, style=styleCorder)
            if len(rec.shipments) + len(rec.invoices):
                tree.setmode(str(rec.id), 'open')
    info.method.refresh_po_tree = refresh_po_tree

    def opendir(tree, path):
        order = info.dmv2.session.query(info.dmv2.Order).get(int(path.split('~')[0]))
        if 'shipments' in path:
            entries = tree.hlist.info_children(path)
            if entries: # Show previously loaded entries
                for entry in entries:
                    tree.hlist.show_entry(entry)
                return
            else: # Add items to entries
                for rec in order.shipments:
                    hid = path+'~'+str(rec.id)
                    tree.hlist.add(hid, itemtype=Tix.TEXT, text=rec.shipmentID, style=styleLship)
                    tree.hlist.item_create(hid, col=H[u'Date'][0], text=rec.shipmentdate, itemtype=Tix.TEXT, style=styleCship)
                    tree.hlist.item_create(hid, col=H[u'品名'][0], text=rec.order.product.label(), itemtype=Tix.TEXT, style=styleCship)
                    tree.hlist.item_create(hid, col=H[u'數量'][0], text=rec.sku_qty, itemtype=Tix.TEXT, style=styleRship)
                    tree.hlist.item_create(hid, col=H[u'單位'][0], text=rec.order.product.UM, itemtype=Tix.TEXT, style=styleLship)
#                    tree.hlist.item_create(hid, col=H[u'價格'][0], text=rec.order.price)
        if 'invoices' in path:
            entries = tree.hlist.info_children(path)
            if entries: # Show previously loaded entries
                for entry in entries:
                    tree.hlist.show_entry(entry)
                return
            else: # Add items to entries
                for rec in order.invoices:
                    hid = path+'~'+str(rec.id)
                    tree.hlist.add(hid, itemtype=Tix.TEXT, text=rec.invoice_no, style=styleLinv)
                    tree.hlist.item_create(hid, col=H[u'Date'][0], text=rec.invoice.invoicedate, itemtype=Tix.TEXT, style=styleCinv)
                    tree.hlist.item_create(hid, col=H[u'品名'][0], text=rec.order.product.label(), itemtype=Tix.TEXT, style=styleCinv)
                    tree.hlist.item_create(hid, col=H[u'數量'][0], text=rec.sku_qty, itemtype=Tix.TEXT, style=styleRinv)
                    tree.hlist.item_create(hid, col=H[u'單位'][0], text=rec.order.product.UM, itemtype=Tix.TEXT, style=styleLinv)
                    tree.hlist.item_create(hid, col=H[u'價格'][0], text=rec.order.price, itemtype=Tix.TEXT, style=styleRinv)
                    tree.hlist.item_create(hid, col=H[u'總價'][0], text=u'{:,}'.format(rec.subtotal()), itemtype=Tix.TEXT, style=styleRinv)
                    if rec.invoice.paid:
                        tree.hlist.item_create(hid, col=H[u'PAID'][0], text=u'\u2713', itemtype=Tix.TEXT, style=styleCinv)
        else:
            entries = tree.hlist.info_children(path)
            if entries: # Show previously loaded entries
                for entry in entries:
                    tree.hlist.show_entry(entry)
                return
            else: # Add items to entries
                if len(order.shipments) > 0:
                    hid = path+'~shipments'
                    tree.hlist.add(hid, itemtype=Tix.TEXT, text=u'出貨單-----')
#                    tree.hlist.item_create(hid, col=H[u'Date'][0], text='------------------------------------')
                    tree.hlist.item_create(hid, col=H[u'品名'][0], text='-----({} records)-----'.format(len(order.shipments)), itemtype=Tix.TEXT, style=styleCorder)
                    tree.hlist.item_create(hid, col=H[u'數量'][0], text='({}'.format(order.qty_shipped()), itemtype=Tix.TEXT, style=styleRorder)
                    tree.hlist.item_create(hid, col=H[u'單位'][0], text='{})-----------'.format(order.product.UM), itemtype=Tix.TEXT, style=styleLorder)
#                    tree.hlist.item_create(hid, col=H[u'價格'][0], text='------------------------------------')
#                    tree.hlist.item_create(hid, col=H[u'總價'][0], text='------------------------------------')
                    tree.setmode(hid, 'open')
                    if len(order.shipments) < 5:
                        opendir(tree, hid)
                if len(order.invoices) > 0:
                    hid = path+'~invoices'
                    tree.hlist.add(hid, itemtype=Tix.TEXT, text=u'發票-------')
#                    tree.hlist.item_create(hid, col=H[u'Date'][0], text='------------------------------------')
                    tree.hlist.item_create(hid, col=H[u'品名'][0], text='-----({} records)-----'.format(len(order.invoices)), itemtype=Tix.TEXT, style=styleCorder)
                    tree.hlist.item_create(hid, col=H[u'數量'][0], text='({}'.format(order.qty_invoiced()), itemtype=Tix.TEXT, style=styleRorder)
                    tree.hlist.item_create(hid, col=H[u'單位'][0], text='{})-----------'.format(order.product.UM), itemtype=Tix.TEXT, style=styleLorder)
#                    tree.hlist.item_create(hid, col=H[u'價格'][0], text='------------------------------------')
                    tree.hlist.item_create(hid, col=H[u'總價'][0], text=u'({:,})'.format(order.qty_quote(order.total_paid())), itemtype=Tix.TEXT, style=styleRorder)
                    tree.setmode(hid, 'open')
                    if len(order.invoices) < 5:
                        opendir(tree, hid)
                separator = path+'~---'
                tree.hlist.add(separator, itemtype=Tix.TEXT, text=u'---------------------------------------')
                for i in range(1, len(H)):
                    tree.hlist.item_create(separator, col=i, text='----------------------------------------------')


























