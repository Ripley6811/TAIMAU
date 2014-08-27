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
:SINCE: Tue Aug 26 19:02:13 2014
:VERSION: 0.1
"""
#===============================================================================
# PROGRAM METADATA
#===============================================================================
__author__ = 'Ripley6811'
__contact__ = 'python@boun.cr'
__copyright__ = ''
__license__ = ''
__date__ = 'Tue Aug 26 19:02:13 2014'
__version__ = '0.1'

#===============================================================================
# IMPORT STATEMENTS
#===============================================================================
import Tix

#===============================================================================
# METHODS
#===============================================================================






#===============================================================================
# MAIN METHOD AND TESTING AREA
#===============================================================================
def create(_):
    """Creates the main purchase and sale window in the supplied frame."""
    _.curr_company = None
    _.edit_ID = None
    _.listbox = type(_)()
    _.poF = type(_)()
#    _state.settings.font = "NSimSun"#"PMingLiU"

    #-------
    def manage_companies():
        # If window already open then set focus.
        try:
            if info.co_select.state() == 'normal':
                info.co_select.focus_set()
            return
        except:
            pass

        info.co_select = Tix.Toplevel(width=1200, height=600)
        info.co_select.title(_.loc(u"Manage List"))

        grouplist = info.dmv2.cogroups()
        ROWperCOL = 25
        wlist = {}
        for i, group in enumerate(grouplist):
            # Show company group name and additional branches.
            branchlist = [br.name for br in group.branches]
            try:
                branchlist.remove(group.name)
            except ValueError as e:
                print e
            text = u'          {}'.format(group.name)
            if len(branchlist):
                text += u' ({})'.format(u', '.join(branchlist))
            tl = Tix.Label(info.co_select, text=text)
            tl.grid(row=i%ROWperCOL, column=2*(i/ROWperCOL))

            # 'Supplier' and 'Customer' switches.
            # Not using 'Select' label option in order to keep things aligned.
            selectParams = dict(
                radio=False,
                allowzero=True,
                selectedbg=u'cyan',
            )
            tsel = Tix.Select(info.co_select, **selectParams)
            tsel.add(u's', text=u'Supplier')
            tsel.add(u'c', text=u'Customer')
            tsel.grid(row=i%ROWperCOL, column=2*(i/ROWperCOL)+1)

            # Activate buttons according to database records.
            if group.is_supplier:
                tsel.invoke(u's')
            if group.is_customer:
                tsel.invoke(u'c')

            # Add 'Select' widget to widget list
            wlist[group.name] = tsel
            print group.is_supplier,  group.is_customer

        tb = Tix.Button(info.co_select, text=u'提交改變', bg=u'light salmon')
        def submit():
            session = info.dmv2.session
            CG = info.dmv2.CoGroup
            for coname, tsel in wlist.iteritems():
                updates = dict(
                    is_supplier= u's' in tsel['value'],
                    is_customer= u'c' in tsel['value'],
                )
                print updates
                session.query(CG).filter_by(name=coname).update(updates)
                session.commit()
            info.co_select.destroy()
        tb['command'] = submit
        tb.grid(row=100, columnspan=20)


    left_pane = Tix.Frame(_.po_frame)


    # Set up mode switching buttons: Purchases, Sales
    def ps_switch(mode):
        print mode
        _.ps_mode = mode
        for each_butt in cog_butts:
            if "{}1".format(mode) in each_butt["value"]:
                each_butt.configure(bg='burlywood')
            else:
                each_butt.configure(bg='NavajoWhite4')



    modebox = Tix.Frame(left_pane)
    options = dict(variable="modebuttons", indicatoron=False,
                   bg="NavajoWhite4", font=(_.font, "15", "bold"),
                   selectcolor="light sky blue",
                   activebackground="light sky blue")
    tr = Tix.Radiobutton(modebox, value="s", textvariable=_.loc("Purchases"),
                         command=lambda:ps_switch("p"), **options)
    tr.pack(side=Tix.LEFT, expand=True, fill=Tix.X)
#    tr.invoke()
    tr = Tix.Radiobutton(modebox, value="p", textvariable=_.loc("Sales"),
                         command=lambda:ps_switch("s"), **options)
    tr.pack(side=Tix.RIGHT, expand=True, fill=Tix.X)
    modebox.pack(side=Tix.TOP, fill=Tix.X)

    b = Tix.Button(left_pane, textvariable=_.loc(u"Manage List"))
    b['command'] = manage_companies
    b.pack(side=Tix.BOTTOM, fill=Tix.X)


    # Set up company switching buttons
    def select_cogroup(cogroup):
        _.curr.cogroup = cogroup
        if _.debug: print(cogroup)


    cogroups = _.dbm.cogroups()

    colist_frame = Tix.Frame(left_pane)
    options = dict(variable="companybuttons", indicatoron=False,
                   font=(_.font, "12", "bold"), bg="burlywood",
                   selectcolor="gold",
                   activebackground="gold")
    cog_butts = []
    for i, cog in enumerate(cogroups):
        print(i, cog.name)
        tr = Tix.Radiobutton(colist_frame, text=cog.name, value=u"s{}p{} {}".format(int(cog.is_supplier), int(cog.is_customer), cog.name),
                             command=lambda x=cog:select_cogroup(x),
                             **options)
        #TODO: color by supplier/client
        tr.grid(row=i/4,column=i%4, sticky=Tix.W+Tix.E)
        cog_butts.append(tr)
    colist_frame.pack(side=Tix.LEFT, fill=Tix.BOTH)

#    if src == u'Sales':
#        companies = [cg.name for cg in cogroups if cg.is_customer]
#    else:
#        companies = [cg.name for cg in cogroups if cg.is_supplier]
#    for i, each in enumerate(companies):
#        info.listbox.companies.insert(i, each)
#        info.listbox.companies.itemconfig(i, bg=u'seashell2',
#                                          selectbackground=u'maroon4')

    left_pane.pack(side=Tix.LEFT, fill=Tix.Y, padx=2, pady=3)

    #==========================================================================
    # SET UP TABBED SECTIONS
    #==========================================================================
#    info.record = {}
#    nb = tTix.Notebook(frame)
#    #--------------- Overview of database ---------------------
#    frame = Tix.Frame(nb)
#    frame_overview.create_frame(frame, info)
#    nb.add(frame, text=u'概貌', padding=2)
#    #--------------- Order entry tab -----------------------
#    frame = ttk.Frame(nb)
#    frame_order_entry.make_order_entry_frame(frame, info)
#    nb.add(frame, text=u'訂單 (造出貨單)', padding=2)
#
#    #------------------ Manifest tab ----------------------------
#    frame = ttk.Frame(nb)
#    frame_manifest.create_manifest_frame(frame, info)
#    nb.add(frame, text=u'出貨單 (造發票)', padding=2)
#    #------------------ Invoice tab -----------------------------
#    frame = ttk.Frame(nb)
#    frame_payment.set_invoice_frame(frame, info)
#    nb.add(frame, text=u'發票 (已支付?)', padding=2)
#    #------------------ Pack notebook ----------------------------
#    nb.pack(side=Tix.RIGHT, fill=Tix.BOTH, expand=Tix.Y, padx=2, pady=3)








if __name__ == '__main__':
    pass

