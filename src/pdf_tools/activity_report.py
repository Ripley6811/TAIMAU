#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Tix
from utils import date_picker, settings
import fpdf
import tkFileDialog, tkMessageBox
import os
import subprocess

def main(_, records=[]):
    pdfwin = Tix.Toplevel(width=700)
    pdfwin.title(u"New Purchase Order (PO) Form")
    pdfwin.focus_set()


    tl = Tix.Label(pdfwin, textvariable=_.loc(u"Start date"))
    tl.grid(row=0, column=0, columnspan=2)
    startdate = date_picker.Calendar(pdfwin)
    startdate.grid(row=1, rowspan=6, column=0, columnspan=2)

    tl = Tix.Label(pdfwin, textvariable=_.loc(u"End date"))
    tl.grid(row=0, column=2, columnspan=2)
    enddate = date_picker.Calendar(pdfwin)
    enddate.grid(row=1, rowspan=6, column=2, columnspan=2)



    tb = Tix.Button(pdfwin, textvariable=_.loc(u"\u2713 Submit"), bg=u'light salmon')
    tb['command'] = lambda: submit()
    tb.grid(row=10, column=0, columnspan=4, sticky='ew')

    def submit(separate_products=False):
        #TODO: Add client branch column

        # Retrieve shipment data within date range
        session = _.dbm.session
        Order = _.dbm.Order
        ShipmentItem = _.dbm.ShipmentItem
        Shipment = _.dbm.Shipment

        q = session.query(ShipmentItem)
        q = q.join(Shipment)
        q = q.filter(Shipment.shipmentdate >= startdate.selection)
        q = q.filter(Shipment.shipmentdate <= enddate.selection)
        q = q.order_by(Shipment.shipmentdate)
        q = q.order_by(Shipment.shipment_no)
        q = q.join(Order).filter_by(group=_.curr.cogroup.name)
        if _.sc_mode == u'c':
            q = q.filter_by(is_sale=True)
        else:
            q = q.filter_by(is_purchase=True)
        q = q.all()

        # Create dictionary
        dfkeys = [u'日期',u'出貨單號',u'品',u'數量',u'單位',u'SKU',u'單價',u'總價']
        df = dict()
        df[u'日期'] = [rec.shipment.shipmentdate for rec in q]
        df[u'出貨單號'] = [rec.shipment.shipment_no for rec in q]
        df[u'品'] = [rec.order.product.label() for rec in q]
        df[u'數量'] = [rec.qty*(rec.order.product.units if rec.order.product.unitpriced else 1) for rec in q]
        df[u'單位'] = [rec.order.product.UM if rec.order.product.unitpriced else rec.order.product.SKU for rec in q]
        df[u'SKU']  = [u'({} {})'.format(rec.qty,rec.order.product.SKU) if (rec.order.product.unitpriced and rec.order.product.SKU != u'槽車') else u'' for rec in q]
        df[u'單價'] = [rec.order.price for rec in q]
        df[u'總價'] = [u'{:,}'.format(rec.order.qty_quote(rec.qty)) for rec in q]
        sub_amt = sum([rec.order.qty_quote(rec.qty) for rec in q])
        try:
            df[u'數量'] = [int(rec) if float(rec).is_integer() else rec for rec in df[u'數量']]
        except:
            pass
        try:
            df[u'單價'] = [int(rec) if float(rec).is_integer() else rec for rec in df[u'單價']]
        except:
            pass

        # PDF class and settings
        font = r'C:\Windows\Fonts\simfang.ttf'
#        font = r'C:\Windows\Fonts\simkai.ttf'
        font = r'C:\Windows\Fonts\simhei.ttf'
        x =     [ 10, 36, 62,102,122,136,154,174]
        w =     [ 26, 26, 40, 20, 16, 18, 20, 24]
        align = ['C','C','L','R','L','C','R','R']
        class myPDF(fpdf.FPDF):
            def header(self):
                if _.sc_mode == u'c':
                    self.image(u'images/TaimauChemicals.png', 25, 5)
                    self.add_font(u'SimHei', 'B', font, uni=True) # Only .ttf and not .ttc
                    self.set_font(u'SimHei', 'B', 16)
                    self.set_xy(25, 25)
                    self.cell(40, 10, u'台茂化工儀器原料行', align='L')

                    # Client name
                    self.set_font(u'SimHei', 'B', 12)
                    self.set_xy(100, 14)
                    self.cell(40, 8, u'客戶: {}'.format(_.curr.cogroup.name))
                else:
                    self.add_font(u'SimHei', 'B', font, uni=True) # Only .ttf and not .ttc
                    self.set_font(u'SimHei', 'B', 16)
                    self.set_xy(25, 25)
                    self.cell(40, 10, u'確認表: {}'.format(_.curr.cogroup.name), align='L')

                    # Client name
                    self.set_font(u'SimHei', 'B', 12)
                    self.set_xy(100, 14)
                    self.cell(40, 8, u'客戶: {}'.format(u'台茂化工儀器原料行'))

                # Time period
                self.set_xy(100, 20)
                self.cell(50, 8, u'日期: {0} : {1.month}-{1.day}'.format(startdate.selection, enddate.selection))

                # Write a separation line
                FPDF.set_line_width(0.3)
                FPDF.line(10, 40, 200, 40)

                # Write column header
                for col, key in enumerate(dfkeys):
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
        last_manifest_no = None
        for row in range(len(q)):
            for col, key in enumerate(dfkeys):
                if col in (0,1) and unicode(df[u'出貨單號'][row]) == last_manifest_no and last_manifest_no not in (None, u''):
                    continue
                else:
                    if col == 1:
                        last_manifest_no = unicode(df[u'出貨單號'][row])
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
        FPDF.ln()


        FPDF.line(10, FPDF.get_y()+1, 200, FPDF.get_y()+1)
        FPDF.line(10, FPDF.get_y()+3, 200, FPDF.get_y()+3)
        FPDF.ln()

        aggregated = dict()
        for i, product in enumerate(df[u'品']):
            if product not in aggregated:
                aggregated[product] = [0, df[u'單位'][i], 0]
            aggregated[product][0] += df[u'數量'][i]
            aggregated[product][2] += int(''.join(df[u'總價'][i].split(',')))


        total = 0
        for key, vals in aggregated.iteritems():
            FPDF.set_x(x[2])
            FPDF.cell(w[2], 6, txt=key, align='L')
            FPDF.set_x(x[3])
            FPDF.cell(w[3], 6, txt=u'{:,}'.format(vals[0]), align='R')
            FPDF.set_x(x[4])
            FPDF.cell(w[4], 6, txt=u'{}'.format(vals[1]), align='L')
            FPDF.set_x(x[5])
            FPDF.cell(w[5], 6, txt=u'${:,}'.format(vals[2]), align='R')
            total += vals[2]
            FPDF.ln()


        FPDF.line(x[5], FPDF.get_y()+1, x[6], FPDF.get_y()+1)
        FPDF.line(x[5], FPDF.get_y()+2, x[6], FPDF.get_y()+2)
        FPDF.ln()
        FPDF.set_x(x[5])
        FPDF.cell(w[5], 6, txt=u'${:,}'.format(total), align='R')





        FILE_OPTS = dict(
            parent = _.po_frame,
            title = u'PDF name and location.',
            defaultextension = '.pdf',
            initialdir = os.path.expanduser('~') + '/Desktop/',
            initialfile = u'{}_{}_{}_{}'.format(_.curr.cogroup.name,
                                             u'Sales' if _.sc_mode == u'c' else u'Purchases',
                                             str(startdate.selection),
                                             str(enddate.selection)),
        )
        if settings.load().get(u'pdfpath'):
            FILE_OPTS['initialdir'] = settings.load()[u'pdfpath']

        pdfwin.destroy()

        outfile = tkFileDialog.asksaveasfilename(**FILE_OPTS)
        print outfile

        if os.path.exists(outfile):
            os.remove(outfile)
        if outfile and not os.path.exists(outfile):
            FPDF.output(name=outfile)

            if _.debug:
                print u'start {0}'.format(outfile.replace("/","\\"))
                print u'start {0}'.format(os.path.normpath(outfile))
            try:
                subprocess.call(['start', os.path.normpath(outfile)],
                                 shell=True)
            except:
                print u'Trying alternate subprocess command.'
                subprocess.call(['start', '/D'] +
                                list(os.path.split(outfile.replace("/","\\"))),
                                shell=True)
        else:
            tkMessageBox.showinfo(u'',u'Canceled PDF creation.')