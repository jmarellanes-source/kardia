# -*- coding: utf-8 -*-
"""Genera los documentos ejecutivos de la auditoría KARDIA/SAF:
06_ejecutivo.html, 07_plan_remediacion.html, 08_portal_admin.html y
10_contexto_migracion.html
"""
import csv
import html
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent

CSS = """
*{box-sizing:border-box}
body{margin:0;font:14px/1.6 "Segoe UI",system-ui,sans-serif;background:#0e1420;color:#e8edf6}
a{color:#7fb2ff}
header.top{padding:26px 32px;background:linear-gradient(120deg,#12213d,#0e1420 60%);border-bottom:1px solid #2a3549}
header.top h1{margin:0;font-size:23px;letter-spacing:.3px}
header.top p{margin:6px 0 0;color:#93a1bb}
nav.docs{padding:10px 32px;background:#131b29;border-bottom:1px solid #2a3549;font-size:13px}
nav.docs a{margin-right:16px;text-decoration:none}
.wrap{padding:22px 32px 60px;max-width:1180px}
h2{margin:34px 0 12px;font-size:18px;border-left:3px solid #4c8dff;padding-left:10px}
h3{margin:22px 0 6px;font-size:15px}
p.lead{color:#c9d6ee;font-size:15px}
.kpis{display:flex;gap:14px;flex-wrap:wrap;margin:18px 0 26px}
.kpi{background:#161e2e;border:1px solid #2a3549;border-radius:10px;padding:14px 18px;min-width:140px}
.kpi b{display:block;font-size:27px;line-height:1.1}
.kpi span{color:#93a1bb;font-size:12px;text-transform:uppercase;letter-spacing:.6px}
.kpi.c b{color:#ff6b6b}.kpi.a b{color:#ffa94d}.kpi.m b{color:#ffd43b}.kpi.b b{color:#74c0fc}
.card{background:#161e2e;border:1px solid #2a3549;border-radius:10px;padding:16px 20px;margin:12px 0}
.card.rojo{border-left:3px solid #ff6b6b}
.card.ambar{border-left:3px solid #ffa94d}
.card.azul{border-left:3px solid #4c8dff}
.card.verde{border-left:3px solid #51cf66}
.card h3{margin-top:0}
.card .q{color:#93a1bb;font-size:12.5px;text-transform:uppercase;letter-spacing:.5px;margin:10px 0 2px}
table{width:100%;border-collapse:collapse;background:#161e2e;border:1px solid #2a3549;border-radius:9px;overflow:hidden;margin-top:12px}
th,td{padding:9px 11px;text-align:left;border-bottom:1px solid #26314a;vertical-align:top;font-size:13px}
th{background:#1d2739;color:#93a1bb;font-size:11px;text-transform:uppercase;letter-spacing:.6px}
td.num{white-space:nowrap;color:#93a1bb}
code,.mono{font-family:ui-monospace,Consolas,monospace;font-size:12.5px;color:#c9d6ee}
pre{margin:8px 0 0;background:#0b1220;border:1px solid #26314a;border-radius:6px;padding:12px;overflow-x:auto;
 font:12px/1.5 ui-monospace,Consolas,monospace;color:#c9d6ee;white-space:pre-wrap}
.pill{font-size:11px;padding:3px 8px;border-radius:20px;display:inline-block;white-space:nowrap}
.pill.c{background:#4a1414;color:#ff8787;border:1px solid #7d2020}
.pill.a{background:#4a3211;color:#ffc078;border:1px solid #7d5a20}
.pill.m{background:#443f10;color:#ffe066;border:1px solid #756a1c}
.pill.ok{background:#10331f;color:#8ce99a;border:1px solid #1f6b3c}
.pill.info{background:#122d47;color:#8ecaff;border:1px solid #1f5480}
ul{margin:6px 0;padding-left:20px}li{margin:4px 0}
.ola{background:#161e2e;border:1px solid #2a3549;border-left:3px solid #4c8dff;border-radius:9px;padding:14px 20px;margin:12px 0}
.ola h3{margin:0 0 2px}
.ola .obj{color:#93a1bb;margin:0 0 10px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:14px}
@media(max-width:900px){.grid2{grid-template-columns:1fr}}
.tag{font-size:11px;color:#93a1bb;border:1px solid #35415a;border-radius:5px;padding:2px 7px;margin-right:6px}
footer{color:#93a1bb;font-size:12px;padding:18px 32px;border-top:1px solid #2a3549}
blockquote{margin:10px 0;padding:10px 14px;background:#131b29;border-left:3px solid #35415a;color:#c9d6ee}
"""

NAV = """<nav class="docs">
<a href="index.html">Consolidado</a><a href="06_ejecutivo.html">Resumen ejecutivo</a>
<a href="07_plan_remediacion.html">Plan de remediación</a><a href="08_portal_admin.html">Portal de administración</a>
<a href="09_demo_portal.html">Demo del portal</a>
<a href="10_contexto_migracion.html">Contexto operativo y cambio de core</a>
<a href="11_fase0_fase1.html">Fase 0 y Fase 1 con ejemplos</a>
<a href="12_preguntas_negocio.html">Confirmaciones con negocio</a>
<a href="13_dummy_catalogos.html">Dummy de catálogos y banderas</a>
<a href="05_dependencias.html">Dependencias y reportes</a><a href="00_inventario.html">Inventario</a>
</nav>"""


def page(title, sub, body):
    return f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} &mdash; KARDIA / SAF</title>
<style>{CSS}</style></head><body>
<header class="top"><h1>{title}</h1><p>{sub}</p></header>
{NAV}
<div class="wrap">
{body}
</div>
<footer>Auditoría de código SQL KARDIA / SAF &middot; análisis estático del repositorio (BD, BD_prod y reportes).
No se ejecutó ningún objeto contra una instancia de SQL Server ni se leyeron datos productivos:
los hallazgos que dependen de datos, de plan de ejecución o de reglas contables se marcan como pendientes de validación.</footer>
</body></html>
"""


def e(x):
    return html.escape(str(x))


# ---------------------------------------------------------------- ejecutivo
riesgos = [
    ("R1", "c", "No sabemos con certeza qué código está corriendo en producción",
     "126 de los 256 objetos comunes difieren entre el ambiente de desarrollo y el de producción (49%), "
     "19 de los 27 objetos de la familia de cierre no aparecen en el export de producción, y el procedimiento "
     "de saldos SP_SAF_SALDOS tiene 573 líneas en desarrollo y 223 en producción, sin los bloques de saldos "
     "en cuentas de orden ni post-castigo.",
     "Cualquier corrección puede aplicarse sobre una versión equivocada, y hoy no hay forma de demostrar ante "
     "un revisor externo que la cifra publicada proviene del código autorizado.",
     "Reconciliar ambientes contra los metadatos de producción. Es solo lectura y es el prerrequisito de todo "
     "lo demás."),
    ("R2", "c", "Cuatro procedimientos de producción leen datos de la base de QA",
     "Objetos productivos consultan Quiero_Confianza_CreditoPuente_QA y Quiero_Confianza_shadow; el nombre de "
     "la base externa está escrito 6.485 veces en los 153 archivos que leen del origen, y difiere entre "
     "ambientes.",
     "Cifras de cierre calculadas con datos de prueba, y la imposibilidad de promover una corrección sin "
     "editarla a mano en cada ambiente: de las 125 diferencias entre objetos comunes, 90 son solo el nombre de "
     "la base.",
     "Sustituir los nombres de base embebidos por 38 sinónimos por ambiente. Un solo despliegue elimina el 72% "
     "del drift y habilita el despliegue automatizado; los scripts ya están entregados."),
    ("R3", "c", "El cierre no es repetible y un error puede pasar inadvertido",
     "El cierre diario acumula ajustes por diseño, pero no registra la corrida ni impide un segundo pase del "
     "mismo periodo, y el agregado del cierre mensual individual se toma de todo el histórico sin filtro de "
     "periodo; el cierre comercial lee comisiones "
     "de una fecha fija ('20260123') en lugar del periodo; 89 de 100 objetos revisados hacen rollback sin "
     "propagar el error; y la bitácora de errores de póliza la escriben 102 objetos, pero ninguno la vigila.",
     "Un cierre puede terminar en 'éxito' con cifras incompletas o duplicadas y llegar a contabilidad sin que "
     "ningún control automático lo detecte. La detección depende hoy de que alguien note el descuadre.",
     "Idempotencia por periodo, propagación de errores (THROW) y un monitor sobre la bitácora que alerte antes "
     "de que la póliza llegue a contabilidad."),
    ("R4", "a", "Las reglas de negocio están escritas dentro del código, no en un catálogo",
     "63 grupos de valores hardcodeados: IVA fijo al 16%, participación ION/Afirme partida en 0.10/0.90 "
     "repetida en 28 archivos, catálogos de rubros contables, tipos de crédito, orígenes y cuentas excluidas "
     "embebidos, fechas de vigencia del programa COVID en 45 lugares de un solo procedimiento.",
     "Cada cambio normativo o comercial se convierte en un proyecto de desarrollo con riesgo de que una copia "
     "quede sin actualizar. Ya hay dos definiciones distintas de 'cuota COVID' y dos de 'cartera' conviviendo.",
     "Extraer los valores a catálogos con vigencia y administrarlos desde el portal propuesto, con aprobación "
     "de cuatro ojos y bitácora de cambios."),
    ("R5", "a", "La cifra publicada no es reproducible y el proceso avanza fila por fila",
     "Uso extendido de WITH (NOLOCK) sobre la réplica de lectura en cálculos financieros y reportes (287 usos solo en la familia de "
     "cierre), cursores en los procedimientos de saldos, y funciones escalares con acceso a datos invocadas "
     "desde decenas de procedimientos.",
     "Riesgo de leer filas no confirmadas o duplicadas durante el propio cierre (cifras no reproducibles), "
     "y una ventana de cierre que crece con el volumen de cartera.",
     "Nivel de aislamiento snapshot para lectura, conversión de funciones escalares a funciones en línea y "
     "eliminación de cursores en los procedimientos críticos, midiendo duración antes y después."),
    ("R6", "a", "La entrega de información repite los mismos problemas del código",
     "Los 30 archivos de reportes son 18 reportes lógicos duplicados por ambiente, con la dirección del "
     "servidor escrita dentro del archivo (tres servidores distintos) y ninguno usando origen de datos "
     "compartido. Dos copias del mismo reporte de póliza contable filtran productos y etapas distintos.",
     "El mismo reporte puede entregar cifras distintas según el archivo que se abra, y basta publicar el "
     "artefacto equivocado para que un usuario consulte otro ambiente sin notarlo.",
     "Un artefacto por reporte lógico, origen de datos por ambiente y publicación por script desde el "
     "repositorio."),
]

decisiones = [
    ("Contabilidad / Control interno",
     "Confirmar el destino correcto del UPDATE etiquetado MONTOEXIGIBLECOM en el cierre individual, el criterio "
     "de FEC_CANCELACION, el filtro de moratorios que está comentado y el catálogo oficial de rubros contables. "
     "Son cuatro hallazgos con evidencia en el código cuyo impacto en la cifra solo contabilidad puede confirmar."),
    ("Negocio / Producto",
     "Definir la fuente oficial de IVA, participación ION/Afirme, tipos de crédito, orígenes de fondos, cuentas "
     "excluidas y vigencias de programa; y que valores debe poder cambiar un usuario sin pasar por desarrollo."),
    ("Tecnología / Infraestructura",
     "Autorizar la lectura de metadatos y estadísticas de uso en producción (sys.sql_modules, "
     "sys.dm_exec_procedure_stats), entregar los jobs del Agent y definir los ambientes formales "
     "(desarrollo, QA, producción) con su mecanismo de promoción."),
    ("Riesgos / Auditoría",
     "Validar el modelo de control propuesto: cuatro ojos para cambios de parámetro, bitácora inmutable, "
     "segregación de funciones y evidencia de conciliación por cierre."),
    ("Dirección del proyecto",
     "Aprobar el orden de las olas y la construcción del portal de administración, o pedir explícitamente que "
     "la remediación se haga solo en código, sin portal."),
]

estado = [
    ("Defecto verificable leyendo el código", "ok",
     "Duplicación al reprocesar, fecha fija en el cierre comercial, lectura de la base de QA, DELETE sin filtro "
     "de póliza, importes aleatorios en facturación, correo de prueba en el padrón de clientes, filtros "
     "divergentes entre copias del mismo reporte.",
     "Se puede corregir con la evidencia entregada; solo requiere validar el resultado esperado."),
    ("Riesgo técnico dependiente del entorno", "info",
     "NOLOCK, cursores, funciones escalares, MONEY, ausencia de XACT_ABORT, tablas sin llave natural.",
     "El defecto existe; la magnitud depende de volumen, concurrencia y plan de ejecución, que no se pueden "
     "medir sin acceso a la instancia."),
    ("Pendiente de validación funcional o contable", "m",
     "Columna destino del UPDATE de MONTOEXIGIBLECOM, criterio de FEC_CANCELACION, filtro comentado de "
     "moratorios, catálogo de rubros, granularidad de reportes.",
     "Se documenta como riesgo con su evidencia. No se corrige sin confirmación del área responsable."),
    ("Hipótesis que requiere información externa", "a",
     "Los 110 objetos sin invocador visible, las 187 tablas sin código asociado, el esquema AP en el catálogo "
     "INFORMES, y si el export de producción está incompleto o hay objetos sin promover.",
     "Se resuelve con los jobs del Agent y los metadatos de producción; sin eso no es posible afirmar que algo "
     "sea código muerto."),
]

body = f"""
<p class="lead">Auditoría de los 503 archivos SQL de desarrollo, los 256 de producción y los 30 artefactos de
reportes del sistema KARDIA / SAF, ejecutada en cinco fases por lotes de riesgo. Este documento resume, para
dirección y para las áreas de negocio, qué se encontró, qué significa en términos de riesgo operativo y
contable, y qué decisiones se necesitan para empezar a remediar.</p>

<div class="kpis">
  <div class="kpi"><b>789</b><span>Archivos auditados</span></div>
  <div class="kpi"><b>117</b><span>Hallazgos</span></div>
  <div class="kpi c"><b>22</b><span>Críticos</span></div>
  <div class="kpi a"><b>51</b><span>Altos</span></div>
  <div class="kpi m"><b>35</b><span>Medios</span></div>
  <div class="kpi b"><b>9</b><span>Bajos</span></div>
  <div class="kpi"><b>63</b><span>Grupos de hardcodeo</span></div>
  <div class="kpi"><b>49%</b><span>Drift dev vs prod</span></div>
</div>

<h2>Lo que hay que saber en un minuto</h2>
<div class="card azul">
<p>El sistema funciona y produce la contabilidad todos los días, pero lo hace <b>sin las tres garantías que se
esperan de un proceso bancario</b>: no se puede demostrar que el código que corre en producción es el
autorizado (49% de diferencia entre ambientes, y objetos productivos leyendo la base de QA); el cierre no es
repetible ni avisa cuando falla (no hay marca de corrida que impida un segundo pase, y los errores se
registran en una bitácora que nadie vigila); y las reglas de negocio viven dentro del código (63 grupos de valores fijos, con dos
definiciones distintas de la misma regla conviviendo).</p>
<p>Ninguno de los tres se resuelve comprando software: se resuelven con una secuencia de trabajo acotada, que
empieza por reconciliar ambientes y termina con las reglas administradas desde un portal con aprobación de
cuatro ojos. La buena noticia es que <b>el riesgo está concentrado</b>: ocho objetos son invocados por casi todo
el portafolio y 18 procedimientos alimentan toda la entrega de información, así que proteger menos del 5% del
código cubre la mayor parte del riesgo.</p>
</div>

<h2>Contexto operativo del proceso</h2>
<div class="card verde">
<p>Confirmado con el equipo de desarrollo: el proceso <b>lee diariamente de <code>Quiero_Confianza</code>, una
réplica de solo lectura del transaccional SAF/Sisde</b>, y <b>escribe el histórico contable en
<code>KARDIA</code></b>, dentro del sistema CAS. Minutos después de que SAF cierra operaciones se dispara el
cierre de la póliza del día; el histórico queda bloqueado y los ajustes de días anteriores se registran como
<b>adiciones acumuladas</b> en lugar de modificar el pasado, y los valores fijos se concentran en la
clasificación de las <b>cuatro pólizas principales</b>: devengados de intereses, devengados de moratorios,
seguros y otras comisiones.</p>
<p>Este contexto no cambia el alcance ni los hallazgos, pero sí precisa tres lecturas, y así están redactados
los reportes: el uso de <code>NOLOCK</code> no pone en riesgo al core (la fuente es una réplica) y queda como
riesgo de <b>reproducibilidad de la cifra</b>; la acumulación del cierre es intencional, de modo que el defecto
es la <b>ausencia de marca de corrida y de acotamiento por periodo</b>, no la suma en sí; y la parametrización
debe atacar primero las cuatro pólizas. El detalle, junto con la estrategia para el futuro reemplazo del core,
está en <a href="10_contexto_migracion.html">Contexto operativo y cambio de core</a>.</p>
</div>

<h2>Los seis riesgos que importan</h2>
{''.join(f'''
<div class="card {'rojo' if sev=='c' else 'ambar'}">
  <h3><span class="pill {sev}">{'Crítico' if sev=='c' else 'Alto'}</span> &nbsp;{rid}. {e(t)}</h3>
  <p class="q">Evidencia</p><p>{e(ev)}</p>
  <p class="q">Qué significa para el negocio</p><p>{e(imp)}</p>
  <p class="q">Qué hay que hacer</p><p>{e(acc)}</p>
</div>''' for rid, sev, t, ev, imp, acc in riesgos)}

<h2>Como leer los hallazgos: cuatro niveles de certeza</h2>
<p>Es la parte que suele generar discusión con el área de desarrollo, y por eso se declara de entrada. La
auditoría es <b>estática</b>: se leyó el código del repositorio, no se ejecutó nada contra SQL Server ni se
consultaron datos productivos.</p>
<table><thead><tr><th>Nivel</th><th>Ejemplos</th><th>Como se trata</th></tr></thead><tbody>
{''.join(f'<tr><td><span class="pill {c}">{e(n)}</span></td><td>{e(ej)}</td><td>{e(tr)}</td></tr>' for n, c, ej, tr in estado)}
</tbody></table>

<h2>Decisiones que necesitamos del cliente</h2>
<table><thead><tr><th>Área</th><th>Decisión</th></tr></thead><tbody>
{''.join(f'<tr><td><b>{e(a)}</b></td><td>{e(d)}</td></tr>' for a, d in decisiones)}
</tbody></table>

<h2>Que no cubre esta auditoría</h2>
<div class="card">
<ul>
<li>Seguridad de la instancia: usuarios, roles, permisos efectivos, cifrado y auditoría de SQL Server. Requiere acceso al servidor.</li>
<li>Rendimiento real: planes de ejecución, índices, esperas y volumetría. Los hallazgos de rendimiento se basan en el patrón de código, no en mediciones.</li>
<li>Conciliación contable con datos: no se compararon cifras entre el sistema y la contabilidad; los hallazgos contables se plantean como riesgo con su evidencia.</li>
<li>Código que no está en el repositorio: la aplicación, los ETL, los jobs del Agent y el esquema AP del catálogo INFORMES quedan fuera del alcance porque no fueron entregados.</li>
</ul>
</div>

<h2>Documentos de soporte</h2>
<p>Todos los detalles técnicos, con evidencia línea por línea y filtros por severidad, categoría y ambiente:</p>
<ul>
<li><a href="index.html">Consolidado de la auditoría</a> &mdash; entrada única a todos los lotes</li>
<li><a href="01_lote1.html">Lote 1</a>: 20 objetos de mayor riesgo &middot;
    <a href="02_lotes2-5.html">Lotes 2-5</a>: 80 objetos y familias clonadas &middot;
    <a href="03_lote6.html">Lote 6</a>: PAG, edc, SAF, dbo, RPT y funciones</li>
<li><a href="04_lotes10-11.html">Lotes 10-11</a>: familia completa de cierre &middot;
    <a href="05_dependencias.html">Dependencias y capa de reportes</a></li>
<li><a href="07_plan_remediacion.html">Plan de remediación por olas</a> &middot;
    <a href="08_portal_admin.html">Propuesta del portal de administración</a> &middot;
    <a href="09_demo_portal.html">Demo navegable del portal</a> (prototipo sin backend)</li>
<li><a href="10_contexto_migracion.html">Contexto operativo y estrategia ante el cambio de core</a> &mdash;
    ajustes de interpretación, matriz de las cuatro pólizas y salida de SAF/Sisde</li>
</ul>
"""

(OUT / '06_ejecutivo.html').write_text(page(
    'Resumen ejecutivo de la auditoría SQL',
    '789 archivos auditados &middot; 117 hallazgos &middot; 5 fases de análisis &middot; 2026-08-19',
    body), encoding='utf-8')

# ------------------------------------------------------------ remediacion
olas = [
    ("Ola 0", "Reconciliación de ambientes y línea base", "3-4 sesiones",
     "Saber que corre en producción antes de tocar una línea de código.",
     ["Comparar los 256 objetos comunes contra sys.sql_modules de producción (nombre, fecha de modificación y hash) y resolver los 19 objetos de cierre ausentes en el export. Los tres scripts ya están entregados en auditoria/fase0 y son de solo lectura; el detalle paso por paso está en el documento de Fase 0 y Fase 1.",
      "Correr el comparador de paridad con la salida de cada ambiente. Ejecutado hoy sobre el repositorio da 71 objetos iguales, 90 cuya única diferencia es el nombre de la base de origen, 35 con diferencias reales y 50 ausentes del export de producción: el análisis humano se concentra en esos 35.",
      "Aclarar SP_SAF_SALDOS: 573 líneas en desarrollo contra 223 en producción.",
      "Exportar al repositorio los jobs del SQL Server Agent y las tareas del orquestador, un script por job.",
      "Definir la rama por ambiente y congelar cambios manuales en producción.",
      "Publicar la matriz de paridad como línea base del control de cambios."],
     ["Existe una matriz objeto x ambiente con hash y fecha, sin celdas desconocidas.",
      "Todo objeto productivo tiene su equivalente idéntico en el repositorio, o una excepción documentada y con responsable.",
      "Cada procedimiento de cierre tiene identificado su disparador."],
     "Nulo en producción: solo lectura de metadatos.",
     "Ninguna. Es el punto de partida.", "azul"),
    ("Ola 1", "Eliminar la causa del drift: nombres de base y ambiente en el código", "2-3 sesiones",
     "Que el mismo script se despliegue sin editar en los tres ambientes.",
     ["Desplegar los 38 sinónimos del esquema EXT que cubren las 6.485 referencias literales al origen de los 153 archivos que lo leen. El script está generado y es idempotente; la base de origen se pasa como variable de sqlcmd, así que es el único artefacto que difiere entre ambientes.",
      "Sustituir en el código las referencias de tres partes por EXT.<objeto>: 3.617 sustituciones en BD, hechas por un script revisable que escribe en un directorio aparte y no modifica los archivos originales.",
      "Eliminar con ello toda referencia a bases de QA o shadow desde objetos productivos (4 procedimientos apuntan hoy a _CreditoPuente_QA).",
      "Verificar en la instancia con las cuatro consultas de control: cero objetos con el nombre de la base en sys.sql_modules, 38 sinónimos resolviendo y una sola base de origen distinta.",
      "Compuerta de integración continua que rechace cualquier script con un nombre de base literal."],
     ["Ningún objeto productivo referencia una base de QA o shadow.",
      "El mismo archivo .sql se aplica sin modificación en desarrollo, QA y producción.",
      "La compuerta falla en una prueba deliberada con un nombre de base literal."],
     "Bajo: cambia la resolución de nombres, no la lógica. Verificable comparando el plan y el resultado sobre un periodo cerrado.",
     "Ola 0.", "azul"),
    ("Ola 2", "Correcciones críticas de cifra", "4-6 sesiones",
     "Cerrar los defectos que hoy pueden alterar una cifra contable.",
     ["Control de corrida del cierre: registrar periodo, identificador de ejecución y estado, rechazar el segundo pase del mismo periodo salvo reproceso autorizado, y acotar al periodo el agregado que hoy se toma de todo el histórico. El modelo acumulativo con bloqueo del histórico se conserva; lo que se agrega es la garantía de que un reintento no vuelve a acumular.",
      "Sustituir la fecha fija '20260123' del cierre comercial por el periodo recibido como parámetro.",
      "Corregir el DELETE de PRINCIPAL sin filtro de póliza en PO.SYS_SP_MOV_CARGO.",
      "Retirar edc.SP_Genera_Ordenes_Dummy de producción o protegerlo con guarda de ambiente, y limpiar el correo de prueba del padrón de clientes.",
      "Resolver, ya con respuesta de contabilidad, los cuatro hallazgos contables pendientes de validación."],
     ["Ejecutar dos veces el cierre de un periodo cerrado produce cifras idénticas y la segunda ejecución queda registrada como rechazada o como reproceso autorizado (prueba automatizada).",
      "Un ajuste de un día anterior se refleja como adición acumulada y el saldo del día original no cambia.",
      "El cierre de un periodo histórico reproduce la cifra publicada en su momento.",
      "Ningún objeto productivo genera datos aleatorios ni de prueba.",
      "Cada corrección contable tiene aprobación escrita del área responsable."],
     "Alto: toca cálculo. Exige ambiente de pruebas con copia de datos y comparación de cifras antes y después.",
     "Ola 0, Ola 1 y las respuestas de contabilidad y negocio.", "ambar"),
    ("Ola 3", "Transacciones y observabilidad", "4-5 sesiones",
     "Que un fallo se detenga, se vea y se pueda reprocesar.",
     ["Plantilla transaccional estándar: SET XACT_ABORT ON, control de XACT_STATE() y THROW al final de cada CATCH.",
      "Aplicarla a los objetos con transacción, empezando por la familia de cierre.",
      "Identificador de ejecución y severidad en PO.SAF_POLIZA_ERRORES, con las etiquetas de proceso corregidas.",
      "Monitor que alerte cuando una ejecución cierre con errores, antes de que la póliza llegue a contabilidad.",
      "Bitácora de inicio y fin por proceso, con duración y filas afectadas."],
     ["Un error simulado a mitad del cierre deja la base sin cambios parciales y el job en estado fallido.",
      "Toda ejecución queda registrada con identificador, duración y conteo de errores.",
      "La alerta llega antes del envío de la póliza en una prueba controlada."],
     "Medio: cambia el contrato de error hacia el orquestador. Procesos que hoy terminan en 'éxito' empezarán a fallar de forma visible, lo cual es el objetivo.",
     "Ola 0. Puede avanzar en paralelo con la Ola 2.", "ambar"),
    ("Ola 4", "Catálogos y parametrización", "6-8 sesiones",
     "Sacar las reglas de negocio del código y ponerlas bajo administración con vigencia.",
     ["Modelo de catálogos con vigencia (parámetro, valor, vigencia desde y hasta, ambiente, autor, aprobador).",
      "Empezar por la matriz de las cuatro pólizas principales (devengados de intereses, devengados de moratorios, seguros y otras comisiones): concepto de origen, rubro, tipo de crédito, cuenta contable, naturaleza y vigencia. Es donde se concentra el hardcodeo y donde el alta de un concepto nuevo hoy obliga a liberar código.",
      "Cargar el resto de los 63 grupos de hardcodeo según su clasificación: parametrizables en portal, catálogos en base y defectos.",
      "Unificar las reglas duplicadas: dos definiciones de cuota COVID, dos de cartera, dos de cuentas excluidas.",
      "Reemplazar en el código los valores fijos por lectura del catálogo con la vigencia del periodo procesado.",
      "Primer modulo del portal: consulta, edición con cuatro ojos y bitácora."],
     ["Dar de alta un concepto o rubro nuevo de las cuatro pólizas y verlo clasificado en la póliza del día siguiente, sin liberar código ni reiniciar nada.",
      "Recalcular un periodo histórico usa los valores vigentes en ese periodo y reproduce la cifra publicada.",
      "Todo concepto de origen que llegue sin mapeo se rechaza a una bandeja visible en el portal, en lugar de quedar sin clasificar en silencio.",
      "Ningún valor de la lista de parametrizables aparece como literal en el código (verificado por la compuerta de integración continua).",
      "Todo cambio de parámetro tiene autor, aprobador distinto y fecha en la bitácora."],
     "Medio-alto: el cálculo pasa a depender de datos. Obliga a versionar el catálogo con vigencia, nunca a sobrescribirlo.",
     "Ola 1 y la definición de fuentes oficiales por parte de negocio.", "ambar"),
    ("Ola 5", "Rendimiento y concurrencia", "5-7 sesiones",
     "Cifras reproducibles y una ventana de cierre que no crezca con la cartera.",
     ["Sustituir WITH (NOLOCK) por nivel de aislamiento snapshot sobre la réplica de lectura en los cálculos financieros, empezando por la familia de cierre, y registrar por corrida la marca de sincronía de la réplica para que la cifra sea reproducible.",
      "Convertir las funciones escalares con acceso a datos en funciones en línea o columnas materializadas (seis funciones con 31 a 78 invocadores).",
      "Eliminar cursores en los procedimientos de saldos y reescribirlos en operaciones de conjunto.",
      "Revisar tipos MONEY y las agregaciones con granularidad inconsistente.",
      "Medir duración y lecturas antes y después de cada cambio."],
     ["El cierre produce la misma cifra al repetirse sobre el mismo punto de lectura de la réplica.",
      "Duración del cierre igual o menor que la línea base, documentada objeto por objeto.",
      "Ninguna lectura sucia en los cálculos que alimentan la póliza."],
     "Medio: sin cambio funcional esperado, pero exige medición antes y después y ventana de pruebas con volumen.",
     "Ola 0 y línea base de duración.", "azul"),
    ("Ola 6", "Capa de reportes", "3-4 sesiones",
     "Que el ambiente y los filtros salgan de los artefactos de reporte.",
     ["Consolidar los 30 archivos .rdl en 18 reportes lógicos con origen de datos compartido por ambiente.",
      "Corregir los filtros fijos divergentes de la póliza contable y el reporte con nombre equivocado.",
      "Decidir el destino de los artefactos QA y del esquema AP en el catálogo INFORMES.",
      "Publicar por script desde el repositorio y cerrar la matriz procedimiento a consumidor."],
     ["Un solo artefacto por reporte lógico, sin direcciones de servidor dentro del archivo.",
      "El reporte nuevo y el anterior producen la misma cifra sobre un periodo cerrado.",
      "La publicación es reproducible desde el repositorio, sin pasos manuales."],
     "Bajo: cambia la entrega, no el cálculo.",
     "Ola 1 (definición de ambientes).", "azul"),
    ("Ola 7", "Controles preventivos y cierre del ciclo", "4-5 sesiones",
     "Que los patrones corregidos no vuelvan a entrar.",
     ["Compuerta de integración continua sobre cada cambio: nombres de base literales, NOLOCK en cálculos, transacciones sin XACT_ABORT, CATCH sin THROW, valores de la lista de parametrizables.",
      "Detección automática de clones divergentes: agrupar procedimientos por similitud y alertar cuando dos copias se separen.",
      "Pruebas de regresión de cifra sobre un periodo cerrado, ejecutadas en cada despliegue.",
      "Despliegue automatizado por ambiente con aprobación, y evidencia de conciliación por cierre."],
     ["Ningún cambio llega a producción sin pasar la compuerta.",
      "La suite de regresión de cifra corre en cada despliegue y bloquea diferencias no explicadas.",
      "Existe evidencia de conciliación archivada por cierre."],
     "Bajo, y es lo que evita repetir la auditoría en dos años.",
     "Olas 1 a 6 (cada compuerta se activa cuando su patrón ya fue corregido).", "verde"),
]

sec = "".join(f"""
<div class="ola">
  <h3>{e(n)} &mdash; {e(t)} <span class="tag">{e(esf)}</span></h3>
  <p class="obj">{e(obj)}</p>
  <div class="grid2">
    <div><p class="q"><b>Acciones</b></p><ul>{''.join(f'<li>{e(a)}</li>' for a in acc)}</ul></div>
    <div><p class="q"><b>Criterios de aceptación</b></p><ul>{''.join(f'<li>{e(c)}</li>' for c in cri)}</ul></div>
  </div>
  <p style="margin:8px 0 0;font-size:12.5px;color:#93a1bb"><b>Riesgo de la ola:</b> {e(r)}<br>
  <b>Depende de:</b> {e(dep)}</p>
</div>""" for n, t, esf, obj, acc, cri, r, dep, col in olas)

body2 = f"""
<p class="lead">Plan de remediación en ocho olas, ordenadas por dependencia y no por severidad: las primeras dos
no corrigen ningún cálculo, pero sin ellas cualquier corrección se aplica sobre una versión equivocada del
código. Cada ola tiene criterios de aceptación verificables, para que el avance se mida con evidencia y no con
porcentajes.</p>

<div class="card azul">
<h3>Tres principios del plan</h3>
<ul>
<li><b>Nada se corrige sin línea base.</b> Primero se establece que corre en producción y cuanto tarda; después se cambia. Sin eso no hay forma de demostrar que la corrección mejoro algo.</li>
<li><b>Ninguna cifra cambia sin aprobación del área responsable.</b> Los hallazgos contables se corrigen con confirmación escrita de contabilidad, no por criterio técnico.</li>
<li><b>Cada patrón corregido queda protegido por una compuerta.</b> De lo contrario vuelve a entrar en el siguiente proyecto, que es exactamente como se llego al estado actual.</li>
</ul>
</div>

<h2>Olas</h2>
{sec}

<h2>Nota sobre el esfuerzo</h2>
<div class="card">
<p>Las estimaciones están en <b>sesiones de trabajo asistido</b> (una sesión equivale a una jornada de desarrollo
enfocado con generación de código asistida), y suman aproximadamente <b>31 a 42 sesiones</b> para las ocho olas.
El tiempo de calendario no lo determina el esfuerzo, sino tres esperas externas que conviene planear desde el
inicio:</p>
<ul>
<li>Respuestas de contabilidad y negocio sobre los cuatro hallazgos contables y las fuentes oficiales de catálogos (bloquea las Olas 2 y 4).</li>
<li>Provisión del ambiente de pruebas con copia de datos y de las autorizaciones de lectura de metadatos en producción (bloquea las Olas 0, 2 y 5).</li>
<li>Ventanas de cierre disponibles para probar con volumen (bloquea la Ola 5).</li>
</ul>
<p>Recomendación: iniciar hoy las Olas 0 y 1, que no dependen de ninguna de las tres esperas, y usar ese tiempo
para conseguir las definiciones que las Olas 2 y 4 necesitan.</p>
</div>

<h2>Secuencia sugerida</h2>
<table><thead><tr><th>Bloque</th><th>Olas</th><th>Resultado al terminar</th></tr></thead><tbody>
<tr><td><b>Bloque 1: control</b></td><td>0 y 1</td><td>Se sabe que corre en producción y el mismo script se despliega en los tres ambientes. Sin cambios de cálculo.</td></tr>
<tr><td><b>Bloque 2: cifra y visibilidad</b></td><td>2 y 3 (en paralelo)</td><td>El cierre es repetible, los errores detienen el proceso y se alertan antes de contabilidad.</td></tr>
<tr><td><b>Bloque 3: reglas</b></td><td>4</td><td>Las reglas de negocio se administran desde el portal con vigencia y cuatro ojos.</td></tr>
<tr><td><b>Bloque 4: desempeño y entrega</b></td><td>5 y 6</td><td>Cifras reproducibles bajo concurrencia y un solo artefacto por reporte.</td></tr>
<tr><td><b>Bloque 5: sostenibilidad</b></td><td>7</td><td>Los patrones corregidos no pueden volver a entrar.</td></tr>
</tbody></table>
"""

(OUT / '07_plan_remediacion.html').write_text(page(
    'Plan de remediación',
    '8 olas &middot; criterios de aceptación verificables &middot; 31-42 sesiones de esfuerzo estimado',
    body2), encoding='utf-8')

# ------------------------------------------------------------------ portal
modulos = [
    ("M1", "Catálogo de parámetros con vigencia",
     "Consulta, alta y edición de los valores hoy hardcodeados: IVA, participación ION/Afirme, umbrales, "
     "vigencias de programa, fechas de negocio. Todo valor tiene vigencia desde y hasta, y nunca se sobrescribe: "
     "se cierra la vigencia anterior y se abre una nueva.",
     "Alta prioridad. Es el modulo que devuelve el control a negocio y el que habilita la Ola 4."),
    ("M2", "Catálogos de negocio",
     "Rubros contables, conceptos, tipos de crédito, orígenes de fondos, cuentas excluidas, convenios. Con "
     "validación referencial, comparación entre ambientes y detección de definiciones duplicadas.",
     "Alta prioridad. Resuelve las reglas duplicadas detectadas en la auditoría."),
    ("M3", "Flujo de aprobación de cuatro ojos",
     "Todo cambio nace como solicitud: autor, justificación, ambiente destino, vista previa del antes y después, "
     "y aprobación de una persona distinta con rol autorizado. Sin aprobación el valor no entra en vigencia.",
     "Alta prioridad. Es el requisito de control interno que hoy no existe."),
    ("M4", "Bitácora y trazabilidad",
     "Registro inmutable de quien cambio que, cuando, con que justificación y quien aprobó; y la consulta "
     "'con que valores se cálculo el cierre de este periodo', que es la pregunta que hace un auditor.",
     "Alta prioridad. Convierte la auditabilidad en una consulta, no en una investigación."),
    ("M5", "Tablero de ejecuciones del cierre",
     "Estado de cada proceso por fecha: inicio, fin, duración, filas afectadas y errores, leídos de la bitácora "
     "de errores de póliza ya normalizada. Con alertas por correo o Teams.",
     "Alta prioridad. Es el modulo que cierra el hallazgo crítico de observabilidad."),
    ("M6", "Paridad y promoción entre ambientes",
     "Matriz objeto x ambiente con hash y fecha, diferencias resaltadas, y promoción de parámetros y catálogos "
     "de desarrollo a QA y a producción con aprobación. El código se sigue promoviendo por integración continua; "
     "el portal gobierna los datos de configuración.",
     "Media-alta. Mantiene vivo el resultado de la Ola 0."),
    ("M7", "Catálogo de dependencias e impacto",
     "El grafo construido en esta auditoría, consultable: quien llama a este objeto, que tablas escribe, que "
     "reportes lo consumen, qué se rompe si cambia. Se regenera en cada despliegue.",
     "Media. Reduce el riesgo de cada cambio posterior."),
    ("M8", "Inventario de reportes",
     "Los 18 reportes lógicos con su procedimiento, su ambiente y su origen de datos, para evitar que vuelvan a "
     "duplicarse por ambiente.",
     "Media-baja. Se construye junto con la Ola 6."),
]

roles = [
    ("Consulta", "Ve parámetros, catálogos, bitácora y tablero. No modifica.", "Negocio, contabilidad, auditoría"),
    ("Solicitante", "Crea solicitudes de cambio de parámetro o catálogo. No puede aprobar las propias.", "Negocio, producto"),
    ("Aprobador", "Aprueba o rechaza solicitudes de su dominio. No puede aprobar lo que el mismo solicito.", "Responsables de área"),
    ("Operador", "Ejecuta la promoción entre ambientes de lo ya aprobado.", "Tecnologia"),
    ("Administrador", "Administra usuarios, roles y definición de parámetros (no sus valores).", "Tecnología con supervisión de riesgos"),
    ("Auditor", "Acceso de solo lectura a toda la bitácora, incluidas las solicitudes rechazadas.", "Auditoría interna"),
]

stack = [
    ("Backend", "ASP.NET Core 8 (C#) con Minimal APIs, Entity Framework Core para configuración y Dapper para las consultas al modelo existente",
     "Es el mismo ecosistema del motor de datos: autenticación integrada con Active Directory sin piezas "
     "intermedias, driver de SQL Server de primera clase, y despliegue tanto en IIS on-premise como en "
     "contenedor. Soporte de largo plazo de Microsoft y el perfil de desarrollador más fácil de contratar en "
     "un entorno SQL Server / SSRS como este."),
    ("Frontend", "React 18 con TypeScript, Vite, TanStack Query y una librería de tabla de datos (AG Grid o TanStack Table) con MUI",
     "El portal es esencialmente rejillas densas, formularios con validación y flujos de aprobación; TypeScript "
     "evita los errores de tipo en un dominio donde un dato mal tipado es un error contable. React es el "
     "ecosistema con más componentes de tabla y más talento disponible."),
    ("Base de datos", "SQL Server: esquema nuevo dedicado (por ejemplo CFG) en la misma instancia",
     "Los parámetros deben ser legibles por los procedimientos de cierre en la misma transacción: ponerlos en "
     "otro motor obligaría a replicarlos y reintroduciría el problema de dos verdades."),
    ("Autenticacion", "Microsoft Entra ID o Active Directory federado (OpenID Connect), roles por grupo de directorio",
     "Sin usuarios locales: el alta y la baja de personas ya están resueltos por el directorio corporativo, que "
     "es lo que espera control interno."),
    ("Integración con el motor", "Vistas y funciones en línea de lectura de parámetros vigentes, consumidas por los procedimientos",
     "El código SQL no llama al portal: lee el catálogo. Así el cierre no depende de que un servicio web este "
     "arriba."),
    ("Despliegue", "Contenedores (Docker) o IIS, con integración continua en Azure DevOps o GitHub Actions y migraciones versionadas del esquema de configuración",
     "Permite que el portal viaje por el mismo camino de aprobación que el resto de los cambios."),
]

alt = [
    ("Node.js con NestJS y React",
     "Viable y con buen ecosistema. Se descarta como primera opción porque la integración con Active Directory "
     "y con SQL Server exige más piezas intermedias, y porque el equipo de este sistema es de perfil "
     "Microsoft: la curva de mantenimiento seria más alta."),
    ("Python con FastAPI y React",
     "Excelente para analítica y para reutilizar el analizador de dependencias de esta auditoría (que ya está en "
     "Python). Recomendación: usarlo para los procesos de análisis y generación de reportes, y no para el "
     "portal transaccional."),
    ("Blazor Server (solo .NET, sin JavaScript)",
     "Reduce el stack a un solo lenguaje y acelera el desarrollo si el equipo no tiene perfil frontend. Se "
     "descarta como primera opción por la dependencia de conexión permanente y por el ecosistema de "
     "componentes de tabla, más limitado."),
    ("Herramienta de bajo código (Power Apps y similares)",
     "Permite un primer modulo en días, pero el flujo de cuatro ojos, la bitácora inmutable y las vigencias "
     "terminan implementándose a la fuerza. Solo recomendable si la decisión es no construir software propio."),
]

body3 = f"""
<p class="lead">Propuesta del portal de administración: el lugar donde las reglas de negocio, los catálogos y la
configuración por ambiente dejan de vivir dentro del código SQL. No es una herramienta de reportes ni un
reemplazo del sistema: es la capa de gobierno que hoy no existe, y es lo que hace sostenible la remediación.</p>

<div class="card azul">
<h3>El problema que resuelve, en concreto</h3>
<p>La auditoría encontró <b>63 grupos de valores hardcodeados</b>, y el caso más ilustrativo es la participación
ION/Afirme partida en 0.10 y 0.90 dentro de <b>28 archivos distintos</b>. Cambiar ese porcentaje hoy significa
un proyecto de desarrollo con 28 oportunidades de equivocarse, sin bitácora de quien lo pidió ni de quien lo
autorizo, y sin forma de recalcular un periodo anterior con el valor que estaba vigente entonces. Con el
portal es un cambio con autor, aprobador, vigencia y trazabilidad.</p>
</div>

<h2>Módulos</h2>
<table><thead><tr><th>&nbsp;</th><th>Modulo</th><th>Alcance</th><th>Prioridad</th></tr></thead><tbody>
{''.join(f'<tr><td class="num">{e(i)}</td><td><b>{e(n)}</b></td><td>{e(d)}</td><td>{e(p)}</td></tr>' for i, n, d, p in modulos)}
</tbody></table>

<h2>Modelo de parámetros con vigencia</h2>
<p>Es la decisión de diseño más importante del portal: <b>nunca se sobrescribe un valor</b>. Recalcular un
periodo anterior debe reproducir la cifra publicada en su momento, y eso solo se logra si el valor se lee con
la fecha del periodo procesado.</p>
<pre>CFG.PARAMETRO        (ID, CLAVE, DESCRIPCION, TIPO_DATO, DOMINIO, ID_DUENIO, REQUIERE_APROBACION)
CFG.PARAMETRO_VALOR  (ID, ID_PARAMETRO, ID_AMBIENTE, VALOR, VIGENTE_DESDE, VIGENTE_HASTA,
                      ID_SOLICITUD, FEC_ALTA, USR_ALTA)
CFG.SOLICITUD        (ID, ID_AMBIENTE, ESTADO, JUSTIFICACION, USR_SOLICITA, FEC_SOLICITA,
                      USR_APRUEBA, FEC_APRUEBA, MOTIVO_RECHAZO)
CFG.BITACORA         (ID, ENTIDAD, ID_ENTIDAD, ACCION, VALOR_ANTERIOR, VALOR_NUEVO,
                      USR, FEC, ID_SOLICITUD)          -- solo insercion

-- Lectura desde el codigo de cierre: no llama al portal, lee el catalogo
CREATE FUNCTION CFG.FN_PARAMETRO_VIGENTE (@CLAVE varchar(60), @FECHA date)
RETURNS TABLE AS RETURN
  SELECT TOP 1 V.VALOR
  FROM CFG.PARAMETRO_VALOR V
  JOIN CFG.PARAMETRO P ON P.ID = V.ID_PARAMETRO
  WHERE P.CLAVE = @CLAVE
    AND V.ID_AMBIENTE = CFG.FN_AMBIENTE_ACTUAL()
    AND @FECHA &gt;= V.VIGENTE_DESDE
    AND (V.VIGENTE_HASTA IS NULL OR @FECHA &lt; V.VIGENTE_HASTA)
  ORDER BY V.VIGENTE_DESDE DESC;</pre>
<p>Restricciones que el modelo debe imponer en la base, no solo en la aplicación: sin traslapes de vigencia por
parámetro y ambiente, sin valor sin solicitud aprobada cuando el parámetro lo exige, aprobador distinto del
solicitante, y bitácora sin actualización ni borrado (permisos, no confianza).</p>

<h2>Roles y segregación de funciones</h2>
<table><thead><tr><th>Rol</th><th>Puede</th><th>Perfil típico</th></tr></thead><tbody>
{''.join(f'<tr><td><b>{e(r)}</b></td><td>{e(p)}</td><td>{e(q)}</td></tr>' for r, p, q in roles)}
</tbody></table>
<p>Regla no negociable: <b>quien solicita no aprueba</b>, y la restricción vive en la base de datos. Si el
control depende solo de la interfaz, no es un control.</p>

<h2>Stack recomendado</h2>
<table><thead><tr><th>Capa</th><th>Tecnología</th><th>Por que</th></tr></thead><tbody>
{''.join(f'<tr><td><b>{e(c)}</b></td><td>{e(t)}</td><td>{e(j)}</td></tr>' for c, t, j in stack)}
</tbody></table>

<div class="card verde">
<h3>Recomendación en una línea</h3>
<p><b>ASP.NET Core 8 (C#) en el backend y React 18 con TypeScript en el frontend, sobre SQL Server y con
autenticación contra el directorio corporativo.</b> La razón principal no es técnica sino de contexto: el
sistema, los reportes y el equipo ya son de ecosistema Microsoft, y el mayor riesgo de este portal no es
escribirlo, es mantenerlo después.</p>
</div>

<h3>Alternativas consideradas</h3>
{''.join(f'<div class="card"><h3>{e(n)}</h3><p>{e(d)}</p></div>' for n, d in alt)}

<h2>Como se construye: entregas cortas y útiles</h2>
<table><thead><tr><th>Entrega</th><th>Contenido</th><th>Esfuerzo</th><th>Valor al terminar</th></tr></thead><tbody>
<tr><td><b>E1 &mdash; Núcleo</b></td><td>Esquema de configuración con vigencias, autenticación contra el directorio, roles, bitácora, y M1 con solo lectura de los parámetros ya cargados</td><td class="num">4-6 sesiones</td><td>Negocio ve, por primera vez y en un solo lugar, con que valores calcula el sistema</td></tr>
<tr><td><b>E2 &mdash; Cuatro ojos</b></td><td>M3 completo, edición con solicitud y aprobación, vista previa del antes y después, y M4</td><td class="num">4-5 sesiones</td><td>Los parámetros se pueden cambiar sin desarrollo y con control interno satisfecho</td></tr>
<tr><td><b>E3 &mdash; Catálogos</b></td><td>M2 con validación referencial y comparación entre ambientes</td><td class="num">4-6 sesiones</td><td>Rubros, conceptos y cuentas excluidas dejan de estar en el código</td></tr>
<tr><td><b>E4 &mdash; Operación</b></td><td>M5 (tablero de ejecuciones con alertas) y M6 (paridad y promoción)</td><td class="num">5-7 sesiones</td><td>El cierre se vigila desde una pantalla y las promociones dejan rastro</td></tr>
<tr><td><b>E5 &mdash; Conocimiento</b></td><td>M7 (dependencias e impacto) y M8 (inventario de reportes)</td><td class="num">3-4 sesiones</td><td>Cada cambio posterior se estima con datos y no con memoria</td></tr>
</tbody></table>
<p>Total aproximado: <b>20 a 28 sesiones</b> de trabajo asistido para los cinco bloques. E1 y E2 son la
condición para la Ola 4 del plan de remediación, por lo que conviene arrancarlos en paralelo con las Olas 0 y 1.</p>

<h2>Lo que el portal no debe hacer</h2>
<div class="card ambar">
<ul>
<li><b>No ejecutar el cierre.</b> Lo dispara el orquestador; el portal lo observa. Mezclar ambas cosas convierte una pantalla en un riesgo operativo.</li>
<li><b>No editar código SQL.</b> El código viaja por integración continua con revisión; el portal gobierna datos de configuración.</li>
<li><b>No ser la única copia de la verdad.</b> Los parámetros viven en la base y se versionan; el portal es la interfaz, no el almacén exclusivo.</li>
<li><b>No permitir cambios sin vigencia.</b> Un valor sin fecha de inicio destruye la capacidad de recalcular periodos anteriores, que es el motivo principal para construirlo.</li>
</ul>
</div>
"""

(OUT / '08_portal_admin.html').write_text(page(
    'Portal de administración de parámetros y ambientes',
    '8 módulos &middot; parámetros con vigencia y cuatro ojos &middot; ASP.NET Core 8 + React con TypeScript sobre SQL Server',
    body3), encoding='utf-8')

# ------------------------------------------- contexto operativo y migracion
arq = [
    ("Origen (lectura)", "Quiero_Confianza",
     "Réplica de solo lectura del transaccional SAF/Sisde. El proceso no escribe en ella.",
     "Que sea réplica elimina el riesgo de afectar al core, pero no garantiza que la fotografía sea estable "
     "mientras el cierre la recorre: sin punto de lectura fijo, dos corridas pueden diferir."),
    ("Destino (escritura)", "KARDIA",
     "Base central donde vive el histórico contable, envuelta por el sistema CAS.",
     "Es el activo a proteger: aquí aplican la idempotencia por corrida, el bloqueo del histórico y la "
     "bitácora de errores que hoy nadie vigila."),
    ("Disparo", "Minutos después del cierre de SAF",
     "El cierre de la póliza del día se ejecuta de forma automática al cerrar operaciones el core.",
     "La ventana es corta y no hay intervención humana: si un paso falla en silencio, la póliza sale "
     "incompleta. Por eso la propagación de errores (Ola 3) vale más que cualquier optimización."),
    ("Ajustes", "Adiciones acumuladas, sin modificar el pasado",
     "Los ajustes de días anteriores se registran como movimientos nuevos; el histórico queda bloqueado.",
     "Es un diseño contable correcto. El control que falta no es evitar la suma, es evitar la suma repetida: "
     "marca de corrida por periodo y rechazo del segundo pase."),
    ("Hardcodeo", "Cuatro pólizas principales",
     "Devengados de intereses, devengados de moratorios, seguros y otras comisiones.",
     "Confirma la prioridad de la parametrización: la matriz de esas cuatro pólizas es la Ola 4 y el primer "
     "módulo del portal con valor visible."),
]

reencuadres = [
    ("WITH (NOLOCK) sobre el origen", "L1-014, L10-016",
     "Lectura sucia que puede introducir transacciones revertidas en la póliza.",
     "El origen es una réplica de solo lectura: no hay riesgo para el core ni transacciones en vuelo del "
     "aplicativo. El riesgo que permanece es de reproducibilidad: la réplica cambia mientras el cierre la "
     "lee, y filas pueden duplicarse u omitirse por movimiento de páginas.",
     "Se mantiene la severidad Alto, con la remediación redirigida a snapshot sobre la réplica más una marca "
     "de sincronía por corrida."),
    ("Idempotencia del cierre", "L1-006",
     "Reprocesar duplica PRINCIPAL_FINAL: defecto de cálculo.",
     "La acumulación es intencional en el diseño del cierre diario. El defecto real es doble: el agregado se "
     "toma de todo el histórico sin filtro de periodo, y no existe marca de corrida que impida un segundo "
     "pase por reintento del job o ejecución manual.",
     "Se conserva como crítico, reescrito y marcado como pendiente de validación del comportamiento esperado "
     "ante reintento."),
    ("Lectura desde bases de QA y shadow", "L1-007, L1-016",
     "Objetos productivos leen datos que no son productivos.",
     "Sin cambio, y ahora con más sustento: el origen autorizado es Quiero_Confianza; _CreditoPuente_QA y "
     "_shadow no son la réplica productiva.",
     "Se mantiene crítico. La remediación por sinónimos por ambiente sigue siendo la correcta."),
    ("Drift entre ambientes", "L1-016 y matriz de paridad",
     "49% de objetos distintos entre desarrollo y producción.",
     "Se confirma que 119 de 126 diferencias son solo el nombre de la base por ambiente, lo que refuerza que "
     "no es divergencia funcional sino falta de sinónimos.",
     "Sin cambio de severidad; el mensaje al cliente se precisa: el drift es artificial y barato de eliminar."),
    ("Normalización del modelo", "Lote 6 (tablas)",
     "Tablas sin llave natural, sin restricciones y con tipos MONEY.",
     "El equipo declara normalización hasta tercera forma normal, y a la vez reconoce en la arquitectura "
     "general tablas duplicadas, identificadores de cliente no unificados entre aplicativos y tablas vacías.",
     "Sin cambio: la declaración de normalización no sustituye la verificación de llaves y restricciones, que "
     "requiere metadatos de la instancia."),
]

matriz = [
    ("Devengado de intereses", "Rubros de interés ordinario por tipo de crédito y programa",
     "Rubro, tipo de crédito, origen, cuenta contable, naturaleza, vigencia"),
    ("Devengado de moratorios", "Rubros moratorios y su exclusión por estado de cartera",
     "Rubro, estado de cartera, cuenta contable, naturaleza, vigencia, criterio de exclusión"),
    ("Seguros", "Conceptos de seguro y su prorrateo",
     "Concepto, aseguradora o esquema, cuenta contable, base de cálculo, IVA aplicable, vigencia"),
    ("Otras comisiones", "Comisiones de prepago, visitas, avalúos y administración",
     "Concepto, rubro, cuenta contable, tasa de IVA, participación por convenio, vigencia"),
]

mig = [
    ("M1", "Congelar el contrato de datos que el proceso necesita del core", "Ahora, junto con la Ola 1",
     "Documentar, por cada uno de los objetos que leen del origen, qué entidades y campos consume y con qué "
     "semántica: crédito, cliente, pago, movimiento, saldo, concepto de cobro, reversa. El resultado es un "
     "diccionario canónico independiente de SAF, no un diagrama de SAF.",
     "Es el único entregable que sobrevive intacto al cambio de core y hoy se puede construir con el análisis "
     "de dependencias ya entregado."),
    ("M2", "Interponer una capa de fachada entre el core y el cálculo", "Ola 1 y Ola 5",
     "Sustituir las lecturas directas de tres partes por vistas o procedimientos de extracción en un esquema "
     "dedicado (por ejemplo EXT o STG) que expongan el modelo canónico. El cálculo contable deja de conocer "
     "el nombre, el esquema y la forma de las tablas de SAF.",
     "Convierte la migración de origen en reescribir una capa delgada, en lugar de tocar 245 objetos. Es la "
     "misma remediación que ya se propuso para eliminar el drift, así que no cuesta trabajo adicional."),
    ("M3", "Inventariar las excepciones del core", "En paralelo con la auditoría",
     "El equipo domina reglas particulares de SAF que no están escritas: reversas de movimientos mal "
     "aplicados que se buscan en tablas específicas, casos de cancelación, programas especiales. Cada una "
     "debe quedar como regla nombrada, con su condición, su tabla de origen y su tratamiento contable.",
     "Es el conocimiento que se pierde si el desarrollador no está disponible, y el que hará imposible "
     "estimar la migración si no se documenta antes."),
    ("M4", "Materializar el staging del día", "Ola 5",
     "Extraer una sola vez por corrida los datos del origen a un área de staging con la marca de sincronía, y "
     "calcular sobre el staging en lugar de volver a leer la réplica en cada procedimiento.",
     "Resuelve al mismo tiempo la reproducibilidad de la cifra, el rendimiento de la ventana de cierre y la "
     "sustitución del origen: cambiar de core es cambiar quién llena el staging."),
    ("M5", "Preparar la prueba de paridad entre core actual y nuevo", "Cuando exista el nuevo core",
     "Con el staging y el contrato canónico, la validación de la migración es mecánica: llenar el staging "
     "desde el core nuevo para un periodo ya cerrado y comparar la póliza resultante contra la publicada, "
     "partida por partida.",
     "Convierte una migración de fe en una migración con evidencia, y permite coexistencia temporal: doble "
     "extracción, una sola contabilidad."),
]

body4 = f"""
<p class="lead">Contexto operativo confirmado con el equipo de desarrollo el 31 de agosto de 2026, cómo ajusta
la lectura de los hallazgos ya entregados, y la estrategia recomendada para el día en que SAF/Sisde salga del
ecosistema. No cambia el alcance ni el número de hallazgos de la auditoría: cambia la redacción de cinco de
ellos y el orden de prioridad de la parametrización.</p>

<div class="card verde">
<h3>Conclusión primero</h3>
<p>La información recibida <b>confirma el propósito de la auditoría</b> (eliminar los valores fijos y
estructurar las reglas contables como una matriz configurable, administrable desde una interfaz) y no invalida
ningún hallazgo. Lo que aporta es precisión: el origen es una réplica de solo lectura, el cierre es diario con
histórico bloqueado y ajustes acumulados, y el hardcodeo se concentra en cuatro pólizas. Con eso, dos hallazgos
se reencuadran, uno se refuerza y la Ola 4 gana un foco concreto.</p>
</div>

<h2>Arquitectura del proceso y qué implica para la auditoría</h2>
<table><thead><tr><th>Elemento</th><th>Qué es</th><th>Como opera</th><th>Implicación de auditoría</th></tr></thead><tbody>
{''.join(f'<tr><td><b>{e(a)}</b></td><td class="mono">{e(b)}</td><td>{e(c)}</td><td>{e(d)}</td></tr>' for a, b, c, d in arq)}
</tbody></table>

<h2>Los cinco hallazgos que se reencuadran</h2>
{''.join(f'''
<div class="card ambar">
  <h3>{e(t)} <span class="tag">{e(ids)}</span></h3>
  <p class="q">Lectura original</p><p>{e(antes)}</p>
  <p class="q">Lectura con el contexto</p><p>{e(ahora)}</p>
  <p class="q">Efecto en el reporte</p><p>{e(efe)}</p>
</div>''' for t, ids, antes, ahora, efe in reencuadres)}

<h2>La matriz de las cuatro pólizas: el corazón de la parametrización</h2>
<p>El equipo ubica los valores fijos en la clasificación de cuatro pólizas, y hoy el alta de un concepto nuevo
obliga a editar el procedimiento, liberarlo y desplegarlo. Esa es exactamente la forma que debe tomar el
catálogo de la Ola 4 y el primer módulo del portal.</p>
<table><thead><tr><th>Póliza</th><th>Que se clasifica hoy en código</th><th>Dimensiones de la matriz</th></tr></thead><tbody>
{''.join(f'<tr><td><b>{e(p)}</b></td><td>{e(q)}</td><td class="mono">{e(r)}</td></tr>' for p, q, r in matriz)}
</tbody></table>
<div class="card azul">
<h3>Criterio de aceptación del módulo</h3>
<p>Un usuario de negocio da de alta un concepto de cobro nuevo, lo mapea a rubro y cuenta contable con fecha de
vigencia, un segundo usuario lo aprueba, y la póliza del día siguiente lo clasifica correctamente <b>sin que
nadie toque el repositorio</b>. Además, todo concepto que llegue del origen sin mapeo debe caer en una bandeja
visible, en lugar de quedar silenciosamente fuera de la póliza: hoy ese caso no tiene detección.</p>
</div>

<h2>Cuando SAF/Sisde salga: como reducir el esfuerzo desde hoy</h2>
<p>El desarrollador tiene razón en que remapear el core es una carga mayor, y en que el conocimiento crítico
está en las excepciones. La recomendación no es adelantar la migración, es <b>cambiar dónde vive el
acoplamiento</b>: hoy el nombre y la forma de las tablas de SAF están escritos en 245 objetos; después de la
remediación deberían estar en una sola capa. Los cinco movimientos siguientes se solapan con trabajo que ya
está en el plan, así que casi no agregan costo.</p>
{''.join(f'''
<div class="ola">
  <h3>{e(k)} &mdash; {e(t)} <span class="tag">{e(w)}</span></h3>
  <p>{e(d)}</p>
  <p style="margin:6px 0 0;font-size:12.5px;color:#93a1bb"><b>Por que vale la pena ahora:</b> {e(v)}</p>
</div>''' for k, t, w, d, v in mig)}

<div class="card rojo">
<h3>Lo que no conviene hacer</h3>
<ul>
<li><b>Esperar al nuevo core para remediar.</b> La parametrización y la trazabilidad del cierre son
independientes del origen: se pierden solo si se escriben otra vez contra tablas de SAF.</li>
<li><b>Diseñar el modelo canónico a partir del esquema de SAF.</b> Debe describir el negocio (crédito, pago,
devengo, concepto de cobro), no el sistema del que hoy se leen los datos.</li>
<li><b>Dejar las excepciones sin documentar.</b> Es el único activo que no se puede reconstruir leyendo
código, y es el que determinará el costo real de la migración.</li>
</ul>
</div>

<h2>Lo que se necesita del cliente para cerrar los pendientes</h2>
<div class="card">
<ul>
<li><b>Consulta a KARDIA en QA (CUA) y metadatos de la instancia.</b> Cierra la Ola 0, los 110 objetos sin
invocador visible, las 187 tablas sin referencia y la verificación de llaves y restricciones.</li>
<li><b>Los jobs del SQL Server Agent y la definición del orquestador CAS.</b> Es lo que hoy impide afirmar qué
dispara cada procedimiento de cierre y con qué frecuencia.</li>
<li><b>Confirmación de contabilidad</b> sobre los cuatro hallazgos contables pendientes y sobre el
comportamiento esperado del cierre ante un reintento.</li>
<li><b>Definición del identificador maestro de cliente</b> (SAF o RFC) entre aplicativos, para el módulo de
catálogos.</li>
</ul>
</div>
"""

(OUT / '10_contexto_migracion.html').write_text(page(
    'Contexto operativo y estrategia ante el cambio de core',
    'Réplica de lectura &middot; cierre diario con histórico bloqueado &middot; matriz de las cuatro pólizas '
    '&middot; salida de SAF/Sisde',
    body4), encoding='utf-8')

# ------------------------------------------- 11 fase 0 y fase 1 con ejemplos
entregables = [
    ("fase0/01_inventario_instancia.sql", "Solo lectura",
     "Extrae de cada instancia el nombre, tipo, fecha de modificación y hash SHA-256 del texto normalizado de "
     "los objetos programables, más columnas, llaves, restricciones, índices, columnas MONEY y filas de cada "
     "tabla. Es la fotografía de lo que realmente corre."),
    ("fase0/02_disparadores_cierre.sql", "Solo lectura",
     "Jobs del SQL Server Agent con su comando exacto, su calendario y las últimas 30 corridas con duración y "
     "resultado, más las últimas filas de la bitácora PO.SAF_POLIZA_ERRORES."),
    ("fase0/03_comparar_paridad.py", "No toca la base",
     "Cruza el CSV de cada ambiente contra el repositorio y clasifica cada objeto en IGUAL, SOLO_ORIGEN, "
     "DIFERENTE, SOLO_INSTANCIA, SOLO_REPO o AUSENTE_EXPORT. Sin argumentos compara BD contra BD_prod, que es "
     "lo que ya se puede correr hoy."),
    ("fase1/generar_sinonimos.py", "No toca la base",
     "Recorre BD y BD_prod y genera el script de sinónimos a partir de las referencias reales al origen. "
     "Reproducible: si aparece una tabla nueva del core, se vuelve a correr."),
    ("fase1/01_crear_sinonimos_EXT.sql", "Crea 38 sinónimos",
     "Script generado, idempotente y parametrizado por ambiente con sqlcmd. Es el único artefacto que difiere "
     "entre producción y QA."),
    ("fase1/02_sustituir_referencias.py", "No modifica los originales",
     "Reescribe las referencias de tres partes a EXT.&lt;objeto&gt; en un directorio de salida separado, "
     "preservando el encoding de cada archivo, y reporta cuántas sustituciones hizo por archivo."),
    ("fase1/03_verificar_sin_referencias.sql", "Solo lectura",
     "Cuatro consultas de verificación posterior al despliegue, cada una con su resultado esperado."),
    ("fase1/04_gate_ci.py", "Compuerta de CI",
     "Falla la construcción si vuelve a entrar una referencia literal al origen; el resto de patrones "
     "(fecha fija, IVA, participación, IP) empieza en modo aviso y pasa a bloqueante conforme cierra cada ola."),
]

f0 = [
    ("Paso 1", "Fotografiar el código que corre",
     "Hoy la única fuente es un export de fecha desconocida: 19 de los 27 objetos de cierre no están en "
     "BD_prod y SP_SAF_SALDOS aparece con 223 de sus 573 líneas.",
     "Ejecutar 01_inventario_instancia.sql en producción y en QA (CUA) y guardar la salida como CSV. Es solo "
     "lectura sobre catálogos del sistema, no toca datos ni objetos.",
     "Un CSV por ambiente con hash por objeto. Cierra cuando existen los dos CSV y su fecha es conocida."),
    ("Paso 2", "Cruzar contra el repositorio",
     "El drift se mide comparando archivos, así que un cambio de formato cuenta igual que un cambio de lógica "
     "y no se sabe qué diferencias importan.",
     "Correr 03_comparar_paridad.py con los CSV. Normaliza CRLF, tabuladores y espacios, y quita el "
     "envoltorio que agrega el export de SSMS, de modo que solo reporta diferencias de código real.",
     "Matriz de paridad en CSV con un estado por objeto. Cierra cuando SOLO_INSTANCIA queda en cero, es "
     "decir cuando nada corre sin estar versionado."),
    ("Paso 3", "Saber quién dispara el cierre",
     "El repositorio no dice qué objeto es punto de entrada, a qué hora arranca ni con qué parámetros; solo "
     "que ocurre minutos después de que SAF cierra.",
     "Ejecutar 02_disparadores_cierre.sql en msdb y revisar las últimas 30 corridas junto con la bitácora de "
     "errores, que hoy nadie consulta.",
     "Lista de jobs, horario y duración real de la ventana. Cierra cuando cada procedimiento de cierre tiene "
     "identificado su disparador."),
    ("Paso 4", "Congelar la línea base y decidir objeto por objeto",
     "Mientras no exista una versión declarada como autorizada, cualquier corrección puede aplicarse sobre "
     "código equivocado y no hay contra qué comparar.",
     "Crear en el repositorio una rama de línea base con el código extraído de producción, y resolver cada "
     "objeto marcado DIFERENTE con una decisión explícita: gana producción, gana desarrollo o requiere "
     "análisis. Las decisiones se registran en la matriz, no en un correo.",
     "Rama de línea base y matriz con decisión firmada por objeto. Cierra cuando no queda ningún objeto en "
     "estado DIFERENTE sin decisión."),
]

paridad = [
    ("IGUAL", "71", "Mismo código en desarrollo y producción una vez normalizado el formato."),
    ("SOLO_ORIGEN", "90", "La única diferencia es el nombre de la base de origen. Desaparecen solas al "
     "aplicar los sinónimos de la Fase 1: es el 72% del drift entre objetos comunes."),
    ("DIFERENTE", "35", "Diferencias reales de código que exigen decisión objeto por objeto, encabezadas por "
     "CIERRE.SP_SAF_SALDOS y la familia PO.SP_COM_*."),
    ("AUSENTE_EXPORT", "50", "Programables que existen en BD y no en el export de producción. No se puede "
     "concluir que no existan allá: es exactamente lo que responde el Paso 1."),
]

f1 = [
    ("Paso 1", "Generar el catálogo de sinónimos",
     "38 objetos del origen concentran las 6.485 referencias literales de los 153 archivos que leen del core. "
     "Ese es el tamaño real del acoplamiento: no son 245 objetos que haya que rediseñar, son 38 nombres.",
     "python3 auditoria/fase1/generar_sinonimos.py"),
    ("Paso 2", "Desplegar los sinónimos en cada ambiente",
     "El mismo script, con el nombre de la base como variable. A partir de aquí la diferencia entre ambientes "
     "vive en una sola línea de despliegue, no en el código.",
     'sqlcmd -S PROD -d KARDIA -i 01_crear_sinonimos_EXT.sql -v ORIGEN="Quiero_Confianza"\n'
     'sqlcmd -S CUA  -d KARDIA -i 01_crear_sinonimos_EXT.sql -v ORIGEN="Quiero_Confianza_shadow"'),
    ("Paso 3", "Sustituir las referencias en el código",
     "Sustitución textual, revisable línea a línea y reversible. Escribe en un directorio aparte: los "
     "archivos de BD y BD_prod no se modifican.",
     "python3 auditoria/fase1/02_sustituir_referencias.py --carpeta BD --salida BD_ext\n"
     "-> 153 archivos, 3.617 sustituciones, 38 objetos distintos del origen"),
    ("Paso 4", "Verificar en la instancia",
     "Las cuatro consultas tienen resultado esperado explícito; si alguna falla, el despliegue no se promueve.",
     "sqlcmd -S PROD -d KARDIA -i 03_verificar_sin_referencias.sql\n"
     "-- 1) 0 filas con 'Quiero_Confianza' en sys.sql_modules\n"
     "-- 2) 38 sinonimos, todos resolviendo\n"
     "-- 3) 1 sola base de origen distinta\n"
     "-- 4) 0 sinonimos rotos con la cuenta que ejecuta el cierre"),
    ("Paso 5", "Cerrar la puerta para que el drift no regrese",
     "Sin compuerta, la primera liberación urgente vuelve a escribir el nombre de la base y el trabajo se "
     "pierde. La regla del origen entra en modo bloqueante desde el primer día.",
     "python3 auditoria/fase1/04_gate_ci.py BD BD_prod   # exit 1 si hay violaciones"),
]

body5 = f"""
<p class="lead">Este documento responde dos preguntas concretas: <b>cómo se reconcilian los ambientes</b> (Fase 0)
y <b>cómo se elimina el drift</b> (Fase 1), con los scripts ya escritos y ejecutados donde era posible sin
acceso a las instancias. Nada de lo que se entrega aquí modifica los archivos SQL originales ni escribe en
ninguna base de datos: los scripts de servidor son de solo lectura, salvo la creación de los sinónimos, que es
la única acción de despliegue de la Fase 1.</p>

<div class="kpis">
<div class="kpi"><b>38</b><span>objetos del origen</span></div>
<div class="kpi"><b>6.485</b><span>referencias literales</span></div>
<div class="kpi"><b>90</b><span>diferencias que son solo el nombre de la base</span></div>
<div class="kpi c"><b>35</b><span>diferencias reales por decidir</span></div>
</div>

<h2>Lo que se entrega, y qué hace cada pieza</h2>
<table><thead><tr><th>Artefacto</th><th>Efecto</th><th>Para qué sirve</th></tr></thead><tbody>
{''.join(f'<tr><td class="mono">{e(a)}</td><td><span class="pill info">{e(b)}</span></td><td>{c}</td></tr>'
         for a, b, c in entregables)}
</tbody></table>

<h2>Fase 0 &mdash; Reconciliación de ambientes, paso por paso</h2>
<p>El objetivo no es "comparar carpetas", es poder afirmar, con evidencia, qué código produce la póliza que se
publica. La Fase 0 es enteramente de lectura y no requiere ventana de mantenimiento.</p>
{''.join(f'''
<div class="ola">
  <h3>{e(k)} &mdash; {e(t)}</h3>
  <p class="q">Situación hoy</p><p>{e(hoy)}</p>
  <p class="q">Qué se hace</p><p>{e(acc)}</p>
  <p class="q">Evidencia y criterio de cierre</p><p>{e(fin)}</p>
</div>''' for k, t, hoy, acc, fin in f0)}

<h3>Ejemplo real: el hash que hace comparable el código</h3>
<p>La comparación no puede ser byte a byte, porque el export de SSMS agrega su propio envoltorio y el formato
cambia entre ambientes. Ambos lados calculan el mismo hash sobre el texto normalizado: en el servidor con
T-SQL y en el repositorio con Python.</p>
<div class="grid2">
<div class="card"><h3>En la instancia (T-SQL)</h3><pre>plano = REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
         texto, CHAR(13), N' '), CHAR(10), N' '), CHAR(9), N' '),
         N'  ', N' '), N'  ', N' ')
...
hash_sha2 = CONVERT(char(64),
   HASHBYTES('SHA2_256', LTRIM(RTRIM(plano))), 2)</pre></div>
<div class="card"><h3>En el repositorio (Python)</h3><pre>def firma(texto, neutralizar_origen=False):
    plano = cuerpo(texto)            # quita SET ANSI_NULLS / GO
    if neutralizar_origen:
        plano = ORIGEN.sub('@ORIGEN@', plano)
    plano = ESPACIOS.sub(' ', plano).strip()
    return hashlib.sha256(plano.encode('utf-8')).hexdigest().upper()</pre></div>
</div>

<h3>Resultado de correrlo hoy: BD contra BD_prod</h3>
<p>El comparador ya se ejecutó sobre el repositorio, sin acceso a las instancias. La cifra de drift del
inventario (126 objetos, 49%) era byte a byte; al descontar formato y envoltorio el cuadro queda así, y es un
cuadro mucho más manejable.</p>
<pre>$ python3 auditoria/fase0/03_comparar_paridad.py
paridad_repo.csv -&gt; AUSENTE_EXPORT=50, DIFERENTE=35, IGUAL=71, SOLO_ORIGEN=90</pre>
<table><thead><tr><th>Estado</th><th>Objetos</th><th>Lectura</th></tr></thead><tbody>
{''.join(f'<tr><td><span class="pill {"c" if k == "DIFERENTE" else "ok" if k == "IGUAL" else "a" if k == "AUSENTE_EXPORT" else "info"}">{e(k)}</span></td><td class="num">{e(n)}</td><td>{e(d)}</td></tr>'
         for k, n, d in paridad)}
</tbody></table>
<div class="card verde">
<p><b>El mensaje para el cliente:</b> de las 125 diferencias entre objetos comunes, <b>90 son solo el nombre de
la base de origen</b> y se van completas con la Fase 1, que es un despliegue de 38 sinónimos. El trabajo de
análisis humano se concentra en <b>35 objetos</b>, no en 126.</p>
</div>

<h2>Fase 1 &mdash; Eliminar el drift con una fachada de sinónimos</h2>
<p>El drift no se corrige objeto por objeto: se corrige quitando del código el dato que cambia entre ambientes.
Hoy el nombre de la base está escrito 6.485 veces; después de la Fase 1 está escrito una vez, en la línea de
despliegue.</p>

<h3>El cambio, con código real de PO.SP_IND_CONDONACION</h3>
<div class="grid2">
<div class="card rojo"><h3>Antes (BD, desarrollo)</h3><pre>FROM Quiero_Confianza_shadow.PR.PR_ENCABEZADO_PAGO A WITH (NOLOCK)
INNER JOIN Quiero_Confianza_shadow.PR.PR_DETALLE_PAGO B WITH (NOLOCK)
        ON A.ID_SECUENCIA = B.ID_SECUENCIA
INNER JOIN Quiero_Confianza_shadow.PR.PR_CREDITOS C WITH (NOLOCK)
        ON A.COD_EMPRESA = C.COD_EMPRESA
JOIN [Quiero_Confianza_shadow].PR.PR_CREDITOS D
        ON A.NUM_CREDITO = D.NUM_CREDITO</pre>
<p style="margin:8px 0 0;font-size:12.5px;color:#93a1bb">En producción el mismo bloque dice
<code>Quiero_Confianza</code>, y en cuatro objetos dice
<code>Quiero_Confianza_CreditoPuente_QA</code>. Esa es toda la diferencia en 90 de los 125 objetos.</p></div>
<div class="card verde"><h3>Después (idéntico en los dos ambientes)</h3><pre>FROM EXT.PR_ENCABEZADO_PAGO A WITH (NOLOCK)
INNER JOIN EXT.PR_DETALLE_PAGO B WITH (NOLOCK)
        ON A.ID_SECUENCIA = B.ID_SECUENCIA
INNER JOIN EXT.PR_CREDITOS C WITH (NOLOCK)
        ON A.COD_EMPRESA = C.COD_EMPRESA
JOIN EXT.PR_CREDITOS D
        ON A.NUM_CREDITO = D.NUM_CREDITO</pre>
<p style="margin:8px 0 0;font-size:12.5px;color:#93a1bb">El objeto queda byte a byte igual en los dos
ambientes, así que puede desplegarse desde una sola fuente y compararse por hash.</p></div>
</div>

<h3>Y el artefacto que absorbe la diferencia</h3>
<pre>-- fase1/01_crear_sinonimos_EXT.sql  (generado, 38 sinonimos, idempotente)
IF SCHEMA_ID(N'EXT') IS NULL EXEC(N'CREATE SCHEMA EXT');
GO
-- 1329 referencias en el corpus auditado
IF OBJECT_ID(N'EXT.PR_RUBRO_COBRO_X_CREDITO', N'SN') IS NOT NULL DROP SYNONYM EXT.PR_RUBRO_COBRO_X_CREDITO;
CREATE SYNONYM EXT.PR_RUBRO_COBRO_X_CREDITO FOR [$(ORIGEN)].[PR].[PR_RUBRO_COBRO_X_CREDITO];
-- 1039 referencias en el corpus auditado
IF OBJECT_ID(N'EXT.PR_ENCABEZADO_PAGO', N'SN') IS NOT NULL DROP SYNONYM EXT.PR_ENCABEZADO_PAGO;
CREATE SYNONYM EXT.PR_ENCABEZADO_PAGO FOR [$(ORIGEN)].[PR].[PR_ENCABEZADO_PAGO];
-- ... 36 mas</pre>

{''.join(f'''
<div class="ola">
  <h3>{e(k)} &mdash; {e(t)}</h3>
  <p>{e(d)}</p>
  <pre>{e(c)}</pre>
</div>''' for k, t, d, c in f1)}

<h2>Orden de despliegue y vuelta atrás</h2>
<table><thead><tr><th>#</th><th>Acción</th><th>Ventana</th><th>Vuelta atrás</th></tr></thead><tbody>
<tr><td class="num">1</td><td>Crear el esquema EXT y los 38 sinónimos en QA (CUA)</td><td>Ninguna: no afecta
código existente, los sinónimos conviven con las referencias de tres partes</td><td><code>DROP SYNONYM</code>
de los 38</td></tr>
<tr><td class="num">2</td><td>Desplegar el código sustituido en QA y recalcular un periodo ya cerrado</td>
<td>Fuera de la ventana de cierre</td><td>Volver a desplegar la versión de la línea base</td></tr>
<tr><td class="num">3</td><td>Comparar la póliza recalculada contra la publicada: debe ser idéntica peso por
peso</td><td>Ninguna</td><td>No aplica, es verificación</td></tr>
<tr><td class="num">4</td><td>Crear los sinónimos en producción apuntando a <code>Quiero_Confianza</code></td>
<td>Ninguna</td><td><code>DROP SYNONYM</code></td></tr>
<tr><td class="num">5</td><td>Desplegar el código en producción después del cierre del día, nunca antes</td>
<td>Ventana posterior al cierre, con el cierre siguiente como primera prueba real</td><td>Reaplicar la línea
base; los sinónimos pueden quedarse sin efecto sobre el código anterior</td></tr>
<tr><td class="num">6</td><td>Activar la compuerta de CI en modo bloqueante</td><td>Ninguna</td><td>No
aplica</td></tr>
</tbody></table>
<div class="card ambar">
<h3>Dos condiciones que hay que verificar antes del paso 4</h3>
<ul>
<li><b>Permisos de la cuenta de servicio</b> sobre el origen: el sinónimo no otorga acceso, solo resuelve el
nombre. La consulta 4 de la verificación debe ejecutarse con la cuenta que corre el cierre, no con una
administrativa.</li>
<li><b>Los 30 reportes .rdl siguen con servidor y catálogo embebidos</b> y no se benefician de los sinónimos:
esos requieren pasar a un <code>DataSourceReference</code> compartido, que es trabajo de la misma ola pero de
otro artefacto.</li>
</ul>
</div>

<h2>Por qué esta fase también paga la salida de SAF/Sisde</h2>
<p>La Fase 1 no es solo higiene de ambientes: es el primer tramo de la capa de fachada del movimiento M2 del
<a href="10_contexto_migracion.html">contexto operativo</a>. Cuando el core cambie, el inventario de lo que hay
que remapear ya no serán 245 objetos programables repartidos en 153 archivos, serán <b>38 sinónimos</b> y, en
el paso siguiente, las vistas canónicas que los sustituyan. La misma tabla que se generó para desplegar los
sinónimos sirve como lista de trabajo de la migración, con el número de referencias como medida de impacto.</p>

<h2>Lo que se necesita para arrancar</h2>
<div class="card">
<ul>
<li><b>Acceso de consulta a KARDIA en producción y en QA (CUA)</b> con permiso de lectura sobre
<code>sys.sql_modules</code>, <code>sys.objects</code> y <code>msdb</code>. Solo lectura; es todo lo que
requiere la Fase 0 completa.</li>
<li><b>Un periodo ya cerrado acordado con contabilidad</b> para la prueba de equivalencia del paso 3, con su
póliza publicada como referencia.</li>
<li><b>Autorización para crear el esquema EXT y los sinónimos</b> en QA primero, y la ventana posterior al
cierre para producción.</li>
<li><b>Definición de quién decide</b> en los 35 objetos con diferencias reales: sin un responsable por objeto
la matriz de la Fase 0 no se cierra.</li>
</ul>
</div>
"""

(OUT / '11_fase0_fase1.html').write_text(page(
    'Fase 0 y Fase 1 &mdash; ejemplos concretos de reconciliación y eliminación del drift',
    'Scripts entregados y ejecutados &middot; 38 sinónimos &middot; 90 de 125 diferencias se van solas',
    body5), encoding='utf-8')

# ------------------------------------- 12 preguntas de confirmacion con negocio
# (area, id, pregunta, hallazgos, por que bloquea, opciones de respuesta, prioridad)
preguntas = [
    ("Contabilidad", "Q01",
     "¿Cuál es la columna correcta del segundo bloque de ajustes ballon: PRINCIPAL_FINAL o MONTOEXIGIBLECOM?",
     "L10-001",
     "El bloque está comentado como MONTOEXIGIBLECOM pero suma intereses, comisiones y moratorios al capital. "
     "Si la columna correcta es la otra, el capital reportado está inflado en todos los cierres con ajustes ballon.",
     ["Es correcto como está: los accesorios ballon capitalizan.",
      "Debe ir a MONTOEXIGIBLECOM; se requiere recálculo de los periodos afectados.",
      "Requiere revisión conjunta con el desarrollador sobre datos de un periodo cerrado."],
     "Bloquea la Ola 2"),
    ("Contabilidad", "Q02",
     "¿Cuál es el criterio único de crédito cancelado para el universo del cierre?",
     "L10-005",
     "El universo de créditos activos y los dos universos de saldos en cuentas de orden usan criterios "
     "distintos de FEC_CANCELACION, así que un mismo crédito puede entrar en un bloque y no en otro.",
     ["FEC_CANCELACION nula o mayor a la fecha de corte.",
      "FEC_CANCELACION nula únicamente.",
      "Depende del tipo de saldo; contabilidad define la regla por bloque."],
     "Bloquea la Ola 2"),
    ("Contabilidad", "Q03",
     "¿Cuál es el catálogo oficial de rubros del cierre, y para cada rubro: se materializa, en qué reporte "
     "participa y causa IVA?",
     "L10-007, L2-017, L1-024",
     "Hoy el generador materializa rubros por lista negra y los reportes los consumen por lista blanca: un "
     "rubro nuevo entra a la tabla y no aparece en ningún reporte, sin que nadie se enteré. Es el catálogo "
     "central del portal.",
     ["Contabilidad entrega el catálogo con los tres atributos por rubro.",
      "Se construye desde el código actual y contabilidad lo valida rubro por rubro.",
      "Se requiere sesión de trabajo con contabilidad y el área de producto."],
     "Bloquea la Ola 4 y el portal"),
    ("Contabilidad", "Q04",
     "¿Cuál es la definición oficial de cartera sin restricción por COD_ORIGEN, y cuáles son las etiquetas de "
     "salida correctas?",
     "L10-008",
     "Dos reportes de cierre usan dos listas distintas de COD_ORIGEN para la misma definición, así que las dos "
     "cifras no cuadran entre sí y ambas se publican.",
     ["Prevalece la lista del reporte diario.",
      "Prevalece la lista del reporte general.",
      "Ninguna es correcta; contabilidad entrega la lista vigente con su vigencia."],
     "Bloquea la Ola 2"),
    ("Contabilidad", "Q05",
     "¿Cuál es la política de redondeo y la tolerancia de cuadre cargo-abono aceptable en la póliza?",
     "L2-013",
     "Los importes viajan en MONEY con redondeos intermedios a dos decimales en varios pasos. Sin una regla "
     "única, dos cálculos válidos dan cifras distintas por centavos y no hay criterio para decir cuál falla.",
     ["Redondeo únicamente al final del cálculo, tolerancia cero en el cuadre.",
      "Redondeo por movimiento, con tolerancia definida por póliza.",
      "Contabilidad define la regla y la tolerancia por tipo de póliza."],
     "Bloquea la Ola 2"),
    ("Contabilidad", "Q06",
     "El cierre comercial lee 'otras comisiones' de la fecha fija '20260123': ¿las pólizas ya publicadas de "
     "otros periodos deben recalcularse y reexpresarse?",
     "L1-001",
     "Corregir el código es trivial; la decisión de negocio es qué hacer con las cifras ya emitidas con el "
     "universo equivocado.",
     ["Se corrige a futuro sin reexpresar.",
      "Se recalculan y reexpresan los periodos afectados.",
      "Contabilidad evalúa la materialidad antes de decidir."],
     "Bloquea la Ola 2"),
    ("Contabilidad", "Q07",
     "¿El reproceso de un periodo ya cerrado está permitido? ¿Quién lo autoriza y qué se espera del resultado: "
     "acumular o recalcular?",
     "L1-006, L6-014",
     "El diseño acumula ajustes por diseño, pero nada impide un segundo pase del mismo periodo y no existe "
     "marca de corrida. La respuesta define si el control es 'rechazar el segundo pase' o 'reproceso "
     "determinista'.",
     ["Nunca se reprocesa: el segundo pase se rechaza siempre.",
      "Se reprocesa con autorización, y debe recalcular (no sumar sobre lo acumulado).",
      "Se reprocesa libremente y la acumulación es el comportamiento esperado."],
     "Bloquea la Ola 2 y la Ola 3"),
    ("Contabilidad", "Q08",
     "¿Cuáles son los valores vigentes, con su fecha de vigencia, de la tasa de IVA, la base de días del "
     "devengo, el umbral de avalúo de vivienda y las fechas del programa COVID?",
     "L1-020, L10-025, L2-017",
     "Son los primeros parámetros que se migran al catálogo del portal. Sin el valor oficial y su vigencia, la "
     "migración copiaría el literal actual sin saber si es el correcto.",
     ["Negocio y contabilidad entregan la tabla de valores con vigencias.",
      "Se toman los valores del código como línea base y se validan uno por uno.",
      "Se requiere confirmar con el área normativa."],
     "Bloquea la Ola 4"),
    ("Negocio", "Q09",
     "¿Cuál es el porcentaje de participación del convenio vigente, desde cuándo, y debe conservarse el monto "
     "bruto además del participado?",
     "L2-001",
     "La participación está escrita como dos literales complementarios (0.10 y 0.90) en 28 archivos, y algunos "
     "procedimientos sobrescriben el monto bruto, con lo que el dato original se pierde.",
     ["El valor vigente es el que está en el código y no ha cambiado.",
      "Hay más de un convenio y cada uno tiene su porcentaje.",
      "El porcentaje cambia en el tiempo y requiere vigencia."],
     "Bloquea la Ola 4"),
    ("Negocio", "Q10",
     "¿La cartera sindicada debe aplicar el tratamiento COVID y la separación balance/cuentas de orden de la "
     "etapa 3?",
     "L2-007",
     "La familia sindicada no lo aplica y sus hermanas sí. Hoy la diferencia solo existe en el código, sin "
     "documento que diga si es deliberada.",
     ["Es deliberada por la naturaleza del producto: se documenta y se cierra.",
      "Es una deuda de la versión sindicada: hay que portar el tratamiento.",
      "Aplica solo para una parte de los créditos sindicados."],
     "Ya en tu lista &middot; bloquea la Ola 2"),
    ("Negocio", "Q11",
     "¿Dos procesos distintos pueden compartir el mismo número de póliza?",
     "L2-012",
     "Hay 74 números de póliza escritos uno por procedimiento y al menos uno reutilizado en dos procesos. Si no "
     "se permite, hoy existe un defecto; si se permite, el catálogo del portal necesita otra llave lógica.",
     ["No: el número es único por proceso y el caso actual es un defecto.",
      "Sí: la póliza agrupa varios procesos por diseño.",
      "Depende del tipo de póliza."],
     "Ya en tu lista &middot; bloquea la Ola 4"),
    ("Negocio", "Q12",
     "¿Cuáles de las divergencias entre los procedimientos hermanos comercial e individual son intencionales?",
     "L2-008, L10-010",
     "La misma operación está implementada dos veces con filtros, rubros y redondeos distintos. Antes de "
     "unificar hay que saber qué diferencia es una regla de producto y qué diferencia es un descuido.",
     ["Negocio revisa la matriz de divergencias y marca cada fila.",
      "Todas las diferencias deben desaparecer: la regla es la misma.",
      "Se resuelve caso por caso durante la remediación."],
     "Bloquea la Ola 2"),
    ("Negocio", "Q13",
     "¿Cuál es el catálogo oficial de tipos de crédito, con la marca de en qué procesos participa cada uno, y "
     "qué debe pasar cuando aparece un tipo desconocido?",
     "L2-018, L6-015",
     "La clasificación está repetida en 37 listas distintas dentro de 104 archivos. El comportamiento ante un "
     "tipo nuevo hoy es silencioso: el crédito simplemente no entra al cálculo.",
     ["El tipo desconocido debe detener el cierre con error explícito.",
      "Debe registrarse como excepción y continuar.",
      "Debe tomar un tratamiento por omisión definido por negocio."],
     "Bloquea la Ola 4"),
    ("Negocio", "Q14",
     "¿Quién es el dueño de cada catálogo y quién autoriza el alta de un rubro o concepto nuevo, con qué "
     "tiempo de respuesta?",
     "L1-024, L2-017, portal M1-M3",
     "Es la pregunta que define el portal: hoy un concepto nuevo es un cambio de código. El flujo de cuatro "
     "ojos necesita nombres de roles, no de personas.",
     ["Un solo dueño por catálogo, con aprobador distinto del capturista.",
      "Dueño por familia de póliza.",
      "Se requiere definir la matriz de responsabilidades."],
     "Bloquea el portal"),
    ("Negocio", "Q15",
     "El reporte a Afirme deja la comisión de administración en cero por un literal de rubro mal escrito: "
     "¿el área receptora lo ha detectado y hay que reemitir los reportes ya enviados?",
     "L6-007",
     "El defecto es de una línea, pero la información salió de la institución con un concepto en cero.",
     ["Se corrige a futuro sin reemitir.",
      "Hay que reemitir los periodos afectados.",
      "Se escala al área que administra el convenio."],
     "Bloquea la Ola 2"),
    ("Negocio", "Q16",
     "¿Cuál es la salida autoritativa cuando dos artefactos publican la misma cifra: reporte diario o general, "
     "y qué variante del reporte de póliza contable es la oficial?",
     "L10-010, L12-005, L12-008",
     "Existen pares de reportes que ejecutan el mismo procedimiento con filtros fijos distintos. Ambas cifras "
     "circulan y no hay definición de cuál manda.",
     ["Negocio designa la oficial y la otra se retira.",
      "Ambas son válidas para audiencias distintas: se renombran y documentan.",
      "Se requiere comparar cifras antes de decidir."],
     "Bloquea la Ola 6"),
    ("Riesgos", "Q17",
     "¿El canal minorista o comercial puede seguir derivándose de TIP_TASA='F' para efectos de reporte "
     "regulatorio?",
     "lote 6, pendientes no técnicos",
     "Es una inferencia: se usa el tipo de tasa como proxy del canal. Si el regulador exige el canal real, la "
     "cifra reportada se sostiene en una equivalencia no documentada.",
     ["Sí, la equivalencia es válida y se documenta.",
      "No: se requiere el atributo de canal real en la fuente.",
      "Riesgos debe validarlo con el área normativa."],
     "Ya en tu lista &middot; bloquea la Ola 2"),
    ("Riesgos", "Q18",
     "¿Cuál es el criterio correcto de asignación de etapa de riesgo, y hubo periodos mal clasificados por el "
     "filtro de periodo anulado?",
     "L1-002",
     "Una precedencia de OR/AND deja el filtro de periodo sin efecto en el UPDATE de etapa, así que el "
     "resultado depende de datos de otros periodos.",
     ["El criterio es el declarado y hay que corregir el código y revisar el histórico.",
      "Se corrige a futuro sin revisar el histórico.",
      "Riesgos revisa el impacto sobre las etapas ya reportadas."],
     "Bloquea la Ola 2"),
    ("Riesgos", "Q19",
     "¿La granularidad del reporte de riesgos es folio o folio más sección?",
     "L10-018",
     "El procedimiento agrupa por folio pero publica una llave que incluye la sección y colapsa atributos "
     "descriptivos con MIN y MAX, con lo que la llave publicada no es única.",
     ["Folio: la sección se retira de la llave.",
      "Folio más sección: se corrige el agrupamiento.",
      "Riesgos define la granularidad esperada del entregable."],
     "Bloquea la Ola 2"),
    ("Riesgos", "Q20",
     "¿El universo del programa COVID se define por el umbral NUM_CREDITO menor a 6051, o por un atributo del "
     "crédito?",
     "L6-003, L1-015, L10-025",
     "Una función escalar consumida por 66 procedimientos decide el tratamiento COVID con un número de crédito "
     "como frontera, y el umbral difiere entre desarrollo y producción. Si entra un crédito nuevo con número "
     "menor, recibe tratamiento COVID.",
     ["El umbral es correcto y es histórico cerrado.",
      "Debe sustituirse por una marca del crédito o por vigencia.",
      "Riesgos y negocio definen el universo formalmente."],
     "Bloquea la Ola 4"),
    ("Operación", "Q21",
     "¿Los esquemas PAG, edc, edcc, juicios, demandas, ori y cierre_puente existen en producción, y qué "
     "versión del cierre corre realmente?",
     "L2-019, L6-004, L10-006, L12-002",
     "26 objetos programables del repositorio no aparecen en el export de producción y SP_SAF_SALDOS está "
     "desplegado con 223 de sus 573 líneas. Es lo que resuelve la Fase 0 con acceso de solo lectura.",
     ["Existen y el export está incompleto: se entrega acceso para reconciliar.",
      "No existen: son módulos solo de desarrollo.",
      "Existen parcialmente y hay que revisar objeto por objeto."],
     "Ya en tu lista &middot; bloquea toda la remediación"),
    ("Operación", "Q22",
     "¿Quién debe recibir la alerta cuando el cierre termina con errores, en qué tiempo, y qué se hace "
     "mientras se resuelve?",
     "L12-004, L10-002",
     "102 objetos escriben en la bitácora de errores de póliza y ninguno la vigila. Un cierre puede terminar en "
     "éxito con la póliza incompleta y la detección depende de que alguien note el descuadre.",
     ["Se define un responsable de guardia y un canal de alerta.",
      "La alerta va al área de sistemas y contabilidad en paralelo.",
      "Se requiere definir el procedimiento de escalamiento."],
     "Bloquea la Ola 3"),
    ("Operación", "Q23",
     "¿Cuál es el calendario oficial de días hábiles y la fecha de negocio que debe usar el proceso?",
     "L6-012, L10-019",
     "Varios procedimientos usan la fecha del servidor y ventanas de días naturales. En un cierre diario que "
     "corre minutos después de SAF, la diferencia entre fecha de sistema y fecha de negocio cambia el "
     "universo.",
     ["Existe un calendario institucional y se debe consumir.",
      "Se usa la fecha de sistema y es correcto.",
      "Hay que construir el calendario como catálogo del portal."],
     "Bloquea la Ola 2"),
    ("Operación", "Q24",
     "¿Se ha ejecutado alguna vez en producción el generador de órdenes de facturación con importes "
     "aleatorios, y puede retirarse el objeto?",
     "L6-001",
     "El procedimiento inserta importes aleatorios en la cola de facturación por cada estado de cuenta real del "
     "corte, sin guarda de ambiente. Si se ejecutó en producción, hay un incidente de datos, no un hallazgo de "
     "código.",
     ["Nunca se ejecutó en producción y el objeto puede retirarse.",
      "Se usa para pruebas y debe quedar bloqueado por guarda de ambiente.",
      "Se requiere revisar la bitácora de ejecuciones."],
     "Bloquea la Ola 2"),
    ("Operación", "Q25",
     "¿Se requiere una revisión retroactiva de los pagos emparejados por coincidencia parcial de referencia?",
     "L6-002, L6-013",
     "El identificador de pagos empareja el crédito con una coincidencia invertida y se queda con el número de "
     "crédito más bajo cuando hay varios candidatos: pudo aplicar pagos al crédito equivocado.",
     ["Sí, con alcance y periodo definidos por operación.",
      "No: el layout garantiza unicidad y no hay casos ambiguos.",
      "Se ejecuta primero un diagnóstico de cuántos casos ambiguos existen."],
     "Bloquea la Ola 2"),
    ("Seguridad y legal", "Q26",
     "¿Cuál es el alcance del enmascaramiento de datos personales y bancarios, y quién puede verlos sin "
     "máscara?",
     "L6-017",
     "251 tablas contienen datos personales y bancarios sin enmascaramiento ni cifrado, y solo 30 tienen rastro "
     "de auditoría. El alcance lo define cumplimiento, no el equipo técnico.",
     ["Cumplimiento entrega la clasificación de datos por tabla.",
      "Se enmascara todo dato personal salvo excepción autorizada.",
      "Se limita al ambiente de QA y desarrollo."],
     "Ya en tu lista &middot; bloquea la Ola 7"),
    ("Seguridad y legal", "Q27",
     "Cuatro procedimientos de producción leyeron datos de la base de QA: ¿se requiere revisión de las pólizas "
     "generadas y nota a auditoría interna?",
     "L1-007, L12-007",
     "Es el hallazgo con mayor exposición ante un revisor externo: cifras contables calculadas con una fuente "
     "que no es la réplica autorizada.",
     ["Sí: se revisan los periodos afectados y se documenta.",
      "No: esos procedimientos no se ejecutan en producción.",
      "Se requiere primero determinar desde cuándo apuntan a QA."],
     "Bloquea la Ola 1"),
    ("Seguridad y legal", "Q28",
     "El correo de prueba en el campo de contacto de los clientes: ¿se usa para envíos y hay que notificar el "
     "incidente?",
     "L6-009",
     "Un proceso deja un correo de prueba como segundo contacto de todos los clientes. Si el envío usa ese "
     "campo, es un incidente de datos personales.",
     ["El campo no se usa para envíos: solo se corrige el dato.",
      "Sí se usa: hay que evaluar notificación conforme a la política.",
      "Se requiere revisar el proceso de envío."],
     "Bloquea la Ola 2"),
    ("Negocio", "Q29",
     "¿Cómo debe tratarse el tipo de crédito 8 en los estados de cuenta? El pendiente está escrito como "
     "comentario en el código desde 2024.",
     "lote 6, pendientes no técnicos",
     "El código declara explícitamente que falta definir el tratamiento y sigue sin resolverse, así que hoy los "
     "créditos de ese tipo reciben el tratamiento por omisión sin que nadie lo haya autorizado.",
     ["Recibe el mismo tratamiento que el tipo equivalente vigente.",
      "Requiere reglas propias que negocio debe definir.",
      "El tipo ya no se opera y puede retirarse del catálogo."],
     "Bloquea la Ola 4"),
    ("Gobierno del portal", "Q30",
     "¿Se permiten cambios de parámetro con vigencia retroactiva, y quién los autoriza?",
     "portal M1-M3",
     "Determina el diseño del catálogo: un cambio retroactivo obliga a recalcular pólizas ya publicadas, así "
     "que puede ser una función del portal o algo explícitamente prohibido.",
     ["Prohibido: la vigencia siempre es a futuro.",
      "Permitido con doble autorización y recálculo controlado.",
      "Permitido solo antes del cierre del día."],
     "Bloquea el portal"),
    ("Gobierno del portal", "Q31",
     "¿Quién es el propietario de cada uno de los 63 grupos de valores hoy hardcodeados?",
     "catálogo de hardcodeo completo",
     "Sin propietario, el parámetro migra al portal pero nadie puede autorizar su cambio, y el proceso vuelve a "
     "depender del desarrollador.",
     ["Se asigna propietario por grupo en una sesión de trabajo.",
      "Todo queda bajo contabilidad.",
      "Se define por familia de póliza."],
     "Bloquea el portal"),
]

areas = []
for a, *_ in preguntas:
    if a not in areas:
        areas.append(a)

preguntas = [(a, 'Q{:02d}'.format(i), *resto)
             for i, (a, _, *resto) in enumerate(
                 sorted(preguntas, key=lambda p: areas.index(p[0])), start=1)]

filas = "".join(f"""
<div class="ola">
  <h3>{e(qid)} &mdash; {e(preg)}</h3>
  <p style="margin:2px 0 8px"><span class="tag">{e(area)}</span><span class="tag">{e(orig)}</span>
  <span class="pill info">{blo}</span></p>
  <p class="q" style="color:#93a1bb;font-size:12.5px;text-transform:uppercase;letter-spacing:.5px;margin:8px 0 2px">
  Por qué hay que preguntarlo</p>
  <p style="margin:0">{e(por)}</p>
  <p class="q" style="color:#93a1bb;font-size:12.5px;text-transform:uppercase;letter-spacing:.5px;margin:10px 0 2px">
  Respuestas posibles (para acotar la conversación)</p>
  <ul>{''.join(f'<li>{e(o)}</li>' for o in ops)}</ul>
</div>""" for area, qid, preg, orig, por, ops, blo in preguntas)

conteo = "".join(
    f'<tr><td>{e(a)}</td><td class="num">{sum(1 for p in preguntas if p[0] == a)}</td></tr>'
    for a in areas)

body6 = f"""
<p class="lead">Las {len(preguntas)} confirmaciones que hoy bloquean la remediación, ordenadas por área
responsable. No son dudas de implementación: cada una es una decisión que el equipo técnico no puede tomar
porque la respuesta define cuál es la cifra correcta, y cinco de ellas ya estaban identificadas por el equipo
del proyecto. Para cada pregunta se indica el hallazgo que la origina, por qué no se puede avanzar sin ella y
un conjunto de respuestas posibles, de modo que la sesión con el área sea de decisión y no de exploración.</p>

<div class="kpis">
<div class="kpi c"><b>{sum(1 for p in preguntas if 'Ola 1' in p[6] or 'toda la remediación' in p[6])}</b>
<span>bloquean el arranque</span></div>
<div class="kpi a"><b>{sum(1 for p in preguntas if 'Ola 2' in p[6])}</b><span>bloquean correcciones de cifra</span></div>
<div class="kpi m"><b>{sum(1 for p in preguntas if 'portal' in p[6] or 'Ola 4' in p[6])}</b>
<span>bloquean el portal</span></div>
<div class="kpi b"><b>{len(areas)}</b><span>áreas involucradas</span></div>
</div>

<table><thead><tr><th>Área</th><th>Preguntas</th></tr></thead><tbody>{conteo}</tbody></table>

<div class="card ambar">
<h3>Cómo usarlo</h3>
<ul>
<li><b>Una sesión por área</b>, no una reunión general: las preguntas de contabilidad no se resuelven con
riesgos presente y viceversa.</li>
<li><b>Toda respuesta queda por escrito con fecha y responsable.</b> Varias de estas decisiones cambian cifras
ya publicadas; el registro es parte de la evidencia de la remediación.</li>
<li><b>Las respuestas alimentan directamente el catálogo del portal</b>: las de contabilidad y negocio son, en
su mayoría, el contenido inicial de los parámetros con vigencia.</li>
<li>Hay una hoja de seguimiento en <code>auditoria/12_preguntas_negocio.csv</code> para llenar respuesta,
responsable y fecha.</li>
</ul>
</div>

<h2>Preguntas por área</h2>
{filas}

<h2>Lo que no es una pregunta de negocio</h2>
<p>Para no mezclar agendas: los hallazgos transaccionales (78 de 80 procedimientos revierten y reportan éxito),
los de rendimiento, los de estándares y la eliminación del drift <b>no requieren decisión de negocio</b>. Son
correcciones técnicas con criterio de aceptación objetivo y avanzan en paralelo a estas confirmaciones. Del
lado técnico solo hacen falta tres cosas, ya listadas en
<a href="11_fase0_fase1.html">Fase 0 y Fase 1</a>: acceso de consulta a KARDIA en producción y QA, un periodo
cerrado de referencia y la autorización para crear el esquema EXT.</p>
"""

(OUT / '12_preguntas_negocio.html').write_text(page(
    'Confirmaciones pendientes con negocio, contabilidad, riesgos y operación',
    f'{len(preguntas)} decisiones que bloquean la remediación &middot; con el hallazgo que las origina',
    body6), encoding='utf-8')

with (OUT / '12_preguntas_negocio.csv').open('w', encoding='utf-8-sig', newline='') as fh:
    w = csv.writer(fh, delimiter=';')
    w.writerow(['Id', 'Area', 'Pregunta', 'Hallazgos', 'Por que bloquea', 'Que bloquea',
                'Respuestas posibles', 'Respuesta', 'Responsable', 'Fecha'])
    for area, qid, preg, orig, por, ops, blo in preguntas:
        w.writerow([qid, area, preg, orig, por, blo.replace('&middot;', '/'),
                    ' | '.join(ops), '', '', ''])

# ------------------------------------------------- 13 dummy de catálogos
MET = json.loads((OUT / 'dummy' / 'metricas.json').read_text(encoding='utf-8'))
TC = MET['tipo_credito']['BD_prod']
TCD = MET['tipo_credito']['BD']
RC = MET['reporte_cobranza']

BANDERAS = [
    ('SEGMENTO_INDIVIDUAL', 'Contabilidad', [1, 3, 4, 9, 10, 11, 16, 17],
     'Pólizas individuales (SP_IND_*)'),
    ('SEGMENTO_COMERCIAL', 'Contabilidad', [2, 12, 13, 14, 15, 18, 27, 28],
     'Pólizas comerciales (SP_COM_*); el 5 se agrega vía ES_MEZZANINE'),
    ('SEGMENTO_SINDICADA', 'Negocio', [7], 'Pólizas de cartera sindicada (SP_SND_*)'),
    ('ES_MINORISTA', 'Negocio', [12, 13, 14, 15, 28], 'Etiquetado «minoristas» en el cierre comercial'),
    ('ES_PUENTE', 'Negocio', [2, 18, 27], 'Etiquetado «puente» en el cierre comercial'),
    ('ES_MEZZANINE', 'Negocio', [5], 'Presente en 24 de los 50 filtros comerciales'),
    ('ES_EMPLEADO', 'Negocio', [9, 10, 11], 'Fuerza ID_PRODUCTO 51 y NOMBRE_PRODUCTO EMPLEADO'),
    ('ES_ADMINISTRADA_IND', 'Negocio', [4, 20, 23], 'Cartera administrada individual'),
    ('ES_ADMINISTRADA_COM', 'Negocio', [6, 19, 21, 22, 24], 'Etiquetado «administrada»'),
    ('ES_CASTIGO_COMERCIAL', 'Contabilidad', [25, 29], 'Castigo comercial'),
    ('ES_CASTIGO_INDIVIDUAL', 'Contabilidad', [26], 'Castigo individual'),
    ('ES_ADMON_AFIRME', 'Negocio', [4], 'Sujeta a factor de participación'),
]


def med(bandera):
    """Filtros de BD_prod cuyo conjunto contiene el grupo completo de la bandera."""
    d = TC['por_bandera'].get(bandera)
    return (str(d['predicados']), str(d['archivos'])) if d else ('&mdash;', '&mdash;')


matriz = "".join(
    f'<tr><td><code>{e(b)}</code></td><td class="num">{e(area)}</td>'
    f'<td class="num">{e(", ".join(str(t) for t in tipos))}</td>'
    f'<td class="num">{med(b)[0]}</td><td class="num">{med(b)[1]}</td>'
    f'<td>{e(nota)}</td></tr>'
    for b, area, tipos, nota in BANDERAS)

celdas = sum(len(t) for _, _, t, _ in BANDERAS)

ESCENARIOS = [
    ("Nace un tipo de crédito nuevo (por ejemplo un producto verde)",
     f"Buscar las {TC['predicados']} listas del código, decidir en cuáles entra, editar los archivos "
     f"afectados, probar, liberar y repetir el mismo ejercicio en el ambiente de desarrollo "
     f"({TCD['predicados']} predicados).",
     "Un alta en el catálogo y marcar las banderas que le aplican, con fecha de inicio. Cero cambios "
     "de código, cero liberaciones."),
    ("Un tipo sale de un proceso (el caso real de la cartera sindicada en el cierre comercial)",
     "Comentar el valor en la lista, como está hoy con «--,7»: sin fecha, sin autor y sin motivo "
     "registrado.",
     "Cerrar la vigencia de la bandera. Queda usuario, fecha y motivo, y el cierre del periodo "
     "anterior sigue dando la misma cifra."),
    ("Nace un rubro de cobro nuevo",
     f"Agregarlo a las {RC['predicados_rubro']} listas de rubro del reporte de cobranza, en sus dos "
     f"bloques, y a los demás procedimientos que lo consideren. Es el escenario que el equipo describió "
     f"como «escribir coma nuevo y volver a liberar».",
     "Dos filas en el catálogo de rubros: el rubro y su IVA, con el grupo al que suman."),
    ("Llega un rubro que nadie dio de alta",
     "Nadie se entera: el rubro no suma en ninguna columna y solo se nota al cuadrar el total.",
     "El proceso lo reporta como excepción de configuración el mismo día y el portal lo muestra como "
     "pendiente de clasificar."),
    ("Cambia el factor de participación de la cartera administrada",
     "Editar las 14 apariciones de «monto * 9» del reporte y revisar si concuerda con el 0.10 / 0.90 de "
     "los cierres comerciales.",
     "Una fila nueva con vigencia en el catálogo de participación, previa aprobación de contabilidad. "
     "El histórico no se altera."),
]

escen = "".join(
    f'<tr><td>{e(c)}</td><td>{e(hoy)}</td><td>{e(prop)}</td></tr>'
    for c, hoy, prop in ESCENARIOS)

CLASES = [
    ("Pertenencia a un grupo", "ok",
     "Qué tipos de crédito participan en qué proceso; qué rubro suma a qué columna; qué pólizas entran "
     "en el reporte.",
     "Autoservicio en el portal, con vigencia, bitácora y aprobación de cuatro ojos del área dueña. "
     "Es el 100% de lo que este dummy resuelve."),
    ("Etiquetas y atributos de salida", "info",
     "Textos como «INDIVIDUAL CASTIGO», el ID_PRODUCTO 51 o el nombre «EMPLEADO».",
     "Catálogo, pero con aprobación de contabilidad: cambian la presentación de la cifra y su "
     "trazabilidad con el reporte publicado."),
    ("Fórmulas y multiplicadores", "m",
     "El factor 9 de la cartera administrada, la partición 0.10 / 0.90, el IVA al 16%.",
     "Catálogo solo después de validar la base de cálculo. Migrarlos tal cual como configuración "
     "editable trasladaría al portal una inconsistencia que hoy ya existe entre procesos."),
    ("Reglas y precedencias contables", "c",
     "Que comercial gane sobre individual cuando un crédito cae en los dos grupos; el criterio de "
     "etapa; el tratamiento de reversas.",
     "Se quedan en código, bajo control de cambios. No son parámetros: son la contabilidad."),
]

clases = "".join(f"""
<div class="card {'rojo' if p == 'c' else 'ambar' if p == 'm' else 'azul' if p == 'info' else 'verde'}">
<h3>{e(t)}</h3><p style="margin:0"><b>Qué es:</b> {e(q)}</p>
<p style="margin:6px 0 0"><b>Cómo se trata:</b> {e(c)}</p></div>""" for t, p, q, c in CLASES)

body7 = f"""
<p class="lead">Cómo se elimina el hardcodeo de <code>NUM_DESC_TIPO_CREDITO</code> y de los rubros de cobranza
sin construir un catálogo gigante. La propuesta son <b>tres catálogos pequeños y una matriz de banderas</b>:
{len(BANDERAS)} banderas para los 28 tipos de crédito que aparecen en el código, {RC['rubros_distintos']} rubros
y 5 pólizas. No hay un registro por póliza ni
por combinación: las combinaciones se derivan por consulta. Todo el código de ejemplo está en
<code>auditoria/dummy/</code>, se crea en un esquema <code>DUMMY</code> aparte y no modifica ningún objeto
existente.</p>

<div class="kpis">
<div class="kpi c"><b>{TC['predicados']}</b><span>filtros por tipo de crédito en producción</span></div>
<div class="kpi a"><b>{TC['archivos']}</b><span>archivos que hay que tocar hoy</span></div>
<div class="kpi m"><b>{TC['listas_distintas']}</b><span>listas distintas mantenidas a mano</span></div>
<div class="kpi b"><b>{len(BANDERAS)}</b><span>banderas que las sustituyen</span></div>
</div>

<h2>1. El problema, medido</h2>
<p>En el export de producción, <code>NUM_DESC_TIPO_CREDITO</code> aparece {TC['ocurrencias']} veces en
{TC['archivos']} archivos, de las cuales {TC['predicados']} son decisiones (un <code>IN (...)</code> o una
igualdad) y forman {TC['listas_distintas']} conjuntos distintos escritos a mano. En desarrollo la cuenta es
mayor todavía: {TCD['predicados']} decisiones en {TCD['archivos']} archivos. Ninguna de esas listas tiene
nombre, fecha ni dueño; el único rastro de intención son comentarios como
<code>-- minoristas</code> o <code>--,7 -- sindicada</code>. Las cifras se reproducen con
<code>python3 auditoria/dummy/06_medir_esfuerzo.py</code>.</p>

<div class="card azul">
<h3>El punto de partida ya existe</h3>
<p style="margin:0">No hace falta inventar un catálogo: <code>PO.SAF_CAT_DESC_TIPO</code> ya guarda los tipos
con su descripción, cartera y administrador &mdash; lo que no tiene es una sola bandera por proceso &mdash;, y <code>CIERRE.SP_CMR_GEN_MES</code> ya centraliza el conjunto en
la temporal <code>#TIPO_CREDITOS</code> y lo reutiliza en sus filtros. Lo que falta es una sola cosa: que la
<b>pertenencia a cada proceso</b> viva en datos y no en la lista literal que llena esa temporal. Por eso el
cambio es acotado y no un rediseño.</p>
</div>

<h2>2. El diseño: una matriz de banderas, no un catálogo por póliza</h2>
<p>Tres objetos, en <code>auditoria/dummy/01_catalogo_tipo_credito.sql</code>:</p>
<ul>
<li><b>Catálogo de tipos</b> (28 filas en la semilla, las que aparecen en algún filtro del código): el que ya
existe, sin cambios de estructura.</li>
<li><b>Catálogo de banderas</b> ({len(BANDERAS)} filas): una fila por concepto de negocio, con su área dueña.
Se consulta, no se edita en la operación diaria.</li>
<li><b>Matriz tipo &times; bandera con vigencia</b> ({celdas} filas hoy): solo se guardan las casillas marcadas.
Es lo que el usuario ve en el portal como una pantalla de casillas de verificación.</li>
</ul>
<p>Y una función en línea, <code>DUMMY.FN_TIPOS_CREDITO(bandera, fecha)</code>, que devuelve el conjunto
vigente a una fecha. Es una función de tabla en línea, no escalar: el optimizador la expande dentro de la
consulta, así que no reintroduce el problema de rendimiento de las funciones fila por fila del hallazgo L6-005.</p>

<h3>Las {len(BANDERAS)} banderas se derivan del código actual, no se inventan</h3>
<table><thead><tr><th>Bandera</th><th>Área dueña</th><th>Tipos de crédito hoy</th><th>Filtros que sustituye</th>
<th>Archivos</th><th>De dónde sale</th></tr>
</thead><tbody>{matriz}</tbody></table>
<p style="color:#93a1bb;margin-top:8px">Los tipos de cada fila son exactamente los números que aparecen hoy en
las listas del código. «Filtros que sustituye» cuenta, en el export de producción, los filtros cuyo conjunto
contiene por completo el grupo de la bandera: son los que esa bandera resuelve sola o combinada con otra, y por
eso la suma de la columna es mayor que los {TC['predicados']} filtros totales. Si el catálogo no reproduce las mismas listas, la prueba del punto 6 lo detecta.</p>

<div class="card ambar">
<h3>Regla de diseño que evita el catálogo gigante</h3>
<p style="margin:0">No se crea una bandera por cada lista que aparezca en el código: eso convertiría las
{TC['listas_distintas']} listas de hoy en {TC['listas_distintas']} banderas y no resolvería nada. Las banderas
son <b>conceptos de negocio</b> (segmento, castigo, empleado, administrada); las combinaciones se expresan en la
consulta pidiendo dos banderas a la vez. Por eso {len(BANDERAS)} banderas cubren {TC['predicados']} filtros.</p>
</div>

<h2>3. Antes y después, con las líneas reales</h2>
<p>Los cuatro casos completos están en <code>auditoria/dummy/02_antes_despues_tipo_credito.sql</code>. Estos son
los dos que resumen el patrón.</p>

<h3>Caso A &mdash; el más frecuente: lista literal en un filtro</h3>
<p><code>BD_prod/dbo.FN_CARTERA_CREDITO.UserDefinedFunction.sql</code></p>
<pre>-- ANTES
WHERE NUM_CREDITO = @NUM_CREDITO
  AND NUM_DESC_TIPO_CREDITO IN (1, 3, 4, 9, 10, 11, 16, 17, 26, 4, 20, 23)

-- DESPUÉS
WHERE C.NUM_CREDITO = @NUM_CREDITO
  AND EXISTS (SELECT 1 FROM DUMMY.FN_TIPOS_CREDITO('SEGMENTO_INDIVIDUAL', @FECHA_PROCESO) T
              WHERE T.NUM_DESC_TIPO_CREDITO = C.NUM_DESC_TIPO_CREDITO)</pre>
<p>Se usa <code>EXISTS</code> y no <code>JOIN</code> como regla del proyecto: en un filtro,
<code>EXISTS</code> no puede multiplicar filas aunque el catálogo devolviera un duplicado. Solo se usa
<code>JOIN</code> cuando además se necesita una columna del catálogo. De paso, esa lista muestra tres cosas que
el catálogo corrige por construcción: el 4 está repetido, el 26 (castigo individual) viene mezclado dentro de la
lista de segmento, y un tipo nuevo que nadie agregue a ninguna lista termina
clasificado como comercial en silencio.</p>

<h3>Caso B &mdash; el más favorable: la temporal que ya está centralizada</h3>
<p><code>BD_prod/CIERRE.SP_CMR_GEN_MES.StoredProcedure.sql</code></p>
<pre>-- ANTES
SELECT NUM_DESC_TIPO_CREDITO INTO #TIPO_CREDITOS
FROM Quiero_Confianza.PR.PR_DESC_TIPOS_CREDITO
WHERE COD_EMPRESA = '001' AND NUM_DESC_TIPO_CREDITO IN (
         12,13,14,15,28 -- minoristas
        ,2,18,27        -- puente
        --,7              -- sindicada
        ,25             -- castigo
        ,5              -- mezzanine
        ,6,19,21,22,24) -- administrada

-- DESPUÉS
SELECT T.NUM_DESC_TIPO_CREDITO INTO #TIPO_CREDITOS
FROM DUMMY.FN_TIPOS_CREDITO('SEGMENTO_COMERCIAL', @FECHA_PROCESO) T;

-- los ~14 filtros posteriores del procedimiento NO se tocan:
AND C.NUM_DESC_TIPO_CREDITO IN (SELECT NUM_DESC_TIPO_CREDITO FROM #TIPO_CREDITOS)</pre>
<p>Este patrón es el que conviene generalizar en toda la familia de cierre: sembrar una vez el conjunto vigente
al inicio del procedimiento y filtrar contra la temporal, para no consultar el catálogo decenas de veces. Y el
<code>--,7</code> comentado es exactamente el problema de gobierno: sacar la cartera sindicada del cierre
comercial fue un cambio de código sin fecha, sin autor y sin motivo. En el catálogo es un cierre de vigencia.</p>

<h2>4. El reporte de cobranza: tres catálogos, no uno</h2>
<p><code>dbo.REPORTE_COBRANZA_INTEGRACION</code> concentra en {RC['lineas']} líneas tres hardcodeos de
naturaleza distinta, y por eso <b>una sola tabla de tipos de crédito no lo resuelve</b>:</p>
<table><thead><tr><th>Hoy</th><th>Cuánto hay</th><th>Catálogo que lo sustituye</th></tr></thead><tbody>
<tr><td>Listas de rubro dentro de cada columna del reporte</td>
<td class="num">{RC['predicados_rubro']} filtros, {RC['rubros_distintos']} rubros,
{RC['ocurrencias_literales_rubro']} literales</td>
<td><code>CAT_RUBRO</code> (rubro &rarr; grupo, marca de IVA)</td></tr>
<tr><td>Identificadores de póliza y sus etiquetas de cartera</td>
<td class="num">{RC['predicados_id_poliza']} predicados sobre ID_POLIZA</td>
<td><code>CAT_POLIZA_COBRANZA</code> (5 filas)</td></tr>
<tr><td><code>monto * 9</code> / <code>monto * 1</code> y los dos bloques del UNION ALL</td>
<td class="num">{RC['factor_hardcodeado']} apariciones,
{RC['literal_admon_individual']} veces la cadena ADMINISTRACION INDIVIDUAL</td>
<td><code>CAT_PARTICIPACION</code> (2 vistas con factor y vigencia)</td></tr>
</tbody></table>

<p>Con eso, cada columna de importe deja de ser un bloque con dos listas y pasa a una línea:</p>
<pre>-- ANTES (y otras 13 columnas iguales, duplicadas en el segundo bloque del UNION ALL)
SUM(CASE WHEN rubro IN ('MORATORIOS','INTERES_MORATORIO','MORA_EMPRESARIAL')
              AND tipo_credito =  'ADMINISTRACION INDIVIDUAL' THEN monto * 9
         WHEN rubro IN ('MORATORIOS','INTERES_MORATORIO','MORA_EMPRESARIAL')
              AND tipo_credito &lt;&gt; 'ADMINISTRACION INDIVIDUAL' THEN monto * 1
         ELSE 0 END) AS MORATORIOS,

-- DESPUÉS
SUM(CASE WHEN A.GRUPO='MORATORIOS' AND A.ES_IVA=0 THEN A.MONTO*A.FACTOR ELSE 0 END) AS MORATORIOS,</pre>
<p>El segundo bloque del <code>UNION ALL</code> desaparece como código duplicado: hoy son dos consultas casi
idénticas (la del total administrado con factor 9 y la de la parte propia con factor 1); en la versión
parametrizada son <b>dos filas del catálogo de participación</b>, y el movimiento se anota una vez por vista
aplicable. Las columnas de salida, su nombre y su orden no cambian: son el contrato con quien consume el
reporte. Versión completa en <code>auditoria/dummy/04_reporte_cobranza_v2.sql</code>.</p>

<div class="card rojo">
<h3>Cuatro defectos que aparecieron al normalizar las listas</h3>
<ul>
<li>En la columna <code>OTRO</code> del primer bloque, la rama de cartera propia pide
<code>'IVA COMISION_ANTICIPADA'</code> donde debía pedir <code>'COMISION_ANTICIPADA'</code>: la comisión
anticipada de cartera propia no entra en <code>OTRO</code> y su IVA entra ahí en lugar de
<code>IVA_OTRO</code>.</li>
<li>La columna <code>IVA_OTRO</code> del primer bloque omite <code>'IVA COMISION_ANTICIPADA'</code>, que el
segundo bloque sí incluye: los dos bloques no son consistentes entre sí.</li>
<li>La póliza 35 se etiqueta <code>'INDIVIDUAL '</code> en el primer bloque y
<code>'INDIVIDUAL EMPLEADO '</code> en el segundo.</li>
<li>La cartera administrada se etiqueta <code>'AFIRME'</code> en el primer bloque y <code>'ION'</code> en el
segundo. Es intencional (total contra parte propia), pero no está documentado en ninguna parte del código.</li>
</ul>
<p style="margin:6px 0 0">Los cuatro son consecuencia del mismo mecanismo: mantener {RC['predicados_rubro']}
listas a mano en dos bloques casi idénticos. Con grupo y marca de IVA en catálogo, los dos primeros son
imposibles de escribir. Falta cuantificar su impacto con datos reales, y es una diferencia que debe firmar
contabilidad antes de sustituir el procedimiento.</p>
</div>

<h2>5. Qué se gana: el mismo cambio, hoy y con catálogo</h2>
<table><thead><tr><th>Situación</th><th>Hoy</th><th>Con catálogo y banderas</th></tr></thead>
<tbody>{escen}</tbody></table>
<p>El ahorro no está en escribir menos SQL una vez, está en que <b>el cambio deja de ser un despliegue</b>: hoy
cada alta recorre el ciclo de editar, probar, liberar y verificar en dos ambientes, y depende de la
disponibilidad del desarrollador que conoce las {TC['listas_distintas']} listas. Con el catálogo es un cambio de
datos autorizado por el área dueña, con vigencia y bitácora. Cuánto tiempo de calendario representa cada ciclo
hoy es el dato que falta y que conviene medir con el equipo con los últimos cambios reales, para poner la cifra
en la presentación.</p>

<h2>6. Cómo se demuestra que no cambia ninguna cifra</h2>
<p><code>auditoria/dummy/05_prueba_equivalencia.sql</code>. Regla del proyecto: ningún objeto parametrizado
entra a producción sin este resultado firmado.</p>
<ul>
<li><b>Equivalencia del catálogo contra el código:</b> por cada bandera migrada, comparar el conjunto que
devuelve la función contra la lista literal que hoy está en el código, en los dos sentidos. Resultado exigido:
cero filas de diferencia.</li>
<li><b>Equivalencia del reporte:</b> ejecutar el procedimiento actual y el parametrizado sobre un día ya cerrado
y conciliado y comparar con <code>EXCEPT</code> en ambos sentidos, más un resumen del delta por columna. Se
espera delta cero en todo excepto <code>OTRO</code> y <code>IVA_OTRO</code>, por la corrección del defecto
anterior; ese monto se documenta y lo firma contabilidad.</li>
<li><b>Integridad de la configuración</b>, que se ejecuta después de cada cambio hecho en el portal y antes de
aplicarlo: tipos activos sin segmento, tipos en dos segmentos a la vez, vigencias traslapadas, rubros sin su
contraparte de IVA y rubros presentes en los movimientos del día que no estén catalogados.</li>
</ul>
<p>Ese último punto agrega algo que hoy no existe: los huecos de configuración se vuelven visibles el mismo día
en lugar de aparecer como un descuadre.</p>

<h2>7. Qué se parametriza y qué no</h2>
<p>La distinción importa porque de ella depende quién autoriza cada cambio. No todo hardcodeo debe volverse
configurable.</p>
{clases}

<h2>8. Vigencia, ambiente y gobierno</h2>
<ul>
<li><b>Vigencia obligatoria en las tres tablas.</b> El proceso resuelve las reglas con la fecha del movimiento,
no con la fecha de hoy: reejecutar un día anterior devuelve la misma cifra aunque el catálogo haya cambiado
después. Es lo que hace compatible el catálogo con el bloqueo del histórico contable y con los ajustes como
adiciones acumuladas.</li>
<li><b>Un cambio nunca es retroactivo por omisión.</b> La vigencia arranca en la fecha que autorice el área
dueña; si se necesita efecto retroactivo, es una excepción con aprobación explícita y con reproceso declarado.</li>
<li><b>Separación por ambiente.</b> El catálogo se edita en QA (CUA), se valida con la prueba de equivalencia y
se promueve a producción; el portal no permite editar producción directamente.</li>
<li><b>Cuatro ojos y bitácora</b> sobre las tablas de catálogo, con usuario y fecha en cada fila, tal como está
maquetado en <a href="09_demo_portal.html">la demo del portal</a>.</li>
<li><b>Dueño por bandera.</b> La columna de área dueña de la tabla de banderas es donde aterrizan las
respuestas de Q14 y Q31 de las <a href="12_preguntas_negocio.html">confirmaciones pendientes</a>.</li>
</ul>

<h2>9. Orden de adopción sugerido</h2>
<div class="ola"><h3>Paso 1 &mdash; Catálogo y matriz en QA, sin tocar un solo procedimiento</h3>
<p class="obj">Crear las tablas, sembrarlas con las listas actuales y correr la prueba de equivalencia por
bandera. Criterio de aceptación: las {len(BANDERAS)} banderas reproducen exactamente las listas del código.</p></div>
<div class="ola"><h3>Paso 2 &mdash; Un solo objeto piloto: CIERRE.SP_CMR_GEN_MES</h3>
<p class="obj">Es el caso de menor riesgo porque solo cambia cómo se llena <code>#TIPO_CREDITOS</code> y no
toca los filtros. Criterio: el cierre comercial de un periodo cerrado da cifra idéntica.</p></div>
<div class="ola"><h3>Paso 3 &mdash; Reporte de cobranza con los tres catálogos</h3>
<p class="obj">Es el que más código elimina y el que ya tiene defectos detectados. Criterio: delta cero salvo
las columnas <code>OTRO</code> e <code>IVA_OTRO</code>, con el monto documentado y firmado.</p></div>
<div class="ola"><h3>Paso 4 &mdash; Resto de la familia por olas, empezando por castigo y devengo</h3>
<p class="obj">Una bandera a la vez y todos sus usos juntos, nunca un procedimiento aislado: migrar la mitad de
los usos de una bandera dejaría dos fuentes de verdad. Criterio: cero listas literales de
<code>NUM_DESC_TIPO_CREDITO</code> en los objetos migrados, verificable con el mismo control automático que ya
usa la Fase 1.</p></div>
<div class="ola"><h3>Paso 5 &mdash; El portal administra lo ya migrado</h3>
<p class="obj">El portal se conecta cuando el catálogo ya es la fuente de verdad y las validaciones de
integridad están en su lugar; no antes.</p></div>

<h2>10. Límites de esta propuesta</h2>
<ul>
<li>Es un <b>dummy</b>: todo se crea en un esquema <code>DUMMY</code> y nada se ejecutó contra una instancia de
SQL Server. Las descripciones de los tipos viven en la base, no en el repositorio, así que la semilla trae los
números y no los nombres.</li>
<li><code>TIPO_CREDITO</code> (el texto que viaja en el movimiento) y <code>NUM_DESC_TIPO_CREDITO</code> (el
número del crédito) son <b>dimensiones distintas</b>. Este dummy no las une: hacerlo requiere una relación
explícita validada con negocio.</li>
<li>El factor 9 se conserva tal como está. No se propone volverlo editable hasta entender su relación con la
partición 0.10 / 0.90 de los cierres comerciales: son bases de cálculo que no coinciden.</li>
<li><b>Ninguna pregunta pendiente bloquea este diseño.</b> Lo que bloquean es su operación: sin dueño por
bandera (Q14, Q31) el catálogo existe pero nadie puede autorizar un cambio, y el proceso volvería a depender del
desarrollador.</li>
</ul>
"""

(OUT / '13_dummy_catalogos.html').write_text(page(
    'Dummy de la estrategia: catálogo de tipos de crédito con banderas y catálogos de cobranza',
    'CIERRE, SAF, PO y dbo.REPORTE_COBRANZA_INTEGRACION &middot; antes y después del código real',
    body7), encoding='utf-8')

print('ok', [p.name for p in sorted(OUT.glob('[01]*.html'))])
