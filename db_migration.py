#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy.orm import sessionmaker
import database_management as DM
import datetime
from TM2014_tables_v2 import get_database, CoGroup, Branch, Product, Contact, Stock, Order, Shipment, Invoice


dbname = r"C:\Users\Jay\Dropbox\GitHub\TAIMAU\TM2014_v2.db"
database = get_database(dbname)
Session = sessionmaker(bind=database)
newsession = Session()





######################################################################
# MIGRATE COGROUP, COMPANIES and CONTACTS
added = set()
for rec in DM.session.query(DM.tables.Company):
    gid = rec.group_id
    rec = rec.__dict__
    if rec['group_id']== u'TT':
        continue
    if gid not in added:
        added.add(gid)
        newsession.add(CoGroup(name=gid))
    for key in rec:
        if rec[key] == None:
            rec[key] = u''
    rec['is_active'] = True
    rec['address'] = u''
    rec['name'] = rec.pop('id')
    rec['group'] = rec.pop('group_id')

    condict = dict(
        branch = rec['name'],
        group = rec['group'],
        name = rec.pop('contact'),
        phone = rec['phone'],
        fax = rec['fax'],
        email = rec['email'],
    )
    del rec['_sa_instance_state']
    newsession.add(Branch(**rec))
    newsession.add(Contact(**condict))
#newsession.commit()


#for each in newsession.query(CoGroup).all():
#    print each
#for each in newsession.query(Branch).all():
#    print each

#######################################################################
# MIGRATE PRODUCTS
for rec in DM.session.query(DM.tables.Product):
    rec = rec.__dict__
    for key in rec:
        if rec[key] == None:
            rec[key] = u''
    rec['is_supply'] = rec.pop('incoming')
    try:
        rec['MPN'] = str(int(float(rec['MPN'])))
    except:
        pass
    rec['group'] = rec.pop('company')
    rec['unitpriced'] = not rec.pop('SKUpricing')


    del rec['_sa_instance_state']
    newsession.add(Product(**rec))
#newsession.commit()

#for each in newsession.query(Product).all():
#    print each

#######################################################################
# MIGRATE PURCHASES
# Fix subtotals!
count = 1
for rec in DM.session.query(DM.tables.Purchases):
    rec = dict(rec.__dict__)
    for key in rec:
        if rec[key] == None:
            rec[key] = u''

    rec['group'] = rec.pop('parentcompany')
    rec['seller'] = rec.pop('sellercompany')
    rec['buyer'] = rec.pop('buyingcompany')
    rec['duedate'] = rec['orderdate']
    rec['orderdate'] = rec['recorddate']
    rec['MPN'] = str(int(float(rec.pop('mpn'))))
#    rec['invoiced'] = False
#    rec['delivered'] = False
    rec['checked'] = False
    rec['is_sale'] = False
#    rec['invoicenote'] = u''
#    rec['invoiceID'] = rec['paymentID']
#    rec['invoicedate'] = rec['paymentdate']
#    if rec['paid'] == u'':
#        rec['paid'] = False
    rec['discount'] = 0
#    rec['recorddate'] = datetime.date.today()
    rec['id'] = count
#            print type(rec[key]), rec[key]


    shiprec = dict(
        order_id=rec['id'],
        sku_qty=rec['totalskus'],
        shipmentdate=rec.pop('deliverydate'),
        shipmentID=rec.pop('deliveryID'),
        shipmentnote=rec.pop('deliverynote'),
        driver=u'',
        truck=u'',
        note=u'',
        checked=False
    )

    invoice_rec = dict(
        order_id=rec['id'],
        seller= rec['seller'],
        buyer= rec['buyer'],
        amount=rec['totalcharge'],
        paid=True, # Most records have been paid... need to edit newest later.
        invoicedate=rec.pop('paymentdate'),
        invoiceID=rec.pop('paymentID'),
        invoicenote=rec.pop('paymentnote'),
        note=u'',
        checked=False
    )


    del rec['delivered']
    del rec['paid']
#    del rec['invoiceID']
#    del rec['invoicedate']
#    del rec['invoicenote']
    del rec['_sa_instance_state']
    for key in rec.keys():
        if 'date' in key:
            if isinstance(rec[key], unicode):
                del rec[key]

    if not isinstance(shiprec['shipmentdate'], datetime.date):
        rec['orderdate'] = rec['duedate']
    newsession.add(Order(**rec))
    if not isinstance(shiprec['shipmentdate'], datetime.date):
        shiprec['shipmentdate'] = rec['duedate']
    newsession.add(Shipment(**shiprec))
    if not isinstance(invoice_rec['invoicedate'], datetime.date):
        invoice_rec['invoicedate'] = rec['duedate']
    newsession.add(Invoice(**invoice_rec))
    count += 1
#newsession.commit()
#
#for each in newsession.query(Order).all():
#    print each
#print '--------------------------------------------'

#######################################################################
# MIGRATE SALES
# Fix subtotals!
for rec in DM.session.query(DM.tables.Sales):
    rec = dict(rec.__dict__)
    for key in rec:
        if rec[key] == None:
            rec[key] = u''

    rec['group'] = rec.pop('parentcompany')
    rec['seller'] = rec.pop('sellercompany')
    rec['buyer'] = rec.pop('buyingcompany')
    rec['duedate'] = rec['orderdate']
    rec['orderdate'] = rec['recorddate']
    rec['MPN'] = rec.pop('mpn')
#    rec['invoiced'] = False
#    rec['delivered'] = True if rec['deliverydate'] else False
    rec['checked'] = False
    rec['is_sale'] = True
#    rec['invoicenote'] = u''
#    rec['invoiceID'] = rec['paymentID']
#    rec['invoicedate'] = rec['paymentdate']
#    if rec['paid'] == u'':
#        rec['paid'] = False
    rec['discount'] = 0
#    rec['recorddate'] = datetime.date.today()
    rec['id'] = count
#            print type(rec[key]), rec[key]


    shiprec = dict(
        order_id=rec['id'],
        sku_qty=rec['totalskus'],
        shipmentdate=rec.pop('deliverydate'),
        shipmentID=rec.pop('deliveryID'),
        shipmentnote=rec.pop('deliverynote'),
        driver=u'',
        truck=u'',
        note=u'',
        checked=False
    )

    invoice_rec = dict(
        order_id=rec['id'],
        seller= rec['seller'],
        buyer= rec['buyer'],
        amount=rec['totalcharge'],
        paid=True, # Most records have been paid... need to edit newest later.
        invoicedate=rec.pop('paymentdate'),
        invoiceID=rec.pop('paymentID'),
        invoicenote=rec.pop('paymentnote'),
        note=u'',
        checked=False
    )


    del rec['delivered']
    del rec['paid']
    del rec['_sa_instance_state']
    for key in rec.keys():
        if 'date' in key:
            if isinstance(rec[key], unicode):
                del rec[key]

    newsession.add(Order(**rec))
    if not isinstance(shiprec['shipmentdate'], datetime.date):
        shiprec['shipmentdate'] = rec['duedate']
    newsession.add(Shipment(**shiprec))
    if not isinstance(invoice_rec['invoicedate'], datetime.date):
        invoice_rec['invoicedate'] = rec['duedate']
    newsession.add(Invoice(**invoice_rec))
    count += 1
newsession.commit()
#
#for each in newsession.query(Invoice).all():
#    print each


rec = newsession.query(CoGroup).first()
print 'NAME:', rec
print ' BRANCHES'
for each in rec.branches:
    print '  branch:', each
print ' CONTACTS'
for each in rec.contacts:
    print '  contact:', each
print ' PRODUCTS'
for each in rec.products:
    print '  products:', each
print ' ORDERS'
for each in rec.orders:
    print '  orders:', each

rec = newsession.query(CoGroup).all()[2]
print 'NAME:', rec
print ' BRANCHES'
for each in rec.branches:
    print '  branch:', each
print ' CONTACTS'
for each in rec.contacts:
    print '  contact:', each
print ' PRODUCTS'
for each in rec.products:
    print '  products:', each
print ' ORDERS'
for each in rec.orders:
    print '  orders:', each