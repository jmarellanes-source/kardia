"""Fase 1 - Paso 4: compuerta de integracion continua.

Falla la construccion (codigo de salida 1) si vuelve a entrar al repositorio una
referencia literal a la base de origen o alguno de los patrones que la Fase 1
declara cerrados. Es lo que evita que el drift regrese despues de eliminarlo.

Uso en el pipeline (Azure DevOps o GitHub Actions):
    python3 auditoria/fase1/04_gate_ci.py BD BD_prod

Cada regla se puede activar por olas: al inicio solo 'origen' esta en modo
bloqueante y el resto reporta; a medida que cada ola cierra, se pasa a bloqueante
cambiando BLOQUEANTES.
"""
import glob
import os
import re
import sys

BLOQUEANTES = {'origen'}

REGLAS = {
    'origen': (re.compile(r'Quiero_Confianza', re.I),
               'referencia literal a la base de origen; usar el sinonimo EXT.<objeto>'),
    'base_qa': (re.compile(r'Quiero_Confianza_CreditoPuente_QA|_shadow', re.I),
                'referencia a una base de QA o shadow desde codigo desplegable'),
    'fecha_fija': (re.compile(r"'\d{8}'|'\d{4}-\d{2}-\d{2}'"),
                   'fecha literal en un proceso diario; debe venir del periodo procesado'),
    'iva_fijo': (re.compile(r'0\.16\b|1\.16\b'),
                 'tasa de IVA literal; debe leerse del catalogo de parametros vigente'),
    'participacion': (re.compile(r'0\.10\b|0\.90\b'),
                      'participacion por convenio literal; parametrizable en portal'),
    'servidor': (re.compile(r'\b\d{1,3}(\.\d{1,3}){3}\b'),
                 'IP o servidor embebido; usar datasource compartido o sinonimo'),
}


def leer(ruta):
    b = open(ruta, 'rb').read()
    if b[:2] == b'\xff\xfe':
        return b.decode('utf-16-le', errors='replace')
    if b[:2] == b'\xfe\xff':
        return b.decode('utf-16-be', errors='replace')
    return b.decode('utf-8-sig', errors='replace')


def main(carpetas):
    fallos = 0
    for carpeta in carpetas:
        for ruta in sorted(glob.glob(os.path.join(carpeta, '*.sql'))):
            texto = leer(ruta)
            for linea_no, linea in enumerate(texto.splitlines(), 1):
                if linea.lstrip().startswith('--'):
                    continue
                for regla, (patron, mensaje) in REGLAS.items():
                    if patron.search(linea):
                        nivel = 'ERROR' if regla in BLOQUEANTES else 'aviso'
                        print('{}: {}:{}: [{}] {}'.format(
                            nivel, ruta, linea_no, regla, mensaje))
                        if nivel == 'ERROR':
                            fallos += 1
    print('\ncompuerta: {} violaciones bloqueantes'.format(fallos))
    return 1 if fallos else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:] or ['BD']))
