#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Tkinter as Tk
import tkMessageBox
import ttk
import tkFont
from random import randint

#TODO: Add a merge option to merge all related records for two products to the same product.
#      This will be useful if a new product is created that is identical to a discontinued product.


class Info(object):
    # Container for passing state parameters
    pass


def get_company_editor(frame,dm):
    info = Info()
    info.companySVar = {} # String Variables
    info.co_query = None # Query data for selected company
    info.listbox = Info()
    info.activeID = None
    info.activeG_ID = None
    info.dmv2 = dm


    def refresh_companies_list():
        info.listbox.IDs = []
        queryresult = info.dmv2.session.query(info.dmv2.Branch).order_by(info.dmv2.Branch.group).all()
        clist = [u"{}: {} - {}".format(c.group,c.name,c.fullname) for c in queryresult]
        info.listbox.IDs = [c.name for c in queryresult]

        info.listbox.companies.delete(0,Tk.END)
        info.listbox.companies.insert(0,*clist)


    def refresh_products_list():
        info.listbox.pIDs = []
        queryresult = info.dmv2.session.query(info.dmv2.Product).filter(info.dmv2.Product.group==info.co_query.group).order_by(info.dmv2.Product.product_label).all()
        def truncate(number):
            if float(number).is_integer():
                return int(float(number))
            return number
        alist = [u"{1} {0}{2}{0}  ({3})".format(u'\u26D4' if c.discontinued else u'',
                    u'$' if not c.is_supply else u'\u2697',
                    c.product_label if c.product_label else c.inventory_name,
                    c.inventory_name) for c in queryresult]
        clist = [u"{0}{1} {2} per {3} ({4}){0}".format(u'\u26D4' if c.discontinued else u'',
                    truncate(c.units), c.UM, c.SKU, c.SKUlong) for c in queryresult]
        info.listbox.pIDs = [c.MPN for c in queryresult]

        info.listbox.products.delete(0,Tk.END)
        info.listbox.products.insert(0,*alist)
        info.listbox.products2.delete(0,Tk.END)
        info.listbox.products2.insert(0,*clist)


    def discontinueSelection():
        activeP_ID = info.listbox.products.index(Tk.ACTIVE)
        id = info.listbox.pIDs[activeP_ID]
        query = info.dmv2.session.query(info.dmv2.Product).filter(info.dmv2.Product.MPN==id)
        q_ret = query.one()
        query.update({'discontinued': False if q_ret.discontinued else True})
        info.dmv2.session.commit()

        refresh_products_list()
        info.listbox.products.select_set(activeP_ID)
        info.listbox.products.activate(activeP_ID)


    def showrecord(id = None):
        if not id:
            id = info.activeID = info.listbox.IDs[info.listbox.companies.index(Tk.ACTIVE)]
        info.co_query = info.dmv2.session.query(info.dmv2.Branch).filter(info.dmv2.Branch.name==id).one()
        queryresult = info.co_query.__dict__
        for key in info.companySVar:
            info.companySVar[key].set(queryresult[key] if queryresult[key] and queryresult[key] != 'None' else u'')
        refresh_products_list()


    def sendupdate():
        is_confirmed = tkMessageBox.askokcancel('Confirm Data', u'Save all changes?')

        if is_confirmed:
            updates = dict([(key,info.companySVar[key].get()) for key in info.companySVar])
            info.dmv2.session.query(info.dmv2.Branch).filter(info.dmv2.Branch.name==info.activeID).update(updates)
            info.dmv2.session.commit()
            refresh_companies_list()
        else:
            info.tempWindow.focus_set()
        refresh_companies_list()


    def newcompany():
        '''Popup window asking for a permanent and unique id for new company.
        Then allow other information to be filled in normally.
        '''
        try:
            if info.tempWindow.state() == 'normal':
                info.tempWindow.focus_set()
            return
        except:
            pass

        def submit_new_id(info):
            '''Test if ID is acceptable then add to database.'''
            G_ID = info.new_gid.get()
            ID = info.new_id.get()
            if not G_ID or not ID:
                return
            if ID in info.listbox.IDs: #encoding checked
                tkMessageBox.showinfo('ID already exists!', 'Please enter a different ID name.')
                return
            is_confirmed = tkMessageBox.askokcancel('Confirm Data',
                u'''Please confirm the group and branch ID names.
                Group (parent) name: {}
                Branch (child) name: {}'''.format(G_ID, ID))

            if is_confirmed:
                info.tempWindow.destroy()
                new_co = info.dmv2.Branch(group=G_ID, name=ID)
                info.dmv2.session.add(new_co)
                info.dmv2.session.commit()
                refresh_companies_list()
                showrecord(ID)
            else:
                info.tempWindow.focus_set()

        info.tempWindow = Tk.Toplevel(width=500)
        info.tempWindow.title("Enter a unique ID")
        ttk.Label(info.tempWindow, text="Enter a group ID and branch ID.").pack()
        ttk.Label(info.tempWindow, text="Use 2 to 3 characters.").pack()
        ttk.Label(info.tempWindow, text="Group and Branch ID's can be the same.").pack()
        info.new_id = Tk.StringVar()
        info.new_gid = Tk.StringVar()
        new_gid = ttk.Entry(info.tempWindow, textvariable=info.new_gid, width=8).pack()
        new_id = ttk.Entry(info.tempWindow, textvariable=info.new_id, width=8).pack()
        Tk.Button(info.tempWindow, text="Submit ID", command=lambda:submit_new_id(info)).pack()
        info.tempWindow.focus_set()






    def scrolldrag(*args):
        info.listbox.products.yview(*args)
        info.listbox.products2.yview(*args)
    def productsdrag(*args):
        if info.listbox.products2.yview() != info.listbox.products.yview():
            info.listbox.products2.yview_moveto(args[0])
        scrollbar.set(*args)
    def products2drag(*args):
        if info.listbox.products.yview() != info.listbox.products2.yview():
            info.listbox.products.yview_moveto(args[0])
        scrollbar.set(*args)

    frameLeft = ttk.Frame(frame)
    scrollbar = Tk.Scrollbar(frameLeft, orient=Tk.VERTICAL)
    info.listbox.companies = Tk.Listbox(frameLeft, selectmode=Tk.BROWSE,
                         yscrollcommand=scrollbar.set,
                         font=("PMingLiU", "14"), width=30, exportselection=0)

    info.listbox.companies.bind("<Double-Button-1>", lambda _:showrecord())
    scrollbar.config(command=info.listbox.companies.yview)
    scrollbar.pack(side=Tk.RIGHT, fill=Tk.Y)
    info.listbox.companies.pack(side=Tk.LEFT, fill=Tk.Y)
    frameLeft.pack(side=Tk.LEFT, fill=Tk.Y, padx=2, pady=3)


    frameRTop = ttk.Frame(frame)
    fields = "group, name, fullname, english_name, tax_id, phone, fax, email, address_office, address_shipping, address_billing, note".split(', ')
    for i, each in enumerate(fields):
        info.companySVar[each] = Tk.StringVar()
        ttk.Label(frameRTop, text=each).grid(row=i,column=0)
        ttk.Entry(frameRTop, textvariable=info.companySVar[each], width=45).grid(row=i,column=1)
    Tk.Button(frameRTop, text="New Company", command=newcompany).grid(row=20,column=0)
    Tk.Button(frameRTop, text="Save Updates", command=sendupdate).grid(row=20,column=1)
    frameRTop.pack(side=Tk.TOP, fill=Tk.Y, padx=2, pady=3)


    frameRBottom = ttk.Frame(frame)
    frameSubRB = ttk.Frame(frameRBottom)
    ttk.Label(frameSubRB, text=u"\u2697=買的材料  $=賣的產品  \u26D4=停用").pack(side=Tk.BOTTOM)
    Tk.Button(frameSubRB, text="New Product", command=lambda:addProductWindow(info, refresh_products_list)).pack(side=Tk.LEFT)
    Tk.Button(frameSubRB, text="Edit Product", command=lambda:editProductWindow(info, refresh_products_list)).pack(side=Tk.LEFT)
    Tk.Button(frameSubRB, text="Discontinue", command=discontinueSelection).pack(side=Tk.LEFT)
    frameSubRB.pack(side=Tk.BOTTOM)
    scrollbar = Tk.Scrollbar(frameRBottom, orient=Tk.VERTICAL)
    scrollbar.pack(side=Tk.RIGHT, fill=Tk.Y)
    info.listbox.products = Tk.Listbox(frameRBottom, selectmode=Tk.BROWSE,
                         yscrollcommand=productsdrag,
                         font=("PMingLiU", "13"), width=24)
    info.listbox.products.pack(side=Tk.LEFT, fill=Tk.Y)
    info.listbox.products2 = Tk.Listbox(frameRBottom, selectmode=Tk.BROWSE,
                         yscrollcommand=products2drag,
                         font=("PMingLiU", "13"), width=30)
    scrollbar.config(command=scrolldrag)
    info.listbox.products2.pack(side=Tk.LEFT, fill=Tk.Y)
    frameRBottom.pack(side=Tk.LEFT, fill=Tk.Y, padx=2, pady=3)




    refresh_companies_list()
    showrecord()

def addProductWindow(info, refresh_products_list=None, group=None):
    try:
        if info.prodWin.state() == 'normal':
            info.prodWin.focus_set()
        return
    except:
        pass

    if not group:
        try:
            group = info.co_query.group
        except:
            raise Warning, "Group id not found!"
            return

    info.prodWin = Tk.Toplevel(width=500)
    info.prodWin.title(group + u" : 增加產品")

    productSVar = dict()

    used_ids = [p[0] for p in info.dmv2.session.query(info.dmv2.Product.MPN).all()]
    print used_ids
    fields = info.dmv2.Product.__table__.c.keys()
    fields = [(key, repr(info.dmv2.Product.__table__.c[key].type)) for key in fields]
    print fields

    def submit_new_product(dm,productSVar,refresh_products_list):
        #Check field entries
        new_prod = dict([(key,productSVar[key].get()) for key in productSVar])

        if not new_prod['inventory_name']:
            return
        if not new_prod['UM']:
            return
        if not new_prod['SKU']:
            return
        try:
            float(new_prod['units'])
        except:
            return
        if new_prod['is_supply'] == True:
            newMPN = u'100'
            while(newMPN in used_ids):
                newMPN = u'{}'.format(randint(100,999))
            new_prod['MPN'] = newMPN
        else: #Outgoing products have dashed MPNs
            newMPN = u'{}-{}'.format(new_prod['group'],'001')
            while(newMPN in used_ids):
                newMPN = u'{}-{}'.format(new_prod['group'],randint(100,999))
            new_prod['MPN'] = newMPN
        print repr(new_prod['MPN'])

        is_confirmed = tkMessageBox.askokcancel('Confirm Data',
            u'Add {} to items {}.'.format(new_prod['inventory_name'],
                        u'to purchase' if new_prod['is_supply'] else u'for sale'))

        if is_confirmed:
            info.prodWin.destroy()
            new_prod = info.dmv2.Product(**new_prod)
            info.dmv2.session.add(new_prod)
            info.dmv2.session.commit()
            if refresh_products_list:
                refresh_products_list()
        else:
            info.prodWin.focus_set()


    for i, field in enumerate(fields):
        if field[0] in [u'MPN',u'group',u'discontinued']:
            continue
        ttk.Label(info.prodWin, text=field[0]).grid(row=i,column=0)
        if field[1].startswith("Bool"):
            productSVar[field[0]] = Tk.BooleanVar()
            Tk.Radiobutton(info.prodWin, text="True", variable=productSVar[field[0]], value=True)\
                    .grid(row=i,column=1)
            Tk.Radiobutton(info.prodWin, text="False", variable=productSVar[field[0]], value=False)\
                    .grid(row=i,column=2)
        else:
            productSVar[field[0]] = Tk.StringVar()
            ttk.Entry(info.prodWin, textvariable=productSVar[field[0]], width=20).grid(row=i,column=1,columnspan=2)
    Tk.Button(info.prodWin, text="Submit Product", command=lambda:submit_new_product(info.dmv2,productSVar,refresh_products_list)).grid(row=99,column=0,columnspan=3)

    productSVar['MPN'] = Tk.StringVar()
    productSVar['group'] = Tk.StringVar()
    productSVar['group'].set(group)
    productSVar['discontinued'] = Tk.BooleanVar()
    productSVar['discontinued'].set(False)
    #Set boolean defaults to False
    for field in fields:
        #XXX: The GUI is not responding as expected. Need to figure out why.
        if field[1].startswith("Bool"):
            productSVar[field[0]].set(False)


def editProductWindow(info, refresh_products_list=None, group=None):
    try:
        if info.prodWin.state() == 'normal':
            info.prodWin.focus_set()
        return
    except:
        pass

    try:
        group = info.co_query.group
    except:
        raise Warning, "Group id not found!"
        return

    i = info.listbox.products.index(Tk.ACTIVE)
    pID = info.listbox.pIDs[i]
    prodvars = dict(info.dmv2.get_product(pID).__dict__)
    print ' XX prodvars', prodvars

    info.prodWin = Tk.Toplevel(width=500)
    info.prodWin.title(group + u" : 增加產品")

    productSVar = dict()

    used_ids = [p[0] for p in info.dmv2.session.query(info.dmv2.Product.MPN).all()]
    print used_ids
    fields = info.dmv2.Product.__table__.c.keys()
    fields = [(key, repr(info.dmv2.Product.__table__.c[key].type)) for key in fields]

    def submit_new_product(dm,productSVar,refresh_products_list):
        #Check field entries
        new_prod = dict([(key,productSVar[key].get()) for key in productSVar])

        if not new_prod['inventory_name'] or not new_prod['UM'] or not new_prod['SKU']:
            return

        try:
            float(new_prod['units'])
        except:
            return


        is_confirmed = tkMessageBox.askokcancel('Confirm Data',
            u'Update {} as a {}?'.format(new_prod['inventory_name'],
                        u'purchase item' if new_prod['is_supply'] else u'sale item'))
        if is_confirmed:
            info.prodWin.destroy()
            try:
                del productSVar['MPN']
            except:
                pass
            info.dmv2.session.query(info.dmv2.Product).filter(info.dmv2.Product.MPN==pID).update(new_prod)
            info.dmv2.session.commit()
            if refresh_products_list:
                refresh_products_list()
        else:
            info.prodWin.focus_set()


    for i, field in enumerate(fields):
        if field[0] in [u'MPN',u'group']:
            continue
        ttk.Label(info.prodWin, text=field[0]).grid(row=i,column=0)
        if field[1].startswith("Bool"):
            productSVar[field[0]] = Tk.BooleanVar()
            Tk.Radiobutton(info.prodWin, text="True", variable=productSVar[field[0]], value=True)\
                    .grid(row=i,column=1)
            Tk.Radiobutton(info.prodWin, text="False", variable=productSVar[field[0]], value=False)\
                    .grid(row=i,column=2)
        else:
            productSVar[field[0]] = Tk.StringVar()
            ttk.Entry(info.prodWin, textvariable=productSVar[field[0]], width=20).grid(row=i,column=1,columnspan=2)
    Tk.Button(info.prodWin, text="Submit Product", command=lambda:submit_new_product(info.dmv2,productSVar,refresh_products_list)).grid(row=99,column=0,columnspan=3)

    productSVar['MPN'] = Tk.StringVar()
    productSVar['group'] = Tk.StringVar()
    productSVar['group'].set(group)
#    if productSVar['discontinued'].get() not in [True,False]:
#        productSVar['discontinued'].set(False)
    print prodvars
    for field in fields:
        print field[0]
        productSVar[field[0]].set(prodvars[field[0]])