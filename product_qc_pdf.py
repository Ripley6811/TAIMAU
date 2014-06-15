#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
summary

description

:REQUIRES:

:TODO:

:AUTHOR: Ripley6811
:ORGANIZATION: None
:CONTACT: python@boun.cr
:SINCE: Wed Jun 11 22:55:50 2014
:VERSION: 0.1
"""
#===============================================================================
# PROGRAM METADATA
#===============================================================================
__author__ = 'Ripley6811'
__contact__ = 'python@boun.cr'
__copyright__ = ''
__license__ = ''
__date__ = 'Wed Jun 11 22:55:50 2014'
__version__ = '0.1'

#===============================================================================
# IMPORT STATEMENTS
#===============================================================================
from fpdf import FPDF
import tkFileDialog, tkMessageBox
import os
from datetime import date
#===============================================================================
# METHODS
#===============================================================================

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
        if True:
            # Company logo left-top corner and smaller
            self.image(u'TaimauChemicals.png', x=12, y=10, w=34)
        else:
            # Company logo centered and the top
            self.image(u'TaimauChemicals.png', x=84, y=8, w=40)
        self.image(u'hsinfa.png', x=48, y=240, w=24)
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
        if not kwargs.get('company'):
            kwargs['company'] = u'台茂化工儀器原料行'
        if not kwargs.get('product'): kwargs['product'] = u'product name?'
        if not kwargs.get('ASE_pn'):  kwargs['ASE_pn'] = u'ASE PN?'
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
        if not kwargs.get('exp_period'):  kwargs['exp_period'] = u'一年'
        if not kwargs.get('amount'):  kwargs['amount'] = u'amount?'
        if not kwargs.get('tester'):  kwargs['tester'] = u'tester?'
        if not kwargs.get('test_params'): kwargs['test_params'] = []
    except Exception as e:
        print e
        return

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





    FILE_OPTS = dict(
        title = u'PDF name and location.',
        defaultextension = '.pdf',
        initialdir = os.path.expanduser('~') + '/Desktop/',
        initialfile = u'QC_{}_{}'.format(kwargs['product'], kwargs['lot_no']),
    )

    outfile = tkFileDialog.asksaveasfilename(**FILE_OPTS)
    if outfile:
        if os.path.exists(outfile):
            while os.path.exists(outfile):
                outfile = outfile[:-4]+u'_.pdf'
        FPDF.output(name=outfile)
    else:
        tkMessageBox.showinfo(u'',u'Canceled PDF creation.')





if __name__ == '__main__':
    create_qc_pdf(product=u'Nitrogen 60%',
                  company=u'台茂化工儀器原料行',
                  ASE_pn=u'2013-001-00816-000',)



#===============================================================================
# QUICK REFERENCE
#===============================================================================
'''Templates and markup notes

>>SPYDER Note markers
    #XXX: !
    #TODO: ?
    #FIXME: ?
    #HINT: !
    #TIP: !


>>SPHINX markup
    :Any words between colons: Description following.
        Indent any continuation and it will be concatenated.
    .. warning:: ...
    .. note:: ...
    .. todo:: ...

    - List items with - or +
    - List item 2

    For a long hyphen use ---

    Start colored formatted code with >>> and ...

    **bold** and *italic* inline emphasis


>>SPHINX Method simple doc template (DIY formatting):
    """ summary

    description

    - **param** --- desc
    - *return* --- desc
    """

>>SPHINX Method longer template (with Sphinx keywords):
    """ summary

    description

    :type name: type optional
    :arg name: desc
    :returns: desc

    (optional intro to block)::

        Skip line and indent monospace block

    >>> python colored code example
    ... more code
    """

See http://scienceoss.com/use-sphinx-for-documentation/ for more details on
running Sphinx
'''
