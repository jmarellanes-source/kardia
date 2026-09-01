"""Genera 01_crear_sinonimos_EXT.sql a partir de las referencias reales al origen.

Recorre BD/ y BD_prod/, decodifica por BOM (UTF-16LE o UTF-8) y extrae toda
referencia de tres partes a la base de origen (Quiero_Confianza y sus variantes
_shadow / _CreditoPuente_QA). Cada objeto distinto del origen se convierte en un
sinonimo del esquema EXT dentro de KARDIA.

Uso:  python3 generar_sinonimos.py            (desde auditoria/fase1)
No modifica ningun archivo de BD/ ni de BD_prod/.
"""
import collections
import glob
import os
import re

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SALIDA = os.path.join(os.path.dirname(__file__), '01_crear_sinonimos_EXT.sql')
REF = re.compile(r'\[?(Quiero_Confianza[A-Za-z_]*)\]?\.\[?(\w+)\]?\.\[?(\w+)\]?', re.I)

CABECERA = """/* ============================================================================
   Fase 1 - Capa de fachada del origen: sinonimos por ambiente
   ----------------------------------------------------------------------------
   Genera los {n} sinonimos del esquema EXT que cubren TODAS las referencias al
   origen encontradas en BD y BD_prod ({refs} referencias literales en {arch}
   archivos se resuelven con estos {n} objetos).

   Se ejecuta con sqlcmd pasando la base de origen del ambiente:
     sqlcmd -S <srv> -d KARDIA -i 01_crear_sinonimos_EXT.sql -v ORIGEN="Quiero_Confianza"
     sqlcmd -S <srv> -d KARDIA -i 01_crear_sinonimos_EXT.sql -v ORIGEN="Quiero_Confianza_shadow"

   El codigo de los procedimientos deja de conocer el nombre de la base: la
   unica diferencia entre ambientes vive en este script. Es tambien el punto
   donde, el dia que salga SAF/Sisde, se apunta al nuevo origen sin tocar los
   245 objetos programables.

   Generado por auditoria/fase1/generar_sinonimos.py - no editar a mano.
   ============================================================================ */
SET NOCOUNT ON;
IF SCHEMA_ID(N'EXT') IS NULL EXEC(N'CREATE SCHEMA EXT');
GO
"""


def leer(ruta):
    b = open(ruta, 'rb').read()
    if b[:2] == b'\xff\xfe':
        return b.decode('utf-16-le', errors='replace')
    if b[:2] == b'\xfe\xff':
        return b.decode('utf-16-be', errors='replace')
    return b.decode('utf-8-sig', errors='replace')


def main():
    objetos = collections.Counter()
    archivos = set()
    for carpeta in ('BD', 'BD_prod'):
        for ruta in sorted(glob.glob(os.path.join(RAIZ, carpeta, '*.sql'))):
            texto = leer(ruta)
            hallado = False
            for m in REF.finditer(texto):
                objetos[(m.group(2).upper(), m.group(3).upper())] += 1
                hallado = True
            if hallado:
                archivos.add(os.path.basename(ruta))

    bloques = []
    for (esquema, tabla), n in objetos.most_common():
        bloques.append(
            '-- {n} referencias en el corpus auditado\n'
            "IF OBJECT_ID(N'EXT.{t}', N'SN') IS NOT NULL DROP SYNONYM EXT.{t};\n"
            'CREATE SYNONYM EXT.{t} FOR [$(ORIGEN)].[{e}].[{t}];'.format(n=n, e=esquema, t=tabla))

    cab = CABECERA.format(n=len(objetos), refs=sum(objetos.values()), arch=len(archivos))
    with open(SALIDA, 'w', encoding='utf-8') as fh:
        fh.write(cab + '\n' + '\n\n'.join(bloques) + '\nGO\n')
    print('{}: {} sinonimos, {} referencias en {} archivos'.format(
        os.path.basename(SALIDA), len(objetos), sum(objetos.values()), len(archivos)))


if __name__ == '__main__':
    main()
