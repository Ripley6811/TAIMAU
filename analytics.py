#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
summary

description

:REQUIRES:

"""
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
import pandas as pd
from datetime import date, timedelta
import tkMessageBox

#===============================================================================
# METHODS
#===============================================================================

def ASE_analysis(info):
    info.ASE = info.__class__()

    query = info.dmv2.session.query

    Order = info.dmv2.Order
    Shipment = info.dmv2.Shipment
    Product = info.dmv2.Product
    CoGroup = info.dmv2.CoGroup

    q = query(Product.MPN).filter_by(is_supply=False) # Filter for sales
    q = q.join(CoGroup).filter_by(name=u'ASE') # Filter by CoGroup name
    q = q.all()

#    print len(q)
    for each in q:
        print each,

        q2 = query(Shipment)
        q2 = q2.filter(Shipment.shipmentdate > date.today()-timedelta(330))
        q2 = q2.join(Order).filter_by(MPN=each.MPN).order_by(u'shipmentdate')
        q2 = q2.all()



        try:
            # Process DataFrame array
            df = pd.DataFrame.from_records([tuple(s.__dict__.values()) for s in q2], columns=q2[0].__dict__.keys())
#            df = df.drop(u'_labels', 1)

            # Show quotas
            used = q2[-1].order.qty_shipped()
            quota = q2[-1].order.totalskus
            latest = q2[-1].sku_qty
            print used, '/', quota

#            df[u'shipmentdate'] = pd.to_datetime(df[u'shipmentdate'])
#            df = df.groupby(df['shipmentdate'].map(lambda x: x.month))#.resample('M', u'sku_qty')
#            for month, group in df:
#                print month,
##                print group
#                print group['sku_qty'].sum()
            df = df.set_index(pd.DatetimeIndex(df['shipmentdate']))
            dfmonthly = df.resample('M', how='sum')
#            dfmonthly.fillna(0, inplace=True)
            print dfmonthly
            mode = dfmonthly[u'sku_qty'].mode()
            mode = mode[0] if len(mode) else None
            print 'MODE:', mode
            mean = dfmonthly[u'sku_qty'].mean()
            print 'MEAN:', mean
            maxval = dfmonthly[u'sku_qty'].max()
            print 'MAX:', maxval
            aveval = max(mode,mean)

            # Show extrapolation for Max and the greater of Mode/Mean
            for i in range(12):
                if used + (maxval * i) >= quota:
                    print "AGGRESIVE: Maxed out in {} months.".format(i)
                    if i <= 2:
                        warning = u'{}餘糧不足!\nApprox. {} month(s) left.'.format(q2[-1].order.product.label(), i)
                        tkMessageBox.showwarning(u'Quota almost reached. (AGGRESSIIVE)',
                                                 warning)
                    break
                elif used + (aveval * i) >= quota:
                    print "AVERAGE: Maxed out in {} months.".format(i)
                    if i <= 2:
                        warning = u'{}餘糧不足!\nApprox. {} month(s) left.'.format(q2[-1].order.product.label(), i)
                        tkMessageBox.showwarning(u'Quota almost reached. (AVERAGE)',
                                                 warning)
                    break

            #TODO: Warn if another order like the last will go over.
            if used + latest >= quota:
                print "Next order could possibly go over quota!"
                warning = u'{}餘糧不足!'.format(q2[-1].order.product.label())
                tkMessageBox.showwarning(warning,
                        u'{}\nNext order could exceed quota!'.format(warning))

        except IndexError:
            print






#===============================================================================
# MAIN METHOD AND TESTING AREA
#===============================================================================
def main():
    """Description of main()"""
    import db_manager_v2 as dbm

    info = type('struct', (), {})()
    info.dmv2 = dbm

    ASE_analysis(info)






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
