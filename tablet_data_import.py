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
:SINCE: Wed May 07 20:16:54 2014
:VERSION: 0.1
"""
#===============================================================================
# PROGRAM METADATA
#===============================================================================
__author__ = 'Ripley6811'
__contact__ = 'python@boun.cr'
__copyright__ = ''
__license__ = ''
__date__ = 'Wed May 07 20:16:54 2014'
__version__ = '0.1'

#===============================================================================
# IMPORT STATEMENTS
#===============================================================================
import tkMessageBox
import collections
import datetime
import os

google_connected = False
try:
    import gdata.docs.service
    import gdata.spreadsheet.service
    import gdata.spreadsheet.text_db
    google_connected = True
except ImportError:
    print(u"Failed to import gdata module.")

import sqlalchemy as sqla
from sqlalchemy.orm import relationship as rel
from sqlalchemy.orm import backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Int = sqla.Integer
Utf = sqla.Unicode
Float = sqla.Float
Col = sqla.Column
Bool = sqla.Boolean
Date = sqla.Date
Time = sqla.Time
DateTime = sqla.DateTime
ForeignKey = sqla.ForeignKey


Base = declarative_base()


class AppRecord(Base): # Information for each unique product (including packaging)
    __tablename__ = 'apprecord'

    product = Col(Utf, nullable=False)
    supervisor = Col(Utf)
    recordtype = Col(Utf, nullable=False)
    packer = Col(Utf)
    lottype = Col(Utf, nullable=False)
    mixer = Col(Utf)
    qty = Col(Int)
    um = Col(Utf)
    specificgravity = Col(Utf)
    materials = Col(Utf)
    recordtimestamp = Col(Utf, primary_key=True)
    time = Col(Time)
    date = Col(Date, nullable=False)
    concentration = Col(Utf)
    recordsignee = Col(Utf)
    recordnote = Col(Utf)

    def __repr__(self):
        retval = self.__dict__
#        if retval.get('_sa_instance_state') != None:
#            del retval['_sa_instance_state']
        return repr(retval)

def get_database(filename, echo=False):
    database = sqla.create_engine('sqlite:///'+filename, echo=echo)
    Base.metadata.create_all(database)   #FIRST TIME SETUP ONLY
    return database

#===============================================================================
# METHODS
#===============================================================================
#class Settings(object):pass
settings = type('Settings', (), {})()

settings.dbname = u'TM2014_appdata.db'

with open('settings.txt', 'r') as rfile:
    settings.base = rfile.readline().strip()
    settings.email = rfile.readline().strip()
    settings.password = rfile.readline().strip()
    settings.app_data_key = rfile.readline().strip()
    settings.dbname = os.path.join(settings.base, settings.dbname)

engine = get_database(settings.dbname, echo=True)

session = sessionmaker(bind=engine)()



def pull_app_data():
    '''Downloads record data from google spreadsheet and adds to local
    database if the primary_key ("recordtimestamp") is not found.
    '''

    service = gdata.spreadsheet.service.SpreadsheetsService()
    service.email = settings.email
    service.password = settings.password
    service.ProgrammaticLogin()

    sheet = {} # Mapping from sheet name to sheet id
    for ws in service.GetWorksheetsFeed(settings.app_data_key).entry:
        title = ws.title.text.decode('utf8')
        ws_id = ws.id.text.rsplit('/', 1)[1] # Key of the sheet
        sheet[ title ] = ws_id

#    print sheet

    records = {}

    list_feed = service.GetListFeed(settings.app_data_key, sheet['Form Responses'])
#    print len(list_feed.entry)
    for entry in list_feed.entry:
        row = gdata.spreadsheet.text_db.Record(row_entry=entry).content
#        print [unicode(h) for h in row.keys()]
        del row['timestamp'] # Worthless information (time of upload from tablet).

        records[row['recordtimestamp']] = row



    # Convert record dictionary into list of records
    records = [records[key] for key in sorted(records.keys())]
    for record in records:
        try:
            record['qty'] = int(record['qty'])
        except:
            record['qty'] = -1
        d = record['date']
        record['date'] = datetime.date(int(d[1:5]),int(d[6:8]),int(d[9:11]))
        if record['time']:
            t = record['time']
#            print record['date'], t,
            record['time'] = datetime.time(int(t[-4:-2]), int(t[-2:]))
#        print record['date'], record['time']
        if session.query(AppRecord).get(record['recordtimestamp']) == None:
            session.add(AppRecord(**record))

    session.commit()
if not google_connected:
    tkMessageBox.showerror(u'gdata import error',u'Could not connect to Google Spreadsheet data.')

def main():
    records = session.query(AppRecord).order_by('date').all()
    for rec in records:
        print rec.lottype, rec.date, rec.qty
    print settings.__dict__


if __name__ == '__main__':
    pull_app_data()
    main()



#===============================================================================
# QUICK REFERENCE
#===============================================================================
'''Templates and markup notes

>>SPYDER Note markers
    #XXX: !
    #TODO: ?
    #FIXME: ?
    #HINT: !
    #TIP: !

'''
