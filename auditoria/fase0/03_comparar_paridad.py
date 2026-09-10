"""Fase 0 - Paso 3: matriz de paridad repositorio vs instancias.

Cruza el CSV que produce 01_inventario_instancia.sql en cada ambiente contra el
codigo del repositorio y clasifica cada objeto en uno de cinco estados:

  IGUAL          el hash normalizado del repo coincide con el de la instancia
  SOLO_ORIGEN    la unica diferencia es el nombre de la base de origen, es decir
                 desaparece sola al aplicar los sinonimos EXT de la Fase 1
  DIFERENTE      el objeto existe en ambos lados con distinto contenido real
  SOLO_INSTANCIA corre en el servidor y no esta versionado  <- riesgo mayor
  SOLO_REPO      esta versionado y no existe en el servidor
  AUSENTE_EXPORT no aparece en el export de ese ambiente (caso CIERRE en prod)

Aplica la MISMA normalizacion que el script T-SQL (CRLF, tabuladores y espacios
colapsados) para que las diferencias de formato no cuenten como diferencias de
codigo, y decodifica por BOM (UTF-16LE o UTF-8) sin borrar los bytes 0x00.

Uso:
  python3 03_comparar_paridad.py inventario_PROD.csv inventario_QA.csv
  -> escribe paridad.csv y resume por estado en pantalla

Sin argumentos compara unicamente BD/ contra BD_prod/, que es lo que se puede
hacer hoy sin acceso a las instancias.
"""
import csv
import glob
import hashlib
import os
import re
import sys

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
ESPACIOS = re.compile(r'[\r\n\t ]+')
CABECERA = re.compile(r'^\s*(SET\s+ANSI_NULLS|SET\s+QUOTED_IDENTIFIER|GO)\b.*$',
                      re.I | re.M)
# Variantes por ambiente de la base de origen: shadow, _CreditoPuente_QA, etc.
ORIGEN = re.compile(r'\[?Quiero_Confianza[A-Za-z_]*\]?', re.I)


def leer(ruta):
    b = open(ruta, 'rb').read()
    if b[:2] == b'\xff\xfe':
        return b.decode('utf-16-le', errors='replace')
    if b[:2] == b'\xfe\xff':
        return b.decode('utf-16-be', errors='replace')
    return b.decode('utf-8-sig', errors='replace')


def cuerpo(texto):
    """Deja solo la definicion del objeto: quita el envoltorio que agrega el
    export de SSMS (SET ANSI_NULLS / QUOTED_IDENTIFIER / GO) para poder comparar
    contra sys.sql_modules, que no lo incluye."""
    return CABECERA.sub('', texto)


def firma(texto, neutralizar_origen=False):
    plano = cuerpo(texto)
    if neutralizar_origen:
        plano = ORIGEN.sub('@ORIGEN@', plano)
    plano = ESPACIOS.sub(' ', plano).strip()
    return hashlib.sha256(plano.encode('utf-8')).hexdigest().upper()


def nombre_objeto(ruta):
    """PO.SP_IND_CONDONACION.StoredProcedure.sql -> [PO].[SP_IND_CONDONACION]"""
    partes = os.path.basename(ruta).split('.')
    return '[{}].[{}]'.format(partes[0], partes[1])


def inventario_repo(carpeta):
    """objeto -> (hash literal, hash con el nombre de la base neutralizado)"""
    salida = {}
    for ruta in sorted(glob.glob(os.path.join(RAIZ, carpeta, '*.sql'))):
        if '.Table.sql' in ruta or '.Schema.sql' in ruta:
            continue
        texto = leer(ruta)
        salida[nombre_objeto(ruta)] = (firma(texto), firma(texto, True))
    return salida


def inventario_csv(ruta):
    salida = {}
    with open(ruta, encoding='utf-8-sig') as fh:
        for fila in csv.DictReader(fh, delimiter='|'):
            nombre = (fila.get('nombre') or '').strip()
            if nombre and not nombre.startswith('-'):
                salida[nombre] = (fila.get('hash_sha2') or '').strip().upper()
    return salida


def comparar(repo, instancia, etiqueta_repo, etiqueta_inst):
    filas = []
    for nombre in sorted(set(repo) | set(instancia)):
        par = repo.get(nombre)
        en_repo, en_inst = (par[0] if par else None), instancia.get(nombre)
        if en_repo and en_inst:
            estado = 'IGUAL' if en_repo == en_inst else 'DIFERENTE'
        elif en_inst:
            estado = 'SOLO_INSTANCIA'
        else:
            estado = 'SOLO_REPO'
        filas.append({'objeto': nombre, 'estado': estado,
                      etiqueta_repo: en_repo or '', etiqueta_inst: en_inst or ''})
    return filas


def main():
    argv = sys.argv[1:]
    if argv:
        repo = inventario_repo('BD')
        for csv_inst in argv:
            etiqueta = os.path.splitext(os.path.basename(csv_inst))[0]
            filas = comparar(repo, inventario_csv(csv_inst), 'hash_repo', 'hash_instancia')
            destino = 'paridad_{}.csv'.format(etiqueta)
            with open(destino, 'w', newline='', encoding='utf-8') as fh:
                w = csv.DictWriter(fh, fieldnames=['objeto', 'estado', 'hash_repo', 'hash_instancia'])
                w.writeheader()
                w.writerows(filas)
            resumen(destino, filas)
        return

    dev, prod = inventario_repo('BD'), inventario_repo('BD_prod')
    filas = []
    for nombre in sorted(set(dev) | set(prod)):
        a, b = dev.get(nombre), prod.get(nombre)
        if a and b:
            if a[0] == b[0]:
                estado = 'IGUAL'
            elif a[1] == b[1]:
                estado = 'SOLO_ORIGEN'
            else:
                estado = 'DIFERENTE'
        else:
            estado = 'AUSENTE_EXPORT' if a else 'SOLO_PROD'
        filas.append({'objeto': nombre, 'estado': estado,
                      'hash_BD': a[0] if a else '', 'hash_BD_prod': b[0] if b else ''})
    with open('paridad_repo.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=['objeto', 'estado', 'hash_BD', 'hash_BD_prod'])
        w.writeheader()
        w.writerows(filas)
    resumen('paridad_repo.csv', filas)


def resumen(destino, filas):
    conteo = {}
    for f in filas:
        conteo[f['estado']] = conteo.get(f['estado'], 0) + 1
    print(destino, '->', ', '.join('{}={}'.format(k, v) for k, v in sorted(conteo.items())))


if __name__ == '__main__':
    main()
