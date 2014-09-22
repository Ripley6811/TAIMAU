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
from ctypes import cdll
import xlrd
from datetime import date, timedelta
from time import sleep
from win32print import EnumPrinters


#XXX: Ensure the TSCLIB.dll is located in windows/system32 folder.
try:
    tsc = cdll.LoadLibrary("TSCLIB.DLL")
except WindowsError as e:
    print e
    tsc = None

portkeyword="243" # "TSC TTP-243 Plus"

printers = [p[2] for p in EnumPrinters(2) if portkeyword in p[2]]
if len(printers):
    try:
        portname, = printers # Asserts only one printer is in list.
        print "Printer:", portname
    except ValueError as e:
        print "More than one printer matches the keyword '{}'".format(portkeyword)
else:
    print "No printer found with keyword '{}'.".format(portkeyword)

#XXX: Portname must match the name of the printer on the system.
def openport():
    try:
        tsc.openport(portname)
    except ValueError:
        #XXX: ValueError always thrown but functions properly. Ignore it.
        pass
    print 'PORT "{}" OPENED'.format(portname)

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
    if not tsc:
        return
    openport()
    setup()
    clearbuffer()

    tab = 35
    tab2 = 154
    tab3 = 408

    noPNadjust = 0
    if not PN:
        noPNadjust = 43
    windowsfont(tab,15+noPNadjust, "Material name:", 30)
    #showinfo(material.encode('utf8'), material.encode('utf8'))
    try:
        windowsfont(tab+180,6+noPNadjust, material.encode('big5'), 42, style=2)
    except UnicodeEncodeError:
        windowsfont(tab+180,6+noPNadjust, material.encode('utf8'), 42, style=2)

    if PN:
        windowsfont(tab,58, "P/N:", h=26)
        windowsfont(tab2,55, PN, h=30, style=2)
        windowsfont(tab3,55, u"料號".encode('big5'), h=30)
        barcode(tab,85, PN, d=40)

    windowsfont(tab,128, "LOT NO:", h=26)
    windowsfont(tab2,125, LOT_NO, h=30, style=2)
    windowsfont(tab3,125, u"批號".encode('big5'), h=30)
    barcode(tab,155, LOT_NO, d=40)

    if PN:
        #windowsfont(tab,198, "ASE No:".encode('big5'), h=26)
        windowsfont(tab,198, "Min Pkg No:".encode('big5'), h=24)
    else:
        windowsfont(tab,198, "BOX NO:".encode('big5'), h=26)

#    windowsfont(tab,198, "BOX NO:".encode('big5'), h=26)
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




if __name__ == '__main__':
    pass
