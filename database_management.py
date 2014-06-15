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
import TM2014_tables as tables
import os  # os.walk(basedir) FOR GETTING DIR STRUCTURE
import dict_from_excel as excel
import datetime
from sqlalchemy.orm import sessionmaker

#===============================================================================
# METHODS
#===============================================================================
dbname = r'TM2014_orders.db'
with open('settings.txt', 'r') as rfile:
    base = rfile.readline()
    dbname = os.path.join(base, dbname)

print os.getcwd()
engine, metadata = tables.open_database(dbname, echo=True)
Session = sessionmaker(bind=engine)
#
session = Session()
#
#session.add()

conn = engine.connect()
purchases = tables.purchases
sales = tables.sales
companydb = metadata.tables['company']
#warehouse = tables.warehouse


def insert_purchase(ins_dict):
    global conn
    conn.execute(purchases.insert(), ins_dict)


def insert_sale(ins_dict):
    global conn
    conn.execute(sales.insert(), ins_dict)


def update_purchase(purchase_ID, ins_dict):
    global conn
    conn.execute(purchases.update(purchases.c.id == purchase_ID), ins_dict)


def update_sale(sale_ID, ins_dict):
    global conn
    conn.execute(sales.update(sales.c.id == sale_ID), ins_dict)


def delete_sale(del_id):
    global conn
    d = sales.delete().where(sales.c.id == del_id)
    conn.execute(d)

def delete_purchase(del_id):
    global conn
    d = purchases.delete().where(purchases.c.id == del_id)
    conn.execute(d)


def get_product(mpn):
    try:
        mpn = int(float(mpn))
        qres = session.query(tables.Product.product_label, tables.Product.inventory_name).filter(tables.Product.MPN==mpn).one()
#        return qres
        return qres.product_label, qres.inventory_name
    except:
        pass
    try:
        qres = session.query(tables.Product.product_label, tables.Product.inventory_name).filter(tables.Product.MPN==mpn).one()
        return qres.product_label, qres.inventory_name
    except:
        pass
    return u"<{}>".format(mpn)


def get_product_data(mpn):
    try:
        mpn = int(float(mpn))
    except:
        pass
#    try:
    return session.query(tables.Product).filter(tables.Product.MPN==mpn).one()
#    except:
#        return u"<{}>".format(mpn)


def get_products(group_id, incoming=False):
#    try
        return session.query(tables.Product).filter((tables.Product.company==group_id)
                                               & (tables.Product.discontinued==False)
                                               & (tables.Product.incoming==incoming)).all()
#    except:
#        return u"<{}>".format(mpn)


def formatrec(rec):
    outname = rec.product_label
    if not outname:
        outname = rec.inventory_name
    if rec.SKU == u'槽車':
        return u"{0} ({1})".format(outname,rec.SKU)
    else:
#        print type(rec.discontinued), type(rec.incoming), type(rec.units), rec.units.is_integer(),int(rec.units) if rec.units.is_integer() else rec.units
        this_units = int(rec.units) if rec.units.is_integer() else rec.units
        return u"{0} ({1} {2} {3})".format(outname,this_units,rec.UM,rec.SKU)

def get_product_summary(group_id, incoming=False):
    '''Returns a list of MPN's for one company'''
    group_id = group_id.decode('utf8')
    if not group_id:
        return []

    query = session.query(tables.Product).filter((tables.Product.company==group_id)
                                               & (tables.Product.discontinued==False)
                                               & (tables.Product.incoming==incoming)).all()
    return [formatrec(rec) for rec in query]


def get_branch_numbers(group_id):
    group_id = group_id.decode('utf8')
    return [u'{} ({} {})  \u260E:{},  \u263B:{}'.format(rec.fullname, rec.id, rec.tax_id.strip().strip("'"),
            rec.phone, rec.contact) for rec in session.query(tables.Company).filter(tables.Company.group_id==group_id).all()]

def get_branch_summary(group_id):
    group_id = group_id.decode('utf8')
    return [u'{}'.format(rec.id)
            for rec in session.query(tables.Company.id).filter(tables.Company.group_id==group_id).all()]

def get_branches(group_id):
    group_id = group_id.decode('utf8')
    return session.query(tables.Company).filter(tables.Company.group_id==group_id).all()


def company_list():
    return list(set([name.group_id for name in session.query(tables.Company)]))


def company_list_from_sales():
    '''Orders the list from companies with most recent entries to older entries.
    '''
    rawlist = list([name.parentcompany for name in session.query(tables.sales).order_by(tables.sales.c.orderdate)])
    outlist = []
    for each in rawlist[::-1]:
        if each not in outlist:
            outlist.append(each)
    return outlist

def company_list_from_purchases():
    '''Orders the list from companies with most recent entries to older entries.
    '''
    rawlist = list([name.parentcompany for name in session.query(tables.purchases).order_by(tables.purchases.c.orderdate)])
    outlist = []
    for each in rawlist[::-1]:
        if each not in outlist:
            outlist.append(each)
    return outlist

#def insert_warehouse(ins_dict):
#    global conn
#    conn.execute(warehouse.insert(), ins_dict)


def _corrections_():
    print 'Running corrections on database'
    with open('_check_.txt', 'w') as wf:
        query = sales.select()
        selconn = conn.execute(query)
        records = selconn.fetchall()
        for rec in records:
            if len(rec['parentcompany'].split(u',')):
                wf.write(rec['parentcompany'].encode('utf8'))
                wf.write(' , ')
                wf.write(rec['buyingcompany'].encode('utf8'))
                newnote = u'送到和鑫. ' + rec['deliverynote']
                updates = dict(deliverynote=newnote)
                updates['parentcompany'] = u'清英'
                updates['buyingcompany'] = u'清英'
                wf.write(updates['deliverynote'].encode('utf8'))
                wf.write(updates['parentcompany'].encode('utf8'))
#                wf.write(tmpget)
#                update_sale(rec['id'],updates)
                wf.write('\n')


def get_purchases(company, recent=False, thirty=True):
    start_date = datetime.date.today()-datetime.timedelta(365)
    query = purchases.select()
    query = query.where(purchases.c.parentcompany == company)
    if recent:
         query = query.where(purchases.c.orderdate >= start_date)
#    if thirty:
#         query = query.limit(30)
    query = query.order_by('orderdate')
    selconn = conn.execute(query)
    records = selconn.fetchall()
    if thirty:
        return records[-100:]
    return records

def get_purchases_2(company, recent=False, thirty=True):
    start_date = datetime.date.today()-datetime.timedelta(365)
    query = purchases.select()
    query = query.where(purchases.c.parentcompany == company)
    if recent:
         query = query.where(purchases.c.orderdate >= start_date)
#    if thirty:
#         query = query.limit(30)
    query = query.order_by('orderdate')
    selconn = conn.execute(query)
    records = selconn.fetchall()
    if thirty:
        return records[-100:]
    return records

def get_sales(company, recent=False, thirty=True):
    start_date = datetime.date.today()-datetime.timedelta(365)
    query = sales.select()
    query = query.where(sales.c.parentcompany == company)
    if recent:
         query = query.where(sales.c.orderdate >= start_date)
#    if thirty:
#         query = query.limit(30)
    query = query.order_by('orderdate')
    selconn = conn.execute(query)
    records = selconn.fetchall()
    if thirty:
        return records[-100:]
    return records

def get_record(rec_id, incoming=False):
    query = sales.select()
    query = query.where(sales.c.id == rec_id)
    if incoming:
        query = purchases.select()
        query = query.where(purchases.c.id == rec_id)
    selconn = conn.execute(query)
    record = selconn.fetchone()
    return record



#def get_warehouse():
#    selconn = conn.execute(warehouse.select())
#    records = selconn.fetchall()


def add_entries_from(filename):
    exdic = excel.open_excel(filename)[u'suppliers']
#    print exdic.keys()
    exheaders = exdic[0]
#    print exdic[1]
    for each in exdic[1:]:
        temp_dic = dict(zip(exheaders,each))
        for key in temp_dic.keys():
            if 'date' in key and not isinstance(temp_dic[key], datetime.date):
                del temp_dic[key]
        insert_purchase(temp_dic)

#exdic = excel.open_excel(r"C:\Users\Jay\SkyDrive\Documents\Taimau Docs\company_product_data.xlsx")
#prods = exdic[u'Incoming']
#prodhead = prods[0]
#prods = prods[1:]
#
#for each in prods:
#    m = dict(zip(prodhead,each))
#    print repr(m['MPN']), m['SKUpricing']
#    session.query(tables.Product).filter(tables.Product.MPN==int(m['MPN'])).update({u'SKUpricing':m['SKUpricing']})
#    session.commit()
# Run this to add initial entries from excel data
#add_entries_from(u'C:\\Users\\Jay\\SkyDrive\\Documents\\Taimau Docs\\clients_data.xlsx')
#add_entries_from(r"C:\Users\Jay\Desktop\new_suppliers_consolidated.xlsx")
#_corrections_()
