#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Calendar widget build with Tix (or Tk) Buttons.

Based on ttk Treeview calendar but with improvements in pre-setting date and
integration into other applications. Uses Tix if available for import or else
uses Tkinter.

If selectrange is set to True then a range of dates can be selected by holding
ctrl or shift or the right mouse button while clicking the left mouse button.

:REQUIRES:
    - Tix or Tkinter

:TODO:
    - Solve Chinese localization month name encoding problem.

:AUTHOR: Ripley6811
:SINCE: Tue Dec 16 16:29:56 2014
:VERSION: 0.1
"""
#===============================================================================
# PROGRAM METADATA
#===============================================================================
__author__ = 'Ripley6811'
__copyright__ = ''
__license__ = ''
__date__ = 'Tue Dec 16 16:29:56 2014'
__version__ = '0.1'

#===============================================================================
# IMPORT STATEMENTS
#===============================================================================
try:
    import Tix as TKx
except ImportError:
    import Tkinter as TKx
import calendar
#XXX: Encoding problem on Chinese system. Will not display Chinese months.
#XXX: Using English of numbered months for now.
#import locale
#locale.setlocale(locale.LC_ALL, '')



class Calendar(TKx.Frame):
    datetime = calendar.datetime.date
    timedelta = calendar.datetime.timedelta
    today = datetime.today()
    range = []

    def __init__(self, master=None, **kw):
        """Setup.

        Display defaults to system current month and year.

        Kwargs:
            year (int): Year integer for displaying year.
            month (int): Month integer for displaying month.
            day (int): Day integer used for preselecting date.
            settoday (bool): Set selection to today.
            selectbackground (str): Color string for selection background.
            textvariable (StringVar): Tk.StringVar for storing selection date.
            preweeks (int): Number of weeks to include before month.
            postweeks (int): Number of weeks to include after month.
            selectrange (bool): True to return dates as a range pair.
        """

        # remove custom options from kw before initializating ttk.Frame
        today = self.datetime.today()
        self.year = kw.pop('year', today.year)
        self.month = kw.pop('month', today.month)
        self.day = kw.pop('day', None)
        self.settoday = kw.pop('settoday', False)
        self.sel_bg = kw.pop('selectbackground', 'gold')
        self.preweeks = kw.pop('preweeks', 0)
        self.postweeks = kw.pop('postweeks', 0)
        self.userange = kw.pop('selectrange', False)

        # StringVar parameter for returning a date selection.
        self.strvar = kw.pop('textvariable', TKx.StringVar())

        TKx.Frame.__init__(self, master, **kw)

        self._cal = calendar.Calendar(calendar.SUNDAY)


        # Insert dates in the currently empty calendar
        self._build_calendar()

        if self.settoday:
            self.date_set(today)
        elif self.day:
            self.date_set(self.year, self.month, self.day)

        self._build_dategrid()


    def _build_calendar(self):
        # Create frame and widgets.
        # Add header.
        hframe = TKx.Frame(self)
        hframe.pack(fill='x', expand=1)
        self.month_str = TKx.StringVar()
        lbtn = TKx.Button(hframe, text=u'\u25c0', command=self._prev_month)
        rbtn = TKx.Button(hframe, text=u'\u25b6', command=self._next_month)
        lbtn.pack(side='left')
        rbtn.pack(side='right')
        tl = TKx.Label(hframe, textvariable=self.month_str)
        tl.pack(side='top')
        self._set_month_str()
        self.days_frame = TKx.Frame(self)
        self.days_frame.pack(fill='x', expand=1)

    def _set_month_str(self):
        #TODO: Fix month name encoding error on Chinese system when localizing.
        text = u'{} {}'.format(calendar.month_name[self.month], self.year)
        self.month_str.set(text)

    def _edit_range(self, event, date):
        #8 normal, 12 held ctrl, 1032 held B3
        if len(self.range) < 2:
            self.range = date, date
            return
        if event.state in (9, 12, 1032):
            self.range = self.range[1], date
        else:
            self.range = date, date
#        start, end = [str(d) for d in sorted(self.range)]
        self._color_buttons()
#        for child in self.days_frame.winfo_children()[7:]:
#            if start <= child['value'] <= end:
#                child['bg'] = self.sel_bg

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
            tl = TKx.Label(self.days_frame, text=text[:2])
            tl.grid(row=0, column=(col+1)%7, sticky='nsew')
        for row, week in enumerate(datematrix):
            for col, day in enumerate(week):
                trb = TKx.Radiobutton(self.days_frame,
                                      text=day.day,
                                      padx=4,
                                      indicator=False,
                                      variable=self.strvar,
                                      value=day)
                trb.grid(row=row + 1, column=col, sticky='nsew')
                self.days_frame.columnconfigure(col, weight=1)
                if self.sel_bg:
                    trb.config(selectcolor=self.sel_bg)
                if self.userange:
                    trb.bind('<1>', lambda e,x=day: self._edit_range(e,x))
        self._color_buttons()

    def _color_buttons(self):
        try:
            start, end = [str(d) for d in sorted(self.range)]
        except:
            start, end = 0,0

        for child in self.days_frame.winfo_children()[7:]:
            month = int(child['value'].split('-')[1])
            if abs(month - self.month) == 0:
                child.config(bg='grey99')
            if abs(month - self.month) in (1,11):
                child.config(bg='grey77')
            if abs(month - self.month) in (2,10):
                child.config(bg='grey55')
            if 3 <= abs(month - self.month) <= 9:
                child.config(bg='grey33')
            if start <= child['value'] <= end:
                child['bg'] = self.sel_bg


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

    def date_set(self, *args):
        """Set the current selected date.

        Args should either be a single datetime.date object or a
        list of three integers, [year, month, day].
        No args sets current date to None.

        Args:
            datetime.date: A date to set as selected.
            [int, int, int]: Three integers for year, month and day.

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
            self.range = args[0], args[0]
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
                self.range = tmpdate, tmpdate
                self.strvar.set(tmpdate)
                if args[1] != self.month or args[0] != self.year:
                    self.year = args[0]
                    self.month = args[1]
                    self._build_dategrid()
            except TypeError:
                pass
            return

    @property
    def date_str(self):
        """Get string representation of selected date.

        Format is YYYY-MM-DD or an empty string if nothing is selected.
        """
        if self.userange:
            return [str(d) for d in sorted(self.range)]
        return self.strvar.get()

    @property
    def date_obj(self):
        """Get a datetime.date object of selected date.

        Returns a datetime.date object or None if nothing is selected.
        """
        if self.userange:
            return sorted(self.range)
        try:
            return self.datetime(*[int(x) for x in self.date_str.split(u'-')])
        except ValueError:
            return None

def test():
    import sys
    root = TKx.Tk()
    root.title('Calendar')
    tixcal = Calendar(preweeks=6, postweeks=8, day=23)
    tixcal.pack(expand=1, fill='both')

    if 'win' not in sys.platform:
        style = TKx.Style()
        style.theme_use('clam')

    print type(tixcal.date_str), tixcal.date_str
    print type(tixcal.date_obj), tixcal.date_obj


    tixcal = Calendar(preweeks=6, postweeks=8)

    print type(tixcal.date_str), tixcal.date_str
    print type(tixcal.date_obj), tixcal.date_obj
    root.mainloop()


if __name__ == '__main__':
    test()