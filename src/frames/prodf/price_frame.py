#!/usr/bin/env python
# -*- coding: utf-8 -*-
import Tix
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler

from matplotlib.figure import Figure
from numpy import transpose


def main(_):
    '''

    _ = state information object. See "main.py".
    '''

    _.product_price = Tix.Frame(_.product_frame)
    mainf = Tix.Frame(_.product_price)
    mainf.pack()

    labellist = Tix.Frame(mainf)
    labellist.pack(side='left', fill='y', expand=1)
    Tix.Label(labellist, textvariable=_.loc(u'Price Changes')).pack(side='top')
    lb = Tix.Listbox(master=labellist, font=(_.font, 14))
    lb.pack(side='top', fill='y', expand=1)
    tb = Tix.Button(labellist, textvariable=_.loc(u'Show All Similar Products'),
               command=lambda:show_all_companies(),
                bg='lawn green',
                activebackground="lime green")
    tb.pack(side='top', fill='x')


    f = Figure(figsize=(10,6), dpi=100, facecolor=u'white')
    # Adjust margins
    f.subplots_adjust(left=0.05, right=0.9, top=0.95, bottom=0.1)
    # a tk.DrawingArea
    canvas = FigureCanvasTkAgg(f, master=mainf)
    # Add toolbar first so that it isn't pushed off view by plot.
    toolbar = NavigationToolbar2TkAgg( canvas, mainf )
    toolbar.update()
    canvas._tkcanvas.pack(side='top', fill='both', expand=1)
    canvas.show()
    # Add plot window
    canvas.get_tk_widget().pack(side='left', fill='both', expand=1)



    def refresh():
        try:
            for ax in f.axes:
                f.delaxes(ax)
        except:
            pass
        try:
            _.curr.product.MPN
        except:
            return

        Order = _.dbm.Order
        cprod = _.curr.product
        query = _.dbm.session.query(Order.orderdate, Order.price)
        query = query.filter_by(MPN=cprod.MPN)
        query = query.order_by('orderdate')
        qresults = query.all()

        lb.delete(0, 'end')
        last_price = -1.
        for each in qresults:
            if each[1] != last_price:
                lb.insert('end', u'{}  ${:>3}'.format(*each))
                last_price = each[1]

        try:
            dates, prices = transpose(qresults)
        except ValueError:
            dates, prices = [], []

        a = f.add_subplot(111)
        a.plot(dates, prices, 'yo-')
        a.yaxis.tick_right()
        a.grid()
        f.autofmt_xdate()
        canvas.draw()


        def on_key_event(event):
            print('you pressed %s'%event.key)
            key_press_handler(event, canvas, toolbar)

        canvas.mpl_connect('key_press_event', on_key_event)

    def show_all_companies():
        try:
            for ax in f.axes:
                f.delaxes(ax)
        except:
            pass
        try:
            _.curr.product.MPN
        except:
            return

        Order = _.dbm.Order
        Prod = _.dbm.Product
        cprod = _.curr.product
        query = _.dbm.session.query(Order.group, Order.orderdate, Order.price, Order.is_purchase)
        query = query.join(Prod)
        query = query.filter_by(inventory_name = cprod.inventory_name)
        query = query.order_by('orderdate')
        qresults = query.all()


        a = f.add_subplot(111)


        last_co = None
        is_supply = None
        x = []
        y = []
        for each in sorted(qresults):
            print each
            if each[0] != last_co:
                #plot last batch if exists
                if last_co and x:
                    print len(x), len(y)
                    if last_co == _.curr.product.group:
                        lw=3.0
                    else:
                        lw=2.0
                    a.plot(x, y, '--' if is_supply else '-', linewidth=lw, label=last_co)

                last_co = each[0]
                is_supply = each[3]
                x = [each[1]]
                y = [each[2]]
            else:
                x.append(each[1])
                y.append(each[2])
        else:
            if last_co and x:
                print len(x), len(y)
                if last_co == _.curr.product.group:
                    lw=3.0
                else:
                    lw=2.0
                a.plot(x, y, '--' if is_supply else '-', linewidth=lw, label=last_co)

        a.yaxis.tick_right()
        a.grid()
        matplotlib.rcParams['font.sans-serif'] = ['SimHei']
        a.legend(loc='upper left')
        f.autofmt_xdate()
        canvas.draw()


    _.product_price.refresh = refresh
    try:
        _.refresh.append(refresh)
    except KeyError:
        _.refresh = [refresh,]