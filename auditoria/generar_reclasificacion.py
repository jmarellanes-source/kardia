# -*- coding: utf-8 -*-
"""Genera 16_reclasificacion.html (hallazgos reclasificados con el alcance nuevo)
y 17_objetos_vigentes.html + CSV (insumo para la lista limpia de objetos vigentes)."""
import json, csv, collections, re, sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plantilla import page, e  # noqa: E402

AUD = '/home/ubuntu/kardia/auditoria'
FUENTES = ['lote1_hallazgos.json', 'lotes2-5_hallazgos.json', 'lote6_hallazgos.json',
           'lotes10-11_hallazgos.json', 'dependencias_hallazgos.json']

SEV_ORDEN = {'Critico': 0, 'Alto': 1, 'Medio': 2, 'Bajo': 3}
PILL = {'Critico': 'c', 'Alto': 'a', 'Medio': 'm', 'Bajo': 'info'}

# --------------------------------------------------------------- decisiones
# estado: cerrado | fuera | sube | baja | reencuadre | vigente
# (sev nueva; cuando es None se mantiene la original)
D = {
 # -- objetos que el cliente declara sin uso -------------------------------
 'L1-002': ('cerrado', None, 'SP_IND_GEN_MES_MOD no está en uso (respuesta a Q01). Se cierra al confirmar el DROP del objeto.'),
 'L1-003': ('cerrado', None, 'Mismo objeto declarado sin uso. El patrón transaccional sigue vivo en los SPs que si corren (L10-011).'),
 'L1-006': ('cerrado', None, 'Mismo objeto declarado sin uso; la falta de marca de corrida se mantiene como riesgo general en L1-035.'),
 'L10-001': ('cerrado', None, 'La columna destino del ajuste ballon deja de ser un riesgo contable vivo: el ejemplo vigente es CIERRE.SP_SAF_SALDOS línea 90 (respuesta a Q01).'),
 'L10-002': ('cerrado', None, 'Mismo objeto declarado sin uso.'),
 'L1-007': ('cerrado', None, 'Los cuatro PO.SYS_SP_* que leen Quiero_Confianza_CreditoPuente_QA son la primera versión de la póliza y serán borrados (respuesta a Q28). Queda como acción de limpieza, no como hallazgo.'),
 'L1-009': ('cerrado', None, 'Objeto de la primera versión de la póliza, pendiente de borrado.'),
 'L1-010': ('cerrado', None, 'Objeto de la primera versión de la póliza, pendiente de borrado.'),
 'L1-020': ('cerrado', None, 'Objeto de la primera versión de la póliza, pendiente de borrado. Si el umbral de avalúo se sigue usando en otro objeto vigente, vuelve a abrirse.'),
 'L2-003': ('cerrado', None, 'PO.SYS_SP_MOV_CARGO es de la primera versión de la póliza (Q28); el borrado masivo de cargos deja de estar en el camino contable.'),
 'L2-020': ('cerrado', None, 'Mismo objeto: la lectura a QA se resuelve con el borrado.'),
 'L6-007': ('cerrado', None, 'El reporte a Afirme no se utiliza (respuesta a Q15) y dbo.REPORTEAFIRME queda fuera del alcance CIERRE/SAF/PO/cobranza.'),
 # -- fuera del alcance acordado ------------------------------------------
 'L6-001': ('fuera', None, 'edc.* fuera del alcance. Se deja registrado: inserta montos aleatorios en tablas de CFDI contra créditos reales, conviene que alguien lo asuma.'),
 'L6-002': ('fuera', None, 'PAG.* fuera del alcance.'),
 'L6-006': ('fuera', None, 'edc.* fuera del alcance; la remediación por catálogo de tipos lo cubriría después sin costo extra.'),
 'L6-008': ('fuera', None, 'edc.* fuera del alcance.'),
 'L6-009': ('fuera', None, 'edc.spUpsertCClienteDaily queda fuera del alcance (respuesta a Q29).'),
 'L6-010': ('fuera', None, 'edc.* fuera del alcance.'),
 'L6-011': ('fuera', None, 'La validación de cuenta se usa desde PAG.*, fuera del alcance.'),
 'L6-013': ('fuera', None, 'PAG.* fuera del alcance.'),
 'L6-014': ('fuera', None, 'edc.* fuera del alcance.'),
 'L6-019': ('fuera', None, 'edc.* fuera del alcance.'),
 'L6-021': ('fuera', None, 'PAG.* fuera del alcance.'),
 'L6-022': ('fuera', None, 'edc.* fuera del alcance.'),
 'L6-024': ('fuera', None, 'Las tablas de respaldo están en cierre_puente y edcc, fuera del alcance.'),
 'L10-023': ('fuera', None, 'RPT.CASTIGO_REEST_SALDOS queda fuera del alcance CIERRE/SAF/PO/cobranza; se reabre si contabilidad lo usa como fuente.'),
 # -- sube de severidad con la evidencia de los catalogos reales ----------
 'L10-007': ('sube', 'Critico', 'Confirmado contra PR.PR_RUBRO: el literal OPI VALOR (con espacio) no existe en el origen, solo OPI_VALOR. El filtro nunca casa, así que ese importe no entra en ninguna póliza. Deja de ser un riesgo de contrato y pasa a ser un defecto con importe.'),
 'L10-008': ('sube', 'Critico', 'Con PR.PR_ORIGEN_FONDOS a la vista, las dos listas no son equivalentes en significado: 046 es CARTERA_CASTIGADA y 008/031 son CAPITAL (RECURSOS PROPIOS) y OBLIGACIONES, y la tercera variante compara códigos char(3) como números. Dos reportes de cierre pueden clasificar la misma cartera de forma distinta.'),
 # -- baja de severidad ---------------------------------------------------
 'L1-014': ('baja', 'Medio', 'Quiero_Confianza es replica de lectura y el cierre corre después del cierre de SAF: el NOLOCK no amenaza al core. Queda como riesgo de reproducibilidad de la cifra.'),
 'L2-009': ('baja', 'Medio', 'Mismo reencuadre que L1-014.'),
 'L10-016': ('baja', 'Medio', 'Mismo reencuadre que L1-014, sobre la familia de cierre.'),
 'L12-001': ('baja', 'Medio', 'Ya no es una lista abierta: de los 198 objetos en foco, 174 están en el export productivo y la clasificación por evidencia deja 16 candidatos a baja y 5 declarados sin uso (ver la lista limpia).'),
 'L12-002': ('baja', 'Medio', 'La mayoría de las 187 tablas sin referencia pertenece a esquemas fuera del alcance (juicios, cierre_puente, ori, edc); dentro del foco quedan 9 tablas de PO.'),
 # -- reencuadres ---------------------------------------------------------
 'L1-016': ('reencuadre', None, 'El nombre embebido es Quiero_Confianza_shadow en QA y Quiero_Confianza en producción: es drift por ambiente, y se absorbe con los 38 sinónimos de la Fase 1.'),
 'L6-004': ('reencuadre', None, 'Mismo reencuadre: shadow es el nombre de la replica en QA, no una base ajena.'),
 'L10-004': ('reencuadre', None, 'Mismo reencuadre; lo que si queda abierto es SP_CMR_GEN_MES mezclando dos bases distintas en el mismo procedimiento.'),
 'L2-007': ('reencuadre', None, 'El cliente fijó la implementación de referencia: COVID en columna propia del origen y separación balance/orden por la leyenda CUENTAS DE ORDEN en OBSERVACION (PO.SP_SND_COBRANZA línea 47). El hallazgo pasa de "la familia SND no aplica la regla" a "62 objetos deciden COVID con el umbral hardcodeado y solo 10 leen la columna del origen".'),
 'L6-003': ('reencuadre', None, 'Se mantiene crítico y ahora tiene patrón de salida: 62 objetos productivos deciden COVID con dbo.FN_ES_COVID (NUM_CREDITO < 6051, distinto entre ambientes) mientras 10 leen la columna del origen, que es la forma correcta.'),
 'L6-015': ('reencuadre', None, 'PR.PR_DESC_TIPOS_CREDITO existe y publica los 30 tipos, así que la remediación es join al catálogo y no un catálogo nuevo. Lo que no publica el origen es cartera ni administrador: esa clasificación es local y es la que administra el portal.'),
 'L6-017': ('reencuadre', None, 'Dentro del alcance quedan las 53 tablas de PO y las de CIERRE; los esquemas juicios, ori, edc y cierre_puente salen.'),
 'L2-019': ('reencuadre', None, 'La ausencia en el export no prueba ausencia en producción: el export puede ser parcial. Se resuelve con la consulta de metadatos de la Fase 0, no con código.'),
 'L10-006': ('reencuadre', None, 'Mismo reencuadre: es una pregunta de metadatos de producción (Fase 0) y es justamente lo que la lista limpia de objetos vigentes debe cerrar.'),
 'L1-008': ('reencuadre', None, 'Alcance reducido: dos de los cinco objetos son de la primera versión de la póliza. Siguen vivos PO.SYS_SP_ACCOUNT_BALANCE_ORDEN, PO.SYS_SP_BALANCE_DETAIL_SQL y PO.SYS_SP_ACTUALIZA_ESTADO_POLIZA.'),
 'L1-019': ('reencuadre', None, 'Alcance reducido a CIERRE.SP_CMR_GEN_MES (6 usos) y PO.SP_IND_COBRANZA (7): el 0.16 de PO.SYS_SP_AVALUO_AND_UPDATE sale con el objeto. El IVA por rubro, en cambio, ya viene del origen (ind_iva), así que el portal lo lee y no lo administra.'),
 'L1-013': ('reencuadre', None, 'Alcance reducido: el RBAR de PO.SYS_SP_MOV_ABONO sale con el objeto; se mantiene en PO.SP_IND_COBRANZA, PO.SP_COM_COBRANZA_CASTIGOS y la familia SND.'),
 'L1-022': ('reencuadre', None, 'Alcance reducido a PO.SP_IND_COBRANZA; las cuentas de los dos SYS_SP_* salen con los objetos.'),
 'L1-024': ('reencuadre', None, 'Alcance reducido, pero el fondo no cambia: los conceptos de póliza siguen escritos como literales en los SPs vigentes.'),
 'L2-001': ('reencuadre', None, 'La participación debe colgar de COD_ORIGEN y no de un nombre: Afirme son tres orígenes distintos (012, 027, 030) en PR.PR_ORIGEN_FONDOS, y el 0.10/0.90 esta escrito en 28 SPs sin distinguirlos.'),
 'L2-018': ('reencuadre', None, 'Sigue siendo el hardcodeo de mayor retorno y ahora tiene catálogo de origen (30 tipos) y matriz de banderas ya prototipada en la demo.'),
}

NUEVOS = [
 dict(id='R-001', sev='Critico', cat='Integridad contable', obj='CIERRE.SP_SAF_SALDOS, CIERRE.SP_CAS_CIERRE_RPT y los reportes que leen CIERRE.SAF_SALDOS',
      titulo='El literal OPI VALOR no existe en PR.PR_RUBRO: el filtro nunca casa',
      det='El origen solo tiene OPI_VALOR (con guion bajo). Todo filtro escrito como OPI VALOR devuelve vacío, '
          'así que el importe de opinión de valor no llega a ninguna póliza. Es medible: basta comparar el importe '
          'del rubro en el origen contra lo publicado.',
      acc='Corregir el literal en los objetos vigentes y, en la versión paramétrica, validar cada literal contra el catálogo antes de liberar.'),
 dict(id='R-002', sev='Alto', cat='Integridad contable', obj='PR.PR_RUBRO (origen) y los 45 rubros que consume el cierre',
      titulo='El origen trae pares de rubros con el mismo significado y dos marcados como "no usar"',
      det='SEGURO tiene descripción SEGURO_DANOS y convive con SEGURO_DANOS; CARGO BALLON convive con CARGO_BALLON; '
          'PRINC_DIFERIDO y PRINCIPAL_DIFERIDO están descritos como "no usar" y siguen existiendo. Si el cierre '
          'suma uno y no el otro, el importe cambia sin que nadie lo note.',
      acc='Definir con contabilidad el rubro sobreviviente de cada par y marcar el resto como no contabilizable en el catálogo del portal.'),
 dict(id='R-003', sev='Alto', cat='Parametrizacion', obj='PR.PR_ORIGEN_FONDOS frente a las tres listas del código',
      titulo='La regla de cartera no restringida esta escrita de tres formas que no significan lo mismo',
      det="IN ('008','031') en 28 archivos, IN ('008','031','046') en 1 y NOT IN (22,23,28,35) en 19. Con el catálogo "
          'real: 008 es CAPITAL (RECURSOS PROPIOS), 031 OBLIGACIONES, 046 CARTERA_CASTIGADA, y la tercera lista son '
          'los cuatro sindicados SHF comparados como números contra códigos char(3).',
      acc='Una sola bandera por COD_ORIGEN en el catálogo (no_restringido, excluido_de_castigo) y reemplazo de las tres listas por join.'),
 dict(id='R-004', sev='Alto', cat='Gobierno de catálogos', obj='PR.PR_DESC_TIPOS_CREDITO frente al uso en CIERRE/SAF/PO',
      titulo='La clasificación de cartera y administrador no existe en el origen: hoy vive en el código',
      det='El origen publica solo num_desc_tipo_credito y desc_tipo_credito. Cartera y administrador, que es lo que '
          'usan las reglas del cierre, no están en ninguna tabla: están implícitos en las listas IN(...). Seis de los '
          '30 tipos no tienen clasificación asignada en ningún lado.',
      acc='Publicar la clasificación como catálogo local con banderas, vigencia y cuatro ojos, y pedir al negocio la definición de los seis tipos sin clasificar.'),
 dict(id='R-005', sev='Medio', cat='Gobierno de catálogos', obj='PO.SAF_CAT_DESC_TIPO frente a PR.PR_DESC_TIPOS_CREDITO',
      titulo='La copia local del catálogo de tipos esta desalineada del origen',
      det='El tipo 5 es DCM en el origen y OPCION MEZZANINE en la copia; el 26 es CASTIGADO_INDIVIDUAL y en la copia '
          'CARTERA_CASTIGADA; el 20 también difiere en la descripción. El cierre opera con la copia.',
      acc='Sincronizacion programada desde el origen con reporte de diferencias, en lugar de copia manual.'),
 dict(id='R-006', sev='Alto', cat='Consistencia de reglas', obj='62 objetos productivos que usan dbo.FN_ES_COVID',
      titulo='La marca COVID se decide con un umbral hardcodeado en 62 objetos y con la columna del origen en 10',
      det='El cliente fijó como correcta la lectura de la columna COVID del origen (PO.SP_SND_COBRANZA línea 47). '
          'Los otros 62 objetos la derivan de NUM_CREDITO < 6051 en dbo.FN_ES_COVID, umbral que ademas difiere entre '
          'ambientes (6086 en el export de desarrollo).',
      acc='Homologar contra el patrón de referencia y retirar la función cuando ningún objeto vigente la use.'),
]


# --------------------------------------------------------- ortografia de salida
# Los motivos por objeto vienen de vigencia_objetos.json (texto sin acentos por
# construccion): se acentuan aqui, sobre el HTML ya armado, sin tocar etiquetas,
# bloques <pre> ni identificadores SQL.
ACC = {'algun': 'algún', 'asi': 'así', 'categoria': 'categoría', 'conversacion': 'conversación',
       'cubriria': 'cubriría', 'ejecucion': 'ejecución', 'estan': 'están', 'esta': 'está',
       'implementacion': 'implementación', 'implicitos': 'implícitos', 'incognitas': 'incógnitas',
       'movio': 'movió', 'opinion': 'opinión', 'poliza': 'póliza', 'polizas': 'pólizas',
       'produccion': 'producción', 'promocion': 'promoción', 'releidos': 'releídos',
       'semaforo': 'semáforo', 'senala': 'señala', 'senales': 'señales', 'senalo': 'señaló',
       'seran': 'serán', 'sincronizacion': 'sincronización', 'tambien': 'también',
       'teniamos': 'teníamos', 'version': 'versión', 'clasifico': 'clasificó',
       'hipotesis': 'hipótesis', 'fijo': 'fijó', 'linea': 'línea', 'lineas': 'líneas',
       'numero': 'número', 'catalogo': 'catálogo', 'catalogos': 'catálogos',
       'critico': 'crítico', 'criticos': 'críticos', 'auditoria': 'auditoría',
       'reclasificacion': 'reclasificación', 'parametrizacion': 'parametrización',
       'declaro': 'declaró', 'mas': 'más'}
_PROT = re.compile(r'(<(?:style|script|code|pre)\b[^>]*>.*?</(?:style|script|code|pre)>|<[^>]+>'
                   r'|&[a-z]+;|\b\w*[._@#]\w[\w.@#]*|(?-i:\b[A-Z][A-Z0-9_]{2,}\b))', re.S | re.I)
_W = re.compile(r'\b(' + '|'.join(sorted(ACC, key=len, reverse=True)) + r')\b')


def _rep(m):
    w = m.group(0)
    if w.isupper():
        return w
    r = ACC[w.lower()]
    return r[0].upper() + r[1:] if w[0].isupper() else r


def acentuar(html_txt):
    return ''.join(q if i % 2 else _W.sub(_rep, q) for i, q in enumerate(_PROT.split(html_txt)))


def cargar():
    hs = []
    for f in FUENTES:
        hs += json.load(open(os.path.join(AUD, f)))['hallazgos']
    return hs


hall = cargar()
for h in hall:
    est, sev, mot = D.get(h['id'], ('vigente', None, ''))
    h['estado'] = est
    h['sev_nueva'] = sev or ('—' if est in ('cerrado', 'fuera') else h['sev'])
    h['motivo'] = mot


def cnt(sevs):
    c = collections.Counter(sevs)
    return [c.get(k, 0) for k in ('Critico', 'Alto', 'Medio', 'Bajo')]


antes = cnt(h['sev'] for h in hall)
vivos = [h for h in hall if h['estado'] not in ('cerrado', 'fuera')]
despues = cnt([h['sev_nueva'] for h in vivos] + [n['sev'] for n in NUEVOS])
cerr = [h for h in hall if h['estado'] == 'cerrado']
fuera = [h for h in hall if h['estado'] == 'fuera']

ETQ = {'cerrado': ('Cerrado', 'ok'), 'fuera': ('Fuera de alcance', 'info'),
       'sube': ('Sube', 'c'), 'baja': ('Baja', 'ok'),
       'reencuadre': ('Reencuadrado', 'info'), 'vigente': ('Sin cambio', 'm')}

# --------------------------------------------------------------- doc 16
b = []
b.append('<p class="lead">Los 117 hallazgos de la auditoría releídos con dos cosas que antes no teníamos: el alcance '
         'acordado (CIERRE, SAF, PO y <span class="mono">dbo.REPORTE_COBRANZA_INTEGRACION</span>) y las respuestas del '
         'cliente, incluidos los tres catálogos reales de <span class="mono">Quiero_Confianza</span>. Nada se borra: '
         'lo que sale del alcance queda registrado con su evidencia por si alguien lo retoma.</p>')
b.append('<div class="kpis">'
         + f'<div class="kpi"><b>{len(hall)}</b><span>hallazgos originales</span></div>'
         + f'<div class="kpi ok"><b>{len(cerr)}</b><span>cerrados por respuesta</span></div>'
         + f'<div class="kpi"><b>{len(fuera)}</b><span>fuera del alcance</span></div>'
         + f'<div class="kpi c"><b>{len(NUEVOS)}</b><span>nuevos por los catálogos</span></div>'
         + f'<div class="kpi a"><b>{len(vivos) + len(NUEVOS)}</b><span>vigentes en foco</span></div></div>')

b.append('<h2>Cómo queda el semáforo</h2>')
b.append('<table><thead><tr><th>Severidad</th><th>Antes</th><th>Después</th><th>Qué lo movió</th></tr></thead><tbody>')
razon = ['Se cierran 5 hallazgos de SP_IND_GEN_MES_MOD y de los cuatro PO.SYS_SP_* que serán borrados, y suben dos '
         'por evidencia de catálogo (OPI VALOR y las listas de COD_ORIGEN)',
         'Bajan los tres hallazgos de NOLOCK y los dos de objetos sin invocador; entran cuatro nuevos de catálogo',
         'Reciben los que bajaron de alto', 'Sin cambios']
for i, k in enumerate(('Critico', 'Alto', 'Medio', 'Bajo')):
    b.append(f'<tr><td><span class="pill {PILL[k]}">{k}</span></td><td class="num">{antes[i]}</td>'
             f'<td class="num">{despues[i]}</td><td>{razon[i]}</td></tr>')
b.append('</tbody></table>')

b.append('<h2>Hallazgos nuevos que salen de los catálogos reales</h2>')
for n in NUEVOS:
    b.append(f'<div class="card rojo"><h3><span class="pill {PILL[n["sev"]]}">{n["sev"]}</span> '
             f'<span class="mono">{n["id"]}</span> &middot; {e(n["titulo"])}</h3>'
             f'<p class="q">Objetos</p><p class="mono">{e(n["obj"])}</p>'
             f'<p class="q">Evidencia</p><p>{e(n["det"])}</p>'
             f'<p class="q">Remediación</p><p>{e(n["acc"])}</p></div>')

b.append('<h2>Hallazgos que se cierran con las respuestas</h2>')
b.append('<p>Se cierran porque el objeto que los origina no está en uso, no porque el defecto se haya corregido. '
         'La condición para cerrarlos de verdad es el <span class="mono">DROP</span> de esos objetos: mientras sigan '
         'en la base, alguien puede ejecutarlos.</p>')
b.append('<table><thead><tr><th>ID</th><th>Severidad original</th><th>Hallazgo</th><th>Por qué se cierra</th></tr></thead><tbody>')
for h in cerr:
    b.append(f'<tr><td class="mono">{h["id"]}</td><td><span class="pill {PILL[h["sev"]]}">{h["sev"]}</span></td>'
             f'<td>{e(h["titulo"])}</td><td>{e(h["motivo"])}</td></tr>')
b.append('</tbody></table>')

b.append('<h2>Hallazgos que cambian de severidad o de lectura</h2>')
b.append('<table><thead><tr><th>ID</th><th>Antes</th><th>Ahora</th><th>Hallazgo</th><th>Qué cambió</th></tr></thead><tbody>')
for h in sorted([x for x in hall if x['estado'] in ('sube', 'baja', 'reencuadre')],
                key=lambda x: (SEV_ORDEN[x['sev_nueva']] if x['sev_nueva'] in SEV_ORDEN else 9, x['id'])):
    et, cls = ETQ[h['estado']]
    b.append(f'<tr><td class="mono">{h["id"]}</td><td><span class="pill {PILL[h["sev"]]}">{h["sev"]}</span></td>'
             f'<td><span class="pill {PILL.get(h["sev_nueva"], "info")}">{h["sev_nueva"]}</span> '
             f'<span class="tag">{et}</span></td><td>{e(h["titulo"])}</td><td>{e(h["motivo"])}</td></tr>')
b.append('</tbody></table>')

b.append('<h2>Hallazgos fuera del alcance acordado</h2>')
b.append('<p>Quedan documentados y sin dueño. Dos merecen una decisión explícita aunque no los trabajemos: '
         '<span class="mono">edc.SP_Genera_Ordenes_Dummy</span> inserta montos aleatorios en tablas de CFDI contra '
         'créditos reales, y <span class="mono">PAG.SP_OBTENER_NUC_DINAMICO</span> empareja pagos con un LIKE '
         'invertido.</p>')
b.append('<table><thead><tr><th>ID</th><th>Severidad</th><th>Hallazgo</th><th>Motivo</th></tr></thead><tbody>')
for h in fuera:
    b.append(f'<tr><td class="mono">{h["id"]}</td><td><span class="pill {PILL[h["sev"]]}">{h["sev"]}</span></td>'
             f'<td>{e(h["titulo"])}</td><td>{e(h["motivo"])}</td></tr>')
b.append('</tbody></table>')

b.append('<h2>Hallazgos vigentes sin cambio</h2>')
b.append('<p>Siguen tal cual: ni el alcance ni las respuestas los tocan.</p>')
b.append('<table><thead><tr><th>ID</th><th>Severidad</th><th>Categoria</th><th>Hallazgo</th></tr></thead><tbody>')
for h in sorted([x for x in hall if x['estado'] == 'vigente'], key=lambda x: (SEV_ORDEN[x['sev']], x['id'])):
    b.append(f'<tr><td class="mono">{h["id"]}</td><td><span class="pill {PILL[h["sev"]]}">{h["sev"]}</span></td>'
             f'<td>{e(h.get("cat", ""))}</td><td>{e(h["titulo"])}</td></tr>')
b.append('</tbody></table>')

b.append('<h2>Lo que sigue abierto con el negocio</h2><div class="card ambar"><ul>'
         '<li>El umbral COVID: se homologa contra la columna del origen, pero hay que decidir que pasa con las cifras '
         'ya publicadas por los 62 objetos que usaron el umbral.</li>'
         '<li>La regla única de cartera no restringida por <span class="mono">COD_ORIGEN</span>, incluido si 046 '
         '(CARTERA_CASTIGADA) pertenece a la misma bolsa que 008 y 031.</li>'
         '<li>El rubro sobreviviente de cada par duplicado del origen y el destino de los dos marcados "no usar".</li>'
         '<li>Si <span class="mono">PRINCIPAL_VENCIDO</span> e <span class="mono">INTERES_NO_EXIGIBLES</span> son '
         'literales obsoletos o rubros de otra fuente.</li>'
         '<li>La clasificación de cartera y administrador de los seis tipos sin definir.</li>'
         '<li>La participación por origen de Afirme (012, 027, 030) y la del sindicado, hoy sin valor.</li></ul></div>')

open(os.path.join(AUD, '16_reclasificacion.html'), 'w').write(acentuar(page(
    'Reclasificación de hallazgos con el alcance acordado',
    'CIERRE · SAF · PO · dbo.REPORTE_COBRANZA_INTEGRACION — releídos con las respuestas del cliente y los catálogos reales',
    '\n'.join(b))))

# --------------------------------------------------------------- doc 17
V = json.load(open(os.path.join(AUD, 'vigencia_objetos.json')))
P = json.load(open(os.path.join(AUD, 'patron_referencia.json')))
grupos = collections.OrderedDict()
for x in sorted(V, key=lambda y: (y['estado'], y['obj'])):
    grupos.setdefault(x['estado'], []).append(x)

EXPL = {
 'Vigente': 'Están en el export de producción y algo los invoca: otro objeto productivo, un reporte .rdl o un job.',
 'Vigente sin invocador conocido': 'Están en producción pero nadie los llama dentro del repositorio: su disparo esta '
    'fuera (job del agente, CAS o ejecución manual). Son los candidatos naturales a ser puntos de entrada del cierre '
    'diario, y hay que confirmarlos contra el historial de jobs.',
 'Vigente de referencia': 'El cliente los señaló como la implementación correcta.',
 'Ausente del export (indeterminado)': 'No aparecen en el export de BD_prod. Eso no prueba que no existan en '
    'producción: el export puede ser parcial. Es exactamente lo que resuelve la consulta de metadatos de la Fase 0.',
 'Candidato a baja': 'No están en el export, nadie los invoca y no alimentan reportes; o su nombre indica que son '
    'una versión paralela de otro objeto.',
 'Solo en el repositorio': 'No están en el export pero un reporte .rdl los ejecuta: o el reporte esta roto en '
    'producción, o el export es incompleto.',
 'Fuera de uso (declarado)': 'El cliente declaro que no están en uso.',
}

c = collections.Counter(x['estado'] for x in V)
b = []
b.append('<p class="lead">Insumo para la lista limpia que pedimos al cliente. No es una respuesta: es la evidencia que '
         'el repositorio puede dar por si solo sobre cada objeto de CIERRE, SAF, PO y el reporte de cobranza, para que '
         'la conversación sea sobre una tabla y no sobre memoria. La confirmación definitiva necesita metadatos de la '
         'instancia productiva, que no hemos consultado.</p>')
b.append('<div class="kpis">'
         + f'<div class="kpi"><b>{len(V)}</b><span>objetos en foco</span></div>'
         + f'<div class="kpi ok"><b>{sum(1 for x in V if x["en_prod"])}</b><span>en el export de producción</span></div>'
         + f'<div class="kpi a"><b>{c["Vigente sin invocador conocido"]}</b><span>sin invocador conocido</span></div>'
         + f'<div class="kpi m"><b>{c["Candidato a baja"]}</b><span>candidatos a baja</span></div>'
         + f'<div class="kpi c"><b>{sum(1 for x in V if not x["crea"] and not x["mod"])}</b><span>sin fecha en el encabezado</span></div></div>')

b.append('<h2>Cómo se clasificó</h2><div class="card azul"><p>Solo con lo que el repositorio permite verificar, sin '
         'tocar SQL Server:</p><ul>'
         '<li>presencia en el export de <span class="mono">BD_prod</span>;</li>'
         '<li>quién lo invoca, resolviendo el grafo de llamadas de los 245 objetos programables;</li>'
         '<li>si algún archivo <span class="mono">.rdl</span> lo ejecuta;</li>'
         '<li>fechas de creación y modificación declaradas en el encabezado del script (69 de 198 las traen);</li>'
         '<li>si escribe o solo lee, y si convive con hermanos por nombre;</li>'
         '<li>las declaraciones del cliente sobre objetos sin uso.</li></ul>'
         '<p>Ninguna de estas señales prueba ejecución. Por eso la columna de estado es una hipótesis con su motivo, '
         'y la lista se cierra con la consulta de la Fase 0.</p></div>')

b.append('<h2>Resumen</h2><table><thead><tr><th>Estado</th><th>Objetos</th><th>Qué significa</th></tr></thead><tbody>')
for k, v in sorted(c.items(), key=lambda kv: -kv[1]):
    b.append(f'<tr><td><b>{e(k)}</b></td><td class="num">{v}</td><td>{e(EXPL.get(k, ""))}</td></tr>')
b.append('</tbody></table>')

for k in grupos:
    b.append(f'<h2>{e(k)} &middot; {len(grupos[k])}</h2>')
    b.append('<table><thead><tr><th>Objeto</th><th>Líneas</th><th>En prod</th><th>Invocadores</th><th>Reportes</th>'
             '<th>Encabezado</th><th>Evidencia</th></tr></thead><tbody>')
    for x in grupos[k]:
        fech = ' / '.join(z for z in (x['crea'], x['mod']) if z) or '—'
        b.append(f'<tr><td class="mono">{e(x["obj"])}</td><td class="num">{x["lineas"]}</td>'
                 f'<td class="num">{"si" if x["en_prod"] else "no"}</td>'
                 f'<td class="num">{len(x["llamadores"])}</td><td class="num">{len(x["rdl"])}</td>'
                 f'<td class="num">{e(fech)}</td><td>{e(x["declarado"] or x["motivo"])}</td></tr>')
    b.append('</tbody></table>')

ref_col = [r for r in P if r['col']]
ref_fn = [r for r in P if r['fn']]
b.append('<h2>Divergencia frente al patrón de referencia</h2>')
b.append('<p>El cliente fijó <span class="mono">PO.SP_SND_COBRANZA</span> (línea 47) como la implementación correcta: '
         'la marca COVID se lee de la columna del origen y la separación balance / cuentas de orden se decide por la '
         'leyenda <span class="mono">CUENTAS DE ORDEN</span> en <span class="mono">OBSERVACION</span>. Esta es la '
         'medida de cuántos objetos productivos no lo hacen así.</p>')
b.append('<div class="kpis">'
         + f'<div class="kpi ok"><b>{len(ref_col)}</b><span>leen la columna del origen</span></div>'
         + f'<div class="kpi c"><b>{len(ref_fn)}</b><span>usan el umbral hardcodeado</span></div>'
         + f'<div class="kpi"><b>{sum(1 for r in P if r["co_obs"])}</b><span>leen OBSERVACION para cuentas de orden</span></div></div>')
b.append('<table><thead><tr><th>Objeto</th><th>Columna COVID del origen</th><th>dbo.FN_ES_COVID</th>'
         '<th>CUENTAS DE ORDEN por OBSERVACION</th><th>Lectura</th></tr></thead><tbody>')
for r in sorted(P, key=lambda r: (0 if r['col'] else 1, r['obj'])):
    if r['col']:
        lec = 'sigue el patrón de referencia'
    elif r['fn']:
        lec = 'deriva COVID del umbral NUM_CREDITO < 6051: candidato a homologar'
    elif r['lit']:
        lec = 'fija IND_COVID como literal'
    else:
        lec = 'toca IND_COVID o cuentas de orden sin decidirlo'
    b.append(f'<tr><td class="mono">{e(r["obj"])}</td><td class="num">{r["col"] or "—"}</td>'
             f'<td class="num">{r["fn"] or "—"}</td><td class="num">{r["co_obs"] or "—"}</td><td>{lec}</td></tr>')
b.append('</tbody></table>')

b.append('<h2>Lo que falta preguntar a la instancia, no al cliente</h2>')
b.append('<p>Tres consultas de solo lectura cierran la lista sin depender de memoria. Son parte de la Fase 0 y '
         'requieren permiso de consulta sobre la base de QA (CUA) y, para el historial de ejecución, sobre '
         'produccion.</p>')
b.append('<pre>-- 1. qué objetos existen de verdad y cuándo se modificaron\nSELECT s.name AS esquema, o.name, o.type_desc, o.create_date, o.modify_date\nFROM sys.objects o JOIN sys.schemas s ON s.schema_id = o.schema_id\nWHERE o.type IN (\'P\',\'FN\',\'IF\',\'TF\') AND s.name IN (\'CIERRE\',\'SAF\',\'PO\',\'dbo\')\nORDER BY s.name, o.name;\n\n-- 2. cuáles se han ejecutado desde el ultimo reinicio (evidencia, no memoria)\nSELECT OBJECT_SCHEMA_NAME(ps.object_id) AS esquema, OBJECT_NAME(ps.object_id) AS objeto,\n       ps.execution_count, ps.last_execution_time, ps.total_elapsed_time/1000 AS ms_total\nFROM sys.dm_exec_procedure_stats ps\nWHERE OBJECT_SCHEMA_NAME(ps.object_id) IN (\'CIERRE\',\'SAF\',\'PO\')\nORDER BY ps.last_execution_time DESC;\n\n-- 3. quien los dispara: pasos de job que los nombran\nSELECT j.name AS job, js.step_id, js.step_name, js.command\nFROM msdb.dbo.sysjobs j JOIN msdb.dbo.sysjobsteps js ON js.job_id = j.job_id\nWHERE js.command LIKE \'%SP_%\'\nORDER BY j.name, js.step_id;</pre>')
b.append('<div class="card ambar"><h3>Lo que necesitamos del cliente</h3><ul>'
         '<li>Confirmar el resultado de la consulta 2 sobre producción: es la única evidencia de ejecución real.</li>'
         '<li>Confirmar los 65 objetos sin invocador conocido: cuáles son puntos de entrada del cierre diario y '
         'cuáles quedaron sueltos.</li>'
         '<li>Autorizar el <span class="mono">DROP</span> de los objetos declarados sin uso: mientras existan, un '
         'error los puede ejecutar.</li>'
         '<li>Decir si el export de <span class="mono">BD_prod</span> es completo; si lo es, los objetos ausentes son '
         'candidatos a baja y no incógnitas.</li></ul></div>')

open(os.path.join(AUD, '17_objetos_vigentes.html'), 'w').write(acentuar(page(
    'Lista limpia de objetos vigentes',
    'CIERRE · SAF · PO · cobranza — evidencia de uso objeto por objeto, como insumo para la confirmación del cliente',
    '\n'.join(b))))

with open(os.path.join(AUD, '17_objetos_vigentes.csv'), 'w', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(['objeto', 'tipo', 'estado', 'lineas', 'en_prod', 'invocadores', 'reportes', 'creacion',
                'modificacion', 'escribe', 'motivo'])
    for x in sorted(V, key=lambda y: (y['estado'], y['obj'])):
        w.writerow([x['obj'], x['tipo'], x['estado'], x['lineas'], 'si' if x['en_prod'] else 'no',
                    len(x['llamadores']), len(x['rdl']), x['crea'], x['mod'],
                    'si' if x['escribe'] else 'no', x['declarado'] or x['motivo']])

print('16 y 17 generados. antes', antes, 'despues', despues,
      'cerrados', len(cerr), 'fuera', len(fuera), 'vivos', len(vivos))
