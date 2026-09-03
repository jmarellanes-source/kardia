#!/usr/bin/env python3
"""Mide el esfuerzo de mantenimiento actual de los hardcodeos que el catalogo
sustituye. Solo lee el repositorio; no toca ninguna base de datos.

    python3 auditoria/dummy/06_medir_esfuerzo.py [BD_prod ...]

Escribe auditoria/dummy/metricas.json, que alimenta el informe 13.
"""
import json
import os
import re
import sys

BOMS = ((b'\xff\xfe', 'utf-16-le'), (b'\xfe\xff', 'utf-16-be'), (b'\xef\xbb\xbf', 'utf-8-sig'))
CAMPO = 'NUM_DESC_TIPO_CREDITO'
PREDICADO = re.compile(r'NUM_DESC_TIPO_CREDITO\s*(?:=\s*(\d+)|(?:NOT\s+)?IN\s*\(([^)]*)\))', re.I)
SOLO_NUM = re.compile(r'^[\d,\s]+$')

# Banderas propuestas y los tipos que hoy agrupan, derivados de las listas del
# codigo (ver auditoria/dummy/01_catalogo_tipo_credito.sql).
BANDERAS = {
    'SEGMENTO_INDIVIDUAL': [1, 3, 4, 9, 10, 11, 16, 17],
    'SEGMENTO_COMERCIAL': [2, 12, 13, 14, 15, 18, 27, 28],
    'SEGMENTO_SINDICADA': [7],
    'ES_MINORISTA': [12, 13, 14, 15, 28],
    'ES_PUENTE': [2, 18, 27],
    'ES_MEZZANINE': [5],
    'ES_EMPLEADO': [9, 10, 11],
    'ES_ADMINISTRADA_IND': [4, 20, 23],
    'ES_ADMINISTRADA_COM': [6, 19, 21, 22, 24],
    'ES_CASTIGO_COMERCIAL': [25, 29],
    'ES_CASTIGO_INDIVIDUAL': [26],
}


def leer(ruta):
    crudo = open(ruta, 'rb').read()
    for bom, enc in BOMS:
        if crudo.startswith(bom):
            return crudo.decode(enc, 'replace')
    return crudo.decode('utf-8', 'replace')


def sin_comentarios(texto):
    texto = re.sub(r'/\*.*?\*/', ' ', texto, flags=re.S)
    return '\n'.join(re.sub(r'--.*$', '', l) for l in texto.splitlines())


def conjunto_de(coincidencia):
    """Tipos de credito de un predicado, o None si la lista no es literal."""
    if coincidencia.group(1):
        return {int(coincidencia.group(1))}
    lista = coincidencia.group(2) or ''
    if not SOLO_NUM.match(lista):
        return None
    return set(int(x) for x in lista.split(',') if x.strip())


def medir_tipo_credito(directorios):
    res = {}
    for d in directorios:
        archivos = predicados = ocurrencias = 0
        listas = set()
        por_bandera = {}
        for nombre in sorted(os.listdir(d)):
            if not nombre.lower().endswith('.sql'):
                continue
            texto = leer(os.path.join(d, nombre))
            n = len(re.findall(CAMPO, texto, re.I))
            if not n:
                continue
            archivos += 1
            ocurrencias += n
            plano = sin_comentarios(texto)
            for m in PREDICADO.finditer(plano):
                predicados += 1
                conjunto = conjunto_de(m)
                if conjunto is None:
                    continue
                listas.add(tuple(sorted(conjunto)))
                for bandera, tipos in BANDERAS.items():
                    if set(tipos) <= conjunto:
                        por_bandera.setdefault(bandera, [0, set()])
                        por_bandera[bandera][0] += 1
                        por_bandera[bandera][1].add(nombre)
        res[os.path.basename(os.path.normpath(d))] = {
            'archivos': archivos, 'ocurrencias': ocurrencias,
            'predicados': predicados, 'listas_distintas': len(listas),
            # Filtros cuyo conjunto contiene por completo el grupo de la bandera:
            # son los que esa bandera sustituye por si sola o como parte de una
            # combinacion.
            'por_bandera': {b: {'predicados': v[0], 'archivos': len(v[1])}
                            for b, v in sorted(por_bandera.items())}}
    return res


def medir_reporte(ruta):
    texto = leer(ruta)
    rubros = set()
    for m in re.finditer(r"rubro\s*(?:=|IN)\s*(\(?[^)]*\)?)", texto, re.I):
        rubros.update(re.findall(r"'([^']+)'", m.group(1)))
    rubros.discard('ADMINISTRACION INDIVIDUAL')
    return {
        'lineas': len(texto.splitlines()),
        'predicados_rubro': len(re.findall(r'\brubro\s*(?:=|IN)', texto, re.I)),
        'rubros_distintos': len(rubros),
        'ocurrencias_literales_rubro': sum(
            len(re.findall(r"'" + re.escape(r) + r"'", texto)) for r in rubros),
        'predicados_id_poliza': len(re.findall(r'ID_POLIZA\s*(?:=|IN|in)', texto)),
        'factor_hardcodeado': len(re.findall(r'monto \* 9', texto, re.I)),
        'literal_admon_individual': len(re.findall(r'ADMINISTRACION INDIVIDUAL', texto)),
    }


def main():
    raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    dirs = sys.argv[1:] or [os.path.join(raiz, 'BD_prod'), os.path.join(raiz, 'BD')]
    metricas = {
        'tipo_credito': medir_tipo_credito(dirs),
        'reporte_cobranza': medir_reporte(
            os.path.join(raiz, 'BD_prod', 'dbo.REPORTE_COBRANZA_INTEGRACION.StoredProcedure.sql')),
    }
    salida = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'metricas.json')
    with open(salida, 'w', encoding='utf-8') as fh:
        json.dump(metricas, fh, indent=2, ensure_ascii=False, sort_keys=True)
    print(json.dumps(metricas, indent=2, ensure_ascii=False, sort_keys=True))


if __name__ == '__main__':
    main()
