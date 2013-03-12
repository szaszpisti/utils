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

def attach(filename):
    '''Elkészíti a MIME részt, benne a fájlnévvel'''
    if not os.path.isfile(filename):
        return None

    ctype, encoding = mimetypes.guess_type(filename)
    if ctype is None or encoding is not None:
        ctype = 'application/octet-stream'

    maintype, subtype = ctype.split('/', 1)
    attachContent = open(filename, 'rb').read()

    if maintype == 'text':
        msg = MIMEText(attachContent, _subtype=subtype)
    elif maintype == 'image':
        msg = MIMEImage(attachContent, _subtype=subtype)
    elif maintype == 'audio':
        msg = MIMEAudio(attachContent, _subtype=subtype)
    else:
        msg = MIMEBase(maintype, subtype)
        msg.set_payload(attachContent)
        encoders.encode_base64(msg)

    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    return msg

def intlAddress(address):
    # RFC 2822 fejléc-mező ("Subject: =?iso-8859-1?q?p=F6stal?=")
    u = lambda text: email.header.Header(text.decode('utf-8')).encode()

    # Az utf-8 email cimből levélben küldhető mezőt állítunk elő
    emil = email.utils.parseaddr(address)

    return '%s <%s>' % (u(emil[0]), emil[1])

def send(debug, header, To, Content, filenames=None):

    header['From'] = intlAddress(header['From'])
    To = intlAddress(To)

    if filenames:
        msg = MIMEMultipart('alternative')
        # a header mezőit átmásoljuk az üzenetbe
        for field in header:
            msg[field] = header[field]
        msg['To'] = To

        body = MIMEText(Content, 'plain', 'utf-8')
        msg.attach(body)

        for filename in filenames:
            msg.attach(attach(filename))

    # Csatolás nélküli szimpla email
    else:
        msg = MIMEText(Content, 'plain', 'utf-8')
        msg['From'], msg['To'], msg['Subject'] = header['From'], header['To'], Subject


    # Ha csak debug kell, akkor elmentjük a config['debug'] mailbox-ba
    if debug:
        open('mailbox', 'a').write('From szaszi Mon Jan 01 00:00:00 2000\n' + msg.as_string() + '\n')
    # egyébként elküldjük
    else:
        s = smtplib.SMTP('localhost')
        s.sendmail(header['From'], [To], msg.as_string())
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
        debug = 'mailbox'
        if config.has_key('debug'): debug = config['debug']
        # üres fájl létrehozása
        open('mailbox', 'w').close()

    for entry in forras_reader:
        data = dict(zip(fejlec, entry))
        # Ha van 'plugEntry' függvény, azt végrehajtjuk
        if 'plugEntry' in locals():
            plugEntry(data)

        send(debug, config['header'], data['email'], sablon % data, config['attach'])

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

header:
- From: Karácsonyi Mikulás <mikulas@lappfold.hu>
- Subject: Ajándék értesítő

#############################################################################
# Ha egyéb parancsot akarunk futtatni
#
# sub plugEntry(data): az adatsorok mindegyikén akarunk valamit módosítani

#plugin: plugin.py

#############################################################################
# Ha van pdf, azt csatolja a levélhez

#attach:
#- csatolmany.pdf
#- egy masik.zip

#############################################################################
# Ha teszteléshez küldés helyett egy mailbox fájlt szeretnénk létrehozni.
# parancssorban: -d

#debug: mailbox
''')
        print "%s létrehozva" % confFile

if __name__ == '__main__':
    main()

