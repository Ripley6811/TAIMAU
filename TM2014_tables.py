import sqlalchemy as sqla
from sqlalchemy.orm import relationship as rel
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Int = sqla.Integer
Str = sqla.String
Utf = sqla.Unicode
Float = sqla.Float
Col = sqla.Column
Bool = sqla.Boolean
Date = sqla.Date
ForeignKey = sqla.ForeignKey

metadata = sqla.MetaData()

'''"purchases" and "sales" databases store individual transactions that include the
requesting company/unit.
'''
def ordertable(tablename, metadata):
    return sqla.Table(tablename, metadata,
        Col('id', Int, primary_key=True),
        Col('recorddate', Date), # Date of entering a record (Now use as order placement date)

        Col('parentcompany', Str(8)), # Of second party
        Col('sellercompany', Str(8)), # For billing/receipts
        Col('buyingcompany', Str(8)), # For billing/receipts

        # Keep all product information in the outgoing product list
        Col('mpn',          Str(10)), # Product code

        Col('price',      Float), # Price for one SKU or unit
        Col('totalskus',    Int),
        Col('totalunits',   Float), # AUTO: unitssku * totalskus
        Col('applytax',     Bool), # True = 5%, False = 0%
        Col('totalcharge',  Int), # AUTO: pricing * (totalskus or totalunits)

        Col('orderdate',    Date),  # Use as "expected" delivery date. (Originally was order placement date)
        Col('orderID',      Str(20)),  # i.e., PO Number
        Col('ordernote',    Str(100)), # Information concerning the order
        Col('deliverydate', Date),
        Col('delivered',    Bool), # True = delivered, False = not delivered yet
        Col('deliveryID',   Str(20)), # i.e., Manifest number
        Col('deliverynote', Str(100)), # Information concerning the delivery
        Col('paymentdate',  Date),
        Col('paymentID',    Str(20)), # i.e., Receipt number
        Col('paymentnote',  Str(100)), # Information concerning the invoice
        Col('paid',    Bool), # True = paid, False = not paid yet
    )
'''
Col('productname',      Str(30)),
Col('unitmeasurement',  Str(8)), # kg, lb, L, gal, etc.
Col('unitssku',         Float), # Number of units per SKU (ex. 18 kg per bag)
Col('skudescription',   Str(30)), # barrel, tank, bag, etc.
Col('skupricing',       Bool), # True if 'pricing' by SKU, False if by unit
'''
purchases = ordertable('purchases', metadata)
sales = ordertable('sales', metadata)

def recat(origenname):
    origenname = origenname.lower()
    mapname = {
        'unit price': 'pricing',
        'product name (unit of measure)': 'productname',
        'dispatch date': 'deliverydate',
        'po number': 'orderID',
        'receipt number': 'paymentID',
        'manifest number': 'deliveryID',
        'a/r confirmation': 'paymentnote',
    }

    if mapname.get(origenname):
        return mapname[origenname]
    return origenname


#'''WAREHOUSE database stores information for a particular companies product.
#'''
#warehouse = sqla.Table('warehouse', metadata,
#    Col('id', Int, primary_key=True),
#
#    Col('date',     Date),
#    Col('product',  Str(30)),
#    Col('note',     Str(100)),
#
#    Col('debitamount',  Float),
#    Col('debitvalue',   Float),
#    Col('creditamount', Float),
#    Col('creditvalue',  Float),
#)


Base = declarative_base()

'''
class OrderProgress(Base):
    __tablename__ = 'salesrec'
    id = Col(Int, primary_key=True)
    rec_id = Col(Int, ForeignKey('sales.id'))
    date = Col(Utf)
    qty = Col(Int)
    note = Col(Utf)
'''

class Purchases(Base):
    __tablename__ = 'purchases'
    id = Col(Int, primary_key=True)
    recorddate = Col(Date) # Date of entering a record (Now use as order placement date)

    parentcompany = Col(Str(8)) # Of second party
    sellercompany = Col(Str(8)) # For billing/receipts
    buyingcompany = Col(Str(8)) # For billing/receipts

    # Keep all product information in the outgoing product list
    mpn = Col(Str(10)) # Product code

    price = Col(Float) # Price for one SKU or unit
    totalskus = Col(Int)
    totalunits = Col(Float) # AUTO: unitssku * totalskus
    applytax = Col(Bool) # True = 5%, False = 0%
    totalcharge = Col(Int) # AUTO: pricing * (totalskus or totalunits)

    orderdate = Col(Date)  # Use as "expected" delivery date. (Originally was order placement date)
    orderID = Col(Str(20))  # i.e., PO Number
    ordernote = Col(Str(100)) # Information concerning the order
    deliverydate = Col(Date)
    delivered = Col(Bool) # True = delivered, False = not delivered yet
    deliveryID = Col(Str(20)) # i.e., Manifest number
    deliverynote = Col(Str(100)) # Information concerning the delivery
    paymentdate = Col(Date)
    paymentID = Col(Str(20)) # i.e., Invoice or Receipt number
    paymentnote = Col(Str(100)) # Information concerning the invoice
    paid = Col(Bool) # True = paid, False = not paid yet
    
    
class Sales(Base):
    __tablename__ = 'sales'
    id = Col(Int, primary_key=True)
    recorddate = Col(Date) # Date of entering a record (Now use as order placement date)

    parentcompany = Col(Str(8)) # Of second party
    sellercompany = Col(Str(8)) # For billing/receipts
    buyingcompany = Col(Str(8)) # For billing/receipts

    # Keep all product information in the outgoing product list
    mpn = Col(Str(10)) # Product code

    price = Col(Float) # Price for one SKU or unit
    totalskus = Col(Int)
    totalunits = Col(Float) # AUTO: unitssku * totalskus
    applytax = Col(Bool) # True = 5%, False = 0%
    totalcharge = Col(Int) # AUTO: pricing * (totalskus or totalunits)

    orderdate = Col(Date)  # Use as "expected" delivery date. (Originally was order placement date)
    orderID = Col(Str(20))  # i.e., PO Number
    ordernote = Col(Str(100)) # Information concerning the order
    deliverydate = Col(Date)
    delivered = Col(Bool) # True = delivered, False = not delivered yet
    deliveryID = Col(Str(20)) # i.e., Manifest number
    deliverynote = Col(Str(100)) # Information concerning the delivery
    paymentdate = Col(Date)
    paymentID = Col(Str(20)) # i.e., Invoice or Receipt number
    paymentnote = Col(Str(100)) # Information concerning the invoice
    paid = Col(Bool) # True = paid, False = not paid yet

    
class Company(Base):
    __tablename__ = 'company'
    id = Col(Utf, primary_key=True) # Abbreviated name of company (2 to 4 chars)
    group_id = Col(Utf)
    fullname = Col(Utf)
    english_name = Col(Str)
    tax_id = Col(Str)
    phone = Col(Str)
    fax = Col(Str)
    email = Col(Str)
    contact = Col(Utf)
    note = Col(Utf)
    address_office = Col(Utf)
    address_shipping = Col(Utf)
    address_billing = Col(Utf)
    contacts = rel('Contact')
    products = rel('Product')

    def __repr__(self):
        return "<Company(tax_id='{}', english_name='{}', email='{}')>".format(
                      self.tax_id, self.english_name, self.email)
                      
                      
class Contact(Base):
    __tablename__ = 'contact'
    id = Col(Int, primary_key=True)
    company = Col(Utf, ForeignKey('company.id'))
    name = Col(Utf)
    phone = Col(Str)
    fax = Col(Str)
    email = Col(Str)
    note = Col(Utf)


class Product(Base):
    __tablename__ = 'product'
#    id = Col(Int, primary_key=True)
    company = Col(Utf, ForeignKey('company.id'))

    MPN = Col(Utf, primary_key=True)
    product_label = Col(Utf)
    inventory_name = Col(Utf)
    english_name = Col(Str)
    units = Col(Float)
    UM = Col(Utf)
    SKU = Col(Utf)
    SKUlong = Col(Utf)
    SKUpricing = Col(Bool)
    ASE_PN = Col(Str)
    note = Col(Utf)
    incoming = Col(Bool)
    discontinued = Col(Bool)

    
def open_database(dbname, echo=False):
    '''Returns the database or creates one and returns the new database.'''
    database = sqla.create_engine('sqlite:///'+dbname, echo=echo)
    metadata.create_all(database) # Only needed the first time to add the table to database
    metadata.reflect(database)
    return database, metadata