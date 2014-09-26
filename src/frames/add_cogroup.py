#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Tix
import tkMessageBox

def main(_):
    # Close any other pop-up windows and open new external window.
    xwin = _.getExtWin(_, title=u'And a company (group)', destroy=True)

    group_name = Tix.StringVar()
    first_branch = Tix.StringVar()

    tv = _.loc(u'Enter the group name for all branches\nUse 2-4 characters')
    Tix.Label(xwin, textvariable=tv).grid(row=0, column=0)

    te = Tix.Entry(xwin, textvariable=group_name, width=5)
    te.grid(row=0, column=1)
    te.focus_set()

    tv = _.loc(u'Enter the first branch name\nAgain, use 2-4 characters')
    Tix.Label(xwin, textvariable=tv).grid(row=1, column=0)

    Tix.Entry(xwin, textvariable=first_branch, width=5).grid(row=1, column=1)

    Tix.Button(xwin, textvariable=_.loc(u"\u2713 Submit"),
               bg=u'lawn green', activebackground=u'lime green',
               command=lambda *args: submit()).grid(row=2, column=0, columnspan=2, sticky='ew')

    def submit():
        CG = _.dbm.CoGroup
        Branch = _.dbm.Branch

        # Test Group name uniqueness.
        if _.dbm.session.query(CG).get(group_name.get()):
            head = u'Cogroup already exists!'
            body = u'Choose a different unique name for this company group.'
            tkMessageBox.showerror(head, body)
            xwin.focus_set()
            return

        # Test branch name uniquenes.
        if _.dbm.session.query(Branch).get(first_branch.get()):
            head = u'Branch already exists!'
            body = u'Choose a different unique name for this branch.'
            tkMessageBox.showerror(head, body)
            xwin.focus_set()
            return

        # Add new group and branch.
        br = Branch(name=first_branch.get(),
                    group=group_name.get(),
                    cogroup=CG(name=group_name.get()))
        _.dbm.session.add(br)
        _.dbm.session.commit()
        xwin.destroy()
        _.refresh_colist()

        # Select new group button
        try:
            for key, val in _.colist.children.iteritems():
                try:
                    if group_name.get() in val['value']:
                        _.colist.children[key].select()
                        _.colist.children[key].invoke()
                except:
                    pass
        except TypeError:
            pass
        _.sc_switch('s')