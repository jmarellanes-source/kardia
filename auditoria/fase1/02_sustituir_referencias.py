"""Fase 1 - Paso 2: sustitucion mecanica de las referencias al origen por EXT.

Convierte cada referencia de tres partes a la base de origen en una referencia
al sinonimo del esquema EXT:

    FROM Quiero_Confianza_shadow.PR.PR_ENCABEZADO_PAGO A WITH (NOLOCK)
    FROM EXT.PR_ENCABEZADO_PAGO A WITH (NOLOCK)

NO modifica los archivos originales: escribe en un directorio de salida
(por omision BD_ext/) preservando el encoding de cada archivo, y emite un
reporte de que cambio en cada uno para que la revision sea linea a linea.

Uso:
  python3 02_sustituir_referencias.py --carpeta BD --salida BD_ext
  python3 02_sustituir_referencias.py --carpeta BD --solo-reporte

La sustitucion es puramente textual y por eso es revisable y reversible; el
control de que no quedo ninguna referencia viva lo hace 04_gate_ci.py, y la
equivalencia funcional se prueba recalculando un periodo cerrado.
"""
import argparse
import collections
import glob
import os
import re

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
# Grupo 1: esquema del origen, grupo 2: objeto. Acepta corchetes en cualquier parte.
REF = re.compile(r'\[?Quiero_Confianza[A-Za-z_]*\]?\s*\.\s*\[?(\w+)\]?\s*\.\s*\[?(\w+)\]?', re.I)


def leer(ruta):
    b = open(ruta, 'rb').read()
    if b[:2] == b'\xff\xfe':
        return b.decode('utf-16-le', errors='replace'), 'utf-16-le-bom'
    if b[:2] == b'\xfe\xff':
        return b.decode('utf-16-be', errors='replace'), 'utf-16-be-bom'
    return b.decode('utf-8-sig', errors='replace'), 'utf-8-bom'


def escribir(ruta, texto, encoding):
    codecs = {'utf-16-le-bom': 'utf-16', 'utf-16-be-bom': 'utf-16', 'utf-8-bom': 'utf-8-sig'}
    with open(ruta, 'w', encoding=codecs[encoding], newline='') as fh:
        fh.write(texto)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--carpeta', default='BD')
    ap.add_argument('--salida', default='BD_ext')
    ap.add_argument('--solo-reporte', action='store_true')
    args = ap.parse_args()

    origen = os.path.join(RAIZ, args.carpeta)
    destino = os.path.join(RAIZ, args.salida)
    if not args.solo_reporte:
        os.makedirs(destino, exist_ok=True)

    tocados = 0
    total = 0
    por_objeto = collections.Counter()
    for ruta in sorted(glob.glob(os.path.join(origen, '*.sql'))):
        texto, enc = leer(ruta)
        nuevo, n = REF.subn(lambda m: 'EXT.{}'.format(m.group(2)), texto)
        if not n:
            continue
        for m in REF.finditer(texto):
            por_objeto['{}.{}'.format(m.group(1).upper(), m.group(2).upper())] += 1
        tocados += 1
        total += n
        print('{:<70} {:>4} referencias'.format(os.path.basename(ruta), n))
        if not args.solo_reporte:
            escribir(os.path.join(destino, os.path.basename(ruta)), nuevo, enc)

    print('\n{} archivos con referencias al origen, {} sustituciones, '
          '{} objetos distintos del origen'.format(tocados, total, len(por_objeto)))
    if not args.solo_reporte:
        print('salida en {} (los archivos de {} quedan intactos)'.format(args.salida, args.carpeta))


if __name__ == '__main__':
    main()
