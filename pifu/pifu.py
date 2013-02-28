#!/usr/bin/python
# coding: utf-8

'''@file pifu.py

A program az egyes évfolyamokat ('pifu-YY') veszi sorra és elkészíti ezekben az 'index.html'-t
Feltételezi, hogy 10 lapszám van egy évben (július és augusztus nincs)

ln -sf ~/git/utils/pifu/* ~/html/iskola/ujsag

'''

from pifuTemplate import *

from os.path import getmtime, isfile, islink
from os import getcwd, chdir, waitpid, symlink
from glob import glob
from sys import argv
from subprocess import Popen

chdir('/var/www/iskola/ujsag')

FORCE = False
if '-f' in argv:
    FORCE = True

# http://codereview.stackexchange.com/questions/5091
TABLE = [['M',1000],['CM',900],['D',500],['CD',400],['C',100],['XC',90],['L',50],['XL',40],['X',10],['IX',9],['V',5],['IV',4],['I',1]]
def int_to_roman (integer):
    '''Szám árírása római számra
    @param integer Az átírandó egész szám
    '''
    parts = ''
    for letter, value in TABLE:
        while value <= integer:
            integer -= value
            parts += letter
    return parts


DIR = sorted(glob('pifu-??'))

# a menü miatt előre el kell készíteni az évfolyamlistát
evLista = ''
evListaIndex = []
for dir in DIR:
    yy = dir[-2:]
    YY = '20' + yy
    evLista += '| <a class="menu" href="../pifu-%s/index.html">%s</a>\n' % (yy, YY)
    evListaIndex += [ '<li><a href="pifu-%s/index.html"><b>%s. évfolyam - %s</b></a>' % (yy, int_to_roman(int(yy)-2), YY) ]

cwd = getcwd()
for dir in DIR:
    # csak akkor generálunk, ha változott a dir, vagy ha '-f' (pl. új évfolyam)
    if (isfile(dir+'/index.html') and getmtime(dir) <= getmtime(dir+'/index.html')) and not FORCE:
        continue
    print dir
    chdir(dir)
    if not islink('pifu.css'):
        symlink("../pifu.css", "pifu.css")
    indexFile = open ('index.html', 'w')
    yy = dir[-2:]
    evfolyam = int_to_roman(int(yy)-2)
    YY = '20' + yy
    indexFile.write ( HEAD % (YY, evLista, evfolyam, YY) )
    for pdfFile in sorted(glob('*.pdf')):
        png = pdfFile[:-3] + 'png'
        if not isfile(png):
            print 'Index-kep: ' + png
            p = Popen("../index-kep " + pdfFile, shell=True)
            waitpid(p.pid, 0)
        lapSzam = []
        mmStr = [] # a megjelenés hónapja szövegesen
        MM = pdfFile[12:-4]
        for mm in MM.split('-'): # A többes lapszámok miatt (03-04)
            honap = mm
            if yy == '03':
                honap = '%02d' % (int(mm) + 1) # 2003-ban az első szám februárban jelent meg
            mmStr += [YY + '. ' + HO[honap]]   # 03-04 -> ['2011. március', '2011. április']
            lapSzam += [str(int(mm))]          # 03-04 => ['3', '4']
        lapSzam = '-'.join(lapSzam) + '. szám' # ['3', '4'] => '3-4. szám'
        sLapSzam = '<br>'.join(mmStr) # 03-04 -> ['2011. március', '2011. április'] => '2011. március<br>2011. április'
        indexFile.write ( ENTRY % (yy, MM, lapSzam, yy, MM, YY, MM, sLapSzam) )
    indexFile.write( TAIL )
    indexFile.close()
    chdir(cwd)

f = open('index.html', 'w')
f.write( open('HEAD').read() )
f.write( '\n'.join(reversed(evListaIndex)) )
f.write( open('TAIL').read() )
