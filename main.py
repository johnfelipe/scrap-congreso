from bs4 import BeautifulSoup
import requests
import re

PARTIDOS = [
  'PAN',
  'PRD',
  'PRI',
  'CONVERGENCIA',
  'VERDE',
  'PT',
  'NUEVA ALIANZA',
  'PSD',
  'N/A',
]

def get_iniciativas_from_session(base_link):
  inic_dipt = []

  link = 'http://sitl.diputados.gob.mx/%s' % base_link
  req = requests.get(link)
  page = BeautifulSoup(req.text)

  # get info
  inidipt_table = page.find_all('table')[1]
  inidipt_rows = inidipt_table.find_all('tr')

  for row in inidipt_rows[1:]:
    tds = row.find_all('td')

    # data
    iniciativa = tds[0].span.text[5:].strip()
    comision = " ".join( [x.strip() for x in tds[1].text.split()] )
    sinopsis = tds[2].span.text.strip()
    tramite = " ".join( [x.strip() for x in tds[3].text.split()] )

    i_d = {
      'iniciativa' : iniciativa,
      'comision' : comision,
      'sinopsis' : sinopsis,
      'tramite' : tramite,
    }

    inic_dipt.append(i_d)

  return inic_dipt

def get_proposiciones_from_session(base_link):
  prop_dipt = []

  link = 'http://sitl.diputados.gob.mx/%s' % base_link
  req = requests.get(link)
  page = BeautifulSoup(req.text)

  # get info
  propdipt_table = page.find_all('table')[1]
  propdipt_rows = propdipt_table.find_all('tr')

  for row in propdipt_rows[1:]:
    tds = row.find_all('td')

    # data
    proposicion = tds[0].span.text[5:].strip()
    comision = " ".join( [x.strip() for x in tds[1].text.split()] )
    resolutivos_p = tds[2].span.text.strip()
    resolutivos_a = " ".join( [x.strip() for x in tds[3].text.split()] )
    tramite = " ".join( [x.strip() for x in tds[4].text.split()] )

    p_d = {
      'proposicion' : proposicion,
      'comision' : comision,
      'resolutivos_proponente' : resolutivos_p,
      'resolutivos_aprobados' : resolutivos_a,
      'tramite' : tramite,
    }

    prop_dipt.append(p_d)

  return prop_dipt

def get_asistencias_from_session(base_link):
  asist_dipt = []

  link = 'http://sitl.diputados.gob.mx/%s' % base_link
  req = requests.get(link)
  page = BeautifulSoup(req.text)

  # get info
  trs = page.table.children
  true_trs = [tr for tr in trs if tr.name]
  table2 = true_trs[3].td.table
  table2_trs = [tr for tr in table2.children if tr.name]
  table3 = table2_trs[1].td.contents[1]
  table_list = table3.find_all('table')[1:-1]

  for tab in table_list:
    tab_trs = tab.find_all('tr')
    asist_date = tab_trs[0].td.span.text.strip()

    a_p_d = []

    for tr in tab_trs[2:]:
      tds = tr.find_all('td')
      for td in tds:
        txt = td.div.font.text
        has_letter = re.search(r'[A-Z]', txt)

        if has_letter:
          match = re.match(r'([0-9]+)([A-Z]+)', txt, re.I)
          apd = {
            'dia': int(match.group(1)),
            'estado': match.group(2),
          }
          a_p_d.append(apd)



    a_d = {
      'fecha' : asist_date,
      'asistencia_por_dia' : a_p_d,
    }

    asist_dipt.append(a_d)

  return asist_dipt

def get_votaciones_from_session(base_link):
  vota_dipt = []

  link = 'http://sitl.diputados.gob.mx/%s' % base_link
  req = requests.get(link)
  page = BeautifulSoup(req.text)

  # get info
  trs = page.table.children
  true_trs = [tr for tr in trs if tr.name]
  vot_table = true_trs[3].td.table
  vot_rows = vot_table.find_all('tr')

  vot_date = ''

  for row in vot_rows:
    tds = row.find_all('td')

    if len(tds) == 1:
      vot_date = tds[0].text.strip()
    elif len(tds) == 4:
      v_d = {
        'fecha' : vot_date,
        'titulo' : tds[1].text.strip(),
        'voto' : tds[3].text.strip()
      }
      vota_dipt.append(v_d)

  return vota_dipt

def get_iniciativas(dip_id):
  print "iniciativas..."
  ini_data = []

  base_link = 'http://sitl.diputados.gob.mx/iniciativas_diputados_xperiodonp.php'
  link = '%s?dipt=%s' % (base_link, dip_id)
  req = requests.get(link)
  page = BeautifulSoup(req.text)

  # get info
  trs = page.table.children
  true_trs = [tr for tr in trs if tr.name]
  ini_table = true_trs[3].td.table
  ini_rows = ini_table.find_all('tr')


  for row in ini_rows:
    tds = row.find_all('td')
    if len(tds) == 3:
      tag = tds[1].a
      session = {
        'sesion' : tag.text.strip(),
        'propuestas' : get_iniciativas_from_session(tag['href']),
      }
      ini_data.append(session)

  return ini_data

def get_proposiciones(dip_id):
  print "propuestas..."
  prop_data = []

  base_link = 'http://sitl.diputados.gob.mx/proposiciones_diputados_xperiodonp.php'
  link = '%s?dipt=%s' % (base_link, dip_id)
  req = requests.get(link)
  page = BeautifulSoup(req.text)

  # get info
  trs = page.table.children
  true_trs = [tr for tr in trs if tr.name]
  prop_table = true_trs[3].td.table
  prop_rows = prop_table.find_all('tr')

  for row in prop_rows:
    tds = row.find_all('td')
    if len(tds) == 3:
      tag = tds[1].a
      session = {
        'sesion' : tag.text.strip(),
        'propuestas' : get_proposiciones_from_session(tag['href']),
      }
      prop_data.append(session)

  return prop_data

def get_asistencias(dip_id):
  print "asistencias..."
  asist_data = []

  base_link = 'http://sitl.diputados.gob.mx/asistencias_diputados_xperiodonp.php'
  link = '%s?dipt=%s' % (base_link, dip_id)

  req = requests.get(link)
  page = BeautifulSoup(req.text)

  # get info
  trs = page.table.children
  true_trs = [tr for tr in trs if tr.name]
  asist_table = true_trs[3].td.table
  asist_rows = asist_table.find_all('tr')

  for row in asist_rows:
    tds = row.find_all('td')
    if len(tds) == 3:
      tag = tds[1].a
      session = {
        'sesion' : tag.text.strip(),
        'asistencias' : get_asistencias_from_session(tag['href']),
      }

      asist_data.append(session)

  return asist_data

def get_votaciones(dip_id):
  print "votaciones..."
  vota_data = []

  base_link = 'http://sitl.diputados.gob.mx/votaciones_diputados_xperiodonp.php'
  link = '%s?dipt=%s' % (base_link, dip_id)

  req = requests.get(link)
  page = BeautifulSoup(req.text)

  # get info
  trs = page.table.children
  true_trs = [tr for tr in trs if tr.name]
  vota_table = true_trs[3].td.table
  vota_rows = vota_table.find_all('tr')

  for row in vota_rows:
    tds = row.find_all('td')
    if len(tds) == 3:
      tag = tds[1].a
      session = {
        'sesion' : tag.text.strip(),
        'votos_por_sesion' : get_votaciones_from_session(tag['href']),
      }

      vota_data.append(session)

  return vota_data

def get_extra(dip_id):
  extra_json = {
    'iniciativas' : get_iniciativas(dip_id),
    'proposiciones' : get_proposiciones(dip_id),
    'asistencias' : get_asistencias(dip_id),
    'votaciones' : get_votaciones(dip_id),
  }

  return extra_json

def get_info(dip_id, partido):
  base_link = 'http://sitl.diputados.gob.mx/curricula.php'
  link = '%s?dipt=%s' % (base_link, dip_id)
  req = requests.get(link)
  page = BeautifulSoup(req.text)

  # get info
  trs = page.table.children
  true_trs = [tr for tr in trs if tr.name]
  info_table = true_trs[2].td.table
  info_rows = info_table.find_all('tr')

  # datos
  nombre = info_rows[1].find_all('td')[1].text[5:].strip()
  entidad = info_rows[3].find_all('td')[1].text.strip()
  distrito = info_rows[4].find_all('td')[1].text.strip()

  print "Obteniendo informacion de \"%s\"" % nombre

  dip_json = {
    'nombre' : nombre,
    'partido' : partido,
    'entidad' : entidad,
    'distrito' : distrito,
    'datos' : get_extra(dip_id),
  }

  return dip_json


def process_data(link, partido):
  url = link['href']
  dip_id = url.split('=')[1]

  return get_info(dip_id, partido)

def scrap():
  full_data = []
  swap_partido = False
  partido_index = -1

  link = 'http://sitl.diputados.gob.mx/listado_diputados_gpnp.php?tipot=TOTAL'
  req = requests.get(link)
  page = BeautifulSoup(req.text)


  print "procesando..."

  trs = page.table.children
  true_trs = [tr for tr in trs if tr.name]

  dip_table = true_trs[3].td.table

  dip_rows = dip_table.find_all('tr')

  for row in dip_rows:
    tds = row.find_all('td')
    if len(tds) > 1:
      if swap_partido:
        partido_index = partido_index + 1
        swap_partido = False
      if tds[0].a:
        full_data.append( process_data(tds[0].a, PARTIDOS[partido_index]) )
        # break
    else:
      swap_partido = True

  print "guardando en el archivo..."
  save_json("data.json", full_data)


def save_json(name, data):
  import json
  with open(name, 'w') as outfile:
    json.dump(data, outfile)

#
# main
#
scrap()
