#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy.orm import sessionmaker
import db_manager as DM # v2 manager
import datetime
import random
from TM2014_tables_v3 import get_database, CoGroup, Branch, Product, Contact, Stock, Order, Shipment, ShipmentItem, Invoice, InvoiceItem, Vehicle


dbname = r"C:\Users\Jay\Dropbox\GitHub\TAIMAU\src\TM2014_v3.db"
database = get_database(dbname)
newsession = sessionmaker(bind=database)()

#TODO: Still needs testing in the program to make sure all records appear normal

#===============================================================================
# MIGRATE COMPANIES AND PRODUCTS AND ASSETS

added = set()
for i, rec in enumerate(DM.session.query(DM.CoGroup)):
    rec = rec.__dict__
    if i==0:
        print "CoGroup -----------------------------------------"
        for each in rec.keys():
            print each
    del rec['_sa_instance_state']
    del rec['branches']
#    print ">", rec

    newsession.add(CoGroup(**rec))

for i, rec in enumerate(DM.session.query(DM.Branch)):
    rec = rec.__dict__
    if i==0:
        print "Branch -----------------------------------------"
        for each in rec.keys():
            print each
    del rec['_sa_instance_state']
#    print ">", rec

    newsession.add(Branch(**rec))

for i, rec in enumerate(DM.session.query(DM.Contact)):
    rec = rec.__dict__
    if i==0:
        print "Contact -----------------------------------------"
        for each in rec.keys():
            print each
    del rec['_sa_instance_state']
#    print ">", rec

    newsession.add(Contact(**rec))

for i, rec in enumerate(DM.session.query(DM.Product)):
    rec = rec.__dict__
    if i==0:
        print "Product -----------------------------------------"
        for each in rec.keys():
            print each
    del rec['_sa_instance_state']
    del rec['summary']
#    print ">", rec

    newsession.add(Product(**rec))

for i, rec in enumerate(DM.session.query(DM.Stock)):
    rec = rec.__dict__
    if i==0:
        print "Stock -----------------------------------------"
        for each in rec.keys():
            print each
    del rec['_sa_instance_state']
#    print ">", rec

    newsession.add(Stock(**rec))

for i, rec in enumerate(DM.session.query(DM.Vehicle)):
    rec = rec.__dict__
    if i==0:
        print "Vehicle -----------------------------------------"
        for each in rec.keys():
            print each
    del rec['_sa_instance_state']
#    print ">", rec

    newsession.add(Vehicle(**rec))


#==============================================================================
# ORDERS, SHIPMENTS AND INVOICES
#==============================================================================
notmatched = 0
for i, rec in enumerate(DM.session.query(DM.Order)):
    # Ref to shipments and invoices for processing later
    Shipments = sorted(rec.shipments, key=lambda x:x.shipmentdate, reverse=True)
    try:
        InvoiceItems = sorted(rec.invoices, key=lambda x:x.invoice.invoicedate, reverse=True)
    except:
        InvoiceItems = rec.invoices

    shipped = rec.all_shipped()
    invoiced = rec.all_invoiced()
#    print shipped, invoiced
    rec = rec.__dict__
    if i==0:
        print "Order -----------------------------------------"
        for each in rec.keys():
            print each

    rec['is_open'] = not(shipped & invoiced)
    rec['is_purchase'] = not rec['is_sale']
    rec['qty'] = rec.pop('totalskus') # Rename

    del rec['_sa_instance_state']
    del rec['totalcharge']
    del rec['subtotal']
    del rec['totalunits']
    del rec['shipments']
    del rec['invoices']
#    print ">", rec

    newsession.add(Order(**rec))
    if i==0:
        print "New Order -----------------------------------------"
        for each in rec.keys():
            print each
    print '  ======================================='
    print '  Order:', rec['id'], ' Shipments:', len(Shipments), ' Invoices:', len(InvoiceItems)
    ### PROCESS SHIPMENTS
    nInv = len(InvoiceItems)
    nInvMatch = 0
    for i, rec in enumerate(Shipments):
        rec = rec.__dict__
        recitem = dict()


#        recitem['shipment_id'] = rec['id']
        recitem['order_id'] = rec.pop('order_id')
        recitem['qty'] = rec.pop('sku_qty')
        del rec['_sa_instance_state']
        rec['shipment_no'] = rec.pop('shipmentID')
        if rec['shipment_no'] == u'N/A':
            rec['shipment_no'] = u''
        recitem['shipment'] = Shipment(**rec)

        # Don't add multiple Shipment manifests
        if nInvMatch < len(InvoiceItems):
            for recinvitem in InvoiceItems:
                try:
                    recinv = recinvitem.invoice.__dict__
                except:
                    continue
                recinvitem = recinvitem.__dict__

                if 'qty' in recinvitem.keys():
                    continue
                if recitem['qty'] == recinvitem['sku_qty']:

        #            print i, "qty:", recitem['qty'], recinvitem['sku_qty'], recitem['qty'] == recinvitem['sku_qty']
#                    if recitem['qty'] != recinvitem['sku_qty']:
#                        notmatched += 1
                    print i, "qty:", recitem['qty'], recinvitem['sku_qty'], recitem['qty'] == recinvitem['sku_qty']
                    del recinv['_sa_instance_state']
                    del recinvitem['_sa_instance_state']
                    recinvitem['qty'] = recinvitem.pop('sku_qty')
                    del recinvitem['invoice_no']

                    recinvitem['shipmentitem'] = ShipmentItem(**recitem)
                    recinvitem['invoice'] = Invoice(**recinv)

                    newsession.add(InvoiceItem(**recinvitem))
                    nInvMatch += 1
                    break
            else:
#                print "InvoiceItem match not found",
#                print "                          STILL MORE" if nInvMatch < len(InvoiceItems) else "DONE"
                newsession.add(ShipmentItem(**recitem))
        else:
#            print "No InvoiceItems available"
            newsession.add(ShipmentItem(**recitem))
    print " ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! ! !" if nInvMatch < len(InvoiceItems) else ""

print "NOT MATCHED =", notmatched

#==============================================================================
# CONSOLIDATE SHIPMENT AND INVOICE, MATCH BY NUMBERS AND REDUCE
#==============================================================================

print newsession.query(Shipment).count(), "B Manifests"
print newsession.query(ShipmentItem).count(), "B Manifest items"
count = 0
for shipment in newsession.query(Shipment).all():
    if len(shipment.items) == 0:
        count += 1
print "Empty manifests:", count
for shipment in newsession.query(Shipment).all():
    if shipment.shipment_no:
#        print shipment.shipment_no,
        shipments = newsession.query(Shipment).filter(Shipment.shipment_no == shipment.shipment_no).all()
        if 1 < len(shipments) < 6:
            date = shipments[0].shipmentdate
            nombre = shipments[0].shipment_no
            _id = shipments[0].id

            for ship in shipments[1:]:
                if (date == ship.shipmentdate) & (nombre == ship.shipment_no):
                    for shipitem in ship.items:
#                        print shipitem.shipment.id, ">>>",
                        shipitem.shipment = shipments[0]
#                        print shipitem.shipment.id

count = 0
for shipment in newsession.query(Shipment).all():
    if len(shipment.items) == 0:
        newsession.delete(shipment)
        count += 1
print "Empty manifests:", count
print newsession.query(Shipment).count(), "A Manifests"
print newsession.query(ShipmentItem).count(), "A Manifest items"

#srec = newsession.query(Shipment).get(7897)

#print srec.__dict__
#for sitems in srec.items:
##    sitems.__dict__.pop('_sa_instance_state')
#    try:
#        sitems.__dict__.pop('invoiceitem')
#    except:
#        pass
#    sitems.__dict__.pop('shipment')
#    print sitems.__dict__
#    orec = newsession.query(Order).get(sitems.order_id)
#    print orec.product.MPN
#    print sitems.order.product.MPN


print "================================================================"
### INVOICES
print newsession.query(Invoice).count(), "B Invoices"
print newsession.query(InvoiceItem).count(), "B Invoice items"
count = 0
for invoice in newsession.query(Invoice).all():
    if len(invoice.items) == 0:
        count += 1
print "Empty manifests:", count
for invoice in newsession.query(Invoice).all():
    if invoice.invoice_no:
#        print shipment.shipment_no,
        invoices = newsession.query(Invoice).filter(Invoice.invoice_no == invoice.invoice_no).all()
        if 1 < len(invoices) < 100:
            date = invoices[0].invoicedate
            nombre = invoices[0].invoice_no
            _id = invoices[0].id

            for inv in invoices[1:]:
                # Merge invoice items if the invoice no and date are the same
                if (date == inv.invoicedate) & (nombre == inv.invoice_no):
                    for invitem in inv.items:
                        print invitem.invoice.id, ">>>",
                        invitem.invoice = invoices[0]
                        print invitem.invoice.id

count = 0
for invoice in newsession.query(Invoice).all():
    if len(invoice.items) == 0:
        newsession.delete(invoice)
        count += 1
print "Empty manifests:", count
print newsession.query(Invoice).count(), "A Invoices"
print newsession.query(InvoiceItem).count(), "A Invoice items"



#srec = newsession.query(Invoice).get(1115)
#
#print srec.__dict__
#for sitems in srec.items:
#    sitems.__dict__.pop('_sa_instance_state')
#    try:
#        sitems.__dict__.pop('shipmentitem')
#    except:
#        pass
#    sitems.__dict__.pop('invoice')
#    print sitems.__dict__
#    orec = newsession.query(Order).get(sitems.order_id)
#    print orec.product.MPN
#    print sitems.order.product.MPN
#TODO: Delete EMPTY Shipments and Invoices
newsession.commit()
print "++++++++++++++++++++++++++++++++++++"
print "           DONE PROCESSING"
print "++++++++++++++++++++++++++++++++++++"

#    ### PROCESS INVOICES
#    for i, rec in enumerate(Invoices):
#        rec = rec.__dict__


#for each in newsession.query(CoGroup).all():
#    print [br.tax_id for br in each.branches]
#
#for each in newsession.query(CoGroup).all():
#    print [br.english_name for br in each.products]

#for each in newsession.query(Order).all():
#    print each.id, "open" if each.is_open else "closed"
#    print len(each.shipments), len(each.invoices)
#print newsession.query(Order).count(), "Orders"



# Ensure each invoice is matched once
inv_matched_id = []


