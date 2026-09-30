# -*- coding: utf-8 -*-
"""Cruza la lista de objetos prioritarios entregada por el cliente
(auditoria/insumos/sp_relacionados_a_poliza.txt) contra las dos copias de codigo
del paquete de septiembre y deja el resultado en alcance_produccion.json.

Solo analisis estatico de archivos .sql: no toca ninguna instancia de SQL Server.

Uso:  python3 analizar_alcance.py [raiz_del_paquete]
      raiz_del_paquete debe contener BD/ y BD_prod/  (por omision /home/ubuntu/sept10)
"""
import difflib
import json
import pathlib
import re
import sys
from collections import Counter

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '/home/ubuntu/sept10')
LISTA = AQUI / 'insumos' / 'sp_relacionados_a_poliza.txt'
SALIDA = AQUI / 'alcance_produccion.json'

FOCO = ('CIERRE', 'SAF', 'PO', 'RPT', 'dbo')


def leer(p):
    b = p.read_bytes()
    if b[:2] in (b'\xff\xfe', b'\xfe\xff'):
        t = b.decode('utf-16')
    elif b[:3] == b'\xef\xbb\xbf':
        t = b[3:].decode('utf-8', 'replace')
    else:
        t = b.decode('utf-8', 'replace')
    return t.replace('\r\n', '\n')


def sin_comentarios(t):
    t = re.sub(r'/\*.*?\*/', ' ', t, flags=re.S)
    return '\n'.join(re.sub(r'--.*$', '', l) for l in t.split('\n'))


PATRONES = {
    'opi_valor_espacio': r"'OPI VALOR'",
    'principal_vencido': r"'PRINCIPAL_VENCIDO'",
    'interes_no_exigibles': r"'INTERES_NO_EXIGIBLES'",
    'base_qa': r'Quiero_Confianza_CreditoPuente_QA',
    'base_shadow': r'Quiero_Confianza_shadow',
    'fn_es_covid': r'FN_ES_COVID',
    'ind_covid': r'IND_COVID',
    'origen_008_031': r"IN\s*\(\s*'008'\s*,\s*'031'",
    'origen_not_in_shf': r'NOT\s+IN\s*\(\s*22\s*,\s*23\s*,\s*28\s*,\s*35\s*\)',
    'nolock': r'WITH\s*\(\s*NOLOCK\s*\)',
    'cuentas_orden': r'CUENTAS DE ORDEN',
    'tipo_credito_filtro': r'NUM_DESC_TIPO_CREDITO\s*(=|<>|!=|IN|NOT\s+IN|BETWEEN)',
    'getdate': r'getdate\s*\(\s*\)',
    'fecha_literal': r"'20\d{6}'",
    'copia_catalogo': r'\bSAF_CAT_DESC_TIPO\b',
    'cat_tipo_autoritativo': r'\bPR_DESC_TIPOS_CREDITO\b',
    'cat_rubro_autoritativo': r'\bPR_RUBRO\b',
    'cat_origen_autoritativo': r'\bPR_ORIGEN_FONDOS\b',
    'tabla_rubro_x_credito': r'PR_RUBRO(?:_COBRO)?_X_CREDITO',
    'servidor_vinculado': r'SRV-IONSQLAWS',
}

LISTAS_TIPO = re.compile(
    r'NUM_DESC_TIPO_CREDITO\s*(?:NOT\s+)?IN\s*\(([^)]*)\)', re.I)


def objetos(sub):
    r = {}
    for f in sorted((RAIZ / sub).glob('*.sql')):
        p = f.name.split('.')
        if len(p) < 3:
            continue
        r[p[0] + '.' + p[1]] = f
    return r


def tipo_objeto(f):
    p = f.name.split('.')
    return p[2] if len(p) > 3 else 'Schema'


def main():
    lista = [l.strip() for l in LISTA.read_text(encoding='utf-8-sig').split('\n') if l.strip()]
    en_lista = set(lista)
    bd, prod = objetos('BD'), objetos('BD_prod')

    filas, listas_tipo = [], Counter()
    dentro = Counter()
    dentro_obj = Counter()
    fuera = Counter()
    fuera_obj = Counter()

    universo = sorted(set(bd) | set(prod))
    for o in universo:
        esq = o.split('.')[0]
        if esq not in FOCO:
            continue
        f = bd.get(o) or prod.get(o)
        t = sin_comentarios(leer(f))
        hits = {k: len(re.findall(v, t, re.I)) for k, v in PATRONES.items()}
        acu, acu_obj = (dentro, dentro_obj) if o in en_lista else (fuera, fuera_obj)
        for k, n in hits.items():
            if n:
                acu[k] += n
                acu_obj[k] += 1
        if o in en_lista:
            for m in LISTAS_TIPO.finditer(t):
                nums = ','.join(sorted(x.strip().strip("'") for x in m.group(1).split(',') if x.strip()))
                listas_tipo[nums] += 1
        if o not in en_lista:
            continue

        clase, dif = '', 0
        if o in bd and o in prod:
            a = [l.rstrip() for l in leer(bd[o]).split('\n')]
            b = [l.rstrip() for l in leer(prod[o]).split('\n')]
            sust = lambda l: l.strip() and not l.strip().startswith('--')
            d = [l for l in difflib.unified_diff(a, b, lineterm='', n=0)
                 if l[:1] in '+-' and l[:3] not in ('+++', '---') and sust(l[1:])]
            if not d:
                clase = 'identico'
            else:
                nb = lambda x: re.sub(r'Quiero_Confianza(_shadow|_CreditoPuente_QA)?', '<BD>', x, flags=re.I)
                d2 = [l for l in difflib.unified_diff([nb(x) for x in a], [nb(x) for x in b], lineterm='', n=0)
                      if l[:1] in '+-' and l[:3] not in ('+++', '---') and sust(l[1:])]
                clase, dif = ('solo_base', len(d)) if not d2 else ('real', len(d2))
        elif o in bd:
            clase = 'ausente_prod'
        else:
            clase = 'ausente_dev'
        filas.append({'objeto': o, 'esquema': esq, 'tipo': tipo_objeto(f),
                      'clase': clase, 'lineas_dif': dif,
                      'patrones': {k: v for k, v in hits.items() if v}})

    # los objetos que no estan en la lista se separan en dependencias (las usa
    # algun objeto de la lista) y candidatos fuera de alcance (nadie de la lista
    # los menciona).  Es la diferencia entre "no lo administra el portal" y
    # "no hace falta instalarlo en el QA nuevo".
    cuerpo = '\n'.join(sin_comentarios(leer(bd.get(o) or prod[o]))
                       for o in en_lista if o in bd or o in prod)
    dependencias, sin_uso = [], []
    for o in universo:
        if o.split('.')[0] not in FOCO or o in en_lista:
            continue
        f = bd.get(o) or prod.get(o)
        t = tipo_objeto(f)
        if t == 'Schema':
            continue
        n = re.escape(o.split('.')[1])
        reg = re.search(r'\b' + n + r'\b', cuerpo, re.I)
        (dependencias if reg else sin_uso).append({'objeto': o, 'tipo': t})

    res = {
        'total_lista': len(lista),
        'unicos': len(en_lista),
        'por_esquema': dict(Counter(o.split('.')[0] for o in en_lista)),
        'clases': dict(Counter(f['clase'] for f in filas)),
        'dependencias_de_la_lista': dependencias,
        'fuera_de_lista_sin_uso': sin_uso,
        'patrones': {k: {'dentro_obj': dentro_obj[k], 'dentro': dentro[k],
                         'fuera_obj': fuera_obj[k], 'fuera': fuera[k]}
                     for k in PATRONES},
        'listas_tipo_credito': listas_tipo.most_common(),
        'objetos': filas,
    }
    SALIDA.write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding='utf-8')
    print('lista:', res['total_lista'], 'unicos:', res['unicos'])
    print('por esquema:', res['por_esquema'])
    print('clases:', res['clases'])
    print('dependencias fuera de la lista pero usadas por ella:', len(dependencias),
          dict(Counter(d['tipo'] for d in dependencias)))
    print('fuera de la lista y sin uso desde ella:', len(sin_uso),
          dict(Counter(d['tipo'] for d in sin_uso)))
    print('listas distintas de NUM_DESC_TIPO_CREDITO dentro de la lista:', len(listas_tipo))
    for k, v in res['patrones'].items():
        print(f"  {k:24} dentro {v['dentro_obj']:3}/{v['dentro']:5}   fuera {v['fuera_obj']:3}/{v['fuera']:4}")


if __name__ == '__main__':
    main()
