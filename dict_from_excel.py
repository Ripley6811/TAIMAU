#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Converts an excel document to a dictionary of 2D lists.

Generic excel to data structure conversion.
Returns a dictionary where the keys are the sheet names of an excel document.
Each key corresponds to a 2D list (list of lists) giving the rows and cols or
a sheet.
- Converts excel date objects to datetime.date objects.
- Duplicates merged cell data to all corresponding cells.
- Attempts to convert Chinese month/day dates to datetime object.

:REQUIRES:

:TODO:

:AUTHOR: Ripley6811
:ORGANIZATION: None
:CONTACT: python@boun.cr
:SINCE: Tue Feb 18 16:41:12 2014
:VERSION: 1.0
"""
#===============================================================================
# PROGRAM METADATA
#===============================================================================
__author__ = 'Ripley6811'
__contact__ = 'python@boun.cr'
__copyright__ = ''
__license__ = ''
__date__ = 'Tue Feb 18 16:41:12 2014'
__version__ = '1.0'

#===============================================================================
# IMPORT STATEMENTS
#===============================================================================
from datetime import datetime
from xlrd import open_workbook, xldate_as_tuple



#===============================================================================
# METHODS
#===============================================================================
def xlDate(val, datemode = 0):
#    try:
        return datetime(*xldate_as_tuple(val, datemode)).date()
#    except:
        #print 'Skipped date fail:', sheet.name, cell
        return None

def open_excel(filename, debug = False):
    DATE_CELL = 3
    FORMATTING_INFO = True
    book = None
    try:
        book = open_workbook(filename, formatting_info=FORMATTING_INFO)
    except NotImplementedError:
        print 'WARNING: XLSX Merged cells cannot be unmerged properly.'
        FORMATTING_INFO = False
        book = open_workbook(filename, formatting_info=FORMATTING_INFO)

    db = {} #Return dictionary

    #Copy each sheet
    for sheet in book.sheets():

        sheetlist = [] #List of sheet rows.

        #Copy each row
        for r in range(sheet.nrows):
            reclist = []
            for c in range(sheet.ncols):
                reclist.append(
                    (xlDate(sheet.cell_value(r,c))
                     if sheet.cell_type(r,c) == DATE_CELL
                     else sheet.cell_value(r,c))
                )
            sheetlist.append( reclist )

        if FORMATTING_INFO:
            for (lr, hr, lc, hc) in sheet.merged_cells:
                if debug: print '----', (lr,hr,lc,hc), '----'
                for r in range(lr,hr):
                    for c in range(lc,hc):
                        if debug: print r,c,':', repr(sheetlist[r][c]),
                        sheetlist[r][c] = sheetlist[lr][lc]
                        if debug: print '>', repr(sheetlist[r][c])

        for r in range(sheet.nrows):
            for c in range(sheet.ncols):
                #Fix Chinese date.
                #XXX: Possible errors if year needs to change from previous
                try:
                    yue = sheetlist[r][c].index(u'月')
                    ri =  sheetlist[r][c].index(u'日')
                    if 3 < len(sheetlist[r][c]) < 7:
                        month = int(sheetlist[r][c][:yue])
                        day = int(sheetlist[r][c][yue+1:ri])
                        if debug: print 'ATTEMPTING DATE CORRECTION'
                        if debug: print r,c, repr(sheetlist[r][c]), month, day
                        if debug: print '      use', r-1, c, repr(sheetlist[r-1][c])
                        if debug: print '             ', repr(sheetlist[r][c])
                        sheetlist[r][c] = sheetlist[r-1][c].replace(month=month, day=day)
                        if debug: print '             ', repr(sheetlist[r][c])
                except AttributeError: #Skip datetime objects
                    pass
                except ValueError: #Chinese month and day not found
                    pass
                except TypeError: #Previous datetime not found
                    pass
        db[sheet.name] = sheetlist


    return db

#===============================================================================
# MAIN METHOD AND TESTING AREA
#===============================================================================
def main():
    """Description of main()"""

    print open_excel(r'C:\Users\Jay\Dropbox\GitHub\TAIMAU\TM2014_Database.xlsx', debug=False)



if __name__ == '__main__':
    main()



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
