#!/usr/bin/python
# -*- coding: utf-8 -*-

'''@file video.py
VIDEOTAR.xls (csv) adatbázisba töltése
Az aktuális könyvtárba kell egy VIDEOTAR.csv, aztán
unoconv -f csv VIDEOTAR.xls
'''

import os, csv, re

# A táblázatbeli időtartam helyes értelmezéséhez
rPerc = re.compile('^\d+:\d+$')
rOra = re.compile('^\d+:\d+:\d+$')
rUres = re.compile('^\s*$')

# A táblázat mezői
# srsz;cim;szerzo;rendezo;orszag;mufaj;tema;ido;megjegyzes;tele;nyelv;hazi DVD?;lgy;;hianyzik
# 0    1   2      3       4      5     6    7   8          9    10    11        12 13 14
# 0-11, amit használunk

reader = csv.reader(open("VIDEOTAR.csv", "rb"), delimiter=',', dialect='excel', quoting=csv.QUOTE_MINIMAL)

# Az adatbázisba üres string esetén NULL (\N) kerüljön
def ures(s):
    if re.match(rUres, s): return '\\N'
    return re.sub('\n', ' ', str(s).strip())

os.system('psql -q iskola < video.sql')

# Ha debugolni akarom
# out = open('VIDEOTAR.sql', 'w')
out = os.popen ('psql -q iskola', 'w')

# Az első fejléces sor nem kell.
reader.next()

out.write ('COPY Video FROM STDIN;\n')
for sor in reader:
    sor[10] = sor[10].replace('Ft', '').replace(' ', '')

    if rPerc.search(sor[7]):
        sor[7] = '00:' + sor[7]
    if not rOra.search(sor[7]):
        sor[7] = ''

    # Ha van adat, kiírjuk a tabulátorral tagolt sort.
    if (sor[0] != ''):
        out.write('\t'.join (map(ures, sor[:12])) + '\n' )

out.write ('\\.\n')
out.close()

