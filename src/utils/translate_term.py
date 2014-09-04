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
#===============================================================================
# PROGRAM METADATA
#===============================================================================
__author__ = 'Ripley6811'
__contact__ = 'python@boun.cr'
__copyright__ = ''
__license__ = ''
__date__ = 'Tue Aug 26 19:49:02 2014'
__version__ = '0.1'

#===============================================================================
# IMPORT STATEMENTS
#===============================================================================
#from numpy import *  # IMPORTS ndarray(), arange(), zeros(), ones()
#set_printoptions(precision=5)
#set_printoptions(suppress=True)
#from visual import *  # IMPORTS NumPy.*, SciPy.*, and Visual objects (sphere, box, etc.)
#import matplotlib.pyplot as plt  # plt.plot(x,y)  plt.show()
#from pylab import *  # IMPORTS NumPy.*, SciPy.*, and matplotlib.*
#import os  # os.walk(basedir) FOR GETTING DIR STRUCTURE
#import pickle  # pickle.load(fromfile)  pickle.dump(data, tofile)
#from tkFileDialog import askopenfilename, askopenfile
#from collections import namedtuple
#from ctypes import *
#import glob
#import random
#import cv2
from Tkinter import StringVar

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





if __name__ == '__main__':
    """TESTING CODE"""
    print(translate_word(u"Purchases"))
    toChinese = True
    print(translate_word(u"Sales"))
    try:
        print(translate_word(u"Purcses"))
    except Warning as e:
        print(e)


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
