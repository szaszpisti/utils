#!/usr/bin/python
# coding: utf-8
# ~/bin/korlevel.py

'''@file korlevel.py
Sablon és adatbázis (csv) alapján kör-emailt küld.

ln -s ~/git/utils/korlevel.py ~/bin/korlevel
'''

import os, sys
import csv, getopt, smtplib, yaml
import email.header, email.utils, email.mime.text

import smtplib

import mimetypes
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import charset

reload(sys)
sys.setdefaultencoding( "utf-8" )

# specify quoted-printable instead of base64
charset.CHARSETS['utf-8'] = ( charset.QP, charset.QP, 'utf-8' )

confFile = 'korlevel.ini'
prog = sys.argv[0]

def Exit(msg=None, exitcode=1):
    if msg: print msg
    sys.exit(exitcode)

def usage(msg=None, exitcode=1):
    if msg: print msg
    print 'Usage: %s [-d|--debug] [-h|--help] [-g|--gen] [dir]' % prog
    print '   dir - a könyvtárban kell legyen korlevel.ini'
    print '   -h|--help    ez a súgó'
    print '   -g|--gen     az adott könyvtárba ír egy default korlevel.ini fájlt'
    print '   -d|--debug   nem küld levelet, hanem a ("debug") könyvtárba írja fájlokba'
    sys.exit(exitcode)

def send(debug, From, To, Subject, Content, pdf=None):

    # RFC 2822 fejléc-mező ("Subject: =?iso-8859-1?q?p=F6stal?=")
    u = lambda text: email.header.Header(text.decode('utf-8')).encode()

    # Az utf-8 email cimből levélben küldhető mezőt állítunk elő
    emil = email.utils.parseaddr(From)
    From = '%s <%s>' % (u(emil[0]), emil[1])
    emil = email.utils.parseaddr(To)
    To = '%s <%s>' % (u(emil[0]), emil[1])
    debugFile = emil[1]


    if pdf:
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from email.mime.application import MIMEApplication
        msg = MIMEMultipart()
        msg['From'], msg['To'], msg['Subject'] = From, To, Subject

        body = MIMEText(Content, 'plain', 'utf-8')
#        body = MIMEText(Content)
        msg.attach(body)

        pdfPart = MIMEApplication(open(pdf).read(), 'pdf')
        pdfPart.add_header('Content-Disposition', 'attachment', filename=pdf)
        msg.attach(pdfPart)

#        print 'Sent to: %s (%d)' % (T['nev'], len(T['pdf']))

    else:
        from email.mime.text import MIMEText
        msg = MIMEText(Content, 'plain', 'utf-8')
        msg['From'], msg['To'], msg['Subject'] = From, To, Subject


    if debug:
        open(os.path.join(debug, debugFile), 'w').write(Content)
        open(os.path.join(debug, 'mailbox'), 'a').write('From szaszi Mon Jan 01 00:00:00 2000\n' + msg.as_string() + '\n')
    else:
        s = smtplib.SMTP('localhost')
        s.sendmail(From, [To], msg.as_string())
        s.quit()

def main():
    try:
        opts, argv = getopt.getopt(sys.argv[1:], "hdg", ['help', 'debug', 'gen'])
    except getopt.GetoptError, err:
        print str(err)
        usage()
    opts = dict(opts)

    if '-h' in opts.keys() or '--help' in opts.keys():
        usage(exitcode=0)

    # alapértelmezetten az aktuális könyvtárat vesszük
    BASE = '.'
    # ha van megadva könyvtár, akkor azt használjuk
    if len(argv) == 1:
        BASE = argv[0]
    os.chdir(BASE)

    if '-g' in opts.keys() or '--gen' in opts.keys():
        confGen()
        sys.exit(0)

    if not os.path.isfile(confFile):
        Exit('Nincs %s fájl!\nÍgy készíthetsz: %s -g' % (confFile, prog))

    debug = False
    if '-d' in opts.keys() or '--debug' in opts.keys():
        debug = True

    config = yaml.load(open('korlevel.ini'))

    try:
        sablon = open(config['sablon']).read()
    except IOError:
        Exit('A megadott sablon fájl (%s) nem létezik.' % config['sablon'])

    try:
        forras_reader = csv.reader(open(config['forras'], "rb"), delimiter=';', quoting=csv.QUOTE_MINIMAL)
    except IOError:
        Exit('A megadott adat fájl (%s) nem létezik.' % config['forras'])
    fejlec = forras_reader.next()

    # Ha van extra módosítási igény, azt az "config['plugin']" fájlba tesszük
    if config.has_key('plugin'):
        exec open(config['plugin']).read()

    # ha "debug" akkor a config['debug'], annak híján a "debug" könyvtárba írjuk a kimenetet.
    if debug:
        debug = 'debug'
        if config.has_key('debug'): debug = config['debug']
        # ha nincs könyvtára, akkor létrehozzuk
        if not os.path.isdir(debug):
            os.mkdir(debug)
        # üres fájl létrehozása
        open(os.path.join(debug, 'mailbox'), 'w').close()

    for entry in forras_reader:
        data = dict(zip(fejlec, entry))
        # Ha van 'plugEntry' függvény, azt végrehajtjuk
        if 'plugEntry' in locals():
            plugEntry(data)

        send(debug, config['from'], data['email'], config['subject'], sablon % data, config['pdf'])

def confGen():
    if os.path.isfile(confFile):
        print 'már van %s' % confFile
        return 0
    else:
        open(confFile, 'w').write('''# YAML
#############################################################################
# A küldendő levél szövege, benne a kitöltendő mezők jelölésével
# %(mezo)s formában.

sablon: sablon.txt

#############################################################################
# A mezők értékei, a sablon mezőin kívül legyen egy 'email' mező,
# amely címekre kell küldeni a leveleket. (csv formátumban)

forras: adatok.csv

#############################################################################
# A küldött levél feladója és tárgya

from: Karácsonyi Mikulás <mikulas@lappfold.hu>
subject: Ajándék értesítő

#############################################################################
# Ha egyéb parancsot akarunk futtatni
#
# sub plugEntry(data): az adatsorok mindegyikén akarunk valamit módosítani

# plugin: plugin.py

#############################################################################
# Ha van pdf, azt csatolja a levélhez

# pdf: csatolmany.pdf

#############################################################################
# Ha teszteléshez küldés helyett fájlokat szeretnénk létrehozni
# parancssorban: -d
# Az adott könyvtárban minden email-címhez létrehoz egy fájlt
# + egy mailbox foldert, amiben minden levél benne van.

# debug: debug
''')
        print "%s létrehozva" % confFile

if __name__ == '__main__':
    main()

