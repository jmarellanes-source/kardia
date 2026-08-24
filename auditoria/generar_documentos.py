# -*- coding: utf-8 -*-
"""Genera los documentos ejecutivos de la auditoria KARDIA/SAF:
06_ejecutivo.html, 07_plan_remediacion.html y 08_portal_admin.html
"""
import html
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
<a href="07_plan_remediacion.html">Plan de remediacion</a><a href="08_portal_admin.html">Portal de administracion</a>
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
<footer>Auditoria de codigo SQL KARDIA / SAF &middot; analisis estatico del repositorio (BD, BD_prod y reportes).
No se ejecuto ningun objeto contra una instancia de SQL Server ni se leyeron datos productivos:
los hallazgos que dependen de datos, de plan de ejecucion o de reglas contables se marcan como pendientes de validacion.</footer>
</body></html>
"""


def e(x):
    return html.escape(str(x))


# ---------------------------------------------------------------- ejecutivo
riesgos = [
    ("R1", "c", "No sabemos con certeza que codigo esta corriendo en produccion",
     "126 de los 256 objetos comunes difieren entre el ambiente de desarrollo y el de produccion (49%), "
     "19 de los 27 objetos de la familia de cierre no aparecen en el export de produccion, y el procedimiento "
     "de saldos SP_SAF_SALDOS tiene 573 lineas en desarrollo y 223 en produccion, sin los bloques de saldos "
     "en cuentas de orden ni post-castigo.",
     "Cualquier correccion puede aplicarse sobre una version equivocada, y hoy no hay forma de demostrar ante "
     "un revisor externo que la cifra publicada proviene del codigo autorizado.",
     "Reconciliar ambientes contra los metadatos de produccion. Es solo lectura y es el prerrequisito de todo "
     "lo demas."),
    ("R2", "c", "Cuatro procedimientos de produccion leen datos de la base de QA",
     "Objetos productivos consultan Quiero_Confianza_CreditoPuente_QA y Quiero_Confianza_shadow; el nombre de "
     "la base externa esta escrito dentro del codigo y difiere entre ambientes en 7 objetos.",
     "Cifras de cierre calculadas con datos de prueba, y la imposibilidad de promover una correccion sin "
     "editarla a mano en cada ambiente: es la causa raiz del 49% de drift.",
     "Sustituir los nombres de base embebidos por sinonimos por ambiente. Un solo cambio elimina la causa del "
     "drift y habilita el despliegue automatizado."),
    ("R3", "c", "El cierre no es repetible y un error puede pasar inadvertido",
     "El cierre mensual individual duplica PRINCIPAL_FINAL si se reprocesa; el cierre comercial lee comisiones "
     "de una fecha fija ('20260123') en lugar del periodo; 89 de 100 objetos revisados hacen rollback sin "
     "propagar el error; y la bitacora de errores de poliza la escriben 102 objetos, pero ninguno la vigila.",
     "Un cierre puede terminar en 'exito' con cifras incompletas o duplicadas y llegar a contabilidad sin que "
     "ningun control automatico lo detecte. La deteccion depende hoy de que alguien note el descuadre.",
     "Idempotencia por periodo, propagacion de errores (THROW) y un monitor sobre la bitacora que alerte antes "
     "de que la poliza llegue a contabilidad."),
    ("R4", "a", "Las reglas de negocio estan escritas dentro del codigo, no en un catalogo",
     "63 grupos de valores hardcodeados: IVA fijo al 16%, participacion ION/Afirme partida en 0.10/0.90 "
     "repetida en 28 archivos, catalogos de rubros contables, tipos de credito, origenes y cuentas excluidas "
     "embebidos, fechas de vigencia del programa COVID en 45 lugares de un solo procedimiento.",
     "Cada cambio normativo o comercial se convierte en un proyecto de desarrollo con riesgo de que una copia "
     "quede sin actualizar. Ya hay dos definiciones distintas de 'cuota COVID' y dos de 'cartera' conviviendo.",
     "Extraer los valores a catalogos con vigencia y administrarlos desde el portal propuesto, con aprobacion "
     "de cuatro ojos y bitacora de cambios."),
    ("R5", "a", "El proceso lee sin control de concurrencia y procesa fila por fila",
     "Uso extendido de WITH (NOLOCK) en calculos financieros y reportes (287 usos solo en la familia de "
     "cierre), cursores en los procedimientos de saldos, y funciones escalares con acceso a datos invocadas "
     "desde decenas de procedimientos.",
     "Riesgo de leer filas no confirmadas o duplicadas durante el propio cierre (cifras no reproducibles), "
     "y una ventana de cierre que crece con el volumen de cartera.",
     "Nivel de aislamiento snapshot para lectura, conversion de funciones escalares a funciones en linea y "
     "eliminacion de cursores en los procedimientos criticos, midiendo duracion antes y despues."),
    ("R6", "a", "La entrega de informacion repite los mismos problemas del codigo",
     "Los 30 archivos de reportes son 18 reportes logicos duplicados por ambiente, con la direccion del "
     "servidor escrita dentro del archivo (tres servidores distintos) y ninguno usando origen de datos "
     "compartido. Dos copias del mismo reporte de poliza contable filtran productos y etapas distintos.",
     "El mismo reporte puede entregar cifras distintas segun el archivo que se abra, y basta publicar el "
     "artefacto equivocado para que un usuario consulte otro ambiente sin notarlo.",
     "Un artefacto por reporte logico, origen de datos por ambiente y publicacion por script desde el "
     "repositorio."),
]

decisiones = [
    ("Contabilidad / Control interno",
     "Confirmar el destino correcto del UPDATE etiquetado MONTOEXIGIBLECOM en el cierre individual, el criterio "
     "de FEC_CANCELACION, el filtro de moratorios que esta comentado y el catalogo oficial de rubros contables. "
     "Son cuatro hallazgos con evidencia en el codigo cuyo impacto en la cifra solo contabilidad puede confirmar."),
    ("Negocio / Producto",
     "Definir la fuente oficial de IVA, participacion ION/Afirme, tipos de credito, origenes de fondos, cuentas "
     "excluidas y vigencias de programa; y que valores debe poder cambiar un usuario sin pasar por desarrollo."),
    ("Tecnologia / Infraestructura",
     "Autorizar la lectura de metadatos y estadisticas de uso en produccion (sys.sql_modules, "
     "sys.dm_exec_procedure_stats), entregar los jobs del Agent y definir los ambientes formales "
     "(desarrollo, QA, produccion) con su mecanismo de promocion."),
    ("Riesgos / Auditoria",
     "Validar el modelo de control propuesto: cuatro ojos para cambios de parametro, bitacora inmutable, "
     "segregacion de funciones y evidencia de conciliacion por cierre."),
    ("Direccion del proyecto",
     "Aprobar el orden de las olas y la construccion del portal de administracion, o pedir explicitamente que "
     "la remediacion se haga solo en codigo, sin portal."),
]

estado = [
    ("Defecto verificable leyendo el codigo", "ok",
     "Duplicacion al reprocesar, fecha fija en el cierre comercial, lectura de la base de QA, DELETE sin filtro "
     "de poliza, importes aleatorios en facturacion, correo de prueba en el padron de clientes, filtros "
     "divergentes entre copias del mismo reporte.",
     "Se puede corregir con la evidencia entregada; solo requiere validar el resultado esperado."),
    ("Riesgo tecnico dependiente del entorno", "info",
     "NOLOCK, cursores, funciones escalares, MONEY, ausencia de XACT_ABORT, tablas sin llave natural.",
     "El defecto existe; la magnitud depende de volumen, concurrencia y plan de ejecucion, que no se pueden "
     "medir sin acceso a la instancia."),
    ("Pendiente de validacion funcional o contable", "m",
     "Columna destino del UPDATE de MONTOEXIGIBLECOM, criterio de FEC_CANCELACION, filtro comentado de "
     "moratorios, catalogo de rubros, granularidad de reportes.",
     "Se documenta como riesgo con su evidencia. No se corrige sin confirmacion del area responsable."),
    ("Hipotesis que requiere informacion externa", "a",
     "Los 110 objetos sin invocador visible, las 187 tablas sin codigo asociado, el esquema AP en el catalogo "
     "INFORMES, y si el export de produccion esta incompleto o hay objetos sin promover.",
     "Se resuelve con los jobs del Agent y los metadatos de produccion; sin eso no es posible afirmar que algo "
     "sea codigo muerto."),
]

body = f"""
<p class="lead">Auditoria de los 503 archivos SQL de desarrollo, los 256 de produccion y los 30 artefactos de
reportes del sistema KARDIA / SAF, ejecutada en cinco fases por lotes de riesgo. Este documento resume, para
direccion y para las areas de negocio, que se encontro, que significa en terminos de riesgo operativo y
contable, y que decisiones se necesitan para empezar a remediar.</p>

<div class="kpis">
  <div class="kpi"><b>789</b><span>Archivos auditados</span></div>
  <div class="kpi"><b>117</b><span>Hallazgos</span></div>
  <div class="kpi c"><b>22</b><span>Criticos</span></div>
  <div class="kpi a"><b>51</b><span>Altos</span></div>
  <div class="kpi m"><b>35</b><span>Medios</span></div>
  <div class="kpi b"><b>9</b><span>Bajos</span></div>
  <div class="kpi"><b>63</b><span>Grupos de hardcodeo</span></div>
  <div class="kpi"><b>49%</b><span>Drift dev vs prod</span></div>
</div>

<h2>Lo que hay que saber en un minuto</h2>
<div class="card azul">
<p>El sistema funciona y produce la contabilidad todos los dias, pero lo hace <b>sin las tres garantias que se
esperan de un proceso bancario</b>: no se puede demostrar que el codigo que corre en produccion es el
autorizado (49% de diferencia entre ambientes, y objetos productivos leyendo la base de QA); el cierre no es
repetible ni avisa cuando falla (reprocesar duplica cifras, y los errores se registran en una bitacora que
nadie vigila); y las reglas de negocio viven dentro del codigo (63 grupos de valores fijos, con dos
definiciones distintas de la misma regla conviviendo).</p>
<p>Ninguno de los tres se resuelve comprando software: se resuelven con una secuencia de trabajo acotada, que
empieza por reconciliar ambientes y termina con las reglas administradas desde un portal con aprobacion de
cuatro ojos. La buena noticia es que <b>el riesgo esta concentrado</b>: ocho objetos son invocados por casi todo
el portafolio y 18 procedimientos alimentan toda la entrega de informacion, asi que proteger menos del 5% del
codigo cubre la mayor parte del riesgo.</p>
</div>

<h2>Los seis riesgos que importan</h2>
{''.join(f'''
<div class="card {'rojo' if sev=='c' else 'ambar'}">
  <h3><span class="pill {sev}">{'Critico' if sev=='c' else 'Alto'}</span> &nbsp;{rid}. {e(t)}</h3>
  <p class="q">Evidencia</p><p>{e(ev)}</p>
  <p class="q">Que significa para el negocio</p><p>{e(imp)}</p>
  <p class="q">Que hay que hacer</p><p>{e(acc)}</p>
</div>''' for rid, sev, t, ev, imp, acc in riesgos)}

<h2>Como leer los hallazgos: cuatro niveles de certeza</h2>
<p>Es la parte que suele generar discusion con el area de desarrollo, y por eso se declara de entrada. La
auditoria es <b>estatica</b>: se leyo el codigo del repositorio, no se ejecuto nada contra SQL Server ni se
consultaron datos productivos.</p>
<table><thead><tr><th>Nivel</th><th>Ejemplos</th><th>Como se trata</th></tr></thead><tbody>
{''.join(f'<tr><td><span class="pill {c}">{e(n)}</span></td><td>{e(ej)}</td><td>{e(tr)}</td></tr>' for n, c, ej, tr in estado)}
</tbody></table>

<h2>Decisiones que necesitamos del cliente</h2>
<table><thead><tr><th>Area</th><th>Decision</th></tr></thead><tbody>
{''.join(f'<tr><td><b>{e(a)}</b></td><td>{e(d)}</td></tr>' for a, d in decisiones)}
</tbody></table>

<h2>Que no cubre esta auditoria</h2>
<div class="card">
<ul>
<li>Seguridad de la instancia: usuarios, roles, permisos efectivos, cifrado y auditoria de SQL Server. Requiere acceso al servidor.</li>
<li>Rendimiento real: planes de ejecucion, indices, esperas y volumetria. Los hallazgos de rendimiento se basan en el patron de codigo, no en mediciones.</li>
<li>Conciliacion contable con datos: no se compararon cifras entre el sistema y la contabilidad; los hallazgos contables se plantean como riesgo con su evidencia.</li>
<li>Codigo que no esta en el repositorio: la aplicacion, los ETL, los jobs del Agent y el esquema AP del catalogo INFORMES quedan fuera del alcance porque no fueron entregados.</li>
</ul>
</div>

<h2>Documentos de soporte</h2>
<p>Todos los detalles tecnicos, con evidencia linea por linea y filtros por severidad, categoria y ambiente:</p>
<ul>
<li><a href="index.html">Consolidado de la auditoria</a> &mdash; entrada unica a todos los lotes</li>
<li><a href="01_lote1.html">Lote 1</a>: 20 objetos de mayor riesgo &middot;
    <a href="02_lotes2-5.html">Lotes 2-5</a>: 80 objetos y familias clonadas &middot;
    <a href="03_lote6.html">Lote 6</a>: PAG, edc, SAF, dbo, RPT y funciones</li>
<li><a href="04_lotes10-11.html">Lotes 10-11</a>: familia completa de cierre &middot;
    <a href="05_dependencias.html">Dependencias y capa de reportes</a></li>
<li><a href="07_plan_remediacion.html">Plan de remediacion por olas</a> &middot;
    <a href="08_portal_admin.html">Propuesta del portal de administracion</a></li>
</ul>
"""

(OUT / '06_ejecutivo.html').write_text(page(
    'Resumen ejecutivo de la auditoria SQL',
    '789 archivos auditados &middot; 117 hallazgos &middot; 5 fases de analisis &middot; 2026-08-19',
    body), encoding='utf-8')

# ------------------------------------------------------------ remediacion
olas = [
    ("Ola 0", "Reconciliacion de ambientes y linea base", "3-4 sesiones",
     "Saber que corre en produccion antes de tocar una linea de codigo.",
     ["Comparar los 256 objetos comunes contra sys.sql_modules de produccion (nombre, fecha de modificacion y hash) y resolver los 19 objetos de cierre ausentes en el export.",
      "Aclarar SP_SAF_SALDOS: 573 lineas en desarrollo contra 223 en produccion.",
      "Exportar al repositorio los jobs del SQL Server Agent y las tareas del orquestador, un script por job.",
      "Definir la rama por ambiente y congelar cambios manuales en produccion.",
      "Publicar la matriz de paridad como linea base del control de cambios."],
     ["Existe una matriz objeto x ambiente con hash y fecha, sin celdas desconocidas.",
      "Todo objeto productivo tiene su equivalente identico en el repositorio, o una excepcion documentada y con responsable.",
      "Cada procedimiento de cierre tiene identificado su disparador."],
     "Nulo en produccion: solo lectura de metadatos.",
     "Ninguna. Es el punto de partida.", "azul"),
    ("Ola 1", "Eliminar la causa del drift: nombres de base y ambiente en el codigo", "2-3 sesiones",
     "Que el mismo script se despliegue sin editar en los tres ambientes.",
     ["Crear sinonimos por ambiente para las bases externas (Quiero_Confianza, Quiero_Confianza_shadow, Quiero_Confianza_CreditoPuente_QA) y sustituir los nombres embebidos en los 7 objetos afectados.",
      "Eliminar toda referencia a bases de QA desde objetos productivos (4 procedimientos).",
      "Reemplazar los nombres de base de tres partes por sinonimos en el resto del portafolio.",
      "Compuerta de integracion continua que rechace cualquier script con un nombre de base literal."],
     ["Ningun objeto productivo referencia una base de QA o shadow.",
      "El mismo archivo .sql se aplica sin modificacion en desarrollo, QA y produccion.",
      "La compuerta falla en una prueba deliberada con un nombre de base literal."],
     "Bajo: cambia la resolucion de nombres, no la logica. Verificable comparando el plan y el resultado sobre un periodo cerrado.",
     "Ola 0.", "azul"),
    ("Ola 2", "Correcciones criticas de cifra", "4-6 sesiones",
     "Cerrar los defectos que hoy pueden alterar una cifra contable.",
     ["Idempotencia del cierre mensual individual: reprocesar un periodo debe dejar el mismo resultado (borrado por periodo con llave, o UPSERT por llave natural).",
      "Sustituir la fecha fija '20260123' del cierre comercial por el periodo recibido como parametro.",
      "Corregir el DELETE de PRINCIPAL sin filtro de poliza en PO.SYS_SP_MOV_CARGO.",
      "Retirar edc.SP_Genera_Ordenes_Dummy de produccion o protegerlo con guarda de ambiente, y limpiar el correo de prueba del padron de clientes.",
      "Resolver, ya con respuesta de contabilidad, los cuatro hallazgos contables pendientes de validacion."],
     ["Ejecutar dos veces el cierre de un periodo cerrado produce cifras identicas (prueba automatizada).",
      "El cierre de un periodo historico reproduce la cifra publicada en su momento.",
      "Ningun objeto productivo genera datos aleatorios ni de prueba.",
      "Cada correccion contable tiene aprobacion escrita del area responsable."],
     "Alto: toca calculo. Exige ambiente de pruebas con copia de datos y comparacion de cifras antes y despues.",
     "Ola 0, Ola 1 y las respuestas de contabilidad y negocio.", "ambar"),
    ("Ola 3", "Transacciones y observabilidad", "4-5 sesiones",
     "Que un fallo se detenga, se vea y se pueda reprocesar.",
     ["Plantilla transaccional estandar: SET XACT_ABORT ON, control de XACT_STATE() y THROW al final de cada CATCH.",
      "Aplicarla a los objetos con transaccion, empezando por la familia de cierre.",
      "Identificador de ejecucion y severidad en PO.SAF_POLIZA_ERRORES, con las etiquetas de proceso corregidas.",
      "Monitor que alerte cuando una ejecucion cierre con errores, antes de que la poliza llegue a contabilidad.",
      "Bitacora de inicio y fin por proceso, con duracion y filas afectadas."],
     ["Un error simulado a mitad del cierre deja la base sin cambios parciales y el job en estado fallido.",
      "Toda ejecucion queda registrada con identificador, duracion y conteo de errores.",
      "La alerta llega antes del envio de la poliza en una prueba controlada."],
     "Medio: cambia el contrato de error hacia el orquestador. Procesos que hoy terminan en 'exito' empezaran a fallar de forma visible, lo cual es el objetivo.",
     "Ola 0. Puede avanzar en paralelo con la Ola 2.", "ambar"),
    ("Ola 4", "Catalogos y parametrizacion", "6-8 sesiones",
     "Sacar las reglas de negocio del codigo y ponerlas bajo administracion con vigencia.",
     ["Modelo de catalogos con vigencia (parametro, valor, vigencia desde y hasta, ambiente, autor, aprobador).",
      "Cargar los 63 grupos de hardcodeo segun su clasificacion: parametrizables en portal, catalogos en base y defectos.",
      "Unificar las reglas duplicadas: dos definiciones de cuota COVID, dos de cartera, dos de cuentas excluidas.",
      "Reemplazar en el codigo los valores fijos por lectura del catalogo con la vigencia del periodo procesado.",
      "Primer modulo del portal: consulta, edicion con cuatro ojos y bitacora."],
     ["Recalcular un periodo historico usa los valores vigentes en ese periodo y reproduce la cifra publicada.",
      "Ningun valor de la lista de parametrizables aparece como literal en el codigo (verificado por la compuerta de integracion continua).",
      "Todo cambio de parametro tiene autor, aprobador distinto y fecha en la bitacora."],
     "Medio-alto: el calculo pasa a depender de datos. Obliga a versionar el catalogo con vigencia, nunca a sobrescribirlo.",
     "Ola 1 y la definicion de fuentes oficiales por parte de negocio.", "ambar"),
    ("Ola 5", "Rendimiento y concurrencia", "5-7 sesiones",
     "Cifras reproducibles y una ventana de cierre que no crezca con la cartera.",
     ["Sustituir WITH (NOLOCK) por nivel de aislamiento snapshot en los calculos financieros, empezando por la familia de cierre.",
      "Convertir las funciones escalares con acceso a datos en funciones en linea o columnas materializadas (seis funciones con 31 a 78 invocadores).",
      "Eliminar cursores en los procedimientos de saldos y reescribirlos en operaciones de conjunto.",
      "Revisar tipos MONEY y las agregaciones con granularidad inconsistente.",
      "Medir duracion y lecturas antes y despues de cada cambio."],
     ["El cierre produce la misma cifra en ejecuciones concurrentes con carga.",
      "Duracion del cierre igual o menor que la linea base, documentada objeto por objeto.",
      "Ninguna lectura sucia en los calculos que alimentan la poliza."],
     "Medio: sin cambio funcional esperado, pero exige medicion antes y despues y ventana de pruebas con volumen.",
     "Ola 0 y linea base de duracion.", "azul"),
    ("Ola 6", "Capa de reportes", "3-4 sesiones",
     "Que el ambiente y los filtros salgan de los artefactos de reporte.",
     ["Consolidar los 30 archivos .rdl en 18 reportes logicos con origen de datos compartido por ambiente.",
      "Corregir los filtros fijos divergentes de la poliza contable y el reporte con nombre equivocado.",
      "Decidir el destino de los artefactos QA y del esquema AP en el catalogo INFORMES.",
      "Publicar por script desde el repositorio y cerrar la matriz procedimiento a consumidor."],
     ["Un solo artefacto por reporte logico, sin direcciones de servidor dentro del archivo.",
      "El reporte nuevo y el anterior producen la misma cifra sobre un periodo cerrado.",
      "La publicacion es reproducible desde el repositorio, sin pasos manuales."],
     "Bajo: cambia la entrega, no el calculo.",
     "Ola 1 (definicion de ambientes).", "azul"),
    ("Ola 7", "Controles preventivos y cierre del ciclo", "4-5 sesiones",
     "Que los patrones corregidos no vuelvan a entrar.",
     ["Compuerta de integracion continua sobre cada cambio: nombres de base literales, NOLOCK en calculos, transacciones sin XACT_ABORT, CATCH sin THROW, valores de la lista de parametrizables.",
      "Deteccion automatica de clones divergentes: agrupar procedimientos por similitud y alertar cuando dos copias se separen.",
      "Pruebas de regresion de cifra sobre un periodo cerrado, ejecutadas en cada despliegue.",
      "Despliegue automatizado por ambiente con aprobacion, y evidencia de conciliacion por cierre."],
     ["Ningun cambio llega a produccion sin pasar la compuerta.",
      "La suite de regresion de cifra corre en cada despliegue y bloquea diferencias no explicadas.",
      "Existe evidencia de conciliacion archivada por cierre."],
     "Bajo, y es lo que evita repetir la auditoria en dos anios.",
     "Olas 1 a 6 (cada compuerta se activa cuando su patron ya fue corregido).", "verde"),
]

sec = "".join(f"""
<div class="ola">
  <h3>{e(n)} &mdash; {e(t)} <span class="tag">{e(esf)}</span></h3>
  <p class="obj">{e(obj)}</p>
  <div class="grid2">
    <div><p class="q"><b>Acciones</b></p><ul>{''.join(f'<li>{e(a)}</li>' for a in acc)}</ul></div>
    <div><p class="q"><b>Criterios de aceptacion</b></p><ul>{''.join(f'<li>{e(c)}</li>' for c in cri)}</ul></div>
  </div>
  <p style="margin:8px 0 0;font-size:12.5px;color:#93a1bb"><b>Riesgo de la ola:</b> {e(r)}<br>
  <b>Depende de:</b> {e(dep)}</p>
</div>""" for n, t, esf, obj, acc, cri, r, dep, col in olas)

body2 = f"""
<p class="lead">Plan de remediacion en ocho olas, ordenadas por dependencia y no por severidad: las primeras dos
no corrigen ningun calculo, pero sin ellas cualquier correccion se aplica sobre una version equivocada del
codigo. Cada ola tiene criterios de aceptacion verificables, para que el avance se mida con evidencia y no con
porcentajes.</p>

<div class="card azul">
<h3>Tres principios del plan</h3>
<ul>
<li><b>Nada se corrige sin linea base.</b> Primero se establece que corre en produccion y cuanto tarda; despues se cambia. Sin eso no hay forma de demostrar que la correccion mejoro algo.</li>
<li><b>Ninguna cifra cambia sin aprobacion del area responsable.</b> Los hallazgos contables se corrigen con confirmacion escrita de contabilidad, no por criterio tecnico.</li>
<li><b>Cada patron corregido queda protegido por una compuerta.</b> De lo contrario vuelve a entrar en el siguiente proyecto, que es exactamente como se llego al estado actual.</li>
</ul>
</div>

<h2>Olas</h2>
{sec}

<h2>Nota sobre el esfuerzo</h2>
<div class="card">
<p>Las estimaciones estan en <b>sesiones de trabajo asistido</b> (una sesion equivale a una jornada de desarrollo
enfocado con generacion de codigo asistida), y suman aproximadamente <b>31 a 42 sesiones</b> para las ocho olas.
El tiempo de calendario no lo determina el esfuerzo, sino tres esperas externas que conviene planear desde el
inicio:</p>
<ul>
<li>Respuestas de contabilidad y negocio sobre los cuatro hallazgos contables y las fuentes oficiales de catalogos (bloquea las Olas 2 y 4).</li>
<li>Provision del ambiente de pruebas con copia de datos y de las autorizaciones de lectura de metadatos en produccion (bloquea las Olas 0, 2 y 5).</li>
<li>Ventanas de cierre disponibles para probar con volumen (bloquea la Ola 5).</li>
</ul>
<p>Recomendacion: iniciar hoy las Olas 0 y 1, que no dependen de ninguna de las tres esperas, y usar ese tiempo
para conseguir las definiciones que las Olas 2 y 4 necesitan.</p>
</div>

<h2>Secuencia sugerida</h2>
<table><thead><tr><th>Bloque</th><th>Olas</th><th>Resultado al terminar</th></tr></thead><tbody>
<tr><td><b>Bloque 1: control</b></td><td>0 y 1</td><td>Se sabe que corre en produccion y el mismo script se despliega en los tres ambientes. Sin cambios de calculo.</td></tr>
<tr><td><b>Bloque 2: cifra y visibilidad</b></td><td>2 y 3 (en paralelo)</td><td>El cierre es repetible, los errores detienen el proceso y se alertan antes de contabilidad.</td></tr>
<tr><td><b>Bloque 3: reglas</b></td><td>4</td><td>Las reglas de negocio se administran desde el portal con vigencia y cuatro ojos.</td></tr>
<tr><td><b>Bloque 4: desempenio y entrega</b></td><td>5 y 6</td><td>Cifras reproducibles bajo concurrencia y un solo artefacto por reporte.</td></tr>
<tr><td><b>Bloque 5: sostenibilidad</b></td><td>7</td><td>Los patrones corregidos no pueden volver a entrar.</td></tr>
</tbody></table>
"""

(OUT / '07_plan_remediacion.html').write_text(page(
    'Plan de remediacion',
    '8 olas &middot; criterios de aceptacion verificables &middot; 31-42 sesiones de esfuerzo estimado',
    body2), encoding='utf-8')

# ------------------------------------------------------------------ portal
modulos = [
    ("M1", "Catalogo de parametros con vigencia",
     "Consulta, alta y edicion de los valores hoy hardcodeados: IVA, participacion ION/Afirme, umbrales, "
     "vigencias de programa, fechas de negocio. Todo valor tiene vigencia desde y hasta, y nunca se sobrescribe: "
     "se cierra la vigencia anterior y se abre una nueva.",
     "Alta prioridad. Es el modulo que devuelve el control a negocio y el que habilita la Ola 4."),
    ("M2", "Catalogos de negocio",
     "Rubros contables, conceptos, tipos de credito, origenes de fondos, cuentas excluidas, convenios. Con "
     "validacion referencial, comparacion entre ambientes y deteccion de definiciones duplicadas.",
     "Alta prioridad. Resuelve las reglas duplicadas detectadas en la auditoria."),
    ("M3", "Flujo de aprobacion de cuatro ojos",
     "Todo cambio nace como solicitud: autor, justificacion, ambiente destino, vista previa del antes y despues, "
     "y aprobacion de una persona distinta con rol autorizado. Sin aprobacion el valor no entra en vigencia.",
     "Alta prioridad. Es el requisito de control interno que hoy no existe."),
    ("M4", "Bitacora y trazabilidad",
     "Registro inmutable de quien cambio que, cuando, con que justificacion y quien aprobo; y la consulta "
     "'con que valores se calculo el cierre de este periodo', que es la pregunta que hace un auditor.",
     "Alta prioridad. Convierte la auditabilidad en una consulta, no en una investigacion."),
    ("M5", "Tablero de ejecuciones del cierre",
     "Estado de cada proceso por fecha: inicio, fin, duracion, filas afectadas y errores, leidos de la bitacora "
     "de errores de poliza ya normalizada. Con alertas por correo o Teams.",
     "Alta prioridad. Es el modulo que cierra el hallazgo critico de observabilidad."),
    ("M6", "Paridad y promocion entre ambientes",
     "Matriz objeto x ambiente con hash y fecha, diferencias resaltadas, y promocion de parametros y catalogos "
     "de desarrollo a QA y a produccion con aprobacion. El codigo se sigue promoviendo por integracion continua; "
     "el portal gobierna los datos de configuracion.",
     "Media-alta. Mantiene vivo el resultado de la Ola 0."),
    ("M7", "Catalogo de dependencias e impacto",
     "El grafo construido en esta auditoria, consultable: quien llama a este objeto, que tablas escribe, que "
     "reportes lo consumen, que se rompe si cambia. Se regenera en cada despliegue.",
     "Media. Reduce el riesgo de cada cambio posterior."),
    ("M8", "Inventario de reportes",
     "Los 18 reportes logicos con su procedimiento, su ambiente y su origen de datos, para evitar que vuelvan a "
     "duplicarse por ambiente.",
     "Media-baja. Se construye junto con la Ola 6."),
]

roles = [
    ("Consulta", "Ve parametros, catalogos, bitacora y tablero. No modifica.", "Negocio, contabilidad, auditoria"),
    ("Solicitante", "Crea solicitudes de cambio de parametro o catalogo. No puede aprobar las propias.", "Negocio, producto"),
    ("Aprobador", "Aprueba o rechaza solicitudes de su dominio. No puede aprobar lo que el mismo solicito.", "Responsables de area"),
    ("Operador", "Ejecuta la promocion entre ambientes de lo ya aprobado.", "Tecnologia"),
    ("Administrador", "Administra usuarios, roles y definicion de parametros (no sus valores).", "Tecnologia con supervision de riesgos"),
    ("Auditor", "Acceso de solo lectura a toda la bitacora, incluidas las solicitudes rechazadas.", "Auditoria interna"),
]

stack = [
    ("Backend", "ASP.NET Core 8 (C#) con Minimal APIs, Entity Framework Core para configuracion y Dapper para las consultas al modelo existente",
     "Es el mismo ecosistema del motor de datos: autenticacion integrada con Active Directory sin piezas "
     "intermedias, driver de SQL Server de primera clase, y despliegue tanto en IIS on-premise como en "
     "contenedor. Soporte de largo plazo de Microsoft y el perfil de desarrollador mas facil de contratar en "
     "un entorno SQL Server / SSRS como este."),
    ("Frontend", "React 18 con TypeScript, Vite, TanStack Query y una libreria de tabla de datos (AG Grid o TanStack Table) con MUI",
     "El portal es esencialmente rejillas densas, formularios con validacion y flujos de aprobacion; TypeScript "
     "evita los errores de tipo en un dominio donde un dato mal tipado es un error contable. React es el "
     "ecosistema con mas componentes de tabla y mas talento disponible."),
    ("Base de datos", "SQL Server: esquema nuevo dedicado (por ejemplo CFG) en la misma instancia",
     "Los parametros deben ser legibles por los procedimientos de cierre en la misma transaccion: ponerlos en "
     "otro motor obligaria a replicarlos y reintroduciria el problema de dos verdades."),
    ("Autenticacion", "Microsoft Entra ID o Active Directory federado (OpenID Connect), roles por grupo de directorio",
     "Sin usuarios locales: el alta y la baja de personas ya estan resueltos por el directorio corporativo, que "
     "es lo que espera control interno."),
    ("Integracion con el motor", "Vistas y funciones en linea de lectura de parametros vigentes, consumidas por los procedimientos",
     "El codigo SQL no llama al portal: lee el catalogo. Asi el cierre no depende de que un servicio web este "
     "arriba."),
    ("Despliegue", "Contenedores (Docker) o IIS, con integracion continua en Azure DevOps o GitHub Actions y migraciones versionadas del esquema de configuracion",
     "Permite que el portal viaje por el mismo camino de aprobacion que el resto de los cambios."),
]

alt = [
    ("Node.js con NestJS y React",
     "Viable y con buen ecosistema. Se descarta como primera opcion porque la integracion con Active Directory "
     "y con SQL Server exige mas piezas intermedias, y porque el equipo de este sistema es de perfil "
     "Microsoft: la curva de mantenimiento seria mas alta."),
    ("Python con FastAPI y React",
     "Excelente para analitica y para reutilizar el analizador de dependencias de esta auditoria (que ya esta en "
     "Python). Recomendacion: usarlo para los procesos de analisis y generacion de reportes, y no para el "
     "portal transaccional."),
    ("Blazor Server (solo .NET, sin JavaScript)",
     "Reduce el stack a un solo lenguaje y acelera el desarrollo si el equipo no tiene perfil frontend. Se "
     "descarta como primera opcion por la dependencia de conexion permanente y por el ecosistema de "
     "componentes de tabla, mas limitado."),
    ("Herramienta de bajo codigo (Power Apps y similares)",
     "Permite un primer modulo en dias, pero el flujo de cuatro ojos, la bitacora inmutable y las vigencias "
     "terminan implementandose a la fuerza. Solo recomendable si la decision es no construir software propio."),
]

body3 = f"""
<p class="lead">Propuesta del portal de administracion: el lugar donde las reglas de negocio, los catalogos y la
configuracion por ambiente dejan de vivir dentro del codigo SQL. No es una herramienta de reportes ni un
reemplazo del sistema: es la capa de gobierno que hoy no existe, y es lo que hace sostenible la remediacion.</p>

<div class="card azul">
<h3>El problema que resuelve, en concreto</h3>
<p>La auditoria encontro <b>63 grupos de valores hardcodeados</b>, y el caso mas ilustrativo es la participacion
ION/Afirme partida en 0.10 y 0.90 dentro de <b>28 archivos distintos</b>. Cambiar ese porcentaje hoy significa
un proyecto de desarrollo con 28 oportunidades de equivocarse, sin bitacora de quien lo pidio ni de quien lo
autorizo, y sin forma de recalcular un periodo anterior con el valor que estaba vigente entonces. Con el
portal es un cambio con autor, aprobador, vigencia y trazabilidad.</p>
</div>

<h2>Modulos</h2>
<table><thead><tr><th>&nbsp;</th><th>Modulo</th><th>Alcance</th><th>Prioridad</th></tr></thead><tbody>
{''.join(f'<tr><td class="num">{e(i)}</td><td><b>{e(n)}</b></td><td>{e(d)}</td><td>{e(p)}</td></tr>' for i, n, d, p in modulos)}
</tbody></table>

<h2>Modelo de parametros con vigencia</h2>
<p>Es la decision de diseno mas importante del portal: <b>nunca se sobrescribe un valor</b>. Recalcular un
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
<p>Restricciones que el modelo debe imponer en la base, no solo en la aplicacion: sin traslapes de vigencia por
parametro y ambiente, sin valor sin solicitud aprobada cuando el parametro lo exige, aprobador distinto del
solicitante, y bitacora sin actualizacion ni borrado (permisos, no confianza).</p>

<h2>Roles y segregacion de funciones</h2>
<table><thead><tr><th>Rol</th><th>Puede</th><th>Perfil tipico</th></tr></thead><tbody>
{''.join(f'<tr><td><b>{e(r)}</b></td><td>{e(p)}</td><td>{e(q)}</td></tr>' for r, p, q in roles)}
</tbody></table>
<p>Regla no negociable: <b>quien solicita no aprueba</b>, y la restriccion vive en la base de datos. Si el
control depende solo de la interfaz, no es un control.</p>

<h2>Stack recomendado</h2>
<table><thead><tr><th>Capa</th><th>Tecnologia</th><th>Por que</th></tr></thead><tbody>
{''.join(f'<tr><td><b>{e(c)}</b></td><td>{e(t)}</td><td>{e(j)}</td></tr>' for c, t, j in stack)}
</tbody></table>

<div class="card verde">
<h3>Recomendacion en una linea</h3>
<p><b>ASP.NET Core 8 (C#) en el backend y React 18 con TypeScript en el frontend, sobre SQL Server y con
autenticacion contra el directorio corporativo.</b> La razon principal no es tecnica sino de contexto: el
sistema, los reportes y el equipo ya son de ecosistema Microsoft, y el mayor riesgo de este portal no es
escribirlo, es mantenerlo despues.</p>
</div>

<h3>Alternativas consideradas</h3>
{''.join(f'<div class="card"><h3>{e(n)}</h3><p>{e(d)}</p></div>' for n, d in alt)}

<h2>Como se construye: entregas cortas y utiles</h2>
<table><thead><tr><th>Entrega</th><th>Contenido</th><th>Esfuerzo</th><th>Valor al terminar</th></tr></thead><tbody>
<tr><td><b>E1 &mdash; Nucleo</b></td><td>Esquema de configuracion con vigencias, autenticacion contra el directorio, roles, bitacora, y M1 con solo lectura de los parametros ya cargados</td><td class="num">4-6 sesiones</td><td>Negocio ve, por primera vez y en un solo lugar, con que valores calcula el sistema</td></tr>
<tr><td><b>E2 &mdash; Cuatro ojos</b></td><td>M3 completo, edicion con solicitud y aprobacion, vista previa del antes y despues, y M4</td><td class="num">4-5 sesiones</td><td>Los parametros se pueden cambiar sin desarrollo y con control interno satisfecho</td></tr>
<tr><td><b>E3 &mdash; Catalogos</b></td><td>M2 con validacion referencial y comparacion entre ambientes</td><td class="num">4-6 sesiones</td><td>Rubros, conceptos y cuentas excluidas dejan de estar en el codigo</td></tr>
<tr><td><b>E4 &mdash; Operacion</b></td><td>M5 (tablero de ejecuciones con alertas) y M6 (paridad y promocion)</td><td class="num">5-7 sesiones</td><td>El cierre se vigila desde una pantalla y las promociones dejan rastro</td></tr>
<tr><td><b>E5 &mdash; Conocimiento</b></td><td>M7 (dependencias e impacto) y M8 (inventario de reportes)</td><td class="num">3-4 sesiones</td><td>Cada cambio posterior se estima con datos y no con memoria</td></tr>
</tbody></table>
<p>Total aproximado: <b>20 a 28 sesiones</b> de trabajo asistido para los cinco bloques. E1 y E2 son la
condicion para la Ola 4 del plan de remediacion, por lo que conviene arrancarlos en paralelo con las Olas 0 y 1.</p>

<h2>Lo que el portal no debe hacer</h2>
<div class="card ambar">
<ul>
<li><b>No ejecutar el cierre.</b> Lo dispara el orquestador; el portal lo observa. Mezclar ambas cosas convierte una pantalla en un riesgo operativo.</li>
<li><b>No editar codigo SQL.</b> El codigo viaja por integracion continua con revision; el portal gobierna datos de configuracion.</li>
<li><b>No ser la unica copia de la verdad.</b> Los parametros viven en la base y se versionan; el portal es la interfaz, no el almacen exclusivo.</li>
<li><b>No permitir cambios sin vigencia.</b> Un valor sin fecha de inicio destruye la capacidad de recalcular periodos anteriores, que es el motivo principal para construirlo.</li>
</ul>
</div>
"""

(OUT / '08_portal_admin.html').write_text(page(
    'Portal de administracion de parametros y ambientes',
    '8 modulos &middot; parametros con vigencia y cuatro ojos &middot; ASP.NET Core 8 + React con TypeScript sobre SQL Server',
    body3), encoding='utf-8')

print('ok', [p.name for p in sorted(OUT.glob('0*.html'))])
