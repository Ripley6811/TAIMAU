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
:SINCE: Thu Dec 12 14:51:06 2013
:VERSION: 0.1
"""
#===============================================================================
# PROGRAM METADATA
#===============================================================================
__author__ = 'Ripley6811'
__contact__ = 'python@boun.cr'
__copyright__ = ''
__license__ = ''
__date__ = 'Thu Dec 12 14:51:06 2013'
__version__ = '0.1'

#===============================================================================
# IMPORT STATEMENTS
#===============================================================================
from TM2014_tables_v3 import (get_database, CoGroup, Branch, Product,
                            Vehicle, Contact, Stock, Order, Shipment,
                            Invoice, InvoiceItem)
import os  # os.walk(basedir) FOR GETTING DIR STRUCTURE
#import dict_from_excel as excel
import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_, and_

#===============================================================================
# METHODS
#===============================================================================
dbname = r'TM2014_v3.db'
try:
    with open('settings.txt', 'r') as rfile:
        base = rfile.readline().strip()
        dbname = os.path.join(base, dbname)
    print "DB LOADED:", dbname
except IOError:
    with open('..\settings.txt', 'r') as rfile:
        base = rfile.readline().strip()
        dbname = os.path.join(base, dbname)
    print "DB LOADED:", dbname



#engine, metadata = open_database(dbname, echo=True)
engine = get_database( dbname, False )
session = sessionmaker(bind=engine)()


#conn = engine.connect()
#purchases = purchases
#sales = sales
#companydb = metadata.tables['company']
##warehouse = warehouse


def insert_purchase(ins_dict):
    insert_order(ins_dict, is_sale=False)
    return True

def insert_sale(ins_dict):
    insert_order(ins_dict, is_sale=True)
    return True

def insert_order(ins_dict, is_sale=None):
    if isinstance(is_sale, bool):
        ins_dict['is_sale'] = is_sale
    if  ins_dict.get('is_sale') == None:
        raise Warning, "is_sale (boolean) must be provided."
    session.add(Order(**ins_dict))
    session.commit()
    return True


def update_order(id, ins_dict):
    session.query(Order).filter(Order.id == id).update(ins_dict)
    session.commit()
    return True


def delete_order(del_id):
    session.query(Order).filter(Order.id==del_id).delete()
    session.query(Shipment).filter(Shipment.order_id==del_id).delete()
    session.query(InvoiceItem).filter(InvoiceItem.order_id==del_id).delete()
    session.commit()
    return True

def append_shipment(order_id, ins_dict):
    ins_dict['order_id'] = order_id
    session.add(Shipment(**ins_dict))
    session.commit()

def append_invoice(inv_dict):
    session.add(Invoice(**inv_dict))
    session.commit()

def append_invoice_item(inv_dict, item):
    record = session.query(Invoice).get(inv_dict['invoice_no'])
    print 'get', repr(record)
    if not record:
        append_invoice(inv_dict)
    session.add(InvoiceItem(**item))
    session.commit()


def get_entire_invoice(rec):
    '''Actually retrieves all partial invoices that make up one invoice.'''
    return session.query(Invoice).filter_by(invoiceID = rec.invoice_no,
                                            invoicedate = rec.invoicedate).all()

def get_entire_shipment(rec):
    '''Actually retrieves all partial shipments that make up one shipment.'''
    return session.query(Shipment).filter_by(shipmentID = rec.shipmentID,
                                             shipmentdate = rec.shipmentdate).all()



#==============================================================================
# CoGroup table methods
#==============================================================================
def cogroups():
    return session.query(CoGroup).all()

def get_cogroup(name):
    return session.query(CoGroup).get(name)

def cogroup_names():
    return [co.name for co in cogroups()]
company_list = cogroup_names # name changed


#==============================================================================
# Branch table methods
#==============================================================================
# Note: Branches can be accessed from their respective CoGroup object.
#
def branches(group=None):
    if group:
        return session.query(Branch).filter_by(group=group).all()
    return session.query(Branch).all()


def get_branch(name):
    return session.query(Branch).get(name)

def get_branch_numbers(group_id):
    group_id = group_id.decode('utf8')
    template = u'{} ({} {})  \u260E:{},  \u263B:{}'
    return [template.format(rec.fullname, rec.name, rec.tax_id.strip().strip("'"),
            rec.contacts[0].phone, rec.contacts[0].name)
            for rec in session.query(Branch).filter(Branch.group==group_id).all()]

def get_branch_summary(group_id):
    group_id = group_id.decode('utf8')
    return [u'{}'.format(rec.name)
            for rec in session.query(Branch.name).filter(Branch.group==group_id).all()]




#==============================================================================
# Order table methods
#==============================================================================
# Note: Lists of orders, sales, or purchases can be accessed from CoGroup or Branch objects.
#
def orders(is_sale, group=None, limit=1000):
    '''Limit is applied when group parameter is given. Otherwise returns all records.
    '''
    if not isinstance(is_sale, bool):
        raise ValueError, 'is_sale (bool) must be True to retrieve sales records or False for purchases.'
    if group:
        return session.query(Order).filter(and_(Order.group==group, Order.is_sale==is_sale)).order_by('duedate').all()[-limit:]
    print "--->>>Returning all {} orders.<<<---".format("sale" if is_sale else "purchase")
    return session.query(Order).filter(Order.is_sale==is_sale).order_by('duedate').all()

def get_order(id):
    return session.query(Order).get(id)

def _orders(is_sale):
    '''Function maker for 'sales' and 'purchases' functions.
    '''
    def retfunc(group=None, id=None, limit=100):
        if id:
            return get_order(id)
        return orders(is_sale=is_sale, group=group, limit=limit)
    return retfunc

sales = _orders(is_sale=True)
purchases = _orders(is_sale=False)


def company_list_from_sales():
    '''Orders the list from companies with most recent entries to older entries.
    '''
    rawlist = [p.group for p in sales()]
    outlist = []
    for each in rawlist[::-1]:
        if each not in outlist:
            outlist.append(each)
    return outlist

def company_list_from_purchases():
    '''Orders the list from companies with most recent entries to older entries.
    '''
    rawlist = list([p.group for p in purchases()])
    outlist = []
    for each in rawlist[::-1]:
        if each not in outlist:
            outlist.append(each)
    return outlist

def get_last_order(group):
    rec = session.query(Order).filter_by(group=group).order_by(Order.recorddate.desc()).first()
    return rec

#==============================================================================
# Product table methods
#==============================================================================
# Note: The product for an order can be accessed through the Order object.
#
def products(info=None, include_discontinued=False):
    if info != None:
        query = session.query(Product).filter(Product.group==info.curr_company)
        incoming = False if info.src == "Sales" else True
        query = query.filter(Product.is_supply==incoming)
        if not include_discontinued:
            query = query.filter(Product.discontinued==False)
        return query.all()
    return session.query(Product).all()

def get_product(mpn):
    return session.query(Product).get(mpn)

def get_product_price(mpn, update=False):
    '''Returns current price in the product record or updates the record from
    recent orders. Force a price update with the keyword.
    '''
    product = session.query(Product).filter(Product.MPN==mpn).one()
    if product.curr_price != 0.0 and update == False:
#        print 'from product record:', product.curr_price
        return product.curr_price
    # Else update current price from order records.
    records = sorted([(o.duedate, o.price) for o in product.orders])
    if len(records) == 0:
        return 0.0
#    print 'from order lookup:', records[-1]
    session.query(Product).filter(Product.MPN==mpn).update(dict(summary=product.summary,curr_price=records[-1][1]))
    session.commit()

    return records[-1][1]


def get_product_recent_order(mpn, update=False):
    '''Returns current price in the product record or updates the record from
    recent orders. Force a price update with the keyword.
    '''
    record = session.query(Order).filter(Order.MPN==mpn).order_by(Order.duedate.desc()).first()
    if record != None:
        product = record.product
        if update == True:
            if product.curr_price != record.price:
                session.query(Product).filter(Product.MPN==mpn)\
                                      .update(dict(summary=product.summary,curr_price=record.price))
                session.commit()
        return record
    return None


def get_product_names(mpn):
    try:
        mpn = str(int(float(mpn)))
    except:
        pass
    try:
        qres = session.query(Product.product_label, Product.inventory_name).filter(Product.MPN==mpn).one()
        return qres.product_label, qres.inventory_name
    except:
        pass
    return u"<{}>".format(mpn)

def product_listing(group, is_supply):
    '''Returns a list of formated product names and a corresponding list of IDs.
    '''
    query = session.query(Product).filter((Product.group==group)
                                        & (Product.discontinued==False)
                                        & (Product.is_supply==is_supply)).all()
    return [rec.summary for rec in query], [rec.MPN for rec in query]

def adj_stock(mpn, units=0.0, value=None, SKUs=0.0, date=None, note=u''):
    if date==None:
        date = datetime.date.today()
    if value == None:
        tmp = get_product(mpn).qty_available()
        value = units * (tmp['value'] / tmp['units'])
    session.add(Stock(MPN=mpn, adj_unit=units, adj_SKU=SKUs, adj_value=value, date=date, note=note))
    session.commit()



#def db_adjustments():
#    # Convert any float manifest numbers into a 6-7 digit integer string.
#    shipments = session.query(Shipment).all()
#    for shipment in shipments:
#        if shipment.shipmentID.endswith(u'.0'):
#            new_no = u'{:0>6}'.format(int(float(shipment.shipmentID)))
#            session.query(Shipment).filter_by(id=shipment.id).update({"shipmentID":new_no})
#    session.commit()
#
#    # Add orderdate if missing. Use earliest available date in record/subrecs.
#    orders = session.query(Order).all()
#    for order in orders:
#        if not order.orderdate:
#            newdict = dict(
#                orderdate = order.duedate,
#                subtotal = order.subtotal,
#                applytax = order.applytax,
#            )
#            session.query(Order).filter_by(id=order.id).update(newdict)
#    session.commit()
#db_adjustments()



#==============================================================================
# Testing and debugging
#==============================================================================
if __name__ == '__main__':
    import subprocess
    with open('DEBUG_db_manager_v2.txt', 'w') as wf:
        wf.write(u'METHOD:cogroups()\n    ')
        wf.write(u' '.join([c.name for c in cogroups()]).encode('utf8'))

        wf.write(u'\n\nMETHOD:company_list()\n    ')
        wf.write(u' '.join(company_list()).encode('utf8'))

        wf.write(u'\n\nMETHOD:company_list_from_sales()\n    ')
        wf.write(u' '.join(company_list_from_sales()).encode('utf8'))

        wf.write(u'\n\nMETHOD:company_list_from_purchases()\n    ')
        wf.write(u' '.join(company_list_from_purchases()).encode('utf8'))



        wf.write(u'\n\nMETHOD:branches()\n    ')
        wf.write(u' '.join([c.name + c.tax_id for c in branches()]).encode('utf8'))

#        wf.write(u'\n\nMETHOD:purchases()\n    ')
#        wf.write(u' '.join([str(int(float(rec.MPN))) for rec in purchases()]).encode('utf8'))

        wf.write(u'\n\nMETHOD:products()\n')
        wf.write(u', '.join([rec.MPN for rec in products()]).encode('utf8'))

#        wf.write(u'\n\nMETHOD:products(group param)\n')
#        for co in company_list():
#            wf.write(co.encode('utf8'))
#            wf.write(u'{{{0}}}'.format(u', '.join([rec.MPN for rec in products(co)])).encode('utf8'))
#            wf.write(u'\n')


        wf.write(u'\n\nMETHOD:insert_purchase()\n')
        fake_order = dict(
                        id=99999,
                        group=cogroup_names()[0],
                        seller=cogroup_names()[0],
                        buyer=cogroup_names()[0],
                        MPN=666,
                        duedate=datetime.date.today(),
                    )
        insert_purchase(fake_order)
        wf.write(repr(purchases(id=99999)))

        wf.write(u'\n\nMETHOD:update_order() with subtotal\n')
        update_order(99999, dict(subtotal=12345))
        try:
            wf.write(repr(purchases(id=99999)))
        except:
            wf.write(u'Deleted record 99999 was not found! NOT GOOD!')

        wf.write(u'\n\nMETHOD:delete_order()\n')
        delete_order(99999)
        try:
            wf.write(repr(purchases(id=99999)))
        except:
            wf.write(u'Deleted record 99999 was not found! Great!')

        wf.write(u'\n\nTEST ORDER.PRODUCT (SALES) RELATIONSHIP\n')
        for rec in orders(True):
            if rec.product == None:
                wf.write(repr(rec.id))
                wf.write(u'  ')
                wf.write(repr(rec.MPN))
                wf.write(u'  ')
                wf.write(repr(rec.product))
                wf.write(u'\n')
            else:
                wf.write(u'y')
        wf.write(u'\n\nTEST ORDER.PRODUCT (PURCHASE) RELATIONSHIP\n')
        for rec in orders(False):
            if rec.product == None:
                wf.write(repr(rec.id))
                wf.write(u'  ')
                wf.write(repr(rec.MPN))
                wf.write(u'  ')
                wf.write(repr(rec.product))
                wf.write(u'\n')
            else:
                wf.write(u'y')


        wf.write(u'\n\nMETHOD:product_listing()\n')
        for co in company_list()[:10]:
            wf.write(co.encode('utf8'))
            li, ids = product_listing(co, True)
            wf.write(u'{{{0}}}'.format(u', '.join(li)).encode('utf8'))
            wf.write(u'\n')
            wf.write(u'{{{0}}}'.format(u', '.join(ids)).encode('utf8'))
            wf.write(u'\n')


        wf.write(u'\n\nMETHOD:cogroups() and purchases/sales\n')
        for group in cogroups():
            wf.write(group.name.encode('utf8'))

            wf.write(u'  orders={}'.format(len(group.orders)))
            wf.write(u'  purchases={}'.format(len(group.purchases)))
            wf.write(u'  sales={}'.format(len(group.sales)))
            wf.write(u'\n')


        wf.write(u'\n\nMETHOD:branches() and purchases/sales\n')
        for group in branches():
            wf.write(u'{}:{}'.format(group.group, group.name).encode('utf8'))

            wf.write(u'  purchases={}'.format(len(group.purchases)))
            wf.write(u'  sales={}'.format(len(group.sales)))
            wf.write(u'\n')


        wf.write(u'\n\nMETHOD:adj_stock()\n')
#        for val in [222,123,453]:
#            adj_stock(u'100',val)
        wf.write(repr(get_product(u'100').qty_available()))
        for rec in get_product(u'100').stock:
            wf.write(u'\n{} {} {}'.format(rec.date, rec.adj_unit, rec.adj_value))

        wf.write(u'\n\nMETHOD:products().order\n')
        outlist = []
        for rec in products()[:20]:
            try:
                outlist.append(rec.order.all())
            except:
                pass
        wf.write(repr(outlist).encode('utf8'))

    subprocess.call(['Notepad.exe', 'DEBUG_db_manager_v2.txt'])