#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlalchemy as sqla
from sqlalchemy.orm import relationship as rel
from sqlalchemy.orm import backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import datetime
import json

Int = sqla.Integer
Str = sqla.String  #TODO: Can probably delete this line
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



def AddDictRepr(aClass):

    def repr_str(obj):
        '''Returns a string representation of the dictionary object with
        underscored keywords removed ("_keyword").
        '''
        copy = obj.__dict__.copy()
        for key in copy.keys():
            if key.startswith(u'_'):
                try:
                    del copy[key]
                except KeyError:
                    pass
        return repr(copy)

    aClass.__repr__ = repr_str
    return aClass

#==============================================================================
# Order class
#==============================================================================
def updatetotal(context):
    subtotal = context.current_parameters['subtotal']
    taxed = context.current_parameters['applytax']
    if taxed:
        return int(round(subtotal * 1.05))
    else:
        return int(round(subtotal))

@AddDictRepr
class Order(Base):
    __tablename__ = 'order'
    id = Col(Int, primary_key=True)
    group = Col(Utf, ForeignKey('cogroup.name'), nullable=False) # Of second party main company
    seller = Col(Utf, ForeignKey('branch.name'), nullable=False) # For billing/receipts
    buyer = Col(Utf, ForeignKey('branch.name'), nullable=False) # For billing/receipts
    parent = rel('CoGroup')

    recorddate = Col(DateTime, nullable=False, default=today) # Date of entering a record

    # Keep all product information in the outgoing product list
    MPN = Col(Utf, ForeignKey('product.MPN'), nullable=False) # Product code

    price = Col(Float) # Price for one SKU or unit on this order
    discount = Col(Int) # Discount percentage as integer (0-100)
    totalskus = Col(Int)
    totalunits = Col(Float) # AUTO: unitssku * totalskus
    subtotal = Col(Float) #TODO: Remove and leave final totals in attached invoice.
    applytax = Col(Bool) # True = 5%, False = 0%
    totalcharge = Col(Int, default=updatetotal, onupdate=updatetotal) #TODO: Remove

    orderdate = Col(Date)  # Use as "expected" delivery date. (Originally was order placement date)
    duedate = Col(Date, nullable=False)  # Expected delivery date
    date = Col(Date) # Extra date field if needed

    orderID = Col(Utf)  # PO Number

    ordernote = Col(Utf) # Information concerning the order
    note = Col(Utf) # Extra note field if needed.

    checked = Col(Bool, nullable=False, default=False) # Match against second party records
    is_sale = Col(Bool, nullable=False) # Boolean for purchase vs. sale. Also check against buyer/seller name.

    shipments = rel('Shipment', backref='order')
    invoices = rel('InvoiceItem', backref='order')
    product = rel('Product')

    def qty_shipped(self):
        '''By number of SKUs'''
        if len(self.shipments) == 0:
            return 0
        return sum([srec.sku_qty if isinstance(srec.sku_qty,int) else 0 for srec in self.shipments])

    def qty_remaining(self):
        '''By number of SKUs remaining to be shipped'''
        return int(self.totalskus - self.qty_shipped())

    def all_shipped(self):
        '''By number of SKUs'''
        if len(self.shipments) == 0:
            return False
        return self.totalskus == self.qty_shipped()

    def qty_invoiced(self):
        '''By number of SKUs'''
        if len(self.invoices) == 0:
            return 0
        return sum([prec.sku_qty if isinstance(prec.sku_qty,int) else 0 for prec in self.invoices])

    def all_invoiced(self):
        '''By number of SKUs'''
        if len(self.invoices) == 0:
            return False
        return self.totalskus == self.qty_invoiced()

    def total_paid(self):
        if len(self.invoices) == 0:
            return 0
        return sum([prec.sku_qty if prec.invoice.paid else 0 for prec in self.invoices])

    def all_paid(self):
        if len(self.invoices) == 0:
            return False
        return not (False in [prec.invoice.paid for prec in self.invoices])

    def qty_quote(self, qty):
        '''Subtotal of total order.'''
        subtotal = self.price * qty
        if self.product.unitpriced:
            subtotal *= self.product.units
        return int(round(subtotal))

#    def formatted(self):
#        txt =  u'PO# {s.orderID:<16}  {s.seller:>8} >> {s.buyer:<8}'
#        txt += u'  {s.totalskus:>5} {s.product.product_label} '
#
#        return txt.format(s=self)


    def listbox_summary(self):
        """
        Single line unicode text summary of order intended for use in a listbox.

        Only displays number of attached shipments and invoices.
        """

        prodtmp = self.product.product_label, self.product.inventory_name
        if prodtmp[0] and prodtmp[0] != prodtmp[1]:
            prodtmp = u'{} (台茂:{})'.format(*prodtmp)
        else:
            prodtmp = prodtmp[1]

        #Start with checkbox to show that order is completed (delivered and paid)
        tmp = u'\u2611' if self.all_paid() and self.all_invoiced() and self.all_shipped() else u'\u2610'

        #PO number if available
        po_no_txt = self.orderID.strip() if self.orderID else '({})'.format(self.id)
        tmp += u"{0:<14}".format(po_no_txt)

        #Shipping icon and number of shipments
        tmp += u'\u26DF' if len(self.shipments)>0 else u'\u25C7'
        tmp += u'*{:<3}'.format(len(self.shipments)) if self.shipments else u'    '

        #Invoice sent icon and number of invoices
        tmp += u'\u2696' if len(self.invoices)>0 else u'\u25C7'
        tmp += u'*{:<3}'.format(len(self.invoices)) if self.invoices else u'    '


        try:
            tmp += u"{0:%y}年{0.month:>2}月{0.day:>2}日".format(self.orderdate)
        except:
            tmp += u'(Order date not entered)'

#        try:
#            tmp += u" \u273F {s.seller}\u2794{s.buyer} ".format(s=self)
#        except Exception as e:
#            tmp += u'(ERROR: {})'.format(e)

        try:
            tmp += u"\u273F {rem_qty:>6}{s.totalskus:>5}{um} {pt:<14} @ ${pr} \u214C {um}".format(
                pt= prodtmp,
                pr= int(self.price) if float(self.price).is_integer() else self.price,
                um= self.product.SKU if self.product.SKU != u'槽車' else self.product.UM,
                rem_qty= u'{}/'.format(self.qty_remaining()),
                s= self,
                )
        except Exception as e:
            tmp += u'(ERROR: {})'.format(e)

        return tmp


#==============================================================================
# Shipment (track multiple shipments in SKU's for one order)
#==============================================================================
@AddDictRepr
class Shipment(Base): # Keep track of shipments/SKUs for one order
    '''
    #TODO: Separate manifest info and manifest items.
    order : backref to Order
    '''
    __tablename__ = 'shipment'
    id = Col(Int, primary_key=True)
    order_id = Col(Int, ForeignKey('order.id'), nullable=False)

    sku_qty = Col(Int, nullable=False) # Deduct from total SKUs due

    shipmentdate = Col(Date, nullable=False)
    shipmentID = Col(Utf, default=u'') # i.e., Manifest number
    shipmentnote = Col(Utf, default=u'') # Information concerning the delivery

    #TODO: Add destination or add to note (maybe JSON)
    driver = Col(Utf) # Track vehicle driver (optional)
    truck = Col(Utf) # Track vehicle by license (optional)
    note = Col(Utf) # Extra note field if needed
    checked = Col(Bool, nullable=False, default=False) # Extra boolean for matching/verifying

    # METHODS
    def listbox_summary(self):
        """
        Return a single line unicode summary intended for a listbox.
        """
        txt = u'{date:<10}   編號: {s.shipmentID:<10}   QTY: {s.sku_qty:>5} {s.order.product.SKU:<6}   品名: {s.order.product.inventory_name}'
        txt = txt.format(s=self, date=str(self.shipmentdate))
        return txt


#==============================================================================
# Invoice class (track multiple invoices for one order)
#==============================================================================
@AddDictRepr
class Invoice(Base): # Keep track of invoices/payments for one order
    __tablename__ = 'invoice'
    invoice_no = Col(Utf, primary_key=True) # i.e., Invoice number
    #id = Col(Int, primary_key=True)

    seller = Col(Utf, ForeignKey('branch.name'), nullable=False) # For billing/receipts
    buyer = Col(Utf, ForeignKey('branch.name'), nullable=False) # For billing/receipts

    invoicedate = Col(Date, nullable=False)
    invoicenote = Col(Utf) # Information concerning the invoice

    check_no = Col(Utf)
    paid = Col(Bool, nullable=False, default=False)
    paydate = Col(Date)

    note = Col(Utf) # Extra note field if needed
    checked = Col(Bool, nullable=False, default=False) # Extra boolean for matching/verifying

    items = rel('InvoiceItem', backref='invoice')

    def subtotal(self):
        return sum([item.subtotal() for item in self.items])

    def tax(self):
        '''Tax is rounded to nearest integer before returning value.'''
        return int(round(self.subtotal() * 0.05))

    def taxtotal(self):
        total = self.subtotal() + (self.tax() if self.items[0].order.applytax else 0)
        return int(round(total))


#==============================================================================
# InvoiceItem class (track multiple products for one invoice)
#==============================================================================
@AddDictRepr
class InvoiceItem(Base): # Keep track of invoices/payments for one order
    '''
    order : backref to Order
    invoice : backref to Invoice

    #TODO: Add ref from InvoiceItem to ShipmentItem, one-to-one
    '''
    __tablename__ = 'invoiceitem'
    id = Col(Int, primary_key=True)

    invoice_no = Col(Utf, ForeignKey('invoice.invoice_no'), nullable=False)

    order_id = Col(Int, ForeignKey('order.id'), nullable=False)

    sku_qty = Col(Int, nullable=False)


    def subtotal(self):
        subtotal = self.order.price * self.sku_qty
        if self.order.product.unitpriced:
            subtotal *= self.order.product.units
        return int(round(subtotal))

    def listbox_summary(self):
        """
        Return a single line unicode summary intended for a listbox.
        """
        txt = u'{date:<10}   編號: {s.invoice_no:<10}   QTY: {s.sku_qty:>5} {s.order.product.SKU:<6}   Subtotal: ${total:<6}   品名: {s.order.product.inventory_name}'
        txt = txt.format(s=self, date=str(self.invoice.invoicedate), total=self.subtotal())
        return txt



#==============================================================================
# CoGroup (company grouping class for branches)
#==============================================================================
@AddDictRepr
class CoGroup(Base):
    # Primary key is abbreviated "name" of group.
    #
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




#==============================================================================
# Branch class
#==============================================================================
@AddDictRepr
class Branch(Base):
    # Primary key is abbreviated "name" of branch company.
    #
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

    parent = rel('CoGroup')
    contacts = rel('Contact')

    purchases = rel('Order', primaryjoin="and_(Branch.name==Order.seller, Order.is_sale==False)") #Purchases FROM this company
    sales = rel('Order', primaryjoin="and_(Branch.name==Order.buyer, Order.is_sale==True)") #Sales TO this company



#==============================================================================
# Contact class
#==============================================================================
@AddDictRepr
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




#==============================================================================
# Product class
#==============================================================================
#def summarize(context):
#    '''Short text of product key values.
#    "product_name (## UM SKU)"
#    e.g. "HCL (20 kg barrel)"
#    '''
#    outname = context.current_parameters['product_label']
#    units = float(context.current_parameters['units'])
#    units = int(units) if int(units)==units else units #Truncate if mantissa is zero
#    UM = context.current_parameters['UM']
#    SKU = context.current_parameters['SKU']
#    if not outname:
#        outname = context.current_parameters['inventory_name']
#    if SKU == u'槽車':
#        return u"{0} (槽車)".format(outname)
#    else:
#        units = int(units) if int(units)==units else units
#        uf = u"{0} ({1} {2} {3})"
#        return uf.format(outname,units,UM,SKU)

@AddDictRepr
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
    note = Col(Utf) # {JSON} contains extra data, i.e. current ASE and RT numbers
                    # {JSON} must be appended to the end after any notes. Last char == '}'
    is_supply = Col(Bool, nullable=False)
    discontinued = Col(Bool, nullable=False, default=False)

    curr_price = Col(Float, default=0.0)

    summary = Col(Utf)

    stock = rel('Stock', backref='product')
    orders = rel('Order', primaryjoin="Product.MPN==Order.MPN")


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

    def label(self):
        '''Returns product_label, which is the client supplied name.
        If a product_label does not exist, then return our inventory_name
        for the product.
        '''
        if self.product_label != u'':
            return self.product_label
        else:
            return self.inventory_name

    def SKUlabel(self):
        if self.unitpriced or self.SKU == u'槽車':
            return self.UM
        else:
            return self.SKU

    def json(self, new_dic=None):
        '''Saves 'new_dic' as a json string and overwrites previous json.
        Returns contents of json string as a dictionary object.
        Note: Commit session after making changes.'''
        if new_dic == None:
            if self.note.find(u'}') != -1:
                return json.loads(self.note[self.note.index(u'{'):])
            else:
                return None
        else:
            old_dic = dict()
            # Delete existing json string
            if self.note.find(u'}') != -1:
                old_dic = self.json()
                self.note = self.note.split(u'{')[0]
            # Merge and overwrite old with new.
            new_dic = dict(old_dic.items() + new_dic.items())
            self.note += json.dumps(new_dic)
            return True
        return False

    def summarize(self):
        '''Short text of product key values.
        "product_name (## UM SKU)"
        e.g. "HCL (20 kg barrel)"
        '''
        outname = self.product_label
        units = float(self.units)
        units = int(units) if int(units)==units else units #Truncate if mantissa is zero
        UM = self.UM
        SKU = self.SKU
        if not outname:
            outname = self.inventory_name
        if SKU == u'槽車':
            return u"{0} (槽車)".format(outname)
        else:
            units = int(units) if int(units)==units else units
            uf = u"{0} ({1} {2} {3})"
            return uf.format(outname,units,UM,SKU)



#==============================================================================
# Stock class
#==============================================================================
@AddDictRepr
class Stock(Base): #For warehouse transactions
    __tablename__ = 'stock'
    id = Col(Int, primary_key=True)
    MPN = Col(Utf, ForeignKey('product.MPN'), nullable=False)

    date = Col(Date, nullable=False)
    adj_unit = Col(Float, nullable=False)   #Use units for stock amounts
    adj_SKU = Col(Float) #Probably will NOT use this
    adj_value = Col(Float, nullable=False)  #Value of units in transaction
    note = Col(Utf)



#==============================================================================
# Vehicle class
#==============================================================================
@AddDictRepr
class Vehicle(Base):
    __tablename__ = 'vehicle'
    id = Col(Utf, primary_key=True) #license plate number

    purchasedate = Col(Date)
    description = Col(Utf)
    value = Col(Float)
    note = Col(Utf)



#==============================================================================
# Database loading method
#==============================================================================
def get_database(filename, echo=False):
    '''Opens a database and returns an 'engine' object.'''
    database = sqla.create_engine('sqlite:///'+filename, echo=echo)
    Base.metadata.create_all(database)   #FIRST TIME SETUP ONLY
    return database


#==============================================================================
# Testing and Debugging
#==============================================================================
if __name__ == '__main__':
    engine = get_database(u'test.db', echo=False)
    session = sessionmaker(bind=engine)()
    session.add(Vehicle(id=u'MONKEY'))
    veh = session.query(Vehicle).get(u'MONKEY')
    print veh
    print veh.__dict__

    order = Order(orderID=u'ZV1234', seller=u'Oscorp', buyer=u'Marvel', group=u'DC comics',
                  is_sale=True, MPN=666, subtotal=1000, duedate=datetime.date.today(), totalskus=24)
    product = Product(MPN=666, group=u'DC comics', units=12, UM=u'ounce', SKU=u'vial', unitpriced=False, is_supply=False, product_label=u'Muscle Juice', inventory_name=u'serim 234')
    shipment = Shipment(shipmentID=u'003568', sku_qty=10, order=order, shipmentdate=datetime.date.today())
    session.add(product)
    session.add(order)
    order = session.query(Order).first()
    print 'order', order
    print order.formatted()
    for each in order.shipments:
        print each.listbox_summary()