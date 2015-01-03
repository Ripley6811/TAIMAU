#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Tix
try:
    from utils import settings
    from utils import calendar_tixradiobutton as date_picker
except ImportError:
    pass
import tkFileDialog
import os
import subprocess
import shutil


from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.pdfbase.ttfonts import TTFont, TTFError
import reportlab.platypus as rlab
# For U.S. 8x11 use "letter" instead of "A4".
from reportlab.lib.pagesizes import A4 # Already the default, just for reference
from reportlab.lib.units import mm



def main(_, records=[]):

    pdfwin = _.getExtWin(_, title=u"Select date range for report.")
    if not pdfwin:
        return


    tl = Tix.Label(pdfwin, textvariable=_.loc(u"Start date"))
    tl.grid(row=0, column=0, columnspan=2)
    startdate = date_picker.Calendar(pdfwin, padx=4, preweeks=4)
    startdate.grid(row=1, rowspan=6, column=0, columnspan=2)

    tl = Tix.Label(pdfwin, textvariable=_.loc(u"End date"))
    tl.grid(row=0, column=2, columnspan=2)
    enddate = date_picker.Calendar(pdfwin, padx=4, preweeks=4)
    enddate.grid(row=1, rowspan=6, column=2, columnspan=2)

    #NOTE: StringVar must be a persistant variable to work properly.
    _.co = Tix.StringVar()
    if _.sc_mode == u'c':
        co_sel_frame = Tix.Frame(pdfwin)
        co_sel_frame.grid(row=10, column=0, columnspan=4)
        names = [u"台茂",u"富茂",u"永茂"]
        _.co.set(names[0])
        for i, n in enumerate(names):
            b = Tix.Radiobutton(co_sel_frame, text=n, variable=_.co, value=n)
            b.pack(side="left")
    print _.co.get()

    include_sum = Tix.BooleanVar()
    cb = Tix.Checkbutton(pdfwin, textvariable=_.loc(u"Include Summary"), variable=include_sum)
    cb.grid(row=20, column=0, columnspan=4)
    include_sum.set(False)


    tb = Tix.Button(pdfwin, textvariable=_.loc(u"\u2713 Submit"), bg=u'light salmon')
#    tb['command'] = lambda: submit() # FPDF
    tb['command'] = lambda: submit_RLab(_,  # Report Lab
                                        start=startdate.date_obj,
                                        end=enddate.date_obj,
                                        summary=include_sum.get())
    tb.grid(row=100, column=0, columnspan=4, sticky='ew')




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
        subprocess.call(['start', outfile], shell=True)
    except:
        os.startfile(outfile)


def submit_RLab(_, start, end, summary=False):

    #TODO: Add client branch column

    # Retrieve shipment data within date range
    session = _.dbm.session
    Order = _.dbm.Order
    ShipmentItem = _.dbm.ShipmentItem
    Shipment = _.dbm.Shipment

    q = session.query(ShipmentItem) # Get list of ShipmentItems
    q = q.join(Shipment) # Join to Shipment for filtering
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
    df = dict()
    df[u'日期'] = [rec.shipment.shipmentdate for rec in q]
    df[u'出貨單號'] = [rec.shipment.shipment_no for rec in q]
    df[u'品名'] = [rec.order.product.label() for rec in q]
    df[u'數量'] = [rec.qty*(rec.order.product.units if rec.order.product.unitpriced else 1) for rec in q]
    df[u'單位'] = [rec.order.product.UM if rec.order.product.unitpriced else rec.order.product.SKU for rec in q]
    df[u'包裝'] = [u'({} {})'.format(rec.qty,rec.order.product.SKU) if (rec.order.product.unitpriced and rec.order.product.SKU != u'槽車') else u'' for rec in q]
    df[u'單價'] = [rec.order.price for rec in q]
    df[u'總價'] = [u'{:,}'.format(rec.order.qty_quote(rec.qty)) for rec in q]
    df[u'發票號碼'] = [rec.invoiceitem[0].invoice.invoice_no if len(rec.invoiceitem) else u'' for rec in q]
    try:
        df[u'數量'] = [int(rec) if float(rec).is_integer() else rec for rec in df[u'數量']]
    except:
        pass
    try:
        df[u'單價'] = [int(rec) if float(rec).is_integer() else rec for rec in df[u'單價']]
    except:
        pass


    initialfilename = u'{}_{}_{}_{}'.format(
                        _.curr.cogroup.name,
                        u'Sales' if _.sc_mode == u'c' else u'Purchases',
                        str(start),
                        str(end) )

    outfile = get_savename(_, initialfilename)

    if outfile == ".":
        print "PDF creation cancelled"
        return False
    _.extwin.destroy()

    if os.path.exists(outfile):
        os.remove(outfile)

#    shutil.move('temp.pdf', outfile)


    tmpd = {u'台茂': u'台茂化工儀器原料行',
            u'富茂': u'富茂工業原料行',
            u'永茂': u'永茂企業行' }

    ActivityReport(savepath=outfile, scMode=_.sc_mode, tableValues=df,
                   dateStart=start, dateEnd=end, useSummary=summary,
                   coName=_.curr.cogroup.name, tmBranch=tmpd[_.co.get()])

    display_pdf(outfile)
    print 'pdf displayed'

#--- NEW! ActivityReport Class


fonts = ('simHei', 'KAIU')


def register_font(font):
    registerFont(TTFont(font, font+'.ttf'))
[register_font(f) for f in fonts]

class ActivityReport(object):

    def __init__(self, *args, **kwargs):
        """init

        Optional arg strings:
            "c" or "customer" for customer report format.
            "s" or "supplier" for supplier report format.
            "summarize" for appending a product totals summary to report.

        Required kwargs:
            scMode (unicode): "c" or "s" for selecting customer or supplier format.
            tableValues (dict): Table column data with Chinese column names as keys.
            dateStart (datetime.date): Starting date for report.
            dateEnd (datetime.date): Ending date for report.
            coName (unicode): Customer/Supplier full name to write on PDF.

        Optional kwargs:
            tmBranch (unicode): Our company branch full name to write on PDF.
            chFont (unicode): Font used in PDF.
            logoSrc (unicode): Path of logo image file.
            logoScale (float): Multiplier for image resizing.
            useSummary (bool): Appends summary of products if true.
            groupSpacing (bool): Reduce spacing between items on one manifest.
            groupBracket (bool): Add a bracket denoting items on one manifest.
            savepath (unicode): Save location and filename.
        """
        self.scMode = kwargs.pop('scMode', None)
        if u's' in args or u'supplier' in args: self.scMode = u's'
        if u'c' in args or u'customer' in args: self.scMode = u'c'
        assert self.scMode in [u's',u'c'], u"'scMode' parameter required."

        self.df = kwargs.pop('tableValues', None)
        assert isinstance(self.df, dict)

        self.tmBranch = kwargs.pop(u'tmBranch', u'')

        self.coName = kwargs.pop(u'coName', None)
        assert isinstance(self.coName, unicode)

        self.chFont = kwargs.pop(u'font', u'simHei')
        # Attempt to register a font if string is an unknown font.
        if self.chFont not in fonts:
            try:
                register_font(self.chFont)
            except TTFError:
                self.chFont = fonts[0]

        self.dateStart = kwargs.pop(u'dateStart', None)
        self.dateEnd = kwargs.pop(u'dateEnd', None)
        try:
            self.dateStart.year, self.dateStart.month, self.dateStart.day
            self.dateEnd.year, self.dateEnd.month, self.dateEnd.day
        except AttributeError:
            raise TypeError, u"'dateStart' or 'dateEnd' are not datetime instances."

        self.groupSpacing = kwargs.pop(u'groupSpacing', True)
        self.groupBracket = kwargs.pop(u'groupBracket', False)

        self.useSummary = kwargs.pop(u'useSummary', False)
        if u'summarize' in args: self.useSummary = True

        self.savepath = kwargs.pop(u'savepath', u'temp.pdf')

        self.logoSrc = kwargs.pop(u'logoSrc', u'png/logo.png')
        self.logoScale = kwargs.pop(u'logoScale', 0.66) # Rescale the logo image

        self._make_report()

    def _make_report(self):
        """Make report

        Central part of class that puts all methods together for creating a
        PDF report and saving it.
        """
        temppath = 'temp.pdf'
        pdf = rlab.BaseDocTemplate(temppath, pagesize=A4)

        frame = rlab.Frame(10*mm, pdf.bottomMargin, 190*mm, pdf.height,
                           id='normal', showBoundary=0)
        template = rlab.PageTemplate(id='test', frames=frame,
                                     onPage=self._onPage_function_get())
        pdf.addPageTemplates([template])

        body = []
        body.append(self._shipments_table_get())
        if self.useSummary:
            body.append(rlab.Spacer(1, 5*mm))
            body.append(self._summary_table_get())

        pdf.build(body)
        shutil.move(temppath, self.savepath)

    def _onPage_function_get(self):
        """onPage function needed for PageTemplate.

        The onPage function adds the same elements to each page that is added
        to the PDF.
        """
        PAGE_LENGTH = 297*mm

        def function(canvas, doc):
            imScale = lambda im: int(im * self.logoScale)
            if self.scMode == u'c':
                try:
                    # Image( file, x, y, w=0, h=0)
                    canvas.drawImage(self.logoSrc, 25*mm, PAGE_LENGTH-18*mm, imScale(147), imScale(59))
                except IOError as e:
                    print e
                canvas.setFont(self.chFont, 14)
                canvas.setFillColorRGB(0,71/256.,18/256.)
                canvas.drawString(25*mm, PAGE_LENGTH-22*mm, self.tmBranch)
                canvas.setFillColorRGB(0,0,0)

                # Client name
                canvas.setFont(self.chFont, 12)
                text = u'客戶名稱: {}'.format(self.coName)
                canvas.drawString(100*mm, PAGE_LENGTH-16*mm, text)
            else:
                canvas.setFont(self.chFont, 16)
                text = u'確認表: {}'.format(self.coName)
                canvas.drawString(25*mm, PAGE_LENGTH-25*mm, text)

                # Client name
                canvas.setFont(self.chFont, 12)
                text = u'客戶名稱: {}'.format(u'台茂化工儀器原料行')
                canvas.drawString(100*mm, PAGE_LENGTH-16*mm, text)

            # Time period
            text = u'日期: {0.year}年 {0.month}月{0.day}日-{1.month}月{1.day}日'.format(self.dateStart, self.dateEnd)
            canvas.drawString(100*mm, PAGE_LENGTH-22*mm, text)

            # Add page number at bottom
            canvas.setFont(self.chFont, 8)
            text = u'Page {}'.format(canvas.getPageNumber())
            canvas.drawCentredString(doc.leftMargin + doc.width/2, 10*mm, text)
        return function

    def _shipments_table_get(self):
        """Shipments table

        The main table that contains shipment information. Date, manifest
        number, quantity, pricing and invoice numbers. Also a total cost and
        tax calculation.
        """
        MIDDLE = 0
        START = 1
        END = 2
        COL_NAMES = (u'日期',u'出貨單號',u'品名',u'數量',u'單位',
                     u'包裝',u'單價',u'總價',u'發票號碼')
        WIDTHS = [a*mm for a in (26, 24, 36, 16, 10, 18, 16, 20, 24)]

        cells = [COL_NAMES] # First line of table is column names.
        cellstyles = [
            ('LINEABOVE', (0,0), (-1,0), 2, 'black'),
            ('LINEBELOW', (0,0), (-1,0), 1, 'black'),
            ('FONTNAME', (0,0), (-1,-1), self.chFont),
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
            ('BOTTOMPADDING', (0,-3), (-1,-1), 2),
        ]

        # APPEND EACH ROW FROM TABLE DATA.
        for i in range(len(self.df[COL_NAMES[0]])):
            cells.append([self.df[key][i] for key in COL_NAMES])

        # ADD PERIOD TOTALS AND TAX.
        sub_amt = int(round(sum([a*b for a,b in zip(self.df[u'數量'], self.df[u'單價'])])))
        cells.append([u'']*len(COL_NAMES))
        cells[-1][5] = u'合 計:'
        cells[-1][7] = u'{:,}'.format(sub_amt)

        tax_amt = int(round(sub_amt * 0.05))
        cells.append([u'']*len(COL_NAMES))
        cells[-1][5] = u'稅 捐:'
        cells[-1][7] = u'{:,}'.format(tax_amt)

        tot_amt = int(sub_amt + tax_amt)
        cells.append([u'']*len(COL_NAMES))
        cells[-1][5] = u'總 計:'
        cells[-1][7] = u'{:,}'.format(tot_amt)

        # GROUP ITEMS THAT ARE SHIPPED TOGETHER.
        # The following adds/changes the cell formatting by adding format rules.
        self.brackets = [] # List of items counts for each manifest.

        def _find_manifest_groups():
            """Make a list that notes where manifest groups begin and end.

            Updates the 'brackets' list to show the item numbering.
            Set to 0 for middle of manifest group, 1 for beginning, 2 for
            end and 3 for a single item manifest.
            """
            length = len(self.df[COL_NAMES[0]])
            brackets = [MIDDLE] * length # Set all to the middle value (zero)
            brackets[0] = START # Set first index to bracket start value (1)

            for i in range(1, length):
                if cells[i][1] != u'':
                    if cells[i][1].strip() != cells[i-1][1].strip():
                        brackets[i-1] += END
                        brackets[i] = START
                else: # Open and close single item if there is no manifest ID.
                    if brackets[i-1] < 2:
                        brackets[i-1] += END
                    brackets[i] = START+END
            else: # Close the last index after iterating.
                if brackets[-1] < 2:
                    brackets[-1] += END
            self.brackets = brackets


        def _del_repeated_manifest_numbers(): # (and dates)
            """Delete repeated IDs and dates for multiple items of the same
            manifest.

            When a manifest number repeats then both the date and number are
            made blank.
            """
            for i in range(1, len(cells)):
                if self.brackets[i] in (MIDDLE,END):
                    cells[i][0] = u''
                    cells[i][1] = u''


        def _add_group_spacing():
            """Items belonging to the same manifest are positioned closer
            together.
            """
            for i in range(1, len(cells)):
                if self.brackets[i] in (MIDDLE, END, START+END):
                    cellstyles.append(('TOPPADDING', (0,i), (-1,i), 0))
                if self.brackets[i] in (MIDDLE, START, START+END):
                    cellstyles.append(('BOTTOMPADDING', (0,i), (-1,i), 0))


        def _add_group_brackets():
            """Items belonging to the same manifest will have a bracket
            extending down from the manifest number on the first item of group.
            """
            MID_CHAR = u' \u2502' #u'\u2560' # Double lined T-junction character.
            END_CHAR = u' \u2515' #u'\u255A' # Double lined L-junction character.
            for i in range(1, len(cells)):
                if self.brackets[i] == MIDDLE:
                    cells[i][1] = MID_CHAR
                elif self.brackets[i] == END:
                    cells[i][1] = END_CHAR
                else:
                    continue
                cellstyles.append(('FONTSIZE', (1,i), (1,i), 12))

        # Adjust manifest item groups for spacing and optional bracketing.
        _find_manifest_groups()
        _del_repeated_manifest_numbers()
        if self.groupSpacing: _add_group_spacing()
        if self.groupBracket: _add_group_brackets()


        table = rlab.Table(cells, colWidths=WIDTHS, repeatRows=1)
        table.setStyle(rlab.TableStyle(cellstyles))
        return table


    def _summary_table_get(self):
        """Table of each product with total quantities and value added up.
        """
        aggregated = dict()
        for i, product in enumerate(self.df[u'品名']):
            if product not in aggregated:
                aggregated[product] = [0, self.df[u'單位'][i], 0, 0]
            aggregated[product][0] += self.df[u'數量'][i]
            aggregated[product][2] += int(''.join(self.df[u'總價'][i].split(',')))
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
               ('FONTNAME', (0,0), (-1,-1), self.chFont),
               ('FONTSIZE', (0,0), (-1,-1), 10),
               ('ALIGN', (2,0), (2,-1), 'RIGHT'),
               ('ALIGN', (4,0), (4,-1), 'RIGHT'),
               ('ALIGN', (0,0), (-1,0), 'CENTER'),]

        WIDTHS = map(lambda x: x*mm, [14, 42, 16, 14, 22])
        WIDTHS = [x*mm for x in [14, 42, 16, 14, 22]]

        table = rlab.Table(cells, colWidths=WIDTHS, repeatRows=1)
        table.setStyle(rlab.TableStyle(cellstyles))
        return table


#==============================================================================
#--- Module Testing
#==============================================================================
def test():
    import datetime
    df = {
        u'\u55ae\u4f4d': [ # 單位
            u'kg', u'kg', u'kg', u'kg', u'kg', u'kg'],
        u'\u7e3d\u50f9': [ # 總價
            u'8,862', u'9,240', u'8,736', u'8,694', u'9,114', u'8,610'],
        u'\u54c1\u540d': [ #品名
            u'HCL', u'HCL', u'HCL', u'HCL', u'HCL', u'HCL'],
        u'\u51fa\u8ca8\u55ae\u865f': [ # 出貨單號
            u'14.46.44', u'15.58.32', u'14.28.42', u'09.40.11', u'12.01.39', u'14.28.03'],
        u'\u5305\u88dd': [ # 包裝
            u'', u'', u'', u'', u'', u''],
        u'\u55ae\u50f9': [ # 價格
            2.1, 2.1, 2.1, 2.1, 2.1, 2.1],
        u'\u65e5\u671f': [ # 日期
            datetime.date(2014, 11, 26), datetime.date(2014, 11, 27),
            datetime.date(2014, 11, 29), datetime.date(2014, 12, 1),
            datetime.date(2014, 12, 6), datetime.date(2014, 12, 6)],
        u'\u767c\u7968\u865f\u78bc': [ # 發票號碼
            u'CZ03164969', u'CZ03164969', u'CZ03164969', u'', u'', u''],
        u'\u6578\u91cf': [ # 數量
            4220, 4400, 4160, 4140, 4340, 4100]
    }
    df = {u'\u55ae\u4f4d': [u'kg', u'kg', u'kg', u'kg', u'kg', u'kg', u'kg', u'kg', u'kg', u'kg', u'kg', u'kg', u'kg', u'kg', u'kg'], u'\u7e3d\u50f9': [u'5,400', u'1,920', u'750', u'3,000', u'4,350', u'1,750', u'800', u'500', u'500', u'14,400', u'10,800', u'4,800', u'4,800', u'14,400', u'10,800'], u'\u54c1\u540d': [u'\u4e9e\u786b\u9178\u6c2b\u9209', u'\u9e7d\u917820%', u'\u6c2b\u6c27\u5316\u9209', u'\u6b21\u6c2f\u9178\u9209', u'\u6ab8\u6aac\u9178', u'\u78f7\u9178\u6c2b\u4e8c\u9240', u'\u6c2e\u78f7', u'\u5c3f\u7d20', u'\u78b3\u9178\u6c2b\u9209', u'\u6db2\u9e7c45%', u'\u6b21\u6c2f\u9178\u9209', u'\u786b\u917850%', u'\u786b\u917850%', u'\u6db2\u9e7c45%', u'\u6b21\u6c2f\u9178\u9209'], u'\u51fa\u8ca8\u55ae\u865f': [u'004381', u'004381', u'004381', u'004381', u'004381', u'004392', u'004392', u'004392', u'004392', u'004399', u'004399', u'004399', u'004409', u'004409', u'004409'], u'\u5305\u88dd': [u'(1 \u6876)', u'(10 \u6876)', u'(1 \u5305)', u'(10 \u6876)', u'(4 \u5305)', u'(1 \u6876)', u'(1 \u6876)', u'(1 \u6876)', u'(1 \u5305)', u'(4 \u6876)', u'(4 \u6876)', u'(4 \u6876)', u'(4 \u6876)', u'(4 \u6876)', u'(4 \u6876)'], u'\u55ae\u50f9': [18, 8, 30, 12, 43.5, 70, 32, 20, 20, 12, 10, 4, 4, 12, 10], u'\u65e5\u671f': [datetime.date(2014, 12, 25), datetime.date(2014, 12, 25), datetime.date(2014, 12, 25), datetime.date(2014, 12, 25), datetime.date(2014, 12, 25), datetime.date(2014, 12, 27), datetime.date(2014, 12, 27), datetime.date(2014, 12, 27), datetime.date(2014, 12, 27), datetime.date(2014, 12, 31), datetime.date(2014, 12, 31), datetime.date(2014, 12, 31), datetime.date(2015, 1, 2), datetime.date(2015, 1, 2), datetime.date(2015, 1, 2)], u'\u767c\u7968\u865f\u78bc': [u'CZ00984031', u'CZ00984031', u'CZ00984031', u'CZ00984031', u'CZ00984031', u'CZ00984038', u'CZ00984038', u'CZ00984038', u'CZ00984038', u'CZ00984041', u'CZ00984041', u'CZ00984041', u'NN01011953', u'NN01011953', u'NN01011953'], u'\u6578\u91cf': [300, 240, 25, 250, 100, 25, 25, 25, 25, 1200, 1080, 1200, 1200, 1200, 1080]}


    print 'total', map(lambda a,b: a*b, df[u'\u55ae\u50f9'], df[u'\u6578\u91cf'])
    print sum(map(lambda a,b: a*b, df[u'\u55ae\u50f9'], df[u'\u6578\u91cf']))
    print sum([a*b for a,b in zip(df[u'數量'], df[u'單價'])])
    ActivityReport(tableValues=df, scMode=u'c', coName=u'三台', savepath=u'test.pdf',
                   dateStart=datetime.date(2014,11,25), useSummary=True, logoSrc=u"../../png/logo.png",
                    dateEnd=datetime.date(2015,1,7), groupSpacing=True, groupBracket=True)


if __name__ == '__main__':
    test()