# coding: utf-8

HEAD = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html>
<head>
  <title>PiárFutár - %s</title>
  <meta name="Author" content="Szász Imre">
  <meta http-equiv="Content-Type" content="text/html; charset=utf8">
  <meta http-equiv="Content-Language" content="hu">
  <link rel="stylesheet" href="pifu.css" type="text/css">
</head>
<body>

<p class="menu">
[ <a class="menu" href="../../../index.html" target="_top">SzePi</a>
| <a class="menu" href="../../index.html">Iskola</a>
| <a class="menu" href="../index.html">Újságok</a>
%s]</p>

<div class="spacer">&nbsp;</div>

<table width="100%%">
<tr>
  <td><img src="../logo-pifu.png" alt="PiárFutár"></td>
  <td width="67" rowspan="3"><img src="../logo-cimer.png" width="67" height="93" alt=""></td>
  <td><img src="../ures.png" width="100" height="1" alt=""></td>
<tr>
  <td><img src="../logo-csik.png" width="100%%" height="10" alt=""></td>
  <td><img src="../logo-csik.png" width="100%%" height="10" alt=""></td>
<tr>
  <td valign="top"><img src="../logo-piar.png" alt="A Dugonics András Piarista Gimnázium lapja"></td>
  <td></td>
</table>

<div class="spacer">&nbsp;</div>
<!-- container -->

<h1>%s. évfolyam - %s</h1>

<div class="container">
<div class="spacer">&nbsp;</div>
'''

TAIL = '''
<div class="spacer">&nbsp;</div>
</div><!-- container -->

<p><hr><img src="../piarfutar.png" alt="piarfutar@szepi_PONT_hu" align="top">
</body>
</html>
'''

HO = {
    '01': 'január',
    '02': 'február',
    '03': 'március',
    '04': 'április',
    '05': 'május',
    '06': 'június',
    '07': 'szeptember',
    '08': 'október',
    '09': 'november',
    '10': 'december'
    }

ENTRY = '''
<a class="pifu" href="PiarFutar-%s%s.pdf" type="application/pdf"><div class="float">
  <p>%s</p>
  <p><img src="PiarFutar-%s%s.png"  alt="PiárFutár %s.%s első oldal" /></p>
  <p style="height: 2.5em;">%s</p>
</div></a>
'''

