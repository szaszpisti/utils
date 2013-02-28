#!/usr/bin/python
# coding: utf-8

'''@file lel.py

A Lélekváró elmélkedésehez készíti el a .hun fájlt
futtatás: cd html/irodalom/vallas/lelekvaro/20xx
../lelekvaro.py

ln -s ~/git/utils/lelekvaro.py ~/html/irodalom/vallas/lelekvaro
'''
import os, re, sys
from glob import glob

honap = {2: 'Február', 3: 'Március', 4: 'Április', 5: 'Május', 6: 'Június'}

# ha sok szóköz van a sorban -> hétköznap
reHetkoznap = re.compile(r'^(.*[^ ])    *(.*)$')
# ha '--' van benne -> vasárnap
reVasarnap  = re.compile(r'^(.* -- .*)$')
reNap = { ho: re.compile(r'^\*(%s ([0-9]+)\..*(hétfő|kedd|szerda|csütörtök|péntek|szombat|vasárnap).*)\*$' % honap[ho]) for ho in honap.keys() }

# Ha a gyökérből hívtuk meg, itt vannak az éveknek megfelelő könyvtárak
try:
    if len(sys.argv) == 2:
        ev = sys.argv[1]
    else:
        ev = sorted(glob('20??'))[-1]
    os.chdir(ev)
except IndexError:
    ev = os.path.realpath('.').split('/')[-1]

fileBase = ev + '_Lelekvaro'

## Ezzel jelezzük, hogy adott hónapban volt-e bejegyzés
honapFlag = [False]*10

## Ide gyűjtjük a kimenetet
out = []

tocTable = {}
for ho in honap.keys():
    tocTable[ho] = ['      <tr>\n        <td>%s</td>' % honap[ho] ] + ['        <td></td>']*31 + [ '      </tr>\n' ]
toc = []

prevDate = '' # előző bejegyzés dátuma, ha változik a dátum, az előzőt le kell zárni
f = open(fileBase + '.txt')
for s in f:
    nap = 0
    s = s.strip()
    # a nap-címek mind vastag betűsek
    if s and s[0] == '*':
        # minden hónapra megnézzük, hogy hónap-nap passzol-e a címre
        for ho in honap.keys():
            m = reNap[ho].match(s)
            if m:
                s = m.group(1)
                nap = int(m.group(2))
                date = '%s-%02d-%02d' % (ev, ho, nap)
                break # ha megtaláltuk, kilépünk a ciklusból

    if nap: # csak akkor nem 0, ha nap-bejegyzés
        tocTable[ho][nap] = '        <td><a href="#" onClick="mutat(\'%s\');">%d</a></td>' % (date, nap)

        # Ha ebben a hónapban még nem volt bejegyzés (új hónap), teszünk egy '<hr>'-t
        if not honapFlag[ho]: toc += [ '    </ul>\n    <hr>\n    <ul>' ]
        honapFlag[ho] = True

        if not prevDate == '': out += [ '</div><!-- %s -->\n' % prevDate ]
        out += [ '\n<div id="%s" name="%s" class="napcim"><div class="h3nap">' % (date, date) ]
        prevDate = date

        m = reHetkoznap.match(s)
        if m:
            out += [ 'H3: ' + m.group(1) + '</h3></div><div class="h3ige"><h3>' + m.group(2) ]
            tocEntry = m.group(1) + ' ' + m.group(2)

        m = reVasarnap.match(s)
        if m:
            out += [ 'H3: ' + s ]
            tocEntry = s

        out += [ '</div><div class="spacer"></div>' ]
        toc += [ '      <li><a href="#%s">%s</a></li>' % (date, tocEntry) ]

    else:
        out += [ s ]

out += [ '</div><!-- %s -->' % prevDate ]
open(fileBase + '.hun', 'w').write ( '\n'.join(out) + '\n' )

p = os.path.join
def link(f, to):
    if not os.path.islink(to):
        os.symlink(f, to)

# a HEAD elkészítése: H1 + tocTable + H2 + toc
HEAD = open('HEAD', 'wb')
HEAD.write(open(p('..', 'H1')).read() % {'ev': ev})
for ho in sorted(tocTable.keys()):
    if honapFlag[ho]: HEAD.write('\n'.join(tocTable[ho]))
HEAD.write(open(p('..', 'H2')).read() % {'ev': ev})
HEAD.write('  <div id="toc" class="noprint">\n    <ul>\n' + '\n'.join(toc) + '\n    </ul>\n  </div><!-- end of toc -->')
HEAD.close()

link(p('..', 'TAIL'), 'TAIL')
os.system('htgen ' + fileBase + '.hun')

# ln -s 20xx/20xx_Lelekvaro.html ../20xx_lelekvaro.html
link(p(ev, fileBase + '.html'), p('..', fileBase + '.html'))

