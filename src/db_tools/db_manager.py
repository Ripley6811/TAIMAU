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
import datetime
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
import tkMessageBox

from utils import settings
from TM2014_tables_v3 import (get_database, CoGroup, Branch, Product,
                            Vehicle, Contact, Stock, Order,
                            Shipment, ShipmentItem,
                            Invoice, InvoiceItem)



class db_manager:
    Order = Order
    Product = Product
    Shipment = Shipment
    ShipmentItem = ShipmentItem
    Invoice = Invoice
    InvoiceItem = InvoiceItem
    Vehicle = Vehicle
    Contact = Contact
    CoGroup = CoGroup
    Branch = Branch
    Stock = Stock


    """Attempts to make a connection to a database.

    Will not exit loop unless a connection is made. Ensure that the server
    is set up and database is created.
    """
    def __init__(self):

        while True:
            try:
                self.open_session()
                break
            except OperationalError:
                title = u"Connection Failed!"
                message = u"Check server ip-address and enter in console."
                message += u"\n"
                message += u"Run application in console mode to enter new ip."
                tkMessageBox.showerror(title, message)
                self.set_ip()


    def set_ip(self):
        '''Change server ip address.

        Interaction is done through the console. Stores the server ip address
        in the settings.json file.
        '''
        json  = settings.load(u'database')
        json.setdefault('ip', u'None')

        print u"Current ip address:{ip}".format(**json)
        retval = raw_input(u'Enter new server ip address:')

        json.update(ip=retval)

        settings.update(database=json)
        return True

    def open_session(self):
        """Open a new database session.

        Uses default values for any not stored in the local settings.json file.
        """
        json  = settings.load(subdir=u'database')
        json.setdefault('name', u'admin')
        json.setdefault('pw', u'admin')
        json.setdefault('api', u'mysql+pymysql')
        json.setdefault('ip', u'000.0.0.000')
        json.setdefault('opt', u'?charset=utf8')
        json.setdefault('port', u':3306')
        json.setdefault('db', u'taimau')

        self.dbpath = u"{ip}{port}/{db}".format(**json)

        db_path = u"{api}://{name}:{pw}@{ip}{port}/{db}{opt}"
        db_path = db_path.format(**json)

        engine = get_database(db_path,  echo=False )
        self.session = sessionmaker(bind=engine)()


    #==============================================================================
    # Order table methods
    #==============================================================================
    def insert_order(self, ins_dict, is_sale=None):
        if isinstance(is_sale, bool):
            ins_dict['is_sale'] = is_sale
        if  ins_dict.get('is_sale') == None:
            raise Warning, "is_sale (boolean) must be provided."
        self.session.add(Order(**ins_dict))
        self.session.commit()
        return True

    def update_order(self, id, ins_dict):
        self.session.query(Order).filter(Order.id == id).update(ins_dict)
        self.session.commit()
        return True

    #==============================================================================
    # Shipment table methods
    #==============================================================================
    def get_shipment(self, _id):
        return self.session.query(Shipment).get(_id)

    def shipment_no(self, no):
        query = self.session.query(Shipment).filter_by(shipment_no=no)
        c = query.count()
        if c and no: # if no == u'', can create an manifest without a number.
            if c > 1:
                print u"Multiple manifest records with the same number found."
                print u">> Manifest number {} has {} records.".format(no, c)
            return query.first()
        else:
            return None

    def existing_shipment(self, number, date, cogroupname=None):
        if number != u'':
            query = self.session.query(Shipment)
            query = query.filter_by(shipment_no=number, shipmentdate=date)
            count = query.count()
            # If any records found, then try to return one.
            if count > 0:
                recs = query.all()
                # If cogroup parameter passed, then must also match a record.
                if cogroupname:
                    for rec in recs:
                        if rec.items[0].order.group == cogroupname:
                            return rec
                    else: # Matching cogroup manifest not found
                        return None
                else: # Return first if skipping cogroup matching
                    return recs[0]
            else: # No records found
                return None



    #==============================================================================
    # Invoice table methods
    #==============================================================================
    def get_invoice(self, _id):
        return self.session.query(Invoice).get(_id)

    def invoice_no(self, no):
        query = self.session.query(Invoice).filter_by(invoice_no=no)
        c = query.count()
        if c and no: # if no == u'', can create an invoice without a number.
            if c > 1:
                print u"Multiple invoice records with the same number found."
                print u">> Manifest number {} has {} records.".format(no, c)
            return query.first()
        else:
            return None

    def existing_invoice(self, number, date, cogroupname=None):
        if number != u'':
            query = self.session.query(Invoice)
            query = query.filter_by(invoice_no=number, invoicedate=date)
            count = query.count()
            # If any records found, then try to return one.
            if count > 0:
                recs = query.all()
                # If cogroup parameter passed, then must also match a record.
                if cogroupname:
                    for rec in recs:
                        if rec.items[0].order.group == cogroupname:
                            return rec
                    else: # Matching cogroup manifest not found
                        return None
                else: # Return first if skipping cogroup matching
                    return recs[0]
            else: # No records found
                return None

    #==============================================================================
    # CoGroup table methods
    #==============================================================================
    def cogroups(self):
        try:
            cogroups = self.session.query(CoGroup).filter(CoGroup.name != u'台茂').all()
            recNumbers = sorted([(len(cg.orders), cg) for cg in cogroups], reverse=True)
            return [each[1] for each in recNumbers]
        except AttributeError:
            return []


    def get_cogroup(self, name):
        try:
            return self.session.query(CoGroup).get(name)
        except AttributeError:
            return None

    def active_POs(self, name):
        query = self.session.query(Order)
        query = query.filter_by(group=name, is_open=True)
        purchase_POs = query.filter_by(is_purchase=True).count()
        sale_POs = query.filter_by(is_sale=True).count()
        return purchase_POs, sale_POs

    #==============================================================================
    # Branch table methods
    #==============================================================================
    def get_branch(self, name):
        return self.session.query(Branch).get(name)

    #==============================================================================
    # Product table methods
    #==============================================================================
    def get_product(self, mpn):
        return self.session.query(Product).get(mpn)

    def get_product_price(self, mpn, update=False):
        '''Returns current price in the product record or updates the record from
        recent orders. Force a price update with the keyword.
        '''
        product = self.session.query(Product).filter(Product.MPN==mpn).one()
        if product.curr_price != 0.0 and update == False:
            return product.curr_price
        # Else update current price from order records.
        records = sorted([(o.orderdate, o.price) for o in product.orders])
        if len(records) == 0:
            return 0.0
        self.session.query(Product).filter(Product.MPN==mpn).update(dict(curr_price=records[-1][1]))
        self.session.commit()

        return records[-1][1]


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
    return session.query(Order).filter(Order.is_sale==is_sale).order_by('duedate').all()

def get_order(id):
    return session.query(Order).get(id)

def get_manifest(id):
    return session.query(Shipment).get(id)

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
        return product.curr_price
    # Else update current price from order records.
    records = sorted([(o.duedate, o.price) for o in product.orders])
    if len(records) == 0:
        return 0.0
    session.query(Product).filter(Product.MPN==mpn).update(dict(curr_price=records[-1][1]))
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
    pass




"""PASTE INTO PYTHON SESSION
os.chdir('C:\\Users\\Jay\\Dropbox\\github\\taimau\\src\\db_tools')
json  = {}
json.setdefault('name', u'admin')
json.setdefault('api', u'mysql+pymysql')
json.setdefault('opt', u'?charset=utf8')
json.setdefault('port', u':3306')
json.setdefault('db', u'taimau')

json['ip'] = #Fill in ip
json['pw'] = #Fill in password

db_path = u"{api}://{name}:{pw}@{ip}{port}/{db}{opt}"
db_path = db_path.format(**json)

engine = get_database(db_path,  echo=False )
session = sessionmaker(bind=engine)()


#### Useful SQL lines. ####

# Get list of table names.
session.execute('Show tables').fetchall()






"""