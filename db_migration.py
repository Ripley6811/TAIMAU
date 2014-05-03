#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy.orm import sessionmaker
import database_management as DM
import datetime
import random
from TM2014_tables_v2 import get_database, CoGroup, Branch, Product, Contact, Stock, Order, Shipment, Invoice, InvoiceItem


dbname = r"C:\Users\Jay\Dropbox\GitHub\TAIMAU\TM2014_v2.db"
database = get_database(dbname)
newsession = sessionmaker(bind=database)()





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
# MIGRATE PURCHASES and SALES
# Fix subtotals!
count = 1
invoice_nos = []
def enter_record(rec):
    global count, invoice_nos
    daylimit = datetime.date.today() + datetime.timedelta(30)
    for key in rec:
        if rec[key] == None:
            rec[key] = u''
        if u'date' in key and isinstance(rec[key],datetime.date):
            if rec[key] > daylimit:
                print rec[key], '>>',
                rec[key] = rec[key].replace(year=rec[key].year-1)
                print rec[key]





    rec['group'] = rec.pop('parentcompany')
    rec['seller'] = rec.pop('sellercompany')
    rec['buyer'] = rec.pop('buyingcompany')
    rec['duedate'] = rec['orderdate']
    rec['orderdate'] = rec['recorddate']
    MPN = rec.pop('mpn')
    try:
        rec['MPN'] = str(int(float(MPN)))
    except UnicodeEncodeError:
        rec['MPN'] = MPN
    rec['checked'] = False
    rec['discount'] = 0
    rec['id'] = count
    if rec['applytax'] == False:
        rec['subtotal'] = rec['totalcharge']
    else:
        est_subtotal = int(rec['totalcharge']*100/105)
        try:
            if est_subtotal-1 <= int(rec['price']*rec['totalskus']) <= est_subtotal+1:
                rec['subtotal'] = rec['price']*rec['totalskus']
            elif est_subtotal-1 <= int(rec['price']*rec['totalunits']) <= est_subtotal+1:
                rec['subtotal'] = rec['price']*rec['totalunits']
            else:
                print count, "Could not estimate...",est_subtotal,u'({})'.format(rec['totalcharge']),int(rec['price']*rec['totalskus']),int(rec['price']*rec['totalunits'])
        except TypeError:
            return False
#            print 'TypeError', u', '.join(map(str,[rec['duedate'],est_subtotal-1,rec['price'],rec['totalskus'],est_subtotal+1,rec['totalunits'] ]))
#            if est_subtotal-1 <= int(rec['price']*rec['totalunits']) <= est_subtotal+1:
#                rec['subtotal'] = rec['price']*rec['totalunits']
#            else:
#                print count, "Could not estimate...",est_subtotal,u'({})'.format(rec['totalcharge']),int(rec['price']*rec['totalskus']),int(rec['price']*rec['totalunits'])


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

    totalcharge = rec['subtotal']
    if rec['applytax']:
        totalcharge *= 1.05


    tmp_inv_no = rec.pop('paymentID')
    if tmp_inv_no in [None, u'None', u'']:
        #Create a random and unique invoice number if none exists.
        tmp_inv_no = str(random.randint(10000,99999)) + u'random' + str(random.randint(10000,99999))
    tmp_inv_no = tmp_inv_no.strip()
    print repr(tmp_inv_no)

    invoice_rec = dict(
        invoice_no= tmp_inv_no,
        seller= rec['seller'],
        buyer= rec['buyer'],

        paid= True, # Most records have been paid... need to edit newest later.
        paydate= rec['paymentdate'],
        invoicedate= rec['paymentdate'],
        invoicenote= rec.pop('paymentnote'),
        note= u'',
        checked= False
    )

    invoice_item_rec = dict(
        invoice_no= tmp_inv_no,
        order_id=rec['id'],
        sku_qty= rec['totalskus'],
    )


    del rec['totalcharge']
    del rec['paymentdate']
    del rec['delivered']
    del rec['paid']
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
    if not isinstance(invoice_rec['paydate'], datetime.date):
        invoice_rec['paydate'] = rec['duedate']
    if tmp_inv_no not in invoice_nos:
        newsession.add(Invoice(**invoice_rec))
        invoice_nos.append(tmp_inv_no)
    newsession.add(InvoiceItem(**invoice_item_rec))
    count += 1

for rec in DM.session.query(DM.tables.Purchases):
    rec = dict(rec.__dict__)
    rec['is_sale'] = False
    enter_record(rec)

for rec in DM.session.query(DM.tables.Sales):
    rec = dict(rec.__dict__)
    rec['is_sale'] = True
    enter_record(rec)

newsession.commit()
#
#for each in newsession.query(Order).all():
#    print each
#print '--------------------------------------------'


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