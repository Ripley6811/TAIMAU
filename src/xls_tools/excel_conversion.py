#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
summary

Parse new format Excel file to make formatted output.

:REQUIRES:

:TODO: Make it a user friendly program

:AUTHOR: Jay William Johnson
:ORGANIZATION: Taimao
:CONTACT: python@boun.cr
:SINCE: Wed Aug 28 10:50:58 2013
:VERSION: 0.1
"""
#===============================================================================
# PROGRAM METADATA
#===============================================================================
__author__ = 'Jay William Johnson'
__contact__ = 'python@boun.cr'
__copyright__ = ''
__license__ = ''
__date__ = 'Fri Sep 13 10:53:58 2013'
__version__ = '0.1'

#===============================================================================
# IMPORT STATEMENTS
#===============================================================================
import os
from datetime import datetime, date, timedelta
import xlwt # FOR WRITING AND FORMATTING EXCEL FILES
import xlrd # FOR READING AND FORMATTING EXCEL FILE DATA
from tkFileDialog import askopenfilename
from win32com.client import Dispatch
from string import ascii_uppercase as AB

# Create "Excel Alphabet" from A to BZ
XL_ALPHABET = list(AB) + ['A' + L for L in AB] + ['B' + L for L in AB]


#===============================================================================
# METHODS
#===============================================================================
def toDate(sheet, cell, book_val):
    '''Convert excel cell value object to a date object if possible.
    Else return 'None'.
    '''
    try:
        d = datetime(*xlrd.xldate_as_tuple(sheet.cell_value(*cell), book_val))
        return d.date()
    except:
        #print 'Skipped date fail:', sheet.name, cell
        return None

'''
Retrieve all entries from an excel file, ASE 月槽車, as a list of records.

Example record in file "ASE ## 月槽車":
8/24 | 鹽酸 | 2003-000-00000-000 | 230 | K# | 純水 | P1
8/24 | 液鹼 | 2003-000-00000-000 | 320 | K# | 純水 |

Parameters: excel filename
Returns a list of dictionaries.
Record properties are:
    date = datetime.date object
    product = product name
    pID = product ID (external source)
    amount = a number
    location = 半__ or 電__ (sheet name)
    department_id = K#
    department_type = 純水, 廢水, 廢氣, etc.
    note = currently used for originating page number (paperwork)
    _origin = originating Excel file and sheet where data is obtained
'''
depts = [u"半導體",u"電子廠"]
def read_entries_from_xl(filename):
    book = xlrd.open_workbook(filename=filename)

    #==============================================================================
    # xlrd notes:
    # book.sheet_names() # returns list of sheet names
    # book.sheets() # returns list of all sheets
    # book.sheet_by_index(0) # returns first sheet
    # book.sheet_by_name(book.sheet_names()[0]) # returns sheet by name
    # book.user_name # returns last person to save file
    #==============================================================================

    ret_list = []
    for sheet in book.sheets():
        if sheet.name not in depts:
            continue
        for r in range(sheet.nrows):
            day = toDate(sheet, (r,0), book.datemode)
            if day:
#                if str(day.year) not in sheet.cell_value(r,1):
#                    print (
#                        "Date year and ID year do not match\n\t"
#                        + sheet.name + ": row " + str(r+1) + "\n\t"
#                        + repr(sheet.cell_value(r,0)) + " not in " + repr(sheet.cell_value(r,1))
#                    )
                # SPLIT THE PRODUCT AND PRODUCT NUMBER
                prod = sheet.cell_value(r,1)
                pID = sheet.cell_value(r,2)
                amt = sheet.cell_value(r,3)
                deptID = sheet.cell_value(r,4)
                deptType = sheet.cell_value(r,5)
                note = sheet.cell_value(r,6)
                origin = os.path.split(filename)[1] + ":" + sheet.name
                ret_list.append({
                    'date':day,
                    'product':prod,
                    'pID':pID,
                    'amount':amt,
                    'location':sheet.name,
                    'department_id':deptID,
                    'department_type':deptType,
                    'note':note,
                    '_origin':origin,
                })
    return ret_list




def write_dept_totals(entries, begin_date, end_date, savedir):

    #default style
    style = xlwt.XFStyle()
    style.font.bold = True
    style.font.height = 250


    records = entries
    w = xlwt.Workbook()
    sheet_ban = w.add_sheet(depts[0])
    sheet_dian = w.add_sheet(depts[1])
    month = records[0]['date'].month

    def addHeader(sheetName, row):
        if row != 0:
            row += 1
        sheetName.write(row, 2, u'台茂槽車進貨需求確認單', style)
        row += 1
        sheetName.write(row, 0, u'進貨日期', style)
        sheetName.write(row, 1, u'材料名稱', style)
        sheetName.write(row, 2, u'料號', style)
        sheetName.write(row, 3, u'需求量', style)
        sheetName.write(row, 4, u'需求單位', style)
        sheetName.write(row, 5, u'備註', style)
        row += 1
        return row


    #botton line
    topstyle = xlwt.XFStyle()
#    topstyle.borders = xlwt.Borders()
    topstyle.borders.top = xlwt.Borders.MEDIUM
#    topstyle.borders = tborders


    def write_to_sheet(sheet, data):
        # Column spacing
        sheet.col(0).width = 2600
        sheet.col(1).width = 3500
        sheet.col(2).width = 5000 # 3333 = 1 inch
        sheet.col(3).width = 2500
        sheet.col(4).width = 3333
        sheet.col(5).width = 2000

        # Freeze top two rows
        sheet.set_panes_frozen(True)
        sheet.set_horz_split_pos(2)

        # Add data
        row = 0
        totals = {}
        pg_start = 0

        dateA = data[-1]["date"]
        dateB = data[0]["date"]
        for each in data:

            if each["location"] != sheet.name:
                continue
            if each["date"] < begin_date:
                continue
            if each["date"] > end_date:
                continue
            if row == 0:
                row = addHeader(sheet,row)
            if each["note"] != "":
#                row = addHeader(sheet,row)
                #row += 1 # Skip a line
                pg_start = row
            date = each["date"]
            addtop = topstyle if pg_start == row else xlwt.XFStyle()
            addtop.alignment.horz = xlwt.Alignment.HORZ_CENTER
            sheet.write(row,0,str(date.month) +'/'+ str(date.day), addtop)
            sheet.write(row,1,each["product"], addtop)
            sheet.write(row,2,each["pID"], addtop)
            sheet.write(row,3,each["amount"], addtop)
            sheet.write(row,4,each["department_id"]+each["department_type"], addtop)
            sheet.write(row,5,each["note"], addtop)
            row += 1
            # Add to totals
            if each["location"] == depts[0]:
                if each['department_type'] == u'廢氣':
                    each['department_type'] = u'廢水'
                if each['department_type'] not in totals:
                    totals[each['department_type']] = {}
                if each['product'] not in totals[each['department_type']]:
                    totals[each['department_type']][each['product']] = {'id': each['pID'],
                                                'total': 0 }
                totals[each['department_type']][each['product']]['total'] += each['amount']
                if each['date'] < dateA:
                    dateA = each['date']
                if each['date'] > dateB:
                    dateB = each['date']
            if each["location"] == depts[1]:
                if each['product'] not in totals:
                    totals[each['product']] = {'id': each['pID'],
                                                'total': 0 }
                totals[each['product']]['total'] += each['amount']
                if each['date'] < dateA:
                    dateA = each['date']
                if each['date'] > dateB:
                    dateB = each['date']


        style = xlwt.XFStyle()
#        borders = xlwt.Borders()
#        borders.left = xlwt.Borders.DASHED
#        style.borders = borders
        style.font.bold = True
        row += 2
        #TODO: WRITE DATE
        sheet.write(row,1,str(dateA.year-1911) + " / " + str(dateA.month) + " / " + str(dateA.day)
            + " ~ " + str(dateB.year-1911) + " / " + str(dateB.month) + " / " + str(dateB.day), style)
        row += 2


        if sheet.name == depts[0]:
            for dp in reversed(totals.keys()):
                print len(totals[dp])
                sheet.write(row,0, dp if dp == u'純水' else u'廢水/氣')
                for line, key in enumerate(reversed(totals[dp].keys()) if len(totals[dp]) == 2 else totals[dp].keys()):
                    row2 = row
                    if line == 1 and len(totals[dp]) > 2: row2 += 1
                    if line == 2: row2 -= 1
                    sheet.write(row2,1, key, style)
                    sheet.write(row2,2, totals[dp][key]['id'])
                    sheet.write(row2,3, totals[dp][key]['total'], style)
                    row += 1
                row += 1
        if sheet.name == depts[1]:
            ordlist = [ u'鹽酸',
                        u'液鹼',
                        u'硫化氫鈉50%',
                        u'凝結劑',
                        u'氯化鐵',
                        u'',
                        u'硫酸50%',
                        u'',
                        u'雙氧水']
            for key in ordlist:
                print key
                if key in totals:
                    sheet.write(row,1, key, style)
                    print totals[key]
                    sheet.write(row,2, totals[key]['id'])
                    sheet.write(row,3, totals[key]['total'], style)
                    row += 1
                if key == '':
                    row += 1



    write_to_sheet(sheet_ban, entries)
    write_to_sheet(sheet_dian, entries)


    print sheet_ban.name




    print "Saved to", repr(savedir) #os.getcwd()
    year = records[0]['date'].year
    savename = savedir + u'/formatted_'+str(begin_date.day)+'.'+str(end_date.day)+'_' + str(year) + '_' + '{0:02}'.format( month ) + u'_totals.xls'
    #print ">>>>", savename
    w.save(savename)


    # Add filter menus across row 2
    # Using win32com
    xl = Dispatch("Excel.Application")
    xl.Workbooks.Open(savename)
    xl.ActiveWorkbook.ActiveSheet.Rows(2).AutoFilter(1)
    s1 = xl.ActiveWorkbook.ActiveSheet
    s1.Range(s1.Cells(1,1),s1.Cells(1000,10)).Font.Name = u"新細明體"
    s1.Range(s1.Cells(1,1),s1.Cells(1000,10)).Font.Size = 11

    # Sheet 2
    xl.ActiveWorkbook.Sheets(2).Select()
    xl.ActiveWorkbook.ActiveSheet.Rows(2).AutoFilter(1)
    s1 = xl.ActiveWorkbook.ActiveSheet
    s1.Range(s1.Cells(1,1),s1.Cells(1000,10)).Font.Name = u"新細明體"
    s1.Range(s1.Cells(1,1),s1.Cells(1000,10)).Font.Size = 11

    # Save and quit
    xl.ActiveWorkbook.Sheets(1).Select() # Open to sheet one
    xl.ActiveWorkbook.Close(SaveChanges=1)
    xl.Quit()





'''
Write an Excel file with five pages showing totals as seen in 'layout' parameter.

Paramters:
    entries = A list of dict objects (records)
'''
layout = __ = dict()
__[u'K9用藥記錄'] = [u'1F 純水',u'2F 線上',u'4KK 廢水',u'6KK 廢水']
__[u'K9純廢水用藥記錄'] = [u'1F 純水',u'4KK 廢水',u'6KK 廢水']
__[u'廢水用藥記錄'] = [u'4KK 廢水',u'6KK 廢水',u'K5 廢水',u'K7 廢水',u'K11 廢水',u'K12 廢水',u'K21 廢水']
__[u'純水用藥記錄'] = [u'1F 純水',u'K15 純水',u'K1 純水',u'K3 純水',u'K5 純水',u'K7 純水',u'K11 純水',u'K12 純水',u'K21 純水']
__[u'全部'] = [u'1F 純水',u'2F 線上',u'K1 純水',u'K3 純水',u'K5 純水',u'K5 廢水',u'K7 純水',u'K7 廢水',u'K11 純水',u'K11 廢水',u'K12 純水',u'K12 廢水',u'K21 純水',u'K21 廢水',u'K15 純水',u'4KK 廢水',u'6KK 廢水']

def write_type_totals(entries, begindate, savedir):
    '''
    1) Create five pages with headers and list of dates
    2) Create a totaling array with an entry for each date
    3) Scan through data and add totals for each header
    4) Write array of data for each column
    5) Write month totals as bottom row
    '''


    #default style
    style = xlwt.XFStyle()

    style2 = xlwt.XFStyle()
    style2.pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    style2.pattern.pattern_fore_colour = xlwt.Style.colour_map['tan']


    style_H1 = xlwt.XFStyle()
    style_H1.borders.bottom = xlwt.Borders.THIN
    style_H1.alignment.horz = xlwt.Alignment.HORZ_CENTER
    style_H1.font.bold = True
    style_H1.pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    style_H1.pattern.pattern_fore_colour = xlwt.Style.colour_map['pale_blue']



    style_date = xlwt.XFStyle()
    style_date.alignment.horz = xlwt.Alignment.HORZ_CENTER
    style_date.borders.right = xlwt.Borders.DASHED


    style_date2 = xlwt.XFStyle()
    style_date2.alignment.horz = xlwt.Alignment.HORZ_CENTER
    style_date2.borders.right = xlwt.Borders.DASHED
    style_date2.pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    style_date2.pattern.pattern_fore_colour = xlwt.Style.colour_map['tan']

    #underline style
    underline = xlwt.XFStyle()
    underline.borders.bottom = xlwt.Borders.THIN
    #underline style
    dbunderline = xlwt.XFStyle()
    dbunderline.borders.bottom = xlwt.Borders.DOUBLE
    dbunderline.alignment.horz = xlwt.Alignment.HORZ_CENTER
    dbunderline.font.bold = True
    dbunderline.pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    dbunderline.pattern.pattern_fore_colour = xlwt.Style.colour_map['gold']



    records = entries#.fetchall()
    #Add dates column starting at row 2
    month = records[0]['date'].month

    iter_date = date(begindate.year,month,1)
    end_date = date(begindate.year+1 if month == 12 else begindate.year,(month%12)+1,1)
    dates = []
    while iter_date < end_date:
        dates.append( str(iter_date.month) +' / '+
                           str(iter_date.day) )# +'/'+
                           #str(iter_date.year) )
        iter_date += timedelta(1)
    print dates


    w = xlwt.Workbook()
    # Add one sheet at a time
    for name in layout:
        sheet = w.add_sheet(name)
        sheet.write(len(dates)+5,0,u"總額",style_date)
        headers = layout[name]
        # Get sub-headers
        products = {}
        for i in range(len(headers)):
            if headers[i] not in products:
                products[headers[i]] = set()
            dept,typ = headers[i].split()
            for rec in entries:
                if rec['department_id'] == dept and \
                   rec['department_type'] == typ:
                    products[headers[i]].add(rec['product'])
#        print products

        # Write dates down first column
        for i in range(len(dates)):
            sheet.write(2+i,0,dates[i], style_date if (i+1)%5 != 0 else style_date2)

        # Write headers in first row along with data, column by column
        col = 1
        for i in range(len(headers)):
            span = len(products[headers[i]])
            dept,typ = headers[i].split()
            if not span:
                continue
            sheet.write_merge(0,0, col, col+span-1, headers[i], style_H1)
            sheet.write_merge(len(dates)+3,len(dates)+3, col, col+span-1, headers[i], style_H1)

            for prod in products[headers[i]]:
                sheet.col(col).width= 3000
                sheet.write(1,col, prod, style_H1)
                sheet.write(len(dates)+4,col, prod, style_H1)
                totals = [0]*len(dates)

                for rec in entries:
                    if rec['department_id'] == dept and \
                       rec['department_type'] == typ and \
                       rec['product'] == prod:
                        rec_day = rec['date'].day
                        print rec_day, len(totals)
                        totals[rec_day-1] += rec['amount']


                for j in range(len(dates)):
                    if totals[j] > 0 and j+1 != len(dates):
                        sheet.write(2+j,col,totals[j], style if (j+1)%5 != 0 else style2)
                    elif (j+1)%5 == 0 and j+1 != len(dates):
                        sheet.write(2+j,col,"", style2)
                    # Style the blank cells
                    if j+1 == len(dates):
                        sheet.write(2+j,col,totals[j] if totals[j] else "", underline)



#                sheet.write(len(dates)+3, col, headers[i], style_H1)
                print "here:", col, XL_ALPHABET[col]
                sheet.write(len(dates)+5, col,
                            xlwt.Formula("SUM("+XL_ALPHABET[col]+"3:"
                                               +XL_ALPHABET[col]+str(len(dates)+2)+")"),
                            dbunderline)
                col += 1
            # Put a narrow divider between departments
            sheet.col(col).width= 300
            col += 1


    year = records[0]['date'].year
    savename = savedir + "/"+ str(year) + '_' + '{0:02}'.format( month ) + '_totals.xls'
    #print "<><><>", savename
    w.save(savename)





#===============================================================================
# MAIN METHOD AND TESTING AREA
#===============================================================================
def main():
    """Description of main()"""

    filename = askopenfilename(initialdir=u"C:\\Documents and Settings\\Administrator\\My Documents\\Google 云端硬盘\\Company\\ASE槽車\\槽車計算新程式")
    savedir = os.path.dirname(filename) #askdirectory(initialdir=u"C:\\Documents and Settings\\Administrator\\My Documents\\Google 云端硬盘\\Company\\ASE槽車\\槽車計算新程式")
    print repr(filename)


    begindate = raw_input("First day (yyyy-mm-dd):")
    lastdate = raw_input("Last day (yyyy-mm-dd):")
    begindate = date(*[int(d) for d in begindate.split("-")])
    lastdate = date(*[int(d) for d in lastdate.split("-")])

    entries = read_entries_from_xl(filename)

    write_type_totals(entries, begindate, savedir=savedir)

    write_dept_totals(entries, begindate, lastdate, savedir=savedir)

    raw_input(""+savedir)


if __name__ == '__main__':
    main()