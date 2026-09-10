# -*- coding: utf-8 -*-
"""Plantilla compartida (CSS, navegacion y armado de pagina) de los informes
HTML de la auditoria KARDIA/SAF."""
import html

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
<a href="14_demo_portal_banderas.html">Demo de banderas</a>
<a href="10_contexto_migracion.html">Contexto operativo y cambio de core</a>
<a href="11_fase0_fase1.html">Fase 0 y Fase 1 con ejemplos</a>
<a href="12_preguntas_negocio.html">Confirmaciones con negocio</a>
<a href="15_respuestas_cliente.html">Respuestas del cliente</a>
<a href="16_reclasificacion.html">Reclasificación de hallazgos</a>
<a href="17_objetos_vigentes.html">Objetos vigentes</a>
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
