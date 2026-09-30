# -*- coding: utf-8 -*-
"""Genera los informes 19 (alcance productivo y normalización), 20 (plan de
ambiente QA confiable) y 21 (preguntas acotadas al alcance) a partir de
alcance_produccion.json, que produce analizar_alcance.py."""
import json
import pathlib

from plantilla import e, page

AQUI = pathlib.Path(__file__).resolve().parent
D = json.loads((AQUI / 'alcance_produccion.json').read_text(encoding='utf-8'))

P = D['patrones']
OBJ = {o['objeto']: o for o in D['objetos']}
CLASES = D['clases']
DEP = D['dependencias_de_la_lista']
SIN_USO = D['fuera_de_lista_sin_uso']


def kpis(items):
    return ('<div class="kpis">' + ''.join(
        f'<div class="kpi {c}"><b>{e(v)}</b><span>{e(t)}</span></div>'
        for v, t, c in items) + '</div>')


def tabla(cols, filas, clases=''):
    h = ''.join(f'<th>{e(c)}</th>' for c in cols)
    b = ''
    for f in filas:
        b += '<tr>' + ''.join(f'<td>{c}</td>' for c in f) + '</tr>'
    return f'<table class="{clases}"><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table>'


# --------------------------------------------------------------------------- 19
AUSENTES = [o for o in D['objetos'] if o['clase'] == 'ausente_prod']
REAL = sorted((o for o in D['objetos'] if o['clase'] == 'real'),
              key=lambda x: -x['lineas_dif'])

QUE_HACE = {
    'CIERRE.SP_IND_GEN_MES': 'cierre mensual de cartera individual (el SP más grande del alcance)',
    'CIERRE.SP_IND_GEN_MES_MOD': 'variante del cierre mensual individual que nos dijeron que ya no se usa',
    'CIERRE.SP_CMR_DIA': 'cierre diario comercial',
    'CIERRE.SP_SAF_SALDOS_SND': 'saldos SAF de la cartera sindicada',
    'CIERRE.SP_CASTIGO_INI_RPT': 'reporte de castigos inicial',
    'CIERRE.SP_CAS_CIERRE_RPT': 'reporte de cierre de castigos',
    'PO.SP_CAP_IMPORTA': 'importación de captura',
}

SENALES = [
    ('opi_valor_espacio', "Literal <code>'OPI VALOR'</code> (con espacio)",
     'no existe en <code>PR.PR_RUBRO</code>: el predicado nunca casa y el importe no entra a la póliza', 'c'),
    ('principal_vencido', "Literal <code>'PRINCIPAL_VENCIDO'</code>",
     'rubro que no está en el catálogo autoritativo; hay que confirmar si es alias', 'a'),
    ('interes_no_exigibles', "Literal <code>'INTERES_NO_EXIGIBLES'</code>",
     'idem: sin concepto contable definido en el catálogo', 'a'),
    ('cuentas_orden', "Clasificación por texto <code>'CUENTAS DE ORDEN'</code>",
     'balance vs. orden decidido por cadena de texto y no por <code>ind_cont_orden</code> del catálogo', 'c'),
    ('origen_not_in_shf', "<code>NOT IN (22,23,28,35)</code>",
     'los cuatro sindicados SHF escritos a mano y comparando el código como número', 'c'),
    ('origen_008_031', "<code>IN ('008','031'...)</code>",
     'la misma regla de origen escrita de otra forma en otros objetos', 'c'),
    ('tipo_credito_filtro', 'Filtros por <code>NUM_DESC_TIPO_CREDITO</code>',
     f"{len(D['listas_tipo_credito'])} listas distintas: es el hardcodeo de mayor volumen", 'c'),
    ('copia_catalogo', 'Lectura de la copia <code>PO.SAF_CAT_DESC_TIPO</code>',
     'copia desalineada del catálogo autoritativo', 'a'),
    ('cat_tipo_autoritativo', 'Lectura de <code>PR.PR_DESC_TIPOS_CREDITO</code>',
     'único origen autoritativo del tipo de cartera; se usa poco', 'ok'),
    ('cat_rubro_autoritativo', 'Lectura de <code>PR.PR_RUBRO</code>',
     'cero: dentro del alcance nadie lee el catálogo de rubros, viajan como literal', 'c'),
    ('cat_origen_autoritativo', 'Lectura de <code>PR.PR_ORIGEN_FONDOS</code>',
     'se usa en el cierre, pero la regla de "no restringido" sigue hardcodeada', 'm'),
    ('fn_es_covid', 'COVID por función <code>FN_ES_COVID</code>',
     'una de las dos implementaciones de la misma regla', 'a'),
    ('ind_covid', 'COVID por columna <code>IND_COVID</code>',
     'la otra implementación; conviven en los mismos cierres', 'a'),
    ('base_shadow', 'Referencias a <code>Quiero_Confianza_shadow</code>',
     'nombre de base escrito en el código: es lo que impide mover el código entre ambientes', 'c'),
    ('base_qa', 'Referencias a <code>Quiero_Confianza_CreditoPuente_QA</code>',
     'cero dentro del alcance: el hallazgo crítico L1-007 sale del alcance productivo', 'ok'),
    ('servidor_vinculado', 'Servidor vinculado <code>SRV-IONSQLAWS</code>',
     'cero dentro del alcance; los 24 usos están en los 3 SPs de pase QA/producción', 'a'),
    ('nolock', '<code>WITH (NOLOCK)</code>',
     'sobre réplica de lectura no amenaza al core, pero sí la reproducibilidad de la cifra', 'm'),
    ('getdate', '<code>getdate()</code>',
     'fecha del reloj en vez de fecha de negocio parametrizada', 'm'),
    ('fecha_literal', "Fechas literales <code>'20######'</code>",
     "incluye <code>FECHA_SISTEMA='20260123'</code> en el cierre comercial (Q06)", 'c'),
]

NORMALIZACION = [
    ('1. Relacional (tablas)',
     'Las tablas del alcance están en 3FN en lo esencial, pero hay catálogos paralelos que existen y '
     f'nadie usa: <code>PO.CAT_RUBROS</code>, <code>CAT_PRODUCTOS</code>, <code>CAT_FONDEOS</code>, '
     '<code>CAT_TRANSACCIONES</code> y <code>CAT_GARANTIAS</code> solo aparecen en la definición de '
     f'<code>PO.REGLA_CONTABLE_INDIVIDUAL</code>. En total {sum(1 for x in SIN_USO if x["tipo"] == "Table")} '
     'tablas y 1 función del paquete no las menciona ningún objeto de la lista.',
     'Aceptable', 'm'),
    ('2. Catálogos',
     f"{P['copia_catalogo']['dentro_obj']} objetos leen la copia <code>PO.SAF_CAT_DESC_TIPO</code> y solo "
     f"{P['cat_tipo_autoritativo']['dentro_obj']} leen el catálogo autoritativo "
     f"<code>PR.PR_DESC_TIPOS_CREDITO</code>. El catálogo de rubros <code>PR.PR_RUBRO</code> "
     '<b>no lo lee ningún objeto del alcance</b>: los rubros viajan como cadena literal.',
     'Roto', 'c'),
    ('3. Reglas de negocio',
     f"{P['tipo_credito_filtro']['dentro']} filtros por tipo de cartera en "
     f"{P['tipo_credito_filtro']['dentro_obj']} objetos, con {len(D['listas_tipo_credito'])} listas distintas; "
     'COVID implementado dos veces (función y columna); el origen de fondos escrito de tres formas; '
     'balance vs. cuentas de orden decidido por texto. La regla vive en el predicado, no en un dato.',
     'Roto', 'c'),
    ('4. Ambientes',
     f"{P['base_shadow']['dentro_obj']} objetos traen el nombre de la base en el código "
     f"({P['base_shadow']['dentro']} referencias). De los 169 objetos presentes en las dos copias, "
     f"{CLASES.get('solo_base', 0)} difieren <b>únicamente</b> por ese nombre. Además hay 3 SPs que "
     'copian datos entre instancias con servidor vinculado y un umbral COVID distinto por ambiente.',
     'Roto', 'c'),
    ('5. Tiempo e identidad',
     f"{P['getdate']['dentro']} usos de <code>getdate()</code> como fecha de negocio y "
     f"{P['fecha_literal']['dentro']} fechas literales en {P['fecha_literal']['dentro_obj']} objetos, "
     "incluida <code>'20260123'</code> en el cierre comercial. Sin fecha de negocio única no hay "
     'reproceso reproducible ni sello de configuración.',
     'Roto', 'c'),
]

DESTINO = [
    ('Tipo de cartera', 'literal en 400 predicados y 25 listas',
     '<code>PR.PR_DESC_TIPOS_CREDITO</code> + banderas por proceso en el portal', 'Cartera'),
    ('Rubro / concepto', 'cadena literal en el SP y columnas por rubro',
     '<code>PR.PR_RUBRO</code> + mapeo rubro&rarr;cuenta administrado', 'Contabilidad'),
    ('Origen de fondos', "<code>IN ('008','031')</code> / <code>NOT IN (22,23,28,35)</code>",
     '<code>PR.PR_ORIGEN_FONDOS</code> + bandera <code>es_restringido</code>', 'Tesorería'),
    ('Balance vs. orden', "texto <code>'CUENTAS DE ORDEN'</code>",
     'bandera <code>ind_cont_orden</code> del catálogo de rubros', 'Contabilidad'),
    ('COVID', 'función y columna en paralelo',
     'una sola definición con vigencia y umbral versionado', 'Riesgos'),
    ('Nombre de la base', 'literal en 124 objetos',
     'sinónimo por ambiente; el código no nombra la base', 'TI / DBA'),
    ('Fecha de negocio', '<code>getdate()</code> y literales',
     'parámetro obligatorio + sello de la corrida', 'Operación'),
]


def doc19():
    b = ['<p class="lead">El cliente entregó la lista de objetos que hoy participan en la póliza contable '
         f'(<code>{e("insumos/sp_relacionados_a_poliza.txt")}</code>, {D["total_lista"]} nombres, '
         f'{D["unicos"]} únicos). Este informe acota la auditoría a esa lista: qué queda dentro, qué queda '
         'fuera, qué dependencias arrastra y cómo cambia la lectura de la normalización.</p>']
    b.append(kpis([
        (D['unicos'], 'objetos declarados en uso', 'b'),
        (len(DEP), 'dependencias que la lista no nombra', 'm'),
        (len(AUSENTES), 'de la lista ausentes del export de producción', 'c'),
        (len(REAL), 'con diferencia real entre ambientes', 'a'),
        (CLASES.get('solo_base', 0), 'difieren solo por el nombre de la base', 'm'),
        (len(SIN_USO), 'objetos del paquete sin uso desde la lista', 'b'),
    ]))

    b.append('<h2>1. Qué prueba la lista y qué no</h2>')
    b.append('<div class="card azul"><p>La lista es una <b>declaración de uso</b>, no telemetría. Vale como '
             'acotamiento de alcance y como fuente de la conversación con el equipo, pero no sustituye la '
             'evidencia de ejecución: eso sale de <code>sys.dm_exec_procedure_stats</code>, del historial de '
             'jobs y de las trazas, que siguen requiriendo acceso de consulta a la instancia.</p>'
             '<p class="q">consecuencia inmediata</p><p>Con la lista en la mano, <b>estar o no en el export de '
             f'<code>BD_prod</code> deja de ser indicio de baja</b>: {len(AUSENTES)} objetos que el cliente '
             'declara en uso no están en ese export. Eso cambia la lectura del informe de objetos vigentes: '
             'no eran candidatos a baja, el export estaba incompleto.</p></div>')

    b.append('<h2>2. Composición del alcance</h2>')
    b.append(tabla(['Esquema', 'Objetos en la lista', 'Papel en la póliza'], [
        ('CIERRE', D['por_esquema'].get('CIERRE', 0), 'cierre diario y mensual, individual y comercial, y sus reportes'),
        ('PO', D['por_esquema'].get('PO', 0), 'movimientos, devengos, castigos, traspasos y armado de la póliza'),
        ('SAF', D['por_esquema'].get('SAF', 0), 'tasas y alertas'),
        ('dbo', D['por_esquema'].get('dbo', 0), 'reporte de cobranza y funciones de apoyo'),
        ('RPT', D['por_esquema'].get('RPT', 0), 'saldos de castigos y reestructuras'),
    ]))
    b.append(f'<div class="card ambar"><h3>El alcance real de instalación es mayor que la lista</h3>'
             f'<p>Los {D["unicos"]} objetos de la lista usan {len(DEP)} objetos que la lista no menciona: '
             f'{sum(1 for x in DEP if x["tipo"] == "Table")} tablas, '
             f'{sum(1 for x in DEP if x["tipo"] == "UserDefinedFunction")} funciones y 1 tipo tabla. '
             f'Para armar un ambiente que corra la póliza hay que instalar <b>{D["unicos"] + len(DEP)} '
             'objetos</b>, no 188. Es el número que usa el plan de QA.</p></div>')

    b.append('<h2>3. Los objetos declarados en uso que no están en el export de producción</h2>')
    b.append(tabla(['Objeto', 'Qué es', 'Consecuencia'],
                   [(f'<code>{e(o["objeto"])}</code>',
                     e(QUE_HACE.get(o['objeto'], 'reporte o vista del cierre (sufijo _VIS / _RPT)')),
                     'falta su DDL vigente: no se puede auditar ni instalar en un ambiente nuevo')
                    for o in AUSENTES]))
    b.append('<div class="card rojo"><p>Entre los ausentes está <code>CIERRE.SP_IND_GEN_MES</code>, el cierre '
             'mensual de cartera individual, que es uno de los dos objetos centrales de la póliza. Auditamos su '
             'versión de desarrollo; <b>no tenemos su versión productiva</b>. También aparece '
             '<code>SP_IND_GEN_MES_MOD</code>, que en la ronda anterior nos dijeron que ya no se usaba: la lista '
             'lo contradice y hay que repreguntarlo (Q34).</p></div>')

    b.append('<h2>4. Diferencia entre las dos copias, dentro del alcance</h2>')
    b.append(tabla(['Clase', 'Objetos', 'Lectura'], [
        ('Idénticos', CLASES.get('identico', 0), 'no requieren decisión'),
        ('Difieren solo por el nombre de la base', CLASES.get('solo_base', 0),
         'los absorbe un sinónimo por ambiente: es trabajo mecánico, no reconciliación'),
        ('Diferencia real de lógica', CLASES.get('real', 0),
         'requieren decisión objeto por objeto sobre cuál versión es la correcta'),
        ('Ausentes del export de producción', CLASES.get('ausente_prod', 0),
         'hay que pedir el DDL a la instancia'),
    ]))
    b.append(tabla(['Objeto con diferencia real', 'Líneas que difieren'],
                   [(f'<code>{e(o["objeto"])}</code>', o['lineas_dif']) for o in REAL]))
    b.append('<div class="card azul"><p>Es una buena noticia para el proyecto: el drift entre ambientes es '
             f'<b>mecánico en {CLASES.get("solo_base", 0)} objetos</b> y solo {CLASES.get("real", 0)} tienen '
             'divergencia de lógica, concentrada en <code>CIERRE.SP_SAF_SALDOS</code>. La reconciliación de '
             'código no es el cuello de botella; el cuello de botella son los datos y el aislamiento del '
             'ambiente.</p></div>')

    b.append('<h2>5. Qué sale del alcance</h2>')
    sps = [x['objeto'] for x in SIN_USO if x['tipo'] == 'StoredProcedure']
    b.append(f'<p>{len(SIN_USO)} objetos del paquete no están en la lista y ningún objeto de la lista los '
             f'menciona: {len(sps)} procedimientos, {sum(1 for x in SIN_USO if x["tipo"] == "Table")} tablas y '
             '<code>dbo.FN_TIPO_CREDITO</code>, una función que clasifica el tipo de crédito y que nadie usa '
             '(la abstracción existía y se abandonó).</p>')
    b.append(tabla(['Procedimiento fuera del alcance', 'Nota'],
                   [(f'<code>{e(o)}</code>',
                     'copia datos entre instancias por servidor vinculado (ver informe de QA)'
                     if 'PASE' in o else
                     ('versión anterior del generador de póliza' if '_POL' in o or 'GEN_DIA' in o
                      else 'apoyo o reporte no ligado a la póliza'))
                    for o in sps]))
    b.append('<div class="card rojo"><h3>Hallazgo nuevo: hay un camino de escritura entre instancias</h3>'
             '<p>Tres de esos procedimientos <code>PO.SP_SAF_POLIZA_PASE_*</code> copian póliza y movimientos '
             f"entre instancias usando el servidor vinculado <code>[SRV-IONSQLAWS\\SAF].[KARDIA]</code> "
             f"({P['servidor_vinculado']['fuera']} referencias). Uno de ellos, "
             '<code>SP_SAF_POLIZA_PASE_EXT_QA_PROD</code>, hace <code>DELETE</code> y <code>INSERT</code> '
             '<b>contra las tablas de póliza histórica del servidor vinculado</b>, filtrando por fecha. '
             'No podemos confirmar desde el código a qué instancia apunta ese nombre; si apunta a producción, '
             'existe un camino por el que datos de un ambiente de prueba entran a la contabilidad. Es Q32 y es '
             'la razón principal por la que el QA actual no puede tratarse como aislado.</p></div>')

    b.append('<h2>6. Dónde caen los hallazgos: dentro o fuera del alcance</h2>')
    b.append('<p>Conteos por análisis estático sobre la copia de desarrollo del paquete de septiembre, '
             'descontando comentarios. "Dentro" son los objetos de la lista; "fuera" es el resto del paquete '
             'en los esquemas de foco.</p>')
    b.append(tabla(['Señal', 'Dentro: objetos / usos', 'Fuera: objetos / usos', 'Lectura'],
                   [(t, f"{P[k]['dentro_obj']} / {P[k]['dentro']}",
                     f"{P[k]['fuera_obj']} / {P[k]['fuera']}",
                     f'<span class="pill {c}">{"cierra" if c == "ok" else "vive"}</span> {n}')
                    for k, t, n, c in SENALES]))
    b.append('<div class="card ambar"><p>El acotamiento <b>no salva casi nada</b>: los literales de rubro '
             'inexistentes, las listas de origen contradictorias, la clasificación de cuentas de orden por texto '
             'y la fecha fija del cierre comercial están todos dentro del alcance. Lo único que sale es el '
             'crítico de la base <code>..._CreditoPuente_QA</code> (L1-007) y los 24 usos del servidor vinculado, '
             'que pasan a ser un hallazgo de ambientes en vez de un hallazgo de la póliza.</p></div>')

    b.append('<h2>7. Estado de normalización, acotado al alcance</h2>')
    b.append('<p>La pregunta "&iquest;está normalizada la base?" se contesta en cinco capas. Las tablas están '
             'razonablemente normalizadas; lo que no está normalizado es la <b>regla</b>.</p>')
    b.append(tabla(['Capa', 'Evidencia dentro del alcance', 'Estado'],
                   [(t, d, f'<span class="pill {c}">{e(s)}</span>') for t, d, s, c in NORMALIZACION]))
    b.append('<div class="card rojo"><p>Conclusión para el cliente: <b>llegar a tercera forma normal en las '
             'tablas no resuelve el problema</b>. Mientras el predicado que decide si un crédito participa en el '
             'castigo o en el devengo viva en el texto del procedimiento, cada concepto nuevo seguirá siendo un '
             'cambio de código y una liberación. La normalización que falta es la de la regla: sacarla del SP y '
             'ponerla en catálogo con banderas, vigencia y aprobación.</p></div>')

    b.append('<h2>8. Dónde debe vivir cada regla</h2>')
    b.append(tabla(['Regla', 'Dónde vive hoy', 'Dónde debe vivir', 'Quién la administra'],
                   [(a, b_, c, f'<span class="tag">{e(d)}</span>') for a, b_, c, d in DESTINO]))

    b.append('<h2>9. Cómo se reproduce este análisis</h2>')
    b.append('<pre>cd auditoria\npython3 analizar_alcance.py /ruta/al/paquete   # escribe alcance_produccion.json\n'
             'python3 generar_alcance_qa.py                    # escribe 19, 20 y 21</pre>')
    b.append('<p>El insumo del cliente quedó versionado en <code>auditoria/insumos/sp_relacionados_a_poliza.txt</code>. '
             'Ningún script toca una instancia de SQL Server.</p>')
    return page('Alcance productivo y estado de normalización',
                f'Auditoría acotada a los {D["unicos"]} objetos que el cliente declara en uso para la póliza contable',
                '\n'.join(b))


# --------------------------------------------------------------------------- 20
EVIDENCIA = [
    ('Existe un camino de escritura entre instancias',
     'Tres SPs copian póliza y movimientos por servidor vinculado, uno de ellos con <code>DELETE</code>/'
     '<code>INSERT</code> sobre el destino filtrando por fecha. Un ambiente que puede escribir en otro '
     'no es un ambiente de prueba.', 'c'),
    ('El QA actual tiene una base que producción no tiene',
     'Cuatro objetos leen <code>Quiero_Confianza_CreditoPuente_QA</code>, que no aparece en ningún objeto '
     'del alcance productivo. El QA no es una copia del productivo: es otra topología.', 'c'),
    ('Las reglas difieren por ambiente',
     'El umbral COVID es 6086 en una copia y 6051 en la otra. Si la regla difiere, el QA no puede usarse '
     'como oráculo de equivalencia.', 'c'),
    ('No hay línea base conocida de datos',
     'No sabemos de qué fecha son los datos del QA ni por qué proceso llegaron: los SPs de pase copian por '
     'fecha y borran el destino. Sin fecha de corte conocida no hay día espejo contra producción.', 'c'),
    ('El export de código está incompleto',
     f'{len(AUSENTES)} objetos declarados en uso no están en el export de producción, incluido el cierre '
     'mensual individual. Cualquier reconciliación partiría de un inventario incompleto.', 'a'),
    ('El drift de código, en cambio, es chico',
     f'{CLASES.get("solo_base", 0)} objetos difieren solo por el nombre de la base y {CLASES.get("real", 0)} '
     'por lógica. Reconstruir no cuesta más que reconciliar, porque el código casi no hay que reconciliarlo.', 'ok'),
]

COMPARATIVA = [
    ('Punto de partida', 'respaldo de producción restaurado a una fecha de corte declarada',
     'estado actual del QA, de origen y fecha desconocidos'),
    ('Inventario', 'lo instalado es exactamente lo que se decidió instalar',
     'hay que descubrirlo objeto por objeto y no tenemos el DDL de 19'),
    ('Aislamiento', 'sin servidores vinculados; el código no nombra la base (sinónimos)',
     'hay que localizar y desactivar los caminos existentes sin romper lo que dependa de ellos'),
    ('Oráculo de equivalencia', 'día espejo contra producción desde el primer día',
     'no hay, hasta reconciliar datos y reglas divergentes'),
    ('Riesgo de tocar producción', 'nulo: ambiente nuevo, sin rutas de escritura',
     'existe mientras vivan los SPs de pase y los servidores vinculados'),
    ('Esfuerzo estimado', '1 sesión de trabajo mía por etapa, 6 etapas, sin contar esperas de '
     'aprovisionamiento y respaldo',
     'similar o mayor, con resultado no garantizado: si el inventario sale incompleto se termina '
     'reconstruyendo igual'),
    ('Resultado', 'ambiente certificado, reproducible y documentado',
     'ambiente probablemente utilizable, pero no demostrable'),
]

ETAPAS = [
    ('E0', 'Inventario de la instancia (solo lectura)',
     ['Correr los scripts de <code>auditoria/fase0/</code> contra producción y contra el QA actual: '
      '<code>sys.objects</code>, <code>sys.sql_modules</code>, <code>sys.dm_exec_procedure_stats</code>, '
      '<code>msdb.dbo.sysjobs</code>, <code>sys.servers</code>, <code>sys.synonyms</code> y permisos.',
      f'Obtener el DDL vigente de los {len(AUSENTES)} objetos que faltan del export.',
      'Mapear qué jobs disparan el cierre, con qué parámetros y en qué orden.',
      'Documentar a qué instancia apunta <code>SRV-IONSQLAWS</code> y quién tiene permiso de usarlo.'],
     'Inventario firmado de los objetos, jobs, permisos y rutas entre instancias; DDL completo de los '
     f'{D["unicos"] + len(DEP)} objetos del alcance.'),
    ('E1', 'Restauración y aislamiento',
     ['Restaurar <code>KARDIA</code> y una copia de <code>Quiero_Confianza</code> a una <b>misma fecha de '
      'corte declarada</b> en la instancia nueva.',
      'Prohibir servidores vinculados en el ambiente: si un objeto los necesita, se sustituye por carga '
      'controlada de archivo.',
      'Crear los sinónimos por ambiente y dejar el código sin ningún nombre de base literal '
      '(<code>auditoria/fase1/generar_sinonimos.py</code> ya genera el juego).',
      'Enmascarar datos personales según el alcance que defina legal (Q10).'],
     'Ambiente que corre sin salir de sí mismo, con fecha de corte conocida y sin ninguna ruta de '
     'escritura hacia producción.'),
    ('E2', 'Instalación del alcance',
     [f'Instalar los {D["unicos"]} objetos de la lista más las {len(DEP)} dependencias que arrastran.',
      f'Resolver los {CLASES.get("real", 0)} objetos con divergencia real declarando cuál versión es la '
      'productiva (los otros los absorbe el sinónimo).',
      'No instalar los procedimientos de pase entre instancias.',
      'Dejar el juego de scripts en control de versiones: el ambiente se reconstruye desde el repositorio, '
      'no desde una copia manual.'],
     'Ambiente reconstruible desde el repositorio en una corrida, con inventario que cuadra objeto por objeto.'),
    ('E3', 'Catálogos y configuración del portal',
     ['Cargar los catálogos autoritativos <code>PR.PR_DESC_TIPOS_CREDITO</code>, <code>PR.PR_RUBRO</code> y '
      '<code>PR.PR_ORIGEN_FONDOS</code> como origen único.',
      'Crear las tablas de configuración del portal (banderas, vigencias, aprobaciones, bitácora) y sembrarlas '
      'con las reglas que hoy están hardcodeadas.',
      'Publicar la configuración inicial con el flujo de cuatro ojos, para que el propio alta quede en bitácora.'],
     'Configuración versionada y sellada, equivalente a lo que hoy dice el código.'),
    ('E4', 'Prueba de equivalencia (día espejo)',
     ['Correr el cierre del día de corte con el código actual y comparar la póliza contra la de producción de '
      'ese día: debe dar cero diferencias. Ese es el certificado del ambiente.',
      'Repetir con el código parametrizado (leyendo catálogo en vez de listas): también cero diferencias.',
      'Guardar las dos corridas con su sello de configuración.'],
     'Evidencia de que el ambiente reproduce la contabilidad y de que la parametrización no la cambia.'),
    ('E5', 'Cierre simulado y gates',
     ['Simular un mes completo, incluyendo el alta de un concepto nuevo desde el portal sin liberar código: '
      'es la demostración de valor para el cliente.',
      'Activar el gate de CI que rechaza código con nombre de base literal, con lista hardcodeada de tipos o '
      'con fecha literal (<code>auditoria/fase1/04_gate_ci.py</code>).',
      'Definir la ventana y el procedimiento de promoción QA &rarr; producción, con producción en solo lectura '
      'para el portal.'],
     'Proceso de cambio cerrado: nada entra a producción sin pasar por el ambiente certificado.'),
]

NECESIDADES = [
    ('Instancia nueva de SQL Server para QA', 'TI / infraestructura', 'misma versión y collation que producción'),
    ('Respaldo de <code>KARDIA</code> y de la réplica de <code>Quiero_Confianza</code> a una fecha de corte',
     'DBA', 'y el tamaño, para dimensionar el disco'),
    ('DDL vigente de los 19 objetos ausentes del export', 'DBA', 'bloquea E0'),
    ('Acceso de consulta de solo lectura a producción y al QA actual', 'DBA / seguridad',
     'para el inventario; sin esto E0 no se puede cerrar'),
    ('Definición del enmascaramiento de datos personales', 'Legal / seguridad', 'Q10, bloquea E1'),
    ('Copia de la póliza publicada del día de corte', 'Contabilidad', 'es el patrón de la prueba de equivalencia'),
    ('Confirmación de a qué instancia apunta el servidor vinculado', 'DBA', 'Q32, hallazgo de control'),
]


def doc20():
    b = ['<p class="lead">Recomendación: <b>construir un ambiente de QA nuevo a partir de un respaldo de '
         'producción</b> y no intentar reparar el actual. No por el código &mdash; el código casi no tiene drift '
         '&mdash; sino porque el QA actual no puede usarse como patrón de comparación ni demostrarse aislado.</p>']
    b.append(kpis([
        (D['unicos'] + len(DEP), 'objetos a instalar en el ambiente nuevo', 'b'),
        (CLASES.get('real', 0), 'objetos que exigen decidir cuál versión es la buena', 'a'),
        (CLASES.get('solo_base', 0), 'objetos que resuelve un sinónimo', 'm'),
        (P['servidor_vinculado']['fuera'], 'usos de servidor vinculado a eliminar', 'c'),
        ('6', 'etapas del plan', 'b'),
    ]))

    b.append('<h2>1. Por qué reconstruir y no reparar</h2>')
    b.append(tabla(['Evidencia', 'Detalle', 'Peso'],
                   [(t, d, f'<span class="pill {c}">{"a favor de reparar" if c == "ok" else "a favor de reconstruir"}</span>')
                    for t, d, c in EVIDENCIA]))
    b.append('<div class="card rojo"><h3>El argumento corto</h3><p>Un ambiente de prueba sirve para dos cosas: '
             'que puedas romperlo sin consecuencias y que puedas comparar su resultado contra el real. El QA '
             'actual no cumple ninguna de las dos: tiene un camino de escritura hacia otra instancia y no tiene '
             'una fecha de corte conocida contra la cual comparar. Repararlo cuesta lo mismo que reconstruirlo y '
             'termina en un ambiente que funciona pero no se puede demostrar.</p></div>')

    b.append('<h2>2. Comparativa de las dos opciones</h2>')
    b.append(tabla(['Criterio', 'A. QA nuevo desde respaldo (recomendada)', 'B. Reparar el QA actual'],
                   COMPARATIVA))
    b.append('<div class="card azul"><h3>Cuándo cambiaría de recomendación</h3><p>Si la etapa E0 muestra que el '
             'QA actual (a) tiene inventario completo y equivalente al alcance, (b) no tiene ningún servidor '
             'vinculado ni permiso de escritura hacia otra instancia, (c) tiene fecha de corte documentada y '
             '(d) puede restaurarse a voluntad, entonces repararlo es más corto y lo recomendaría. Las cuatro '
             'condiciones se verifican con consultas de solo lectura en un día; hasta entonces la recomendación '
             'es reconstruir.</p></div>')

    b.append('<h2>3. Plan por etapas</h2>')
    for cod, tit, pasos, acep in ETAPAS:
        b.append(f'<div class="ola"><h3>{cod}. {e(tit)}</h3><ul>'
                 + ''.join(f'<li>{p}</li>' for p in pasos)
                 + f'</ul><p class="q">criterio de aceptación</p><p>{acep}</p></div>')

    b.append('<h2>4. Reglas del ambiente nuevo</h2>')
    b.append('<div class="grid2">'
             '<div class="card verde"><h3>Obligatorio</h3><ul>'
             '<li>El código no nombra la base: siempre sinónimo.</li>'
             '<li>Fecha de negocio como parámetro; nunca <code>getdate()</code> ni literal.</li>'
             '<li>Toda regla de negocio sale de catálogo, no de una lista en el SP.</li>'
             '<li>Cada corrida guarda el sello de la configuración que usó.</li>'
             '<li>El ambiente se reconstruye desde el repositorio.</li></ul></div>'
             '<div class="card rojo"><h3>Prohibido</h3><ul>'
             '<li>Servidores vinculados y procedimientos de pase entre instancias.</li>'
             '<li>Escrituras hacia cualquier instancia que no sea la propia.</li>'
             '<li>Datos personales sin enmascarar.</li>'
             '<li>Cambios de configuración sin aprobación de cuatro ojos.</li>'
             '<li>Vigencias retroactivas.</li></ul></div></div>')

    b.append('<h2>5. Qué necesitamos del cliente</h2>')
    b.append(tabla(['Insumo', 'Quién lo entrega', 'Nota'], NECESIDADES))

    b.append('<h2>6. Qué cambia respecto del plan anterior</h2>')
    b.append(tabla(['Plan anterior (Fase 0 / Fase 1)', 'Plan corregido'], [
        ('Reconciliar los dos ambientes existentes objeto por objeto',
         'reconciliar solo lo que hace falta para instalar el alcance en un ambiente nuevo: '
         f'{CLASES.get("real", 0)} objetos, no 35'),
        ('Sustituir referencias de base por sinónimos en el ambiente actual',
         'la sustitución sigue igual, pero se aplica al instalar en el ambiente nuevo, donde no hay riesgo'),
        ('Probar equivalencia en el QA existente',
         'probar equivalencia contra la póliza publicada de un día de corte, que es un patrón verificable'),
        ('Alcance de instalación no definido',
         f'{D["unicos"] + len(DEP)} objetos, con inventario y dependencias medidos'),
        ('El riesgo de ambientes se trataba como drift de nombres',
         'se trata además como riesgo de control: hay un camino de escritura entre instancias (Q32)'),
    ]))
    return page('Ambiente QA confiable: reconstruir desde cero',
                'Comparativa contra reparar el QA actual, plan por etapas y criterios de aceptación',
                '\n'.join(b))


# --------------------------------------------------------------------------- 21
CIERRAN = [
    ('Q17-Q19', 'Existencia de los esquemas <code>PAG</code>, <code>edc</code>, <code>edcc</code>, '
     '<code>juicios</code>, <code>demandas</code>, <code>ori</code> y <code>cierre_puente</code>',
     'ninguno de esos esquemas está en la lista ni lo usa un objeto de la lista'),
    ('L1-007', 'Objetos que leen <code>Quiero_Confianza_CreditoPuente_QA</code>',
     f'los {P["base_qa"]["fuera_obj"]} objetos que la leen quedan fuera del alcance; pasa a ser hallazgo de '
     'ambientes (informe de QA) y no de la póliza'),
    ('Q29', 'Reporte a Afirme y <code>dbo.REPORTE</code> / <code>dbo.REPORTEAFIRME</code>',
     'no están en la lista y nadie de la lista los invoca'),
    ('Q24 (parcial)', 'Candidatos a baja del inventario de objetos vigentes',
     'la lista resuelve la duda al revés: no eran bajas, el export estaba incompleto'),
    ('Q20', 'Versión anterior del generador de póliza (<code>SP_IND_ADMINISTRADA_POL</code>, '
     '<code>SP_IND_COBRANZA_POL</code>)', 'fuera de la lista y sin invocador dentro de ella'),
]

VIGENTES = [
    ('Q01', "El literal <code>'OPI VALOR'</code> con espacio no existe en <code>PR.PR_RUBRO</code>",
     f"{P['opi_valor_espacio']['dentro_obj']} objetos del alcance", 'Contabilidad',
     'define si es alias, error de captura o rubro que debe crearse; si es error, hay importes que nunca '
     'entraron a la póliza'),
    ('Q02', "<code>'PRINCIPAL_VENCIDO'</code> e <code>'INTERES_NO_EXIGIBLES'</code> no están en el catálogo",
     f"{P['principal_vencido']['dentro_obj']} y {P['interes_no_exigibles']['dentro_obj']} objetos",
     'Contabilidad', 'sin concepto contable no se pueden migrar a catálogo'),
    ('Q10', 'Alcance del enmascaramiento de datos personales', 'todo el ambiente', 'Legal / seguridad',
     'bloquea la etapa E1 del QA nuevo'),
    ('Q15', 'Regla única de origen "no restringido"',
     f"{P['origen_not_in_shf']['dentro_obj']} objetos con <code>NOT IN (22,23,28,35)</code> y "
     f"{P['origen_008_031']['dentro_obj']} con <code>IN ('008','031'...)</code>", 'Tesorería / contabilidad',
     'son dos reglas distintas escritas como si fueran la misma; hay que declarar cuál es la correcta'),
    ('Q06', "Fecha fija <code>FECHA_SISTEMA='20260123'</code> en el cierre comercial", 'CIERRE.SP_CMR_GEN_MES',
     'Operación / contabilidad', 'sigue en las dos copias del paquete de septiembre; el mismo SP tiene 23 '
     'filtros parametrizados'),
    ('Q22', 'Balance vs. cuentas de orden decidido por el texto <code>\'CUENTAS DE ORDEN\'</code>',
     f"{P['cuentas_orden']['dentro_obj']} objetos", 'Contabilidad',
     'debe salir de <code>ind_cont_orden</code>; hoy no lo lee ningún objeto del alcance'),
    ('Q23', 'Umbral COVID y su vigencia (6051 vs 6086 según ambiente)',
     f"{P['fn_es_covid']['dentro_obj']} objetos por función y {P['ind_covid']['dentro_obj']} por columna",
     'Riesgos', 'dos implementaciones de la misma regla, con distinto valor por ambiente'),
    ('Q14 / Q31', 'Dueño del catálogo de tipos de cartera y de cada bandera', 'portal', 'Gobierno',
     'no bloquea el diseño, bloquea la operación del portal'),
    ('Q28', 'Participación por convenio y su vigencia', 'sindicados y administradas', 'Tesorería',
     'el estado "no establecido" debe bloquear el cierre, no heredar el valor anterior'),
]

NUEVAS = [
    ('Q32', '&iquest;A qué instancia apunta el servidor vinculado <code>[SRV-IONSQLAWS\\SAF]</code> y quién '
     'puede ejecutar <code>PO.SP_SAF_POLIZA_PASE_EXT_QA_PROD</code>?', 'DBA / seguridad', 'si',
     'ese procedimiento borra e inserta póliza histórica en el destino; si el destino es producción, hay un '
     'camino por el que datos de prueba entran a la contabilidad'),
    ('Q33', f'&iquest;Nos pueden entregar el DDL vigente de los {len(AUSENTES)} objetos declarados en uso que '
     'no vienen en el export de producción?', 'DBA', 'si',
     'incluye <code>CIERRE.SP_IND_GEN_MES</code>, el cierre mensual individual: hoy auditamos su versión de '
     'desarrollo sin poder compararla con la productiva'),
    ('Q34', '&iquest;<code>CIERRE.SP_IND_GEN_MES_MOD</code> se usa o no?', 'Operación', 'si',
     'en la ronda anterior nos dijeron que no; la lista de objetos en uso lo incluye'),
    ('Q35', f'De los {CLASES.get("real", 0)} objetos con lógica distinta entre las dos copias, '
     '&iquest;cuál versión es la productiva?', 'Desarrollo / DBA', 'si',
     'destaca <code>CIERRE.SP_SAF_SALDOS</code> con 310 líneas de diferencia: es la base de saldos de todo el cierre'),
    ('Q36', '&iquest;<code>PO.REGLA_CONTABLE_INDIVIDUAL</code> y los catálogos <code>PO.CAT_RUBROS</code>, '
     '<code>CAT_PRODUCTOS</code>, <code>CAT_FONDEOS</code>, <code>CAT_TRANSACCIONES</code> y '
     '<code>CAT_GARANTIAS</code> están en uso?', 'Desarrollo / contabilidad', 'no',
     'es una parametrización contable que ya existe y que ningún objeto del alcance usa; si está viva, el portal '
     'debe administrarla en vez de crear otra'),
    ('Q37', '&iquest;<code>dbo.FN_TIPO_CREDITO</code> quedó obsoleta a propósito?', 'Desarrollo', 'no',
     'es la abstracción que hoy falta y nadie la usa; conviene saber por qué se abandonó antes de repetir el intento'),
    ('Q38', '&iquest;Cuál es la fecha de corte y la póliza publicada que vamos a usar como patrón de la prueba '
     'de equivalencia?', 'Contabilidad / operación', 'si',
     'sin patrón no hay forma de certificar el ambiente nuevo'),
    ('Q39', '&iquest;Qué jobs disparan el cierre, con qué parámetros y en qué orden?', 'Operación / DBA', 'si',
     'hace falta para reproducir el cierre en el ambiente nuevo y para saber qué objetos se ejecutan de verdad'),
    ('Q40', '&iquest;La lista de objetos en uso incluye los reportes <code>_VIS</code> porque se ejecutan en el '
     'cierre o porque los consulta un usuario?', 'Operación', 'no',
     'cambia si entran al alcance de la prueba de equivalencia o solo al inventario'),
]


def doc21():
    b = ['<p class="lead">Reordenamiento de las 31 confirmaciones abiertas usando la lista de objetos en uso: '
         'lo que el acotamiento cierra, lo que sigue bloqueando y las preguntas nuevas que salen del cruce.</p>']
    b.append(kpis([
        (len(CIERRAN), 'preguntas que cierra el acotamiento', 'ok' if False else 'b'),
        (len(VIGENTES), 'siguen vigentes dentro del alcance', 'a'),
        (len(NUEVAS), 'nuevas por el cruce con la lista', 'c'),
        (sum(1 for x in NUEVAS if x[3] == 'si'), 'nuevas que bloquean el QA nuevo', 'c'),
    ]))

    b.append('<h2>1. Lo que el acotamiento cierra o baja de prioridad</h2>')
    b.append(tabla(['Referencia', 'Pregunta', 'Por qué se cierra'],
                   [(f'<span class="tag">{e(a)}</span>', b_, c) for a, b_, c in CIERRAN]))
    b.append('<div class="card ambar"><p>Cierran cinco de las 31, todas por alcance y no por respuesta. '
             'Conviene decirlo así en la reunión: el objeto sigue existiendo en la base, lo que cambia es que '
             'no participa en la póliza y por lo tanto no lo administra el portal ni se instala en el QA '
             'nuevo.</p></div>')

    b.append('<h2>2. Lo que sigue bloqueando, dentro del alcance</h2>')
    b.append(tabla(['Ref.', 'Qué hay que confirmar', 'Extensión', 'Quién decide', 'Por qué bloquea'],
                   [(f'<span class="tag">{e(a)}</span>', b_, c, f'<span class="pill info">{e(d)}</span>', f_)
                    for a, b_, c, d, f_ in VIGENTES]))

    b.append('<h2>3. Preguntas nuevas del cruce con la lista</h2>')
    b.append(tabla(['Ref.', 'Pregunta', 'Quién responde', 'Bloquea', 'Por qué importa'],
                   [(f'<span class="tag">{e(a)}</span>', b_, f'<span class="pill info">{e(c)}</span>',
                     f'<span class="pill {"c" if d == "si" else "m"}">{e(d)}</span>', f_)
                    for a, b_, c, d, f_ in NUEVAS]))

    b.append('<h2>4. Las cinco que valen la reunión</h2>')
    b.append('<div class="card rojo"><ol>'
             '<li><b>Q32</b> &mdash; a qué instancia escribe el procedimiento de pase. Es control interno, no diseño.</li>'
             '<li><b>Q01</b> &mdash; el rubro <code>OPI VALOR</code> que no existe: define si hay importes fuera de la póliza.</li>'
             '<li><b>Q15</b> &mdash; cuál es la regla verdadera de origen "no restringido".</li>'
             '<li><b>Q33 / Q38</b> &mdash; el DDL faltante y la póliza patrón: sin eso no arranca el QA nuevo.</li>'
             '<li><b>Q06</b> &mdash; la fecha fija del cierre comercial, que sigue viva en la entrega de septiembre.</li>'
             '</ol></div>')
    return page('Preguntas acotadas al alcance productivo',
                'Que cierra la lista de objetos en uso, que sigue bloqueando y que preguntas nuevas aparecen',
                '\n'.join(b))


def main():
    for nombre, doc in (('19_alcance_produccion.html', doc19),
                        ('20_qa_confiable.html', doc20),
                        ('21_preguntas_alcance.html', doc21)):
        (AQUI / nombre).write_text(doc(), encoding='utf-8')
        print('escrito', nombre)


if __name__ == '__main__':
    main()
