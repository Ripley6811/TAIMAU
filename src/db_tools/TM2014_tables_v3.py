#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Version 3 splits Order into Order and OrderItem,
Shipment into Shipment and ShipmentItem.
Just as Invoice was split from version 1 to 2.
InvoiceItem and ShipmentItem now reference each other.
Invoice number is removed as primary key and placed with integer.

NOTE: Class functions can be changed and added without migration.

"""

import sqlalchemy as sqla
from sqlalchemy.orm import relationship as rel
from sqlalchemy.orm import backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import datetime
import json

Int = sqla.Integer
#Str = sqla.String  #TODO: Can probably delete this line
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
@AddDictRepr
class Order(Base):
    __tablename__ = 'order'
    id = Col(Int, primary_key=True)
    group = Col(Utf(4), ForeignKey('cogroup.name'), nullable=False) # Of second party main company
    seller = Col(Utf(4), ForeignKey('branch.name'), nullable=False) # For billing/receipts
    buyer = Col(Utf(4), ForeignKey('branch.name'), nullable=False) # For billing/receipts
    parent = rel('CoGroup')

    recorddate = Col(DateTime, nullable=False, default=today) # Date of entering a record

    # Keep all product information in the outgoing product list
    MPN = Col(Utf(20), ForeignKey('product.MPN'), nullable=False) # Product code

    price = Col(Float) # Price for one SKU or unit on this order
    discount = Col(Int, nullable=False, default=0) # Discount percentage as integer (0-100)
    #XXX: name change in version 3: totalskus = Col(Int)
    qty = Col(Int, nullable=False)
    applytax = Col(Bool, nullable=False) # True = 5%, False = 0%

    #XXX: Remove in version 3
    #totalunits = Col(Float) # AUTO: unitssku * totalskus
    #subtotal = Col(Float) #TODO: Remove and leave final totals in attached invoice.
    #totalcharge = Col(Int) #TODO: Remove

    orderdate = Col(Date, nullable=False)  # Order placement date
    duedate = Col(Date)  # Expected delivery date
    date = Col(Date) # Extra date field if needed

    orderID = Col(Utf(20))  # PO Number

    ordernote = Col(Utf(100)) # Information concerning the order
    note = Col(Utf(100)) # Extra note field if needed.

    checked = Col(Bool, nullable=False, default=False) # Match against second party records
    is_sale = Col(Bool, nullable=False, default=False) # Boolean. Customer
    is_purchase = Col(Bool, nullable=False, default=False) # Boolean. Supplier

    shipments = rel('ShipmentItem', backref='order')
    invoices = rel('InvoiceItem', backref='order')
    product = rel('Product')

    #XXX: New in version 3
    is_open = Col(Bool, nullable=False, default=True) # Active or closed PO

    @property
    def units(self):
        return self.qty * self.product.units

    def shipped_value(self):
        '''Return the value of total shipped items.'''
        value = self.qty_shipped() * self.price
        if self.product.unitpriced:
            value = value * self.product.units
        if self.applytax:
            value = value * 1.05
        return value

    def qty_shipped(self):
        '''By number of SKUs'''
        if len(self.shipments) == 0:
            return 0
        return sum([srec.qty if isinstance(srec.qty,int) else 0 for srec in self.shipments])

    def qty_remaining(self):
        '''By number of SKUs remaining to be shipped'''
        return int(self.qty - self.qty_shipped())

    def all_shipped(self):
        '''By number of SKUs'''
        if len(self.shipments) == 0:
            return False
        return self.qty == self.qty_shipped()

    def qty_invoiced(self):
        '''By number of SKUs'''
        if len(self.invoices) == 0:
            return 0
        return sum([prec.qty if isinstance(prec.qty,int) else 0 for prec in self.invoices])

    def all_invoiced(self):
        '''By number of SKUs'''
#        if len(self.invoices) == 0:
#            return False
        return self.qty_shipped() == self.qty_invoiced()

    def total_paid(self):
        if len(self.invoices) == 0:
            return 0
        return sum([prec.qty if prec.paid else 0 for prec in self.invoices])

    def all_paid(self):
        if len(self.invoices) == 0:
            return False
        return not (False in [prec.invoice.paid for prec in self.invoices])

    def qty_quote(self, qty):
        subtotal = self.price * qty
        if self.product.unitpriced:
            subtotal *= self.product.units
        return int(round(subtotal))


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
    shipmentdate = Col(Date, nullable=False)
    shipment_no = Col(Utf(20), default=u'') # i.e., Manifest number
    shipmentnote = Col(Utf(100), default=u'') # Information concerning the delivery
    shipmentdest = Col(Utf(100), default=u'')

    driver = Col(Utf(4)) # Track vehicle driver (optional)
    truck = Col(Utf(10)) # Track vehicle by license (optional)
    note = Col(Utf(100)) # Extra note field if needed
    checked = Col(Bool, nullable=False, default=False) # Extra boolean for matching/verifying

    items = rel('ShipmentItem', backref='shipment')

#    # METHODS
#    def listbox_summary(self):
#        """
#        Return a single line unicode summary intended for a listbox.
#        """
#        txt = u'{date:<10}   編號: {s.shipment_no:<10}   QTY: {s.items[0].qty:>5} {s.order.product.SKU:<6}   品名: {s.order.product.inventory_name}'
#        txt = txt.format(s=self, date=str(self.shipmentdate))
#        return txt

@AddDictRepr
class ShipmentItem(Base):
    __tablename__ = 'shipmentitem'
    id = Col(Int, primary_key=True)

    order_id = Col(Int, ForeignKey('order.id'), nullable=False)
    shipment_id = Col(Int, ForeignKey('shipment.id'), nullable=False)

    qty = Col(Int, nullable=False) # Deduct from total SKUs due

    lot = Col(Utf(20))
    lot_start = Col(Int)
    lot_end = Col(Int)
    rt_no = Col(Utf(20))

    invoiceitem = rel('InvoiceItem', backref='shipmentitem')

#==============================================================================
# Invoice class (track multiple invoices for one order)
#==============================================================================
@AddDictRepr
class Invoice(Base): # Keep track of invoices/payments for one order
    __tablename__ = 'invoice'
    #XXX: New in version 3, primary key change
    id = Col(Int, primary_key=True)

    invoice_no = Col(Utf(20), default=u'') # i.e., Invoice number

    seller = Col(Utf(4), ForeignKey('branch.name'), nullable=False) # For billing/receipts
    buyer = Col(Utf(4), ForeignKey('branch.name'), nullable=False) # For billing/receipts

    invoicedate = Col(Date, nullable=False)
    invoicenote = Col(Utf(100)) # Information concerning the invoice

    check_no = Col(Utf(20))
    paid = Col(Bool, nullable=False, default=False)
    paydate = Col(Date)

    note = Col(Utf(100)) # Extra note field if needed
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
    shipmentitem : backref to ShipmentItem
    '''
    __tablename__ = 'invoiceitem'
    id = Col(Int, primary_key=True)

    invoice_id = Col(Int, ForeignKey('invoice.id'), nullable=False)
    shipmentitem_id = Col(Int, ForeignKey('shipmentitem.id'), nullable=False)

    order_id = Col(Int, ForeignKey('order.id'), nullable=False)

    qty = Col(Int, nullable=False)


    def subtotal(self):
        subtotal = self.order.price * self.qty
        if self.order.product.unitpriced:
            subtotal *= self.order.product.units
        return int(round(subtotal,0))

    def total(self):
        subtotal = self.subtotal()
        if self.order.applytax:
            subtotal *= 1.05
        return int(round(subtotal,0))

#    def listbox_summary(self):
#        """
#        Return a single line unicode summary intended for a listbox.
#        """
#        txt = u'{date:<10}   編號: {s.invoice_no:<10}   QTY: {s.qty:>5} {s.order.product.SKU:<6}   Subtotal: ${total:<6}   品名: {s.order.product.inventory_name}'
#        txt = txt.format(s=self, date=str(self.invoice.invoicedate), total=self.subtotal())
#        return txt



#==============================================================================
# CoGroup (company grouping class for branches)
#==============================================================================
@AddDictRepr
class CoGroup(Base):
    __tablename__ = 'cogroup'
    name = Col(Utf(4), primary_key=True, nullable=False) # Abbreviated name of company (2 to 4 chars)
    is_active = Col(Bool, nullable=False, default=True) # Boolean for listing the company. Continuing business.
    is_supplier = Col(Bool, nullable=False, default=True) # Maybe use in later versions
    is_customer = Col(Bool, nullable=False, default=True) # Maybe use in later versions

    branches = rel('Branch', backref='cogroup', lazy='joined') # lazy -> Attaches on retrieving a cogroup
    orders = rel('Order')
    products = rel('Product', backref='cogroup')
    contacts = rel('Contact')

    purchases = rel('Order', primaryjoin="and_(CoGroup.name==Order.group, Order.is_sale==False)") #Purchases FROM this company
    sales = rel('Order', primaryjoin="and_(CoGroup.name==Order.group, Order.is_sale==True)") #Sales TO this company
    openpurchases = rel('Order', primaryjoin="and_(CoGroup.name==Order.group, Order.is_sale==False, Order.is_open==True)") #Purchases FROM this company
    opensales = rel('Order', primaryjoin="and_(CoGroup.name==Order.group, Order.is_sale==True, Order.is_open==True)") #Sales TO this company




#==============================================================================
# Branch class
#==============================================================================
@AddDictRepr
class Branch(Base):
    __tablename__ = 'branch'
    name = Col(Utf(4), primary_key=True, nullable=False) # Abbreviated name of company (2 to 4 chars)
    group= Col(Utf(4), ForeignKey('cogroup.name'), nullable=False) # Name of main company representing all branches
    fullname = Col(Utf(100), default=u'')
    english_name = Col(Utf(100), default=u'')
    tax_id = Col(Utf(8), nullable=False, default=u'')
    phone = Col(Utf(20), default=u'')
    fax = Col(Utf(20), default=u'')
    email = Col(Utf(20), default=u'')
    note = Col(Utf(100), default=u'')
    address_office = Col(Utf(100), default=u'')
    address_shipping = Col(Utf(100), default=u'')
    address_billing = Col(Utf(100), default=u'')
    address = Col(Utf(100), default=u'') # Extra address space if needed
    is_active = Col(Bool, nullable=False, default=True) # Boolean for listing the company. Continuing business.

#    parent = rel('CoGroup')
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
    group = Col(Utf(4), ForeignKey('cogroup.name'), nullable=False)
    branch = Col(Utf(4), ForeignKey('branch.name'))
    name = Col(Utf(20), nullable=False)
    position = Col(Utf(20), default=u'')
    phone = Col(Utf(20), default=u'')
    fax = Col(Utf(20), default=u'')
    email = Col(Utf(20), default=u'')
    note = Col(Utf(100), default=u'')




#==============================================================================
# Product class
#==============================================================================
@AddDictRepr
class Product(Base): # Information for each unique product (including packaging)
    __tablename__ = 'product'

    MPN = Col(Utf(20), primary_key=True)
    group = Col(Utf(4), ForeignKey('cogroup.name'), nullable=False)

    product_label = Col(Utf(100), default=u'') #Optional 2nd party product name
    inventory_name = Col(Utf(100), nullable=False) #Required
    english_name = Col(Utf(100), default=u'')
    units = Col(Float, nullable=False)  #Units per SKU
    UM = Col(Utf(10), nullable=False)   #Unit measurement
    SKU = Col(Utf(10), nullable=False)  #Stock keeping unit (sold unit)
    SKUlong = Col(Utf(100), default=u'')
    unitpriced = Col(Bool, nullable=False)
    ASE_PN = Col(Utf(20)) # ASE product number
    ASE_RT = Col(Utf(20)) # ASE department routing number
    ASE_END = Col(Int) # Last used SKU index number for current lot
    note = Col(Utf(100)) # {JSON} contains extra data, i.e. current ASE and RT numbers
                    # {JSON} must be appended to the end after any notes. Last char == '}'
    is_supply = Col(Bool, nullable=False)
    discontinued = Col(Bool, nullable=False, default=False)

    curr_price = Col(Float, default=0.0)

    stock = rel('Stock', backref='product')
    orders = rel('Order', primaryjoin="Product.MPN==Order.MPN")


    @property
    def price(self):
        if self.curr_price.is_integer():
            return int(self.curr_price)
        return self.curr_price



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
        '''Returns product_label, which is the client desired name.
        If a product_label does not exist, then return our inventory_name
        for the product.
        '''
        if self.product_label != u'':
            return self.product_label
        else:
            return self.inventory_name

    @property
    def name(self):
        '''Returns product_label, which is the client desired name.
        If a product_label does not exist, then return our inventory_name
        for the product.
        '''
        if self.product_label != u'':
            return self.product_label
        else:
            return self.inventory_name


    @property
    def specs(self):
        '''Short text of product key values.
        "## UM SKU"
        e.g. "20 kg barrel"
        '''
        u = self.units
        units = int(u) if int(u)==u else u #Truncate if mantissa is zero
        if self.SKU == u'槽車':
            return u'槽車-{}'.format(self.UM)
        else:
            txt = u"{0} {1} {2}"
            return txt.format(units,self.UM,self.SKU)


    def json(self, new_dic=None):
        '''Saves 'new_dic' as a json string and overwrites previous json.
        Returns contents of json string as a dictionary object.
        Note: Commit session after making changes.'''
        if new_dic == None:
            if self.note.find(u'}') != -1:
                return json.loads(self.note[self.note.index(u'{'):])
            else:
                return {}
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



#==============================================================================
# Stock class
#==============================================================================
@AddDictRepr
class Stock(Base): #For warehouse transactions
    __tablename__ = 'stock'
    id = Col(Int, primary_key=True)
    MPN = Col(Utf(20), ForeignKey('product.MPN'), nullable=False)

    date = Col(Date, nullable=False)
    adj_unit = Col(Float, nullable=False)   #Use units for stock amounts
    adj_SKU = Col(Float) #Probably will NOT use this
    adj_value = Col(Float, nullable=False)  #Value of units in transaction
    note = Col(Utf(100))



#==============================================================================
# Vehicle class
#==============================================================================
@AddDictRepr
class Vehicle(Base):
    __tablename__ = 'vehicle'
    id = Col(Utf(10), primary_key=True) #license plate number

    purchasedate = Col(Date)
    description = Col(Utf(100))
    value = Col(Float)
    note = Col(Utf(100))



#==============================================================================
# Database loading method
#==============================================================================
def get_database(db_path, echo=False):
    '''Opens a database and returns an 'engine' object.'''
    database = sqla.create_engine(db_path, echo=echo)
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
    shipment = Shipment(shipment_no=u'003568', qty=10, order=order, shipmentdate=datetime.date.today())
    session.add(product)
    session.add(order)
    order = session.query(Order).first()
    print 'order', order
    print order.formatted()
    for each in order.shipments:
        print each.listbox_summary()
