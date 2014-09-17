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
    u"Reports" : u"報告(R)",
    u"Open" : u"開資料庫",
    u"Exit" : u"關閉",
    u"Font" : u"字體",
    u"About" : u"關於",
    u"Help" : u"幫助",
    u"Supplier" : u"供應商",
    u"Customer" : u"顧客",
    u"(NA)" : u"(沒有)",
    u"(Avail:" : u"(剩下:",
    u"Branch" : u"分公司",
    u"\u26DF Create Manifest" : u"\u26DF 創建出貨單",
    u"+ PO" : u"+ 訂單",
    u"% discount" : u"% 折扣(美式)",
    u"Settings" : u"設置",
    u"\u2692 Create Product Order (PO)" : u"\u2692 創建訂單 (PO)",
    u"\u2692 Update Product Order (PO)" : u"\u2692 編輯訂單 (PO)",
    u"\u2620 Archive this PO \u2620" : u"\u2620 非活狀態且歸檔 \u2620",
    u"+ product" : u"+ 產品",
    u"PO #" : u"訂單編號",
    u"Date of PO" : u"訂單創建日期",
    u"Select one product" : u"選一個產品",
    u"Qty" : u"數量",
    u"Taimau" : u"台茂",
    u"Note" : u"備註",
    u"Price" : u"價格",
    u"Apply tax?" : u"收稅？",
    u"\u26D4 Cancel" : u"\u26D4 取消",
    u"NOTE:" : u"備註:",
    u"Edit PO" : u"編輯訂單",
    u"Product" : u"產品",
    u'Active POs' : u'主動訂單',
    u'All POs' : u'全部訂單',
    u'Manifests & Invoices' : u'出貨單 & 發票',
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
    u'Current Price:' : u'目前的價格:',
    u'Clear fields' : u'刪除字段',
    u'Save changes to product' : u'提交產品資料變更',
    u'Add to supply list' : u'添加到採購用品列表',
    u'Add to product list' : u'添加到銷售產品列表',
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
    u'{} orders will be affected.\nContinue with changes?' : u'{}個記錄會被影響到.\n繼續採用變更?'
}
# Storage of StringVar by the english text as keyword.
labeldict = {}


#===============================================================================
# MAIN METHOD AND TESTING AREA
#===============================================================================
def translate_word(word):
    """Translate words to Chinese"""
    if word in worddict:
        return worddict[word] if toChinese else word
    else:
        raise Warning, u'"{}" not found in translation dictionary.'.format(word)


def localize(word, asText=False):
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
        labeldict[word].set(translate_word(word))
        return labeldict[word]


def setLang(lang=None):
    '''Set language to 'lang' or acts as a switch if lang is None.

    Only accepts "Chinese", any other word will set to English.
    If no parameter than alternates between Chinese and English.
    '''
    global toChinese
    # Set 'toChinese' boolean
    if lang == None:
        toChinese = not toChinese
    elif "Chinese" == lang.capitalize():
        toChinese = True
    else:
        toChinese = False
    # Change all StringVar labels
    for key in labeldict:
        labeldict[key].set(translate_word(key))

    settings.update(language=lang)
setLang(settings.load().get(u'language'))




if __name__ == '__main__':
    """TESTING CODE"""
    print(translate_word(u"Purchases"))
    toChinese = True
    print(translate_word(u"Sales"))
    try:
        print(translate_word(u"Purcses"))
    except Warning as e:
        print(e)

