# -*- coding: utf-8 -*-
"""Genera 18_version_sept10.html: que cambia la version SPs_Sept10 entregada por
el equipo respecto al codigo auditado, y que pendientes cierra o no cierra."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plantilla import e, page  # noqa: E402

BASE = os.path.dirname(os.path.abspath(__file__))
DIFF = json.load(open(os.path.join(BASE, 'sept10_diff.json'), encoding='utf-8'))

# Conteos medidos con auditoria/comparar_sept10.py y auditoria/checks_sept10.py
# sobre las dos copias del codigo (la auditada y la de SPs_Sept10).
SENALES = [
    ('Literal <code>OPI VALOR</code> con espacio, inexistente en <code>PR.PR_RUBRO</code>',
     '4 objetos / 16 usos', '4 objetos / 16 usos', 'no', 'R-001 sigue vigente: el filtro sigue escrito con espacio'),
    ('Literal <code>PRINCIPAL_VENCIDO</code> (no aparece en el catálogo entregado)',
     '3 / 5', '3 / 5', 'no', 'pendiente de confirmar con contabilidad'),
    ('Literal <code>INTERES_NO_EXIGIBLES</code> (no aparece en el catálogo entregado)',
     '6 / 20', '6 / 20', 'no', 'pendiente de confirmar con contabilidad'),
    ('Objetos que leen <code>Quiero_Confianza_CreditoPuente_QA</code>',
     '4 / 41', '4 / 41', 'no', 'los cuatro <code>PO.SYS_SP_*</code> declarados «para borrar» siguen en el paquete'),
    ('Marca COVID por función con umbral (<code>dbo.FN_ES_COVID</code>)',
     '63 / 225', '65 / 227', 'no', 'sube: los dos SPs nuevos de sindicado también la usan'),
    ('Marca COVID por columna del origen (<code>IND_COVID</code>)',
     '100 / 714', '102 / 728', 'no', 'siguen conviviendo las dos formas (R-006)'),
    ('Umbral <code>6086</code> en producción y <code>6051</code> en la copia de desarrollo',
     '1 / 1', '1 / 1', 'no', 'la divergencia entre ambientes no se tocó'),
    ("Regla de cartera no restringida escrita como <code>IN ('008','031')</code>",
     '7 / 8', '7 / 8', 'no', 'R-003 sigue vigente'),
    ('Misma regla escrita como <code>NOT IN (22,23,28,35)</code> comparando el código como número',
     '9 / 13', '9 / 13', 'no', 'R-003 sigue vigente'),
    ('<code>WITH (NOLOCK)</code>',
     '76 / 895', '78 / 919', 'no', 'sube por los dos objetos nuevos'),
    ("Cuentas de orden por <code>OBSERVACION LIKE '%CUENTAS DE ORDEN%'</code>",
     '9 / 11', '9 / 11', 'no', 'el patrón de referencia sigue aplicado en 9 objetos, no en la familia completa'),
    ('Filtros con <code>NUM_DESC_TIPO_CREDITO</code> hardcodeado',
     '90 / 314', '92 / 318', 'no', 'el hardcodeo crece: la versión nueva agrega listas, no las quita'),
]

CERRADOS = [
    ('CIERRE.SP_SAF_SALDOS truncado en producción',
     'No cierra: en <code>BD_prod</code> sigue teniendo 223 líneas contra 573 en la copia de desarrollo, '
     'y el archivo no cambió en esta entrega.'),
    ('19 objetos de CIERRE ausentes del export de producción',
     'No cierra: la brecha es idéntica (24 objetos en foco presentes en desarrollo y ausentes del export, '
     '19 de ellos de <code>CIERRE</code>, incluido <code>SP_IND_GEN_MES</code>). '
     'La Fase 0 contra los metadatos de la instancia sigue siendo necesaria.'),
    ('CIERRE.SP_IND_GEN_MES_MOD declarado sin uso',
     'Se mantiene cerrado por declaración, no por código: el objeto sigue publicado en el paquete, '
     'con el mismo <code>UPDATE</code> observado. Conviene borrarlo para que la declaración y el repositorio coincidan.'),
    ('Los cuatro PO.SYS_SP_* que leen la base QA serán borrados',
     'Sigue abierto en el repositorio: los cuatro objetos y sus 41 referencias a '
     '<code>Quiero_Confianza_CreditoPuente_QA</code> continúan en la entrega de septiembre.'),
]

NUEVO = [
    ('La póliza sindicada se agregó a mano en diez objetos', 'rojo',
     'El cambio funcional principal de esta versión es dar de alta la póliza sindicada (<code>ID_POLIZA</code> 77 y 88, '
     'sufijo <code>SND</code>). Para lograrlo hubo que editar diez objetos ya productivos y publicar dos nuevos: '
     '<code>PO.SP_SND_DESEMBOLSO</code> y <code>PO.SP_SND_REVERSO_DESEMBOLSO</code>. '
     'Es la demostración exacta del problema que el portal viene a resolver: un concepto nuevo no se configura, se libera.'),
    ('Cada objeto recibió su propia copia del literal', 'ambar',
     'El mismo par de códigos quedó escrito en varias formas y lugares: la lista de pólizas del reporte de cobranza '
     '(<code>in (7, 35, 37, 40, 51, 77, 88)</code>), las etiquetas <code>when ID_POLIZA = 77 then \'COMERCIAL SINDICADA\'</code>, '
     'el filtro por nombre <code>DESCRIPCION like \'% SND\'</code> en cinco objetos de envío y el nuevo <code>-3</code> '
     'como identificador de «TODO SINDICADA» en el balance. Ninguno de esos valores vive en un catálogo.'),
    ('Se agregó una lista de tipos de crédito nueva, no se quitó ninguna', 'ambar',
     'En <code>PO.SP_COM_DEV_INTERES</code> el bloque nuevo de devengo trae '
     '<code>C.NUM_DESC_TIPO_CREDITO IN (12,13,14,15,28, 2,18,27)</code> y '
     '<code>A.COD_RUBRO IN (\'INTERES_ORDINARIO_A\')</code>. Es una lista más que administrar, sobre la base '
     '<code>Quiero_Confianza_shadow</code>.'),
    ('El canal del cierre comercial ahora depende de un tipo específico', 'ambar',
     'En <code>CIERRE.SP_CMR_GEN_MES</code>: <code>CASE WHEN C.NUM_DESC_TIPO_CREDITO = 5 THEN \'COMERCIAL\' '
     'ELSE dbo.FN_TIPO_CANAL(C.TIP_TASA) END</code>. Confirma la observación de la auditoría: el canal no se deriva '
     'de una sola regla y ahora tiene una excepción por tipo (el 5, <code>DCM</code>) incrustada en el SP.'),
    ('Aparecen dos controles que la auditoría había pedido', 'verde',
     '<code>PO.SP_SAF_POLIZA_FINALIZA</code> ahora sale sin hacer nada si la póliza del día ya está '
     '<code>ENVIADA</code>, que es una guarda de reproceso, y <code>PO.SP_SND_POLIZA_DIARIA</code> registra duración '
     'por paso en <code>PO.PR_EJECUCION_LOG</code>. Son parciales: aplican a la familia sindicada y a la finalización, '
     'no a todo el cierre, y no sustituyen la marca de corrida ni el sello de configuración.'),
    ('La corrida diaria de sindicado ahora borra y recalcula desde la última fecha', 'ambar',
     '<code>PO.SP_SND_POLIZA_DIARIA</code> calcula <code>@FECHA_ULT</code> y ejecuta '
     '<code>DELETE FROM PO.PR_DEVENGO_DET / PR_CAPITAL_DET / PR_COBRANZA_DET / PR_MINISTRACIONES_DET</code> '
     'para lo anterior a esa fecha. Es un borrado de detalle en el camino contable diario: hay que confirmar con '
     'contabilidad que no puede alcanzar días ya publicados.'),
]


def tabla_senales():
    f = ''.join(
        '<tr><td>%s</td><td class="num">%s</td><td class="num">%s</td>'
        '<td><span class="pill %s">%s</span></td><td>%s</td></tr>'
        % (s[0], s[1], s[2], 'c' if s[3] == 'no' else 'b', 'no cierra' if s[3] == 'no' else 'cierra', s[4])
        for s in SENALES)
    return ('<table><thead><tr><th>Señal medida en el código de producción</th><th>Auditado</th>'
            '<th>SPs_Sept10</th><th>Estado</th><th>Lectura</th></tr></thead><tbody>%s</tbody></table>' % f)


def tabla_diff():
    mod = [d for d in DIFF if d['clase'] == 'modificado']
    mod.sort(key=lambda d: -(d['add'] + d['del']))
    f = ''.join(
        '<tr><td class="mono">%s</td><td class="num">+%d / -%d</td><td>%s</td></tr>'
        % (e(d['archivo']), d['add'], d['del'],
           ', '.join(t for t, k in (('póliza sindicada', 'snd'), ('lista de tipos', 'lista_tipos'),
                                    ('base shadow', 'shadow'), ('manejo de fechas', 'fecha'),
                                    ('bitácora de ejecución', 'log'), ('guarda de reproceso', 'guarda')) if d[k]) or '—')
        for d in mod)
    return ('<table><thead><tr><th>Archivo</th><th>Líneas sustantivas</th><th>Qué toca</th></tr></thead>'
            '<tbody>%s</tbody></table>' % f)


def tabla_nuevos():
    nue = sorted(d['archivo'] for d in DIFF if d['clase'] == 'nuevo')
    f = ''.join('<tr><td class="mono">%s</td></tr>' % e(n) for n in nue)
    return '<table><thead><tr><th>Archivo nuevo en SPs_Sept10</th></tr></thead><tbody>%s</tbody></table>' % f


def main():
    mod = len([d for d in DIFF if d['clase'] == 'modificado'])
    nue = len([d for d in DIFF if d['clase'] == 'nuevo'])
    body = f"""
<p class="lead">Comparación línea por línea de la versión <code>SPs_Sept10</code> entregada por el equipo contra la copia
que se auditó. La comparación normaliza codificación y fin de línea (la entrega viene en UTF-16 con CRLF, el repositorio
auditado en UTF-8), y descarta cambios que sólo son comentarios o espacios, para que el conteo sea de cambio real de
lógica. No se ejecutó nada contra SQL Server.</p>

<div class="kpis">
<div class="kpi"><b>{mod}</b><span>objetos con cambio de lógica</span></div>
<div class="kpi"><b>{nue}</b><span>objetos nuevos</span></div>
<div class="kpi"><b>0</b><span>objetos eliminados</span></div>
<div class="kpi c"><b>0</b><span>hallazgos que cierra</span></div>
<div class="kpi m"><b>2</b><span>controles nuevos parciales</span></div>
</div>

<h2>Respuesta corta</h2>
<div class="card rojo"><h3>Ningún hallazgo se cierra con esta versión, y el hardcodeo crece</h3>
<p>Los doce indicadores que sostienen los hallazgos abiertos se midieron en las dos copias del código y ninguno bajó:
tres suben porque los dos objetos nuevos repiten los mismos patrones. La entrega sí trae dos controles que la auditoría
había pedido (guarda de reproceso y bitácora de duración), pero acotados a la familia sindicada.</p></div>

<h2>Los indicadores, medidos en las dos versiones</h2>
<p>Conteo sobre <code>BD_prod</code> (la copia de producción del paquete), en objetos y ocurrencias, descartando comentarios.</p>
{tabla_senales()}

<h2>Qué cambió realmente</h2>
{tabla_diff()}

<h2>Lo que la entrega dice del problema de fondo</h2>
{''.join('<div class="card %s"><h3>%s</h3><p>%s</p></div>' % (c, t, d) for t, c, d in NUEVO)}

<h2>Pendientes que se esperaba cerrar y siguen abiertos</h2>
{''.join('<div class="card ambar"><h3>%s</h3><p>%s</p></div>' % (t, d) for t, d in CERRADOS)}

<h2>Objetos nuevos en la entrega</h2>
<p>Los <code>BAK_*</code> son respaldos de tablas con fecha en el nombre; conviene definir dónde viven y cuándo se
purgan, porque hoy se publican como parte del código.</p>
{tabla_nuevos()}

<h2>Qué haría distinto la remediación con esta versión en la mano</h2>
<div class="card azul"><h3>La póliza sindicada es el caso de prueba ideal para el portal</h3>
<p>Ya existe el «antes» completo y fechado: diez objetos editados y dos publicados para dar de alta un concepto.
Con el catálogo de banderas ese mismo alta sería una fila en <code>CAT_TIPO_POLIZA</code> más su marca en
<code>CAT_TIPO_CREDITO_BANDERA</code>, sin tocar los diez objetos. Propongo usarlo como medición de esfuerzo real
en la presentación, en lugar de un ejemplo hipotético.</p></div>
<div class="card azul"><h3>La lista de pólizas del reporte de cobranza es el primer reemplazo a ejecutar</h3>
<p><code>dbo.REPORTE_COBRANZA_INTEGRACION</code> y <code>CIERRE.SP_RPT_COBRANZA_CARTERA_CMR_IND_VIS</code> mantienen la
misma lista duplicada en dos consultas cada uno; con 77 y 88 ya son cuatro lugares que hay que editar en conjunto.
Es el cambio de menor riesgo y mayor visibilidad de la Ola 1.</p></div>
<div class="card ambar"><h3>Dos preguntas nuevas para el equipo</h3>
<p>¿El <code>DELETE</code> por <code>@FECHA_ULT</code> de <code>PO.SP_SND_POLIZA_DIARIA</code> puede alcanzar días ya
publicados, o hay una garantía externa de que no? ¿La excepción del tipo 5 en el canal del cierre comercial es una
regla de negocio permanente o un parche temporal?</p></div>
"""
    out = os.path.join(BASE, '18_version_sept10.html')
    open(out, 'w', encoding='utf-8').write(page(
        'La versión SPs_Sept10 frente a lo auditado',
        'Qué cambió, qué pendientes cierra y qué sigue abierto — CIERRE, SAF, PO y dbo.REPORTE_COBRANZA_INTEGRACION',
        body))
    print('generado', out, mod, nue)


if __name__ == '__main__':
    main()
