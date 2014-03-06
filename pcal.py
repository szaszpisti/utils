#!/usr/bin/python3

import locale, datetime
locale.setlocale(locale.LC_ALL, 'hu_HU.UTF-8')

import calendar
out = calendar.calendar(datetime.datetime.now().year)
out = out.replace('h  k  sz cs p  sz v ', ' h  k sz cs  p sz  v')
out = out.replace('h  k  sz cs p  sz v\n', ' h  k sz cs  p sz  v\n')

print(out)
