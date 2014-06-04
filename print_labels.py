# -*- coding: utf-8 -*-
'''
Program for printing to a TSC TTP-243E Plus label printer.
Coding information and examples at:
http://www.tscprinters.com/cms/upload/download_en/DLL_instruction.pdf

Date completed: 2013-11-15

Updated: 2013-11-29
-Changed max number to print function: Exits when blank
-Verification of RT. No.: 10 digits and uniqueness

'''
from ctypes import *
import xlrd
from datetime import date, timedelta
from tkMessageBox import showinfo
from time import sleep


#XXX: Ensure the TSCLIB.dll is located in windows/system32 folder.
tsc = None
try:
    tsc = cdll.LoadLibrary("TSCLIB.DLL")
except:
    pass

#XXX: Portname must match the name of the printer on the system.
#def openport(portname="TSC TTP-243(E) - (V)"):
def openport(portname="TSC TTP-243E PLUS"):
    try:
        tsc.openport(portname)
    except ValueError:
        pass

def setup(w="70",h="70",c="2",d="2",e="0",f="3",g="0"):
    # w = label width mm
    # h = label height mm
    # c = print speed
    # d = print density
    # e = sensor type
    # f = vertical gap height in mm
    # g = horizontal gap shift
    try:
        tsc.setup(str(w),str(h),str(c),str(d),str(e),str(f),str(g))
    except ValueError:
        pass

# clear all previously entered barcode and text
def clearbuffer():
    tsc.clearbuffer()

# Must pass strings for all values
def barcode(x,y,text,d="40",c="128",e="0",f="0",g="2",h="4"):
    try:
        # x, y starting point
        # d = height
        tsc.barcode(str(x),str(y),str(c),str(d),str(e),str(f),str(g),str(h),str(text))
    except ValueError:
        pass

def windowsfont(x,y,text,h=40,rotation=0,style=0,line=0,font=u"Arial"):
    # x,y starting point
    # h = font height
    # rotation = counter clockwise rotation degrees
    # style: 0 = Normal, 1 = Italic, 2 = Bold, 3 = Italic Bold
    # line: 0 = no underline, 1 = underline
    # font = Font type face
    # text = Text to print
    try:
        tsc.windowsfont(int(x),int(y),int(h),int(rotation),int(style),int(line),str(font),str(text))
    except ValueError:
        pass

def printlabel(a=1, b=1):
    # a = number of label sets
    # b = number of print copies
    try:
        tsc.printlabel(str(a),str(b))
    except ValueError:
        pass

def sendcommand(s):
    try:
        tsc.sendcommand(s)
    except ValueError:
        pass

def closeport():
    tsc.closeport()

def TM_label(material, PN, LOT_NO, ASE_NO, QTY, ExpDate, DOM, RT_NO):
    openport()
    setup()
    clearbuffer()

    tab = 35
    tab2 = 152
    tab3 = 408

    noPNadjust = 0
    if not PN:
        noPNadjust = 43
    windowsfont(tab,15+noPNadjust, "Material name:", 30)
    #showinfo(material.encode('utf8'), material.encode('utf8'))
    windowsfont(tab+180,6+noPNadjust, material, 42, style=2)

    if PN:
        windowsfont(tab,58, "P/N:", h=26)
        windowsfont(tab2,55, PN, h=30, style=2)
        windowsfont(tab3,55, u"料號".encode('big5'), h=30)
        barcode(tab,85, PN, d=40)

    windowsfont(tab,128, "LOT NO:", h=26)
    windowsfont(tab2,125, LOT_NO, h=30, style=2)
    windowsfont(tab3,125, u"批號".encode('big5'), h=30)
    barcode(tab,155, LOT_NO, d=40)

    windowsfont(tab,198, "ASE NO:".encode('big5'), h=26)
    windowsfont(tab2,195, ASE_NO, h=30, style=2)
    barcode(tab,225, ASE_NO, d=40)

#    if isinstance(QTY, str):
#        QTY = QTY.encode('big5')
    windowsfont(tab,268, "Q'TY:", h=26)
    windowsfont(tab2,265, QTY, h=30, style=2)
    windowsfont(tab3,265, u"容量".encode('big5'), h=30)
    barcode(tab,295, QTY, d=40)

    windowsfont(tab,338, "Exp Date:", h=26)
    windowsfont(tab2,335, ExpDate, h=30, style=2)
    windowsfont(tab3,335, u"使用期限".encode('big5'), h=30)
    barcode(tab,365, ExpDate, d=30)

    windowsfont(tab,398, "DOM:", h=26)
    windowsfont(tab2,395, DOM, h=30, style=2)
    windowsfont(tab3,395, u"製造日期".encode('big5'), h=30)
    barcode(tab,425, DOM, d=30)

    if RT_NO:
        windowsfont(tab,458, "RT NO:", h=26)
        windowsfont(tab2,455, RT_NO, h=30, style=2)
        barcode(tab,485, RT_NO, d=40)

    printlabel(1,1)
    closeport()
    sleep(0.5)

#TM_label("Liu Suan 98%", "2013-001-01116-000", "P13111401", "P131114010002",
#         "6", "20141114", "20131114", "3B1476VB01")

def TM_DMlabel(material, PN, LOT_NO, ASE_NO, QTY, ExpDate, DOM, RT_NO):
    openport()
    setup()
    clearbuffer()

    tab = 145
    tab2 = 262
    tab3 = 408

    BOX_NO = str(int(ASE_NO[-4:]))
    datastr = ('"'+str(RT_NO) + "|" +
              str(PN) + "|" +
              str(LOT_NO) + "|" +
              str(int(QTY)) + "|" +
              str(DOM) + "|" +
              str(BOX_NO)+'"')

    '''The default 'model' does not work. Use 'M2' for enhanced version.
    '''
    #sendcommand('QRCODE 10,10,Q,7,A,0,M1,S0,"M1,S0 THE FIRMWARE HAS BEEN UPDATED"')
    #sendcommand('QRCODE 10,300,Q,7,A,0,M2,S0,"M2,S0 THE FIRMWARE HAS BEEN UPDATED"')
    #sendcommand('QRCODE 300,300,Q,7,A,0,M2,S1,"M2,S1 THE FIRMWARE HAS BEEN UPDATED"')
    sendcommand('DMATRIX 190,40,400,400,'+datastr)


    windowsfont(tab,268, "BATCH:", h=26)
    windowsfont(tab2,265, RT_NO, h=30, style=2)

    windowsfont(tab,308, "Part No:", h=26)
    windowsfont(tab2,305, PN, h=30, style=2)

    windowsfont(tab,348, "Lot No:", h=26)
    windowsfont(tab2,345, LOT_NO, h=30, style=2)

    windowsfont(tab,388, "Qty:", h=26)
    windowsfont(tab2,385, str(int(QTY)), h=30, style=2)

    windowsfont(tab,428, "MFG Date:", h=26)
    windowsfont(tab2,425, DOM, h=30, style=2)

    windowsfont(tab,468, "Box No:", h=26)
    windowsfont(tab2,465, BOX_NO, h=30, style=2)


    printlabel(1,1)
    closeport()
    sleep(0.5)

def TM_QRlabel(material, PN, LOT_NO, ASE_NO, QTY, ExpDate, DOM, RT_NO):
    openport()
    setup()
    clearbuffer()

    tab = 35
    tab2 = 152
    tab3 = 408

    '''windowsfont(tab,15, "Material name:", 30)
    windowsfont(tab+180,6, material.encode('big5'), 42, style=2)

    windowsfont(tab,58, "P/N:", h=26)
    windowsfont(tab2,55, PN, h=30, style=2)
    windowsfont(tab3,55, u"料號".encode('big5'), h=30)
    #sendcommand("QRCODE 35,85,H,7,A,0,'12345|5432134'")
    #sendcommand("DMATRIX 20,20,400,400,'DMATRIX EXAMPLE 1'")
    '''
    '''The default 'model' does not work. Use 'M2' for enhanced version.
    '''
    #sendcommand('QRCODE 10,10,Q,7,A,0,M1,S0,"M1,S0 THE FIRMWARE HAS BEEN UPDATED"')
    sendcommand('QRCODE 10,300,Q,7,A,0,M2,S0,"M2,S0 THE FIRMWARE HAS BEEN UPDATED"')
    sendcommand('QRCODE 300,300,Q,7,A,0,M2,S1,"M2,S1 THE FIRMWARE HAS BEEN UPDATED"')
    #sendcommand('DMATRIX 100,300,400,400,"DMATRIX EXAMPLE 1"')
    '''
    windowsfont(tab,128, "LOT NO:", h=26)
    windowsfont(tab2,125, LOT_NO, h=30, style=2)
    windowsfont(tab3,125, u"批號".encode('big5'), h=30)
    barcode(tab,155, LOT_NO, d=40)

    windowsfont(tab,198, "ASE NO:".encode('big5'), h=26)
    windowsfont(tab2,195, ASE_NO, h=30, style=2)
    barcode(tab,225, ASE_NO, d=40)

    windowsfont(tab,268, "Q'TY:", h=26)
    windowsfont(tab2,265, QTY, h=30, style=2)
    windowsfont(tab3,265, u"容量".encode('big5'), h=30)
    barcode(tab,295, QTY, d=40)

    windowsfont(tab,338, "Exp Date:", h=26)
    windowsfont(tab2,335, ExpDate, h=30, style=2)
    windowsfont(tab3,335, u"使用期限".encode('big5'), h=30)
    barcode(tab,365, ExpDate, d=30)

    windowsfont(tab,398, "DOM:", h=26)
    windowsfont(tab2,395, DOM, h=30, style=2)
    windowsfont(tab3,395, u"製造日期".encode('big5'), h=30)
    barcode(tab,425, DOM, d=30)

    windowsfont(tab,458, "RT NO:", h=26)
    windowsfont(tab2,455, RT_NO, h=30, style=2)
    barcode(tab,485, RT_NO, d=40)
    '''
    printlabel(1,1)
    closeport()
    sleep(0.5)

#TM_label("Liu Suan 98%", "2013-001-01116-000", "P13111401", "P131114010002",
#         "6", "20141114", "20131114", "3B1476VB01")

def lookup_product_code(book, sheetname, lookname):
    # Get product lookup data
    prodsheet = book.sheet_by_name("Products")
    products = []
    for row in range(prodsheet.nrows):
        pname = prodsheet.cell_value(row,0)
        if lookname == pname:
            pcomp = prodsheet.cell_value(row,1)
            pcode = prodsheet.cell_value(row,2)
            pqty = prodsheet.cell_value(row,3)
            pexp = prodsheet.cell_value(row,4)
            products.append((pcomp,pcode,pqty,pexp))
    if len(products) > 1:
#        print "Which product code:"
        for i, each in enumerate(products):
#            print i+1, '=', each[0], ':', each[1], "(", each[2], ")"
            if each[0] in sheetname:
                return each
#        return products[input("Select #")-1]

    if len(products) == 0:
        print "ERROR: Product not found in code lookup list."
        print "Make sure the spelling is correct and matches the desired product."
        raw_input("HIT ENTER TO EXIT...")

#    print 'SELECTED:', products[0][0], ':', products[0][1], "(", products[0][2], ")"
    return products[0]


def rt_check(sheet, valrow, rtn):
    if len(rtn) != 10:
        print "RT No. ERROR: Not 10 characters long."
        return False
    # Find RT No. column
    rtcol = -1
    for icol in range(sheet.ncols):
        if sheet.cell_value(0,icol) == u'RT.No':
            rtcol = icol
    if rtcol < 0:
        print "RT No. ERROR: Column not found."
        return False

    for irow in range(1,valrow):
        if sheet.cell_value(irow,rtcol) == rtn:
            print "RT No. ERROR: Value already exists."
            return False

    return True



def printapp(noprint=False):
    filename = u'C:\\Users\\chairman\\Documents\\桶裝出貨表.xls'
    book = xlrd.open_workbook(filename)


    # Get print info from user
    print "Select sheet by index number:"
    for i, sheetname in enumerate(book.sheet_names()):
        print i+1, "=", sheetname
    sheet = book.sheet_by_index(input("From sheet #")-1)
    row = input("Print row #")-1
    print ''

    # Headers and corresponding data
    dic = {}
    for col in range(sheet.ncols):
        try:
            dic[sheet.cell_value(0,col)] = sheet.cell_value(row,col).decode('utf8')
        except:
            dic[sheet.cell_value(0,col)] = sheet.cell_value(row,col)


    # RT No. validation
    if (sheet.name not in ['PR',u'雙葉']) and not rt_check(sheet, row, dic[u'RT.No']):
        # Exit if check is False
        raw_input("Hit enter to exit.")
        return False

    # Get ASE product code, P/N
    PN, QTY, Exp = lookup_product_code(book, sheet.name, dic[u'品名'])[1:4]
    print repr(PN), repr(QTY), repr(Exp)

    # Check the ASE No and number of units match
    #TODO
    dic[u"ASE.No"] = int(dic[u"ASE.No"].split("-")[0][-4:])
    print 'PRODUCT:', dic[u'品名']
    print 'PN:', PN
    print dic[u"包裝"], "labels in this set."
    print ''

    # Get DOM and Exp date
    ExpDate = "dddddddd"
    pdate = dic[u"製造批號"][1:7]
    dateDOM = date(2000+int(pdate[:2]), int(pdate[2:4]), int(pdate[4:6]))
    DOM = "{0:04}{1:02}{2:02}".format(dateDOM.year, dateDOM.month, dateDOM.day)
    try:
        dateDelta = timedelta((365/12)*Exp)
        ''' # The following is for an exact expiration date
        DOM = "{0:04}{1:02}{2:02}".format(dateDOM.year, dateDOM.month, dateDOM.day)
        dateEXP = dateDOM + dateDelta
        ExpDate = "{0:04}{1:02}{2:02}".format(dateEXP.year, dateEXP.month, dateEXP.day)
        '''
        inc_year = False
        if int((dateDOM.month-1 + Exp) / 12):
            inc_year = True
        ExpDate = "{0:04}{1:02}{2:02}".format(
                (dateDOM.year + int((dateDOM.month-1 + Exp) / 12)) if inc_year else dateDOM.year,
                int((dateDOM.month-1 + Exp) % 12)+1,
                dateDOM.day)
    except:
        raw_input('Error converting expiration date. Using "dddddddd"\nHIT ENTER TO CONTINUE...')


    barQR = "barcode"
    if u"中" in sheet.name:
        print "Select 1 for BARCODE"
        print "Select 2 for DATA MATRIX"
        try:
            barQR = int(raw_input(">"))
            if barQR == 1:
                barQR = "barcode"
            if barQR == 2:
                barQR = "DM"
        except:
            barQR = 0


    while True:
        print "Set max number to print (BLANK will EXIT)."
        nPrint = raw_input("Stop at #")
        try:
            nPrint = int(nPrint)
        except:
            print "Not a valid number... Exiting."
            break
        for i in range(int(dic[u"包裝"])):
            if i >= nPrint:
                break
            ASE_NO = "{0}{1:04}".format(dic[u"製造批號"],dic[u"ASE.No"] + i)
            print "---------------------"
            try:
                print dic[u'品名']
            except:
                print "(can't print a Chinese character)"
            print PN
            print dic[u"製造批號"]
            print ASE_NO
            print QTY
            print ExpDate
            print DOM
            print dic[u"RT.No"]
            print "---------------------"
            if not noprint:
                if barQR == "barcode":
                    TM_label(dic[u'品名'], PN, dic[u"製造批號"], ASE_NO,
                             QTY, ExpDate, DOM, dic[u"RT.No"])
                if barQR == "DM":
                    TM_DMlabel(dic[u'品名'], PN, dic[u"製造批號"], ASE_NO,
                             QTY, ExpDate, DOM, dic[u"RT.No"])
        if noprint:
            raw_input("Finished. Press enter to close")
    raw_input("Hit enter to close")

if __name__ == '__main__':
    printapp()