# -*- coding: utf-8 -*-
"""Ajusta la redaccion de los hallazgos afectados por el contexto operativo
confirmado con el equipo de desarrollo (2026-08-31): el origen de datos es una
replica de solo lectura del core SAF/Sisde y el cierre es diario con bloqueo
historico y ajustes acumulados. No cambia ningun hallazgo ni conteo: agrega la
nota de contexto y precisa impacto y remediacion donde la lectura cambia.
"""
import json
from pathlib import Path

BASE = Path('/home/ubuntu/kardia/auditoria')
NOTA = ' NOTA DE CONTEXTO (sesion con el equipo de desarrollo, 2026-08-31): '

AJUSTES = {
    'lote1_hallazgos.json': {
        'L1-006': {
            'titulo': 'El cierre no acota el periodo ni registra que ya lo proceso: un segundo pase vuelve a acumular',
            'impacto_add': NOTA + 'el diseno declarado trata los ajustes de dias anteriores como '
            'adiciones acumuladas con bloqueo del historico, de modo que sumar sobre el valor previo es '
            'intencional en el cierre diario. El defecto no es la acumulacion, sino que el agregado se toma '
            'de todo el historico de PR_BALLON_DET sin filtro de periodo y que no existe marca de periodo '
            'procesado ni guarda que impida un segundo pase del mismo dia (reintento del job o ejecucion '
            'manual). Pendiente de validar con el equipo cual es el comportamiento esperado ante reintento.',
            'remediacion': 'Registrar la corrida (periodo, id de ejecucion, estado) y rechazar el segundo pase '
            'del mismo periodo salvo reproceso autorizado; acotar el agregado de PR_BALLON_DET al periodo '
            'procesado. Si el reproceso debe permitirse, hacerlo determinista (borrar-e-insertar el periodo o '
            'SET = base + agregado del periodo) en lugar de sumar sobre el valor acumulado.',
        },
        'L1-007': {
            'impacto_add': NOTA + 'el origen legitimo del proceso es Quiero_Confianza, replica de solo '
            'lectura del transaccional SAF/Sisde. Eso confirma la gravedad de este hallazgo: las variantes '
            '_CreditoPuente_QA y _shadow no son la replica productiva, por lo que estos objetos no leen del '
            'origen autorizado.',
        },
        'L1-014': {
            'impacto_add': NOTA + 'el origen es una replica de solo lectura, no la base transaccional viva, '
            'por lo que el NOLOCK no puede bloquear ni degradar el core productivo y el riesgo de lectura '
            'sucia de una transaccion en vuelo es menor. El riesgo que permanece es real: leer la replica '
            'mientras se le aplican cambios admite filas duplicadas u omitidas por movimiento de paginas y '
            'lecturas no repetibles, de modo que dos corridas del mismo periodo pueden arrojar cifras '
            'distintas sin que nada lo advierta.',
            'remediacion': 'Sobre la replica, leer con SNAPSHOT (o READ COMMITTED SNAPSHOT) y fijar el punto '
            'de lectura del cierre: una marca de sincronia de la replica por corrida, registrada junto al id '
            'de ejecucion, para que el resultado sea reproducible y auditable. Eliminar NOLOCK de todo lo que '
            'alimente cifras contables; conservarlo, si acaso, solo en consultas exploratorias.',
        },
        'L1-016': {
            'impacto_add': NOTA + 'el nombre correcto del origen productivo es Quiero_Confianza (replica del '
            'core); shadow y _QA son variantes por ambiente. Confirma que la remediacion correcta es el '
            'sinonimo por ambiente y no editar el nombre en cada copia.',
        },
    },
    'lotes10-11_hallazgos.json': {
        'L10-016': {
            'impacto_add': NOTA + 'la lectura ocurre contra una replica de solo lectura del core, por lo que '
            'el hint no compromete al sistema transaccional; lo que permanece es la falta de reproducibilidad '
            'de la cifra publicada, porque la replica cambia mientras el cierre la lee.',
            'remediacion': 'Sustituir el hint por lectura con SNAPSHOT sobre la replica y registrar la marca '
            'de sincronia usada por cada corrida del cierre, de forma que la poliza del dia sea reproducible '
            'a partir de un punto de lectura conocido.',
        },
    },
}


def main():
    for archivo, cambios in AJUSTES.items():
        ruta = BASE / archivo
        datos = json.loads(ruta.read_text(encoding='utf-8'))
        indice = {h['id']: h for h in datos['hallazgos']}
        for hid, campos in cambios.items():
            h = indice[hid]
            if 'titulo' in campos:
                h['titulo'] = campos['titulo']
            if 'impacto_add' in campos and NOTA.strip() not in h['impacto']:
                h['impacto'] = h['impacto'].rstrip() + campos['impacto_add']
            if 'remediacion' in campos:
                h['remediacion'] = campos['remediacion']
            print('ajustado', archivo, hid)
        ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding='utf-8')


if __name__ == '__main__':
    main()
