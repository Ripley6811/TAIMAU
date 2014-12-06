#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Tix


def main(_, br_name):
    """Edit or view a branches information."""
    branch = _.dbm.session.query(_.dbm.Branch).get(br_name)
    fields = _.dbm.Branch.__table__.columns.keys()
#    if not branch:
#        return False

    # Create new external window.
    if not _.getExtWin(_, co_name=_.curr.cogroup.name,
                       title=u"EDIT"):
        return

    mf = Tix.Frame(_.extwin)
    mf.pack(side='left', fill='both')


    print 'FIELDS:', repr(fields)
    tv_entry = []
    for field in fields:
        le = Tix.LabelEntry(mf, labelside='left')
        le.label.configure(text=field, anchor='center')
        tv_entry.append(Tix.StringVar())
        tv_entry[-1].set( branch.__dict__[field] )
        le.entry.configure(textvariable=tv_entry[-1])
        le.pack(side='top', fill='both')