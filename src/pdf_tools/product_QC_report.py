#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import Tix
import tkFileDialog, tkMessageBox
import subprocess
from datetime import date
from fpdf import FPDF
from utils import settings


def main(_):
    '''Currently aimed at producing product testing results for ASE
    products but could change it to work for any product in the
    future.
    '''

    # Create new external window.
    if not _.getExtWin(_, title=u"Production Analysis Report"):
        return


    options = 'selectColor gold'
    company_w = Tix.Select(_.extwin, label=u'公司',
                           radio=True, orientation='vertical', options=options)
#    company_w.config(selectcolor='gold')
    company_w.add(u'台茂化工儀器原料行', text=u'台茂化工儀器原料行',
                           background='purple')
    company_w.invoke(u'台茂化工儀器原料行')
    company_w.add(u'富茂工業原料行', text=u'富茂工業原料行',
                           background='purple')
    company_w.add(u'永茂企業行', text=u'永茂企業行',
                           background='purple')
    company_w.grid(row=0, column=0, columnspan=3, sticky='ew')

    pname_SV = Tix.StringVar()
#        pname_SV.trace('w', lambda: autofill())
    product_w = Tix.ComboBox(_.extwin, label=u'品名', dropdown=True,
                             editable=True,
                             variable=pname_SV, command=lambda *args: autofill())
    product_w.subwidget('entry').config(disabledforeground='black')
#        product_w.entry.configure(textvariable=pname_SV)
    ASE = _.dbm.get_cogroup(u'ASE')
    MPN_list = []
    for ea in ASE.products:
        product_w.insert('end', ea.name)
        MPN_list.append(ea.MPN)
    product_w.grid(row=1, column=0, columnspan=3, sticky='ew')
#        ASE_w = Tix.LabelEntry(_.extwin, label=u'料號')
#        ASE_w.grid(row=2, column=0, sticky='ew')
    lot_w = Tix.LabelEntry(_.extwin, label=u'批號')
    lot_w.grid(row=3, column=0, columnspan=3, sticky='ew')
    qty_w = Tix.LabelEntry(_.extwin, label=u'數量')
    qty_w.grid(row=4, column=0, columnspan=3, sticky='ew')
    tester_w = Tix.LabelEntry(_.extwin, label=u'取樣人員')
    tester_w.grid(row=5, column=0, columnspan=3, sticky='ew')
    gridlabels = [u'檢 驗 項 目', u'規 格', u'檢 驗 結 果']
    for i in range(3):
        Tix.Label(_.extwin, text=gridlabels[i]).grid(row=6, column=i)

    egrid = []
    for i in range(8):
        egrid.append([])
        for j in range(3):
            egrid[i].append(Tix.Entry(_.extwin, justify='center'))
            egrid[i][j].grid(row=i+10, column=j)


    # Restore previous entries for a particular product
    def autofill():
        # Retrieve product record.
        MPN = MPN_list[product_w.slistbox.listbox.index('active')]
        p_rec = _.dbm.get_product(MPN)
        _dict = p_rec.json()
        if not _dict:
            return
        if _dict.get('amount'):
            qty_w.entry.delete(0, 'end')
            qty_w.entry.insert(0, _dict['amount'])
        if _dict.get('tester'):
            tester_w.entry.delete(0, 'end')
            tester_w.entry.insert(0, _dict['tester'])
        if _dict.get('lot_no'):
            lot_w.entry.delete(0, 'end')
            lot_w.entry.insert(0, _dict['lot_no'])
        if _dict.get('test_params'):
            tp = _dict['test_params']
            for i in range(len(egrid)):
                for j in range(len(egrid[0])):
                    egrid[i][j].delete(0, 'end')
                    egrid[i][j].insert(0, tp[i][j])


    submit_w = Tix.Button(_.extwin, text=u'提交')
    submit_w['command'] = lambda: submit()
    submit_w.grid(row=50, column=0, columnspan=3)


    def submit():
        # Convert matrix of entry widgets into matrix of values.
        for i in range(8):
            for j in range(3):
                egrid[i][j] = egrid[i][j].get()
        # Retrieve product record.
        MPN = MPN_list[product_w.slistbox.listbox.index('active')]
        p_rec = _.dbm.get_product(MPN)
        _.dbm.session.commit()
        # Create dictioinary of values to pass to pdf writing method.
        _dict = dict(
            company=company_w['value'],
            product=product_w['selection'],
            ASE_pn=p_rec.ASE_PN,
            lot_no=lot_w.entry.get(),
            amount=qty_w.entry.get(),
            tester=tester_w.entry.get(),

            test_params=egrid,
        )

        create_qc_pdf(**_dict)

        # Save options as JSON in product database record.
        del _dict['company']
        del _dict['product']
        del _dict['ASE_pn']
        # Update previous json
        p_rec.json(_dict)
        _.dbm.session.commit()

        _.extwin.destroy()




font = r'C:\Windows\Fonts\simfang.ttf'
#font = r'C:\Windows\Fonts\simkai.ttf'
#font = r'C:\Windows\Fonts\simhei.ttf'
font = r'C:\Windows\Fonts\kaiu.ttf' # Shows superscript 3 but not 名
#font = r'C:\Windows\Fonts\fireflysung.ttf' # Shows superscript 3 but not 名


class myPDF(FPDF):
    form_number = u'FM0716A'
    # Left and right margin
    lm = 30
    rm = 178
    def header(self):
        lm = self.lm
        rm = self.rm
        mw = rm-lm
        C = 'C'
        try:
            if True:
                # Company logo left-top corner and smaller
                self.image(u'png/logo.png', x=12, y=10, w=34)
            else:
                # Company logo centered and the top
                self.image(u'png/logo.png', x=84, y=8, w=40)
        except IOError as e:
            print e
        try:
            self.image(u'png/signature1.png', x=48, y=240, w=24)
        except IOError as e:
            print e
        self.add_font(family=u'SimHei', style='B', fname=font, uni=True) # Only .ttf and not .ttc
        self.set_font(family=u'SimHei', style='B', size=16)
#        self.set_xy(lm, 25)
#        self.cell(mw, 10, u'台茂化工儀器原料行', align=C)

        # Client name
        self.set_font(u'SimHei', 'B', 16)
        self.set_xy(lm, 37)
        self.cell(mw, 8, u'產品檢驗報告', align=C)

        # Fill in headers
        self.set_font(u'SimHei', 'B', 13)
        self.set_fill_color(240,240,240)
        self.set_xy(30, 95) # Next cell auto-set to right
        self.cell(48, 10, txt=u'檢 驗 項 目', align=C, fill=True)
        self.cell(50, 10, txt=u'規 格', align=C, fill=True)
        self.cell(50, 10, txt=u'檢 驗 結 果', align=C, fill=True)
        self.set_xy(30, 210)
        self.cell(66-lm, 15, txt=u'結果研判:', align=C)
        self.cell(rm-66, 15, txt=u'符合規格', align=C)
        self.set_xy(30, 225)
        self.cell(104-lm, 10, txt=u'製表', align=C)
        self.cell(rm-104, 10, txt=u'檢驗人員', align=C)

        # Draw lines last, otherwise cell fill will overwrite.
        # Top table borders
        self.rect(lm, 50, mw, 40) # x, y, w, h
        for ea in [65,73,81]:
            self.line(lm, ea, rm, ea) # x1, y1, x2, y2
        self.line(104, 65, 104, 90)

        # Middle table borders
        self.rect(lm, 95, mw, 205-95) # x, y, w, h
        for ea in range(105, 205, 10):
            self.line(lm, ea, rm, ea) # x1, y1, x2, y2
        self.line(78, 95, 78, 205)
        self.line(128, 95, 128, 205)

        # Bottom table borders
        self.rect(lm, 210, mw, 50) # x, y, w, h
        for ea in [225,235]:
            self.line(lm, ea, rm, ea) # x1, y1, x2, y2
        self.line(66, 210, 66, 225)
        self.line(104, 225, 104, 260)

    def xycell(self, x, y, *args, **kwargs):
        # Method to both set starting position and write cell in one command.
        # Preceed 'cell' parameters with x and y position parameters.
        self.set_xy(x, y)
        self.cell(*args, **kwargs)


    def footer(self):
        self.set_font(family=u'SimHei', style='B', size=12)
#        self.set_xy(155, -32)
#        self.cell(21, 5, txt=self.form_number, align='C')
        self.xycell(155, -32, 21, 5, txt=self.form_number, align='C')

headers = ['company',
           'product',
           'ASE_pn',
           'lot_no',
           'exp_period',
           'amount',
           'tester',
           'test_params']

def create_qc_pdf(**kwargs):
    try:
        kwargs['company'] = kwargs.get('company', u'台茂化工儀器原料行')
        kwargs['product'] = kwargs.get('product', u'product name?')
        kwargs['ASE_pn'] = kwargs.get('ASE_pn', u'ASE PN?')
        if not kwargs.get('lot_no'):
            kwargs['make_date'] = date.today()
            kwargs['test_date'] = date.today()
            kwargs['lot_no'] = u'lot number?'
        else:
            year = 2000 + int(kwargs['lot_no'][1:3])
            month = int(kwargs['lot_no'][3:5])
            day = int(kwargs['lot_no'][5:7])
            kwargs['make_date'] = date(year, month, day)
            kwargs['test_date'] = date(year, month, day)
        kwargs['exp_period'] = kwargs.get('exp_period', u'一年')
        kwargs['amount'] = kwargs.get('amount', u'amount?')
        kwargs['tester'] = kwargs.get('tester', u'tester?')
        kwargs['test_params'] = kwargs.get('test_params', [])
    except Exception as e:
        print e
        return

    # Set placement and style of values
    tm_branch = dict(x=30, y=25, w=178-30, h=10, align='C')
    product_name = dict(x=31, y=50, w=104-31, h=15, align='L')
    product_ASE_pn = dict(x=105, y=50, w=104-31, h=15, align='L')

    make_date = dict(x=31, y=65, w=104-31, h=8, align='L')
    test_date = dict(x=31, y=73, w=104-31, h=8, align='L')
    exp_period = dict(x=31, y=81, w=104-31, h=9, align='L')

    lot_no = dict(x=105, y=65, w=104-31, h=8, align='L')
    amount = dict(x=105, y=73, w=104-31, h=8, align='L')
    tester = dict(x=105, y=81, w=104-31, h=9, align='L')


    # Create PDF
    FPDF = myPDF('P','mm','A4')
    FPDF.set_compression(False)
    FPDF.set_creator('TM_2014')
    FPDF.set_title(u'Quality inspection report for lot# {}'.format(kwargs['lot_no']))
    FPDF.set_author(u'Taimau Chemicals')
    FPDF.set_subject(kwargs['lot_no'])
#    FPDF.set_subject(u'{} {}'.format(kwargs['product'], kwargs['lot_no']), isUTF8=True)
    FPDF.alias_nb_pages()
    FPDF.add_page() # Adding a page also creates a page break from last page


    FPDF.add_font(family=u'SimHei', style='', fname=font, uni=True) # Only .ttf and not .ttc

    FPDF.set_font(family=u'SimHei', style='', size=16)
    FPDF.xycell(txt=kwargs['company'], **tm_branch)

    FPDF.set_font(family=u'SimHei', style='B', size=13)
    FPDF.xycell(txt=u'產品: {}'.format(kwargs['product']), **product_name)
    FPDF.xycell(txt=u'料號: {}'.format(kwargs['ASE_pn']), **product_ASE_pn)

    FPDF.xycell(txt=u'製造日期: {}'.format(kwargs['make_date']), **make_date)
    FPDF.xycell(txt=u'檢驗日期: {}'.format(kwargs['test_date']), **test_date)
    FPDF.xycell(txt=u'保存期間: {}'.format(kwargs['exp_period']), **exp_period)

    FPDF.xycell(txt=u'批號: {}'.format(kwargs['lot_no']), **lot_no)
    FPDF.xycell(txt=u'生產數量: {}'.format(kwargs['amount']), **amount)
    FPDF.xycell(txt=u'取樣人員: {}'.format(kwargs['tester']), **tester)

    FPDF.set_left_margin(30)
    FPDF.set_xy(x=30, y=105)
    for (a, b, c) in kwargs['test_params']:
        if a+b+c == u'':
            break
        FPDF.cell(49, 10, txt=a, align='C')
        FPDF.cell(49, 10, txt=b, align='C')
        FPDF.cell(49, 10, txt=c, align='C')
        FPDF.ln()
    FPDF.cell(49)
    FPDF.cell(49, 10, txt=u'以下空白', align='C')




    initialfilename = u'QC_{}_{}'.format(kwargs['product'], kwargs['lot_no'])
    FILE_OPTS = dict(
        title = u'PDF name and location.',
        defaultextension = '.pdf',
        initialdir = os.path.expanduser('~') + '/Desktop/',
        initialfile = initialfilename,
    )
    if settings.load().get(u'pdfpath'):
        FILE_OPTS['initialdir'] = settings.load()[u'pdfpath']

    outfile = os.path.normpath(tkFileDialog.asksaveasfilename(**FILE_OPTS))


    if os.path.exists(outfile):
        os.remove(outfile)
    if outfile and not os.path.exists(outfile):
        FPDF.output(name=outfile)

        try:
            subprocess.call(['start', outfile],
                             shell=True)
            return
        except:
            pass

        try:
            print u'Trying alternate subprocess command.'
            subprocess.call(['start', '/D'] +
                            list(os.path.split(outfile)),
                            shell=True)
            return
        except UnicodeEncodeError:
            pass

        try:
            os.startfile(outfile)
            return
        except:
            pass

        print u'Failed to autoload PDF after creation.'
        return
    else:
        head = u'Cancelled'
        body = u'Canceled PDF creation.'
        tkMessageBox.showinfo(head, body)





#if __name__ == '__main__':
#    create_qc_pdf(product=u'Nitrogen 60%',
#                  company=u'台茂化工儀器原料行',
#                  ASE_pn=u'2013-001-00816-000',)
