#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Use for switching between English and Chinese text in GUI.

description

:REQUIRES:

:TODO:

:AUTHOR: Ripley6811
:ORGANIZATION: None
:CONTACT: python@boun.cr
:SINCE: Tue Aug 26 19:49:02 2014
:VERSION: 0.1
"""

from Tkinter import StringVar

from utils import settings

#===============================================================================
# METHODS
#===============================================================================

# TODO: Read settings from file for user desired language
toChinese = False
worddict = {
    u"Purchases" : u"購買",
    u"Sales" : u"銷售",
    u"Manage List" : u"公司清單管理",
    u"File" : u"文件(F)",
    u'Main' : u'主控制',
    u"Reports" : u"報告(R)",
    u"Open" : u"開資料庫",
    u"Exit" : u"關閉",
    u"Font" : u"字體",
    u"About" : u"關於",
    u"Help" : u"幫助",
    u"Supplier" : u"供應商",
    u"Customer" : u'客戶',
    u"(NA)" : u"(沒有)",
    u"(Avail:" : u"(剩下:",
    u"Branch" : u"分公司",
    u"\u26DF Create Manifest" : u"\u26DF 創建出貨單",
    u"+ PO" : u"+ 訂單",
    u"% discount" : u"% 折扣",
    u"Settings" : u"設置",
    u"\u2692 Create Product Order (PO)" : u"\u2692 創建訂單 (PO)",
    u"\u2692 Update Product Order (PO)" : u"\u2692 編輯訂單 (PO)",
    u"\u2620 Archive this PO \u2620" : u"\u2620 非活狀態且歸檔 \u2620",
    u"Archive this PO?" : u"變成非活狀態且歸檔?",
    u'PO appears to be complete.' : u'訂單好像結束了.',
    u'All units have shipped.' : u'所有的數量已送出去.',
    u"+ product" : u"+ 產品",
    u"PO #" : u"訂單編號",
    u"Order (PO) #:" : "訂單編號:",
    u"Date of PO" : u"訂單創建日期",
    u"Date of order/shipment" : u"訂單或出貨日期",
    u"Select one product" : u"選一個產品",
    u"Qty" : u"數量",
    u"Taimau" : u"台茂",
    u"Note" : u"備註",
    u"Price" : u"價格",
    u"Apply tax?" : u"收稅？",
    u"\u26D4 Cancel" : u"\u26D4 取消",
    u"NOTE:" : u"備註:",
    u'Verify these entries:' : u'確認下面:',
    u"Edit PO" : u"編輯訂單",
    u"Product" : u"產品",
    u'Active POs' : u'主動訂單',
    u'Manage POs' : u'管理訂單',
    u'Order Products' : u'訂購產品',
    u'All POs' : u'所有訂單',
    u'Manifests & Invoices' : u'管理出貨單&發票',
    u"Maximum exceeded" : u"最大突破",
    u"Only a maximum of five items allowed." : u"最多只有5個項目.",
    u"\u2713 Submit" : u"\u2713 提交",
    u'Driver:' : u'司機:',
    u'Truck:' : u'車牌:',
    u'Note:' : u'備註:',
    u'Number of records to show:' : u'顯示數量:',
    u'PO Closed?' : u'用完了?',
    u'Create Invoice' : u'創建發票',
    u'Activity Report' : u'記錄報告',
    u'Mark as Paid' : u'標記為已付款',
    u'Start date' : u'開始日期',
    u'End date' : u'結束日期',
    u'Change Database' : u'還資料庫',
    u'View/edit manifest' : u'編輯出貨單',
    u'View/edit invoice' : u'編輯發票',
    u'Delete manifest item' : u'刪除出貨單項次',
    u'Delete invoice item' : u'刪除發票項次',
    u'Products' : u'產品',
    u'Product Info/Edit' : u'產品資訊/編輯',
    u'Product Price History' : u'產品價格歷史',
    u'Supplies We Purchase' : u'我們採購用品',
    u'Products We Sell' : u'我們銷售產品',
    u'Inventory Label:' : u'庫存標籤(內用):',
    u'Product Label:' : u'產品標籤(客用):',
    u'English Label:' : u'英語標籤(英名):',
    u'SKU (abbrev.):' : u'SKU (1-2字縮寫):',
    u'Units per SKU:' : u'每SKU的數量:',
    u'Unit Measure:' : u'計量單位:',
    u'SKU Description:' : u'SKU 描寫:',
    u'Note:' : u'備註:',
    u'Auto check for updates' : u'自動檢查更新存在',
    u'Current Price:' : u'目前的價格:',
    u"Check for update" : u"立刻上網更新",
    u'Update' : u'更新',
    u'Language' : u'語言選擇',
    u'Clear fields' : u'刪除字段',
    u'Clear' : u'刪除',
    u'Save changes to product' : u'提交產品資料變更',
    u'Save changes' : u'提交變更',
    u'Add to supply list (buy)' : u'添加到採購用品列表(進貨)',
    u'Add to product list (sell)' : u'添加到銷售產品列表(出貨)',
    u'Priced by...:' : u'價格由...:',
    u'Unit (kg, gal, etc.)' : u'單位 (kg, gal, 等.)',
    u'SKU (barrel, bag, etc.)' : u'SKU (桶, 包, 等.)',
    u'Discontinue?:' : u'停止買賣？:',
    u'\u2620 Discontinued' : u'\u2620 已停止',
    u'\u26df Available' : u'\u26df 可以買賣',
    u'Price Changes' : u'價格改變日期',
    u'Show All Similar Products' : u'表現所類色的產品',
    u'{} : {} Order Records' : u'{} : {}個訂單記錄',
    u'(Gold Fields Required!)' : u'(金色參數是必需的!)',
    u'Changing existing records!' : u'變更會影響記錄!',
    u'{} orders will be affected.\nContinue with changes?' : u'{}個記錄會被影響到.\n繼續採用變更?',
    u'Manifest #:' : u'出貨單編號:',
    u'View/edit PO' : u'編輯訂單',
    u'Re-open PO' : u'再開訂單利用',
    u'Delete PO' : u'刪除訂單',
    u'Delete product' : u'刪除產品',
    u'(ASE) PN:' : u'(ASE) PN:',
    u'(ASE) RT:' : u'(ASE) RT:',
    u'(ASE) Last SKU#:' : u'(ASE) 最後桶的號碼:',
    u'Print Labels' : u'列印條碼',
    u'PO List Ordering' : u'訂單順序',
    u'Enter the group name for all branches\nUse 2-4 characters' : \
                u'輸入公司團體的縮寫名稱\n縮寫2到4個字',
    u'Enter the first branch name\nAgain, use 2-4 characters' : \
                u'Enter the first branch name\n縮寫2到4個字',
    u'Include Summary' : u'包括總結',
    u' (group)' : u' (組)',
    u'Expand All' : u'展开所有',
    u'Close All' : u'折叠所有',
    u'Short Name:' : u'名字縮寫:',
    u'Full Name:' : u'名字:',
    u'English Name:' : u'英名:',
    u'Tax ID:' : u'統一編號:',
    u'Phone Number:' : u'電話:',
    u'Fax Number:' : u'傳真:',
    u'Email Address:' : u'Email:',
    u'Office Address:' : u'辦公室地址:',
    u'Shipping Address:' : u'運輸地址:',
    u'Billing Address:' : u'發票地址:',
    u'Address (Extra):' : u'地址 (另外):',
    u'Current Supplier/Customer?' : u'還在聯絡?',
    u'Yes' : u'Yes',
    u'No' : u'No',
    u'This product is connected to {} order{}.' : \
        u'本產品已經有{}個訂單.',
    u'\nAll related orders must be deleted first.' : \
        u'\n要先刪除本產品所有的訂單.',
    u'Cannot delete a used product record.' : \
        u'不能刪掉.',
    u"Create new long-term PO's or one-time shipment (with one-time PO)." : \
        u"創造新的長期訂單或者一次出貨單(一次訂單).",
    u"Manage manifests and invoices." : \
        u"管理出貨單跟發票.",
    u"Ship items from open POs." : u"運送長期訂單的一部分.",
    u"Manage current and archived POs." : u"管理所有的訂單歷史.",
    u"+ Add Company/Branch" : u"+ 加上公司/分司",
}
# Storage of StringVar by the english text as keyword.
labeldict = {}


#===============================================================================
# MAIN METHOD AND TESTING AREA
#===============================================================================
def translate_word(word, showError=True):
    """Translate words to Chinese.
    If string (word) is not present in translation dict (worddict)
    then returns the original string."""
    global toChinese


    if showError:
        if word in worddict:
            return worddict[word] if toChinese else word
        else:
            raise Warning, u'"{}" not found in translation dictionary.'.format(word)
    else:
        return worddict.get(word, word) if toChinese else word

def localize(word, asText=False, showError=True):
    '''Return a StringVar object to use in labels.

    Can easily change between English and Chinese by pushing changes to
    a dictionary of StringVars. If 'asText' is set to True than the translated
    text is returned instead of a StringVar. StringVar changes are immediate
    but changes to text will show after restarting the program.
    '''
    if asText:
        return translate_word(word)
    if word in labeldict:
        return labeldict[word]
    else:
        labeldict[word] = StringVar()
        labeldict[word].set(translate_word(word, showError=True))
        return labeldict[word]


def setLang(lang):
    '''Set language to 'lang' or acts as a switch if lang is None.

    Only looks for u"Chinese", any other word will set to English.
    Changes all Tix.StringVars registered in the global labeldict.
    '''
    global toChinese
    global labeldict

    # Set global option for future translation requests.
    toChinese = lang.capitalize() == u'Chinese'

    # Change all StringVar labels that are registered already.
    for key in labeldict:
        labeldict[key].set(translate_word(key))





if __name__ == '__main__':
    """TESTING CODE"""
    print(translate_word(u"Purchases"))
    toChinese = True
    print(translate_word(u"Sales"))
    try:
        print(translate_word(u"Purcses"))
    except Warning as e:
        print(e)

