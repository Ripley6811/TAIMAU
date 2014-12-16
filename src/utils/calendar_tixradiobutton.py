#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Calendar widget build with Tix Buttons.

Based on ttk Treeview calendar but with improvements in pre-setting date and
integration into other applications.

:REQUIRES:

:TODO:

:AUTHOR: Ripley6811
:ORGANIZATION: None
:CONTACT: python@boun.cr
:SINCE: Tue Dec 16 16:29:56 2014
:VERSION: 0.1
"""
#===============================================================================
# PROGRAM METADATA
#===============================================================================
__author__ = 'Ripley6811'
__contact__ = 'python@boun.cr'
__copyright__ = ''
__license__ = ''
__date__ = 'Tue Dec 16 16:29:56 2014'
__version__ = '0.1'

#===============================================================================
# IMPORT STATEMENTS
#===============================================================================
import Tix
import calendar
import locale
locale.setlocale(locale.LC_ALL, '')



class Calendar(Tix.Frame):
    datetime = calendar.datetime.date
    timedelta = calendar.datetime.timedelta
    today = datetime.today()

    def __init__(self, master=None, **kw):
        """Setup.

        Date defaults to system current date.

        Kwargs:
            year (int): Year integer.
            month (int): Month integer.
            day (int): Day integer.
            today (bool): Select today's date.
            selectbackground (str): Color string for background.
            selectforeground (str): Color string for text.
            textvariable (StringVar): Tk.StringVar for storing selection date.
            preweeks (int): Number of weeks to include before month.
            postweeks (int): Number of weeks to include after month.
        """

        # remove custom options from kw before initializating ttk.Frame
        today = self.datetime.today()
        self.year = kw.pop('year', today.year)
        self.month = kw.pop('month', today.month)
        self.day = kw.pop('day', None)
        self.settoday = kw.pop('settoday', False)
        self.sel_bg = kw.pop('selectbackground', 'gold')
        self.sel_fg = kw.pop('selectforeground', 'gold')
        self.preweeks = kw.pop('preweeks', 0)
        self.postweeks = kw.pop('postweeks', 0)

        # StringVar parameter for returning a date selection.
        self.strvar = kw.pop('textvariable', Tix.StringVar())

        Tix.Frame.__init__(self, master, **kw)

        self._cal = calendar.Calendar(calendar.SUNDAY)


        # Insert dates in the currently empty calendar
        self._build_calendar()

        if self.settoday:
            self.selection_set(today)
        elif self.day:
            self.selection_set(self.year, self.month, self.day)

        self._build_dategrid()



    def _build_calendar(self):
        # Create frame and widgets.
        # Add header.
        hframe = Tix.Frame(self)
        hframe.pack(fill='x', expand=1)
        self.month_str = Tix.StringVar()
        lbtn = Tix.Button(hframe, text=u'\u25c0', command=self._prev_month)
        rbtn = Tix.Button(hframe, text=u'\u25b6', command=self._next_month)
        lbtn.pack(side='left')
        rbtn.pack(side='right')
        tl = Tix.Label(hframe, textvariable=self.month_str)
        tl.pack(side='top')
        self._set_month_str()
        self.days_frame = Tix.Frame(self)
        self.days_frame.pack(fill='x', expand=1)

    def _set_month_str(self):
        text = u'{} {}'.format(calendar.month_name[self.month], self.year)
        self.month_str.set(text)



    def _build_dategrid(self):
        self._set_month_str()
        # Prepare data.
        datematrix = self._cal.monthdatescalendar(self.year, self.month)
        for i in range(self.postweeks + 6 - len(datematrix)):
            # Get first day in list.
            d = datematrix[-1][-1]
            # Add a list of seven days prior to first in datematrix.
            datematrix.append([d + self.timedelta(x) for x in range(1,8)])
        for i in range(self.preweeks):
            # Get first day in list.
            d = datematrix[0][0]
            # Add a list of seven days prior to first in datematrix.
            datematrix.insert(0, [d - self.timedelta(x) for x in range(7,0,-1)])

        # Clear out date frame.
        for child in self.days_frame.winfo_children():
            child.destroy()

        # Add day headers and day radiobuttons.
        for col, text in enumerate(calendar.day_abbr):
            tl = Tix.Label(self.days_frame, text=text[:2])
            tl.grid(row=0, column=(col+1)%7, sticky='nsew')
        for row, week in enumerate(datematrix):
            for col, day in enumerate(week):
                trb = Tix.Radiobutton(self.days_frame,
                                      text=day.day,
                                      padx=4,
                                      indicator=False,
                                      variable=self.strvar,
                                      value=day)
                trb.grid(row=row + 1, column=col, sticky='nsew')
                self.days_frame.columnconfigure(col, weight=1)
                if day.month != self.month:
                    trb.config(bg='grey')
                if self.sel_bg:
                    trb.config(selectcolor=self.sel_bg)

    @property
    def selection(self):
        return self.strvar.get()

    def selection_set(self, *args):
        """Set the current selected date.

        Args should either be a single datetime.date object or a
        list of three integers, [year, month, day].
        No args sets current date to None.

        Args:
            dt (datetime.date) A date to set as selected.
        """
        if len(args) == 0:
            """
            No arguments sets date to None.
            """
            self.strvar.set(None)
            return
        elif isinstance(args[0], self.datetime):
            """
            Date entered as datetime.date object.
            """
            self.strvar.set(args[0])
            if args[0].month != self.month or args[0].year != self.year:
                self.year = args[0].year
                self.month = args[0].month
                self._build_dategrid()
            return
        elif isinstance(args[0], int) and len(args) == 3:
            """
            Date entered as three integers; [year, month, day].
            """
            try:
                tmpdate = self.datetime(args[0], args[1], args[2])
                self.strvar.set(tmpdate)
                if args[1] != self.month or args[0] != self.year:
                    self.year = args[0]
                    self.month = args[1]
                    self._build_dategrid()
            except TypeError:
                pass
            return

    def _prev_month(self):
        tmp = self.datetime(self.year, self.month, 1)
        prev_month = tmp - self.timedelta(1)
        self.year = prev_month.year
        self.month = prev_month.month
        self._build_dategrid()

    def _next_month(self):
        tmp = self.datetime(self.year, self.month, 25)
        next_month = tmp + self.timedelta(10)
        self.year = next_month.year
        self.month = next_month.month
        self._build_dategrid()


def test():
    import sys
    root = Tix.Tk()
    root.title('Tix Calendar')
    tixcal = Calendar(preweeks=3, postweeks=3)
    tixcal.pack(expand=1, fill='both')

    if 'win' not in sys.platform:
        style = Tix.Style()
        style.theme_use('clam')

    root.mainloop()

if __name__ == '__main__':
    test()