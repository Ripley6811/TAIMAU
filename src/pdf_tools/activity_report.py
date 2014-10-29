#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Tix
from utils import date_picker, settings
import tkFileDialog, tkMessageBox
import os
import subprocess
import shutil

def main(_, records=[]):

    pdfwin = _.getExtWin(_, title=u"Select date range for report.")
    if not pdfwin:
        return


    tl = Tix.Label(pdfwin, textvariable=_.loc(u"Start date"))
    tl.grid(row=0, column=0, columnspan=2)
    startdate = date_picker.Calendar(pdfwin)
    startdate.grid(row=1, rowspan=6, column=0, columnspan=2)

    tl = Tix.Label(pdfwin, textvariable=_.loc(u"End date"))
    tl.grid(row=0, column=2, columnspan=2)
    enddate = date_picker.Calendar(pdfwin)
    enddate.grid(row=1, rowspan=6, column=2, columnspan=2)



    tb = Tix.Button(pdfwin, textvariable=_.loc(u"\u2713 Submit"), bg=u'light salmon')
#    tb['command'] = lambda: submit() # FPDF
    tb['command'] = lambda: submit_RLab(_,  # Report Lab
                                        start=startdate.selection,
                                        end=enddate.selection)
    tb.grid(row=10, column=0, columnspan=4, sticky='ew')




def get_savename(_, initialfilename):
        FILE_OPTS = ___ = dict(title = u'PDF name and location.')
        ___['parent'] = _.po_frame
        ___['defaultextension'] = '.pdf'
        ___['initialdir'] = os.path.expanduser('~') + '/Desktop/'
        ___['initialfile'] = initialfilename
        if settings.load().get(u'pdfpath'):
            ___['initialdir'] = settings.load()[u'pdfpath']


        outfile = os.path.normpath(tkFileDialog.asksaveasfilename(**FILE_OPTS))
        return outfile


def display_pdf(outfile):
    try:
        subprocess.call(['start', outfile],
                         shell=True)
    except:
        os.startfile(outfile)


def submit_RLab(_, start, end):

    #TODO: Add client branch column

    # Retrieve shipment data within date range
    session = _.dbm.session
    Order = _.dbm.Order
    ShipmentItem = _.dbm.ShipmentItem
    Shipment = _.dbm.Shipment

    q = session.query(ShipmentItem)
    q = q.join(Shipment)
    q = q.filter(Shipment.shipmentdate >= start)
    q = q.filter(Shipment.shipmentdate <= end)
    q = q.order_by(Shipment.shipmentdate)
    q = q.order_by(Shipment.shipment_no)
    q = q.join(Order).filter_by(group=_.curr.cogroup.name)
    if _.sc_mode == u'c':
        q = q.filter_by(is_sale=True)
    else:
        q = q.filter_by(is_purchase=True)
    q = q.all()

    # Create dictionary
    dfkeys = [u'日期',u'出貨單號',u'品名',u'數量',u'單位',u'SKU',u'單價',u'總價',u'發票號碼']
    df = dict()
    df[u'日期'] = [rec.shipment.shipmentdate for rec in q]
    df[u'出貨單號'] = [rec.shipment.shipment_no for rec in q]
    df[u'品名'] = [rec.order.product.label() for rec in q]
    df[u'數量'] = [rec.qty*(rec.order.product.units if rec.order.product.unitpriced else 1) for rec in q]
    df[u'單位'] = [rec.order.product.UM if rec.order.product.unitpriced else rec.order.product.SKU for rec in q]
    df[u'SKU']  = [u'({} {})'.format(rec.qty,rec.order.product.SKU) if (rec.order.product.unitpriced and rec.order.product.SKU != u'槽車') else u'' for rec in q]
    df[u'單價'] = [rec.order.price for rec in q]
    df[u'總價'] = [u'{:,}'.format(rec.order.qty_quote(rec.qty)) for rec in q]
    df[u'發票號碼'] = [rec.invoiceitem[0].invoice.invoice_no if len(rec.invoiceitem) else u'' for rec in q]
    sub_amt = sum([rec.order.qty_quote(rec.qty) for rec in q])
    try:
        df[u'數量'] = [int(rec) if float(rec).is_integer() else rec for rec in df[u'數量']]
    except:
        pass
    try:
        df[u'單價'] = [int(rec) if float(rec).is_integer() else rec for rec in df[u'單價']]
    except:
        pass



    def footer(self):
        self.set_font(u'SimHei', 'B', 10)
        self.set_xy(0, -12)
        self.cell(0, 10, txt=u'Page {}'.format(self.page), align='C')

    # Create PDF
    # For U.S. 8x11 use letter
    from reportlab.lib.pagesizes import A4 # Already the default, just for reference
    from reportlab.lib.units import mm

    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    pdfmetrics.registerFont(TTFont('KAIU', 'KAIU.ttf'))
    pdfmetrics.registerFont(TTFont('SimHei', 'simhei.ttf'))
    chfont = 'SimHei'

    from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Spacer, Table, TableStyle


    w = map(lambda x: x*mm, [ 26, 24, 36, 16, 10, 18, 16, 20, 24])
    x = 10 *mm
    x = [x]+[reduce(lambda a,b:a+b, w[:i+1])+x for i in range(len(w))][:-1]
    PL = 297*mm # Page Length

    def header(canvas, doc):
        imScale = lambda im: int(im * 0.66)
        if _.sc_mode == u'c':
            try:
                # Image( file, x, y, w=0, h=0)
                canvas.drawImage(u'png/logo.png', 25*mm, PL-18*mm, imScale(147), imScale(59))
            except IOError as e:
                print e
            canvas.setFont(chfont, 14)
            canvas.setFillColorRGB(0,71/256.,18/256.)
            canvas.drawString(25*mm, PL-22*mm, u'台茂化工儀器原料行')
            canvas.setFillColorRGB(0,0,0)

            # Client name
            canvas.setFont(chfont, 12)
            canvas.drawString(100*mm, PL-16*mm, u'客戶名稱: {}'.format(_.curr.cogroup.name))
        else:
            canvas.setFont(chfont, 16)
            canvas.drawString(25*mm, PL-25*mm, u'確認表: {}'.format(_.curr.cogroup.name))

            # Client name
            canvas.setFont(chfont, 12)
            canvas.drawString(100*mm, PL-16*mm, u'客戶名稱: {}'.format(u'台茂化工儀器原料行'))

        # Time period
        canvas.drawString(100*mm, PL-22*mm, u'日期: {0.year}年 {0.month}月{0.day}日-{1.month}月{1.day}日'.format(start, end))

        # Add page number at bottom
        canvas.setFont(chfont, 8)
        text = "Page {}".format(canvas.getPageNumber())
        canvas.drawCentredString(doc.leftMargin + doc.width/2, 10*mm, text)



    pdf = BaseDocTemplate('temp.pdf', pagesize=A4)

    frame = Frame(10*mm, pdf.bottomMargin, 190*mm, pdf.height,
               id='normal', showBoundary=0)
    template = PageTemplate(id='test', frames=frame, onPage=header)
    pdf.addPageTemplates([template])

    body = []

    #### CREATE SHIPMENT TABLE ####
    cells = [dfkeys]
    cellstyles = [('LINEABOVE', (0,0), (-1,0), 2, 'black'),
           ('LINEBELOW', (0,0), (-1,0), 1, 'black'),
           ('FONTNAME', (0,0), (-1,-1), chfont),
           ('FONTSIZE', (0,0), (-1,-1), 10),
           ('ALIGN', (0,0), (1,-1), 'CENTER'),
           ('ALIGN', (3,0), (3,-1), 'RIGHT'),
           ('ALIGN', (5,0), (5,-1), 'CENTER'),
           ('ALIGN', (6,0), (7,-1), 'RIGHT'),
           ('ALIGN', (2,0), (2,0), 'CENTER'),
           ('LINEABOVE', (5,-3), (7,-3), 1, 'black'),
           ('LINEABOVE', (7,-1), (7,-1), 1, 'black'),
           ('LINEBELOW', (5,-1), (7,-1), 2, 'black'),
           ('TOPPADDING', (0,-3), (-1,-1), 2),
           ('BOTTOMPADDING', (0,-3), (-1,-1), 2),]


    for i in range(len(df[dfkeys[0]])):
        cells.append([df[key][i] for key in dfkeys])

    # ADD PERIOD TOTALS AND TAX
    cells.append([u'']*len(dfkeys))
    cells[-1][5] = u'合 計:'
    cells[-1][7] = u'{:,}'.format(sub_amt)

    cells.append([u'']*len(dfkeys))
    tax_amt = int(round(sub_amt * 0.05))
    cells[-1][5] = u'稅 捐:'
    cells[-1][7] = u'{:,}'.format(tax_amt)

    cells.append([u'']*len(dfkeys))
    tot_amt = int(sub_amt + tax_amt)
    cells[-1][5] = u'總 計:'
    cells[-1][7] = u'{:,}'.format(tot_amt)

    # GROUP ITEMS THAT ARE SHIPPED TOGETHER
    continued = False
    for i in range(len(df[dfkeys[0]])-1, 0, -1):
        if cells[i][1] != u'' and cells[i][1] == cells[i-1][1]:
            cells[i][0] = u''
            if continued:
                cells[i][1] = u'\u2560'
                cellstyles.append(('BOTTOMPADDING', (0,i), (-1,i), 0))
            else:
                cells[i][1] = u'\u255A'
                continued = True
            cellstyles.append(('FONTSIZE', (1,i), (1,i), 12))
            cellstyles.append(('TOPPADDING', (0,i), (-1,i), 0))
        else:
            if continued:
                cellstyles.append(('BOTTOMPADDING', (0,i), (-1,i), 0))
                continued = False


    table = Table(cells, colWidths=w, repeatRows=1)
    table.setStyle(TableStyle(cellstyles))
    body.append(table)


    #### CREATE PRODUCT TOTALS TABLE ####
    body.append(Spacer(1, 5*mm))
    aggregated = dict()
    for i, product in enumerate(df[u'品名']):
        if product not in aggregated:
            aggregated[product] = [0, df[u'單位'][i], 0, 0]
        aggregated[product][0] += df[u'數量'][i]
        aggregated[product][2] += int(''.join(df[u'總價'][i].split(',')))
        aggregated[product][3] += 1

    cells = [[u'出貨次數', u'品名', u'總出貨量', u'單位', u'總價']]
    total = 0
    for product_name, vals in aggregated.iteritems():
        line = []
        line.append(vals[3])
        line.append(product_name)
        line.append(u'{:,}'.format(vals[0]))
        line.append(u'{}'.format(vals[1]))
        line.append(u'${:,}'.format(vals[2]))
        cells.append(line)
        total += vals[2]

    cellstyles = [('LINEABOVE', (0,0), (-1,0), 2, 'black'),
           ('LINEBELOW', (0,0), (-1,0), 1, 'black'),
           ('FONTNAME', (0,0), (-1,-1), chfont),
           ('FONTSIZE', (0,0), (-1,-1), 10),
           ('ALIGN', (2,0), (2,-1), 'RIGHT'),
           ('ALIGN', (4,0), (4,-1), 'RIGHT'),
           ('ALIGN', (0,0), (-1,0), 'CENTER'),]

    w = map(lambda x: x*mm, [14, 42, 16, 14, 22])

    table = Table(cells, colWidths=w, repeatRows=1)
    table.setStyle(TableStyle(cellstyles))
    body.append(table)

    #### BUILD PDF ####
    pdf.build(body)
    _.extwin.destroy()

    initialfilename = u'{}_{}_{}_{}'.format(
                        _.curr.cogroup.name,
                        u'Sales' if _.sc_mode == u'c' else u'Purchases',
                        str(start),
                        str(end) )
    outfile = get_savename(_, initialfilename)
    if os.path.exists(outfile):
        os.remove(outfile)

    shutil.move('temp.pdf', outfile)

    display_pdf(outfile)
    print 'pdf displayed'