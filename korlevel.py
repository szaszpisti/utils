#!/usr/bin/python3
# ~/bin/korlevel.py

'''@file korlevel.py
Sablon és adatbázis (csv) alapján kör-emailt küld.

ln -s ~/git/utils/korlevel.py ~/bin/korlevel
'''

import os, sys
import csv, getopt, smtplib, yaml
import mimetypes

from email import charset, encoders

from email.mime import base, text, audio, image, multipart
from email.utils import formataddr, parseaddr

# specify quoted-printable instead of base64
charset.CHARSETS['utf-8'] = (charset.QP, charset.QP, 'utf-8')

confFile = 'korlevel.ini'

def Exit(msg=None, exitcode=1):
    if msg: print(msg)
    sys.exit(exitcode)

def usage(msg=None, exitcode=1):
    if msg: print(msg)
    print('Usage: %s [-d|--debug file] [-h|--help] [-g|--gen]' % sys.argv[0])
    print('   -h|--help         ez a súgó')
    print('   -g|--gen          az aktuális könyvtárba létrehoz egy konfigurációs állományt')
    print('   -c|--conf config  a default korlevel.ini helyett a conf állományt használja')
    print('   -d|--debug file   nem küld levelet, hanem a "file" mailboxba teszi a leveleket')
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
        msg = text.MIMEText(attachContent, _subtype=subtype)
    elif maintype == 'image':
        msg = image.MIMEImage(attachContent, _subtype=subtype)
    elif maintype == 'audio':
        msg = audio.MIMEAudio(attachContent, _subtype=subtype)
    else:
        msg = base.MIMEBase(maintype, subtype)
        msg.set_payload(attachContent)
        encoders.encode_base64(msg)

    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    return msg

def send(debug, header, To, Content, filenames=None):

    header['From'] = formataddr(parseaddr(header['From']))
    To_orig = To
    To = formataddr(parseaddr(To))

    if filenames:
        msg = multipart.MIMEMultipart()
        # a header mezőit átmásoljuk az üzenetbe
        for field in header:
            msg[field] = header[field]
        msg['To'] = To

        body = text.MIMEText(Content, 'plain', 'utf-8')
        msg.attach(body)

        for filename in filenames:
            msg.attach(attach(filename))

    # Csatolás nélküli szimpla email
    else:
        msg = text.MIMEText(Content, 'plain', 'utf-8')
        for field in header:
            msg[field] = header[field]
        msg['To'] = To

    # Ha csak debug kell, akkor elmentjük a "debug" változóba
    if debug:
        open(debug, 'a').write('From pistike Mon Jan 01 00:00:00 2000\n' + msg.as_string() + '\n')
    # egyébként elküldjük
    else:
        s = smtplib.SMTP('localhost')
        try:
            s.sendmail(header['From'], [To], msg.as_string())
        except:
            print('HIBA:', To_orig)
        s.quit()

def main():
    global confFile
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:d:g", ['help', 'conf=', 'debug=', 'gen'])
    except getopt.GetoptError as err:
        print(str(err))
        usage()

    make_conf = False
    debug = False
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage(exitcode=0)
        elif opt in ('-g', '--gen'):
            make_conf = True
        elif opt in ('-c', '--conf'):
            confFile = arg
        elif opt in ('-d', '--debug'):
            debug = arg
            # üres fájl létrehozása
            open(debug, 'w').close()

    if make_conf or not os.path.isfile(confFile):
        confGen()
        Exit('Létrehoztam (%s), nézd át!' % confFile)

    config = yaml.load(open(confFile))

    try:
        sablon = open(config['sablon']).read()
    except IOError:
        Exit('A megadott sablon fájl (%s) nem létezik.' % config['sablon'])

    with open(config['forras']) as csvfile:
        try:
            # kitaláljuk, hogy a csv pontosvesszővel, vesszővel vagy tabulátorral van tagolva
            dialect = csv.Sniffer().sniff(csvfile.read(1024), delimiters=";,\t")
        except csv.Error:
            # Ha csak egy mezőből áll a sor: nincs delimiter, a Sniffer nem tud detektálni
            dialect='excel'
            pass
        csvfile.seek(0)
        forras_reader = csv.reader(csvfile, dialect)
        fejlec = next(forras_reader)

        # Ha van extra módosítási igény, azt az "config['plugin']" fájlba tesszük
        if 'plugin' in config:
            loc = locals()
            exec(open(config['plugin']).read(), globals(), loc)
            plugEntry = loc['plugEntry']

        # Ha a config fájlban nincs csatolmány megadva
        if 'attach' not in config:
            config['attach'] = None

        # Vesszük sorra a címeket
        for entry in forras_reader:
            data = dict(zip(fejlec, entry))

            # Nem foglalkozunk vele, ha üres sor, ha nincs email vagy megjegyzés
            if not entry or not data['email'] or entry[0][0] == '#': continue

            # Ha van 'plugEntry' függvény, azt végrehajtjuk - ezt minden címnél meg kell csinálni
            if 'plugEntry' in locals():
                plugEntry(config, data)

            send(debug, config['header'], data['email'], sablon % data, config['attach'])

def confGen():
    if os.path.isfile(confFile):
        print('már van %s' % confFile)
        return 0
    else:
        open(confFile, 'w').write('''# YAML
#############################################################################
# A küldendő levél szövege, benne a kitöltendő mezők jelölésével
# %(mezo)s formában.

sablon: level.txt

#############################################################################
# A mezők értékei, a sablon mezőin kívül legyen egy 'email' mező,
# amely címekre kell küldeni a leveleket. (csv formátumban)

forras: adatok.csv

#############################################################################
# A küldött levél feladója és tárgya

header:
  From: Dugonics András Piarista Gimnázium <titkarsag@szepi.hu>
  Subject: 

#############################################################################
# Ha egyéb parancsot akarunk futtatni
#
# sub plugEntry(data): az adatsorok mindegyikén akarunk valamit módosítani

#plugin: plugin.py

#############################################################################
# ezeket a fájlokat csatolja a levélhez

#attach:
#- csatolmany.pdf
#- egy masik.zip
''')
        print("%s létrehozva" % confFile)

if __name__ == '__main__':
    main()

