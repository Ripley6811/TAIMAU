#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlalchemy as sqla
from sqlalchemy.orm import relationship as rel
from sqlalchemy.orm import backref
from sqlalchemy.ext.declarative import declarative_base
import datetime

Int = sqla.Integer
Str = sqla.String
Utf = sqla.Unicode
Float = sqla.Float
Col = sqla.Column
Bool = sqla.Boolean
Date = sqla.Date
DateTime = sqla.DateTime
ForeignKey = sqla.ForeignKey






Base = declarative_base()

def today():
    return datetime.datetime.now()

class Order(Base):
    __tablename__ = 'order'
    id = Col(Int, primary_key=True)
    group = Col(Utf, ForeignKey('cogroup.name'), nullable=False) # Of second party main company
    seller = Col(Utf, ForeignKey('branch.name'), nullable=False) # For billing/receipts
    buyer = Col(Utf, ForeignKey('branch.name'), nullable=False) # For billing/receipts

    recorddate = Col(DateTime, nullable=False, default=today) # Date of entering a record

    # Keep all product information in the outgoing product list
    MPN = Col(Utf, ForeignKey('product.MPN'), nullable=False) # Product code

    price = Col(Float) # Price for one SKU or unit
    discount = Col(Int) # Discount percentage as integer
    totalskus = Col(Int)
    totalunits = Col(Float) # AUTO: unitssku * totalskus
    subtotal = Col(Float)
    applytax = Col(Bool) # True = 5%, False = 0%
    totalcharge = Col(Int) # AUTO: pricing * (totalskus or totalunits)

    orderdate = Col(Date)  # Use as "expected" delivery date. (Originally was order placement date)
    duedate = Col(Date, nullable=False)  # Expected delivery date
    date = Col(Date) # Extra date field if needed

    orderID = Col(Utf)  # PO Number

    ordernote = Col(Utf) # Information concerning the order
    note = Col(Utf) # Extra note field if needed.

    checked = Col(Bool, nullable=False, default=False) # Match against second party records
    is_sale = Col(Bool, nullable=False) # Boolean for purchase vs. sale. Also check against buyer/seller name.

    #invoicedate = Col(Date) # Date of sending/receiving invoice
    #invoiceID = Col(Utf) # Invoice number
    #invoicenote = Col(Utf) # Information concerning the invoice
    #invoiced = Col(Bool, nullable=False, default=False) # True = sent, False = not sent yet
    #delivered = Col(Bool, nullable=False, default=False) # True = delivered, False = not delivered yet
    #paid = Col(Bool, nullable=False, default=False) # True = paid, False = not paid yet

    shipments = rel('Shipment')
    invoices = rel('Invoice')
    product = rel('Product')#, backref=backref('order', lazy='dynamic')) #TODO: backref not working

    def qty_shipped(self):
        return sum([srec.sku_qty if isinstance(srec.sku_qty,int) else 0 for srec in self.shipments])

    def all_shipped(self):
        return self.totalskus == self.qty_shipped()

    def total_invoiced(self):
        return sum([prec.amount if isinstance(prec.amount,int) else 0 for prec in self.invoices])

    def all_invoiced(self):
        return self.totalcharge == self.total_invoiced()

    def total_paid(self):
        return sum([prec.amount if prec.paid else 0 for prec in self.invoices])

    def all_paid(self):
        if len(self.invoices) > 0:
            return not (False in [prec.paid for prec in self.invoices])
        return False


    def __repr__(self):
        retval = self.__dict__
#        if retval.get('_sa_instance_state') != None:
#            del retval['_sa_instance_state']
        return repr(retval)

class Shipment(Base): # Keep track of shipments/SKUs for one order
    __tablename__ = 'shipment'
    id = Col(Int, primary_key=True)
    order_id = Col(Int, ForeignKey('order.id'), nullable=False)

    sku_qty = Col(Int, nullable=False) # Deduct from total SKUs due

    shipmentdate = Col(Date, nullable=False)
    shipmentID = Col(Utf, default=u'') # i.e., Manifest number
    shipmentnote = Col(Utf, default=u'') # Information concerning the delivery
    driver = Col(Utf) # Track vehicle driver (optional)
    truck = Col(Utf) # Track vehicle by license (optional)
    note = Col(Utf) # Extra note field if needed
    checked = Col(Bool, nullable=False, default=False) # Extra boolean for matching/verifying

    def __repr__(self):
        retval = self.__dict__
#        if retval.get('_sa_instance_state') != None:
#            del retval['_sa_instance_state']
        return repr(retval)


class Invoice(Base): # Keep track of invoices/payments for one order
    __tablename__ = 'invoice'
    id = Col(Int, primary_key=True)
    order_id = Col(Int, ForeignKey('order.id'), nullable=False)

    seller = Col(Utf, ForeignKey('branch.name'), nullable=False) # For billing/receipts
    buyer = Col(Utf, ForeignKey('branch.name'), nullable=False) # For billing/receipts

    amount = Col(Int, nullable=False)

    invoicedate = Col(Date, nullable=False)
    invoiceID = Col(Utf) # i.e., Invoice number
    invoicenote = Col(Utf) # Information concerning the invoice

    check_no = Col(Utf)
    paid = Col(Bool, nullable=False, default=False)

    note = Col(Utf) # Extra note field if needed
    checked = Col(Bool, nullable=False, default=False) # Extra boolean for matching/verifying

    def __repr__(self):
        retval = self.__dict__
#        if retval.get('_sa_instance_state') != None:
#            del retval['_sa_instance_state']
        return repr(retval)


class CoGroup(Base):
    __tablename__ = 'cogroup'
    name = Col(Utf, primary_key=True, nullable=False) # Abbreviated name of company (2 to 4 chars)
    is_active = Col(Bool, nullable=False, default=True) # Boolean for listing the company. Continuing business.
    is_supplier = Col(Bool, nullable=False, default=True) # Maybe use in later versions
    is_customer = Col(Bool, nullable=False, default=True) # Maybe use in later versions

    branches = rel('Branch', lazy='joined')
    orders = rel('Order')
    products = rel('Product')
    contacts = rel('Contact')

    purchases = rel('Order', primaryjoin="and_(CoGroup.name==Order.group, Order.is_sale==False)") #Purchases FROM this company
    sales = rel('Order', primaryjoin="and_(CoGroup.name==Order.group, Order.is_sale==True)") #Sales TO this company

    def __repr__(self):
        retval = self.__dict__
#        if retval.get('_sa_instance_state') != None:
#            del retval['_sa_instance_state']
        return repr(retval)


class Branch(Base):
    __tablename__ = 'branch'
    name = Col(Utf, primary_key=True, nullable=False) # Abbreviated name of company (2 to 4 chars)
    group= Col(Utf, ForeignKey('cogroup.name'), nullable=False) # Name of main company representing all branches
    fullname = Col(Utf, default=u'')
    english_name = Col(Utf, default=u'')
    tax_id = Col(Utf, nullable=False, default=u'')
    phone = Col(Utf, default=u'')
    fax = Col(Utf, default=u'')
    email = Col(Utf, default=u'')
    note = Col(Utf, default=u'')
    address_office = Col(Utf, default=u'')
    address_shipping = Col(Utf, default=u'')
    address_billing = Col(Utf, default=u'')
    address = Col(Utf, default=u'') # Extra address space if needed
    is_active = Col(Bool, nullable=False, default=True) # Boolean for listing the company. Continuing business.

    contacts = rel('Contact')

    purchases = rel('Order', primaryjoin="and_(Branch.name==Order.seller, Order.is_sale==False)") #Purchases FROM this company
    sales = rel('Order', primaryjoin="and_(Branch.name==Order.buyer, Order.is_sale==True)") #Sales TO this company

    def __repr__(self):
        retval = self.__dict__
#        if retval.get('_sa_instance_state') != None:
#            del retval['_sa_instance_state']
        return repr(retval)


class Contact(Base):
    __tablename__ = 'contact'
    id = Col(Int, primary_key=True)
    group = Col(Utf, ForeignKey('cogroup.name'), nullable=False)
    branch = Col(Utf, ForeignKey('branch.name'))
    name = Col(Utf, nullable=False)
    position = Col(Utf, default=u'')
    phone = Col(Utf, default=u'')
    fax = Col(Utf, default=u'')
    email = Col(Utf, default=u'')
    note = Col(Utf, default=u'')

    def __repr__(self):
        retval = self.__dict__
#        if retval.get('_sa_instance_state') != None:
#            del retval['_sa_instance_state']
        return repr(retval)


def summarize(context):
    '''Short text of product key values.
    '''
    outname = context.current_parameters['product_label']
    units = context.current_parameters['units']
    UM = context.current_parameters['UM']
    SKU = context.current_parameters['SKU']
    if not outname:
        outname = context.current_parameters['inventory_name']
    if SKU == u'槽車':
        return u"{0} (槽車)".format(outname)
    else:
        units = int(units) if units.is_integer() else units
        uf = u"{0} ({1} {2} {3})"
        return uf.format(outname,units,UM,SKU)

class Product(Base): # Information for each unique product (including packaging)
    __tablename__ = 'product'

    MPN = Col(Utf, primary_key=True)
    group = Col(Utf, ForeignKey('cogroup.name'), nullable=False)

    product_label = Col(Utf, default=u'') #Optional 2nd party product name
    inventory_name = Col(Utf, nullable=False) #Required
    english_name = Col(Utf, default=u'')
    units = Col(Float, nullable=False)  #Units per SKU
    UM = Col(Utf, nullable=False)   #Unit measurement
    SKU = Col(Utf, nullable=False)  #Stock keeping unit (sold unit)
    SKUlong = Col(Utf, default=u'')
    unitpriced = Col(Bool, nullable=False)
    ASE_PN = Col(Utf)
    note = Col(Utf)
    is_supply = Col(Bool, nullable=False)
    discontinued = Col(Bool, nullable=False, default=False)

    curr_price = Col(Float, default=0.0)

    summary = Col(Utf, default=summarize, onupdate=summarize)

    stock = rel('Stock')
    orders = rel('Order', primaryjoin="Product.MPN==Order.MPN")

    def __repr__(self):
        retval = self.__dict__
#        if retval.get('_sa_instance_state') != None:
#            del retval['_sa_instance_state']
        return repr(retval)

    def qty_available(self):
        available = dict(
            units = 0.0,
            SKUs = 0.0,
            value = 0.0,
            unit_value = None,
            SKU_value = None
        )
        for each in self.stock:
            available['units'] += each.adj_unit
            available['SKUs'] += each.adj_SKU
            available['value'] += each.adj_value
        if available['units'] != 0.0:
            available['unit_value'] = available['value'] / available['units']
        if available['SKUs'] != 0.0:
            available['SKU_value'] = available['value'] / available['SKUs']
        return available


class Stock(Base): #For warehouse transactions
    __tablename__ = 'stock'
    id = Col(Int, primary_key=True)
    MPN = Col(Utf, ForeignKey('product.MPN'), nullable=False)

    date = Col(Date, nullable=False)
    adj_unit = Col(Float, nullable=False)   #Use units for stock amounts
    adj_SKU = Col(Float) #Probably will NOT use this
    adj_value = Col(Float, nullable=False)  #Value of units in transaction
    note = Col(Utf)

    def __repr__(self):
        retval = self.__dict__
#        if retval.get('_sa_instance_state') != None:
#            del retval['_sa_instance_state']
        return repr(retval)


def get_database(filename, echo=False):
    database = sqla.create_engine('sqlite:///'+filename, echo=echo)
    Base.metadata.create_all(database)   #FIRST TIME SETUP ONLY
    return database
