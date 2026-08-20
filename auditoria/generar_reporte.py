#!/usr/bin/env python3
"""Genera el reporte HTML interactivo de un lote de auditoria a partir del JSON de hallazgos.

Uso:  python3 generar_reporte.py lote1_hallazgos.json 01_lote1.html
"""
import json
import sys
import html
from pathlib import Path

SEV_ORDER = {"Critico": 0, "Alto": 1, "Medio": 2, "Bajo": 3}
SEV_CLASS = {"Critico": "c", "Alto": "a", "Medio": "m", "Bajo": "b"}
CLAS_CLASS = {
    "Parametrizable en portal": "p1",
    "Parametrizable en portal (catalogo)": "p1",
    "Parametrizable en portal (catalogo contable)": "p1",
    "Parametrizable en portal (plantillas)": "p1",
    "Parametrizable en portal (definicion de universo)": "p1",
    "Catalogo en BD (no editable en portal)": "p2",
    "Configuracion de ambiente": "p3",
    "No parametrizable: es un defecto": "p4",
}
ESFUERZO = {"S": "S (&lt;1 dia)", "M": "M (1-3 dias)", "L": "L (&gt;3 dias)"}


def e(x):
    return html.escape(str(x), quote=True)


def env_tags(env):
    return [t for t in env.replace("+", " ").split() if t]


def build(data):
    hs = sorted(data["hallazgos"], key=lambda h: (SEV_ORDER.get(h["sev"], 9), h["id"]))
    sevs = ["Critico", "Alto", "Medio", "Bajo"]
    cats = sorted({h["cat"] for h in hs})
    envs = ["BD", "BD_prod"]
    counts = {s: sum(1 for h in hs if h["sev"] == s) for s in sevs}

    lotes = sorted({str(h["lote"]) for h in hs if h.get("lote")})

    rows = []
    for h in hs:
        tags = " ".join(env_tags(h["env"]))
        rows.append(f"""
    <article class="f" data-sev="{e(h['sev'])}" data-cat="{e(h['cat'])}" data-env="{e(tags)}"
             data-lote="{e(str(h.get('lote','')))}"
             data-txt="{e((h['id'] + ' ' + h['titulo'] + ' ' + h['obj'] + ' ' + h['evidencia']).lower())}">
      <header onclick="this.parentNode.classList.toggle('open')">
        <span class="sev {SEV_CLASS[h['sev']]}">{e(h['sev'])}</span>
        <span class="id">{e(h['id'])}</span>
        <span class="ti">{e(h['titulo'])}</span>
        <span class="meta">{e(h['cat'])} &middot; {e(h['env'])} &middot; esfuerzo {ESFUERZO.get(h.get('esfuerzo', ''), '?')}</span>
        <span class="chev">&#9662;</span>
      </header>
      <div class="body">
        <div class="kv"><b>Objeto</b><span>{e(h['obj'])}</span></div>
        <div class="kv"><b>Ubicacion</b><span>{e(h['loc'])}</span></div>
        <div class="kv"><b>Evidencia</b><pre>{e(h['evidencia'])}</pre></div>
        <div class="kv"><b>Impacto</b><span>{e(h['impacto'])}</span></div>
        <div class="kv rem"><b>Remediacion</b><span>{e(h['remediacion'])}</span></div>
      </div>
    </article>""")

    hc = []
    for r in data["hardcode"]:
        cls = CLAS_CLASS.get(r["clasificacion"], "p2")
        hc.append(f"""      <tr data-clas="{e(r['clasificacion'])}"
          data-txt="{e((r['valor'] + ' ' + r['tipo'] + ' ' + r['destino'] + ' ' + r['nota']).lower())}">
        <td class="mono">{e(r['valor'])}</td><td>{e(r['tipo'])}</td><td class="num">{e(r['ocurrencias'])}</td>
        <td><span class="pill {cls}">{e(r['clasificacion'])}</span></td>
        <td>{e(r['destino'])}</td><td class="nota">{e(r['nota'])}</td></tr>""")
    clases = sorted({r["clasificacion"] for r in data["hardcode"]})

    fases = []
    for f in data["plan_despliegue"]:
        acc = "".join(f"<li>{e(a)}</li>" for a in f["acciones"])
        fases.append(f"""      <div class="fase"><h3>{e(f['fase'])}</h3>
        <p class="obj">{e(f['objetivo'])}</p><ul>{acc}</ul>
        <p class="riesgo"><b>Riesgo:</b> {e(f['riesgo'])}</p></div>""")

    va = "".join(f"<li>{e(v)}</li>" for v in data["valor_agregado"])
    objs = "".join(f"<li>{e(o)}</li>" for o in data["alcance"]["objetos"])

    cob = data.get("cobertura") or []
    cob_rows = "".join(
        f"""      <tr data-lote="{e(str(c['lote']))}" data-txt="{e(c['obj'].lower())}">
        <td class="num">{e(str(c['lote']))}</td><td class="mono">{e(c['obj'])}</td>
        <td class="num">{c['lineas']:,}</td><td>{'si' if c['prod'] else '<b>no</b>'}</td>
        <td class="num">{e(str(c['poliza']))}</td><td class="num">{c['nolock']}</td>
        <td class="num">{c['cursor']}</td><td>{e(c['patron'])}</td></tr>""" for c in cob)
    cob_block = "" if not cob else f"""
  <h2>Cobertura del lote: {len(cob)} objetos revisados</h2>
  <div class="bar">
    <label>Lote</label><select id="cl"><option value="">Todos</option>{''.join(f'<option>{x}</option>' for x in lotes)}</select>
    <input type="search" id="cq" placeholder="Buscar objeto...">
    <button class="rst" onclick="resetCob()">Limpiar</button>
    <span class="count" id="ccnt"></span>
  </div>
  <table><thead><tr><th>Lote</th><th>Objeto</th><th>Lineas</th><th>En BD_prod</th><th>ID_POLIZA</th>
    <th>NOLOCK</th><th>Cursores</th><th>Patron transaccional</th></tr></thead>
  <tbody id="cbody">
{cob_rows}
  </tbody></table>"""

    return f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Auditoria SQL KARDIA &mdash; Lote {data['lote']}</title>
<style>
*{{box-sizing:border-box}}
body{{margin:0;font:14px/1.55 "Segoe UI",system-ui,sans-serif;background:#0e1420;color:#e8edf6}}
a{{color:#7fb2ff}}
header.top{{padding:26px 32px;background:linear-gradient(120deg,#12213d,#0e1420 60%);border-bottom:1px solid #2a3549}}
header.top h1{{margin:0;font-size:23px;letter-spacing:.3px}}
header.top p{{margin:6px 0 0;color:#93a1bb}}
.wrap{{padding:22px 32px 60px;max-width:1500px}}
.kpis{{display:flex;gap:14px;flex-wrap:wrap;margin:18px 0 26px}}
.kpi{{background:#161e2e;border:1px solid #2a3549;border-radius:10px;padding:14px 18px;min-width:132px}}
.kpi b{{display:block;font-size:27px;line-height:1.1}}
.kpi span{{color:#93a1bb;font-size:12px;text-transform:uppercase;letter-spacing:.6px}}
.kpi.c b{{color:#ff6b6b}} .kpi.a b{{color:#ffa94d}} .kpi.m b{{color:#ffd43b}} .kpi.b b{{color:#74c0fc}}
h2{{margin:34px 0 12px;font-size:17px;border-left:3px solid #4c8dff;padding-left:10px}}
.bar{{display:flex;gap:10px;flex-wrap:wrap;align-items:center;background:#161e2e;border:1px solid #2a3549;
 border-radius:10px;padding:12px 14px;position:sticky;top:0;z-index:5}}
.bar label{{font-size:12px;color:#93a1bb;margin-right:4px}}
select,input[type=search]{{background:#0e1420;color:#e8edf6;border:1px solid #35415a;border-radius:6px;padding:7px 9px;font:13px inherit}}
input[type=search]{{min-width:230px}}
button.rst{{background:#243149;color:#e8edf6;border:1px solid #35415a;border-radius:6px;padding:7px 12px;cursor:pointer}}
.count{{margin-left:auto;color:#93a1bb;font-size:12px}}
.f{{background:#161e2e;border:1px solid #2a3549;border-radius:9px;margin:9px 0;overflow:hidden}}
.f>header{{display:flex;gap:12px;align-items:center;padding:11px 14px;cursor:pointer}}
.f>header:hover{{background:#1d2739}}
.sev{{font-size:11px;font-weight:700;padding:3px 8px;border-radius:20px;white-space:nowrap}}
.sev.c{{background:#4a1414;color:#ff8787;border:1px solid #7d2020}}
.sev.a{{background:#4a3211;color:#ffc078;border:1px solid #7d5a20}}
.sev.m{{background:#443f10;color:#ffe066;border:1px solid #756a1c}}
.sev.b{{background:#122d47;color:#8ecaff;border:1px solid #1f5480}}
.id{{color:#93a1bb;font-family:ui-monospace,Consolas,monospace;font-size:12px}}
.ti{{font-weight:600;flex:1}}
.meta{{color:#93a1bb;font-size:12px;white-space:nowrap}}
.chev{{color:#93a1bb;transition:.15s}}
.f.open .chev{{transform:rotate(180deg)}}
.body{{display:none;padding:4px 16px 16px;border-top:1px solid #2a3549;background:#131b29}}
.f.open .body{{display:block}}
.kv{{display:grid;grid-template-columns:118px 1fr;gap:12px;padding:8px 0;border-bottom:1px dashed #263148}}
.kv:last-child{{border:0}}
.kv b{{color:#93a1bb;font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.5px}}
.kv.rem span{{color:#8ce99a}}
pre{{margin:0;background:#0b1220;border:1px solid #26314a;border-radius:6px;padding:10px;overflow-x:auto;
 font:12px/1.5 ui-monospace,Consolas,monospace;color:#c9d6ee;white-space:pre-wrap}}
table{{width:100%;border-collapse:collapse;background:#161e2e;border:1px solid #2a3549;border-radius:9px;overflow:hidden}}
th,td{{padding:9px 11px;text-align:left;border-bottom:1px solid #26314a;vertical-align:top;font-size:13px}}
th{{background:#1d2739;color:#93a1bb;font-size:11px;text-transform:uppercase;letter-spacing:.6px;position:sticky;top:56px}}
td.mono{{font-family:ui-monospace,Consolas,monospace;font-size:12px;color:#c9d6ee;max-width:330px;word-break:break-word}}
td.num{{white-space:nowrap;color:#93a1bb}} td.nota{{color:#93a1bb;max-width:300px}}
.pill{{font-size:11px;padding:3px 8px;border-radius:20px;white-space:nowrap;display:inline-block}}
.pill.p1{{background:#10331f;color:#8ce99a;border:1px solid #1f6b3c}}
.pill.p2{{background:#122d47;color:#8ecaff;border:1px solid #1f5480}}
.pill.p3{{background:#33270f;color:#ffd8a8;border:1px solid #6b4d1f}}
.pill.p4{{background:#3d1420;color:#ffa8b6;border:1px solid #7d2038}}
.fase{{background:#161e2e;border:1px solid #2a3549;border-left:3px solid #4c8dff;border-radius:9px;padding:14px 18px;margin:10px 0}}
.fase h3{{margin:0 0 4px;font-size:15px}} .fase .obj{{margin:0 0 8px;color:#93a1bb}}
.fase ul{{margin:0 0 8px;padding-left:20px}} .fase li{{margin:3px 0}}
.fase .riesgo{{margin:0;font-size:12px;color:#93a1bb}}
ul.va li{{margin:6px 0}}
details.alc{{background:#161e2e;border:1px solid #2a3549;border-radius:9px;padding:12px 16px}}
details.alc summary{{cursor:pointer;color:#93a1bb}}
footer{{color:#93a1bb;font-size:12px;padding:18px 32px;border-top:1px solid #2a3549}}
.hide{{display:none!important}}
</style></head><body>
<header class="top">
  <h1>Auditoria de codigo SQL &mdash; KARDIA / SAF</h1>
  <p>Lote {data['lote']} &middot; {len(cob) or 20} objetos de mayor riesgo &middot; {data['alcance']['lineas_revisadas']:,} lineas revisadas en <b>BD</b> (dev/QA) y <b>BD_prod</b> (produccion) &middot; {data['fecha']}</p>
</header>
<div class="wrap">

  <div class="kpis">
    <div class="kpi c"><b>{counts['Critico']}</b><span>Criticos</span></div>
    <div class="kpi a"><b>{counts['Alto']}</b><span>Altos</span></div>
    <div class="kpi m"><b>{counts['Medio']}</b><span>Medios</span></div>
    <div class="kpi b"><b>{counts['Bajo']}</b><span>Bajos</span></div>
    <div class="kpi"><b>{len(data['hardcode'])}</b><span>Grupos de hardcodeo</span></div>
    <div class="kpi"><b>{sum(1 for r in data['hardcode'] if r['clasificacion'].startswith('Parametrizable'))}</b><span>Parametrizables en portal</span></div>
  </div>

  <details class="alc"><summary>Alcance y criterio de seleccion del lote</summary>
    <p>{e(data['alcance']['criterio'])}</p><ul>{objs}</ul>
    <p><b>Nota de codificacion:</b> los archivos se decodifican por BOM (UTF-16LE en la mayoria, UTF-8 BOM en 30 archivos de BD/).
    Los &quot;caracteres espaciados&quot; son los bytes 0x00 de UTF-16 leidos como ASCII: <b>no deben limpiarse</b>, se resuelven decodificando correctamente.</p>
  </details>

  <h2>Hallazgos</h2>
  <div class="bar">
    <label>Severidad</label><select id="fs"><option value="">Todas</option>{''.join(f'<option>{s}</option>' for s in sevs)}</select>
    <label>Categoria</label><select id="fc"><option value="">Todas</option>{''.join(f'<option>{e(c)}</option>' for c in cats)}</select>
    <label>Entorno</label><select id="fe"><option value="">Ambos</option>{''.join(f'<option>{x}</option>' for x in envs)}</select>
    {'<label>Lote</label><select id="fl"><option value="">Todos</option>' + ''.join(f'<option>{x}</option>' for x in lotes) + '</select>' if lotes else ''}
    <input type="search" id="fq" placeholder="Buscar objeto, evidencia, texto...">
    <button class="rst" onclick="reset()">Limpiar</button>
    <span class="count" id="cnt"></span>
  </div>
  <div id="lista">{''.join(rows)}</div>

{cob_block}

  <h2>Catalogo de valores hardcodeados y clasificacion de parametrizacion</h2>
  <div class="bar">
    <label>Clasificacion</label><select id="hc"><option value="">Todas</option>{''.join(f'<option>{e(c)}</option>' for c in clases)}</select>
    <input type="search" id="hq" placeholder="Buscar valor, tipo, destino...">
    <button class="rst" onclick="resetHc()">Limpiar</button>
    <span class="count" id="hcnt"></span>
  </div>
  <table><thead><tr><th>Valor</th><th>Tipo</th><th>Ocurrencias</th><th>Clasificacion</th><th>Destino propuesto</th><th>Nota</th></tr></thead>
  <tbody id="hbody">
{''.join(hc)}
  </tbody></table>

  <h2>Plan de despliegue de la parametrizacion</h2>
{''.join(fases)}

  <h2>Valor agregado propuesto</h2>
  <ul class="va">{va}</ul>
</div>
<footer>Generado por la auditoria automatizada + revision manual del codigo. Los hallazgos se sustentan en el codigo fuente;
los que dependen de datos o de plan de ejecucion se marcan como tales en el impacto. Siguiente paso: validar los hallazgos y continuar con el siguiente lote.</footer>
<script>
const $=s=>document.querySelector(s), fs=$('#fs'),fc=$('#fc'),fe=$('#fe'),fq=$('#fq'),fl=$('#fl');
function apply(){{
  let n=0, all=document.querySelectorAll('.f');
  all.forEach(f=>{{
    const ok=(!fs.value||f.dataset.sev===fs.value)
      &&(!fc.value||f.dataset.cat===fc.value)
      &&(!fe.value||f.dataset.env.split(' ').includes(fe.value))
      &&(!fl||!fl.value||f.dataset.lote===fl.value)
      &&(!fq.value||f.dataset.txt.includes(fq.value.toLowerCase()));
    f.classList.toggle('hide',!ok); if(ok)n++;
  }});
  $('#cnt').textContent=n+' de '+all.length+' hallazgos';
}}
[fs,fc,fe,fl].forEach(x=>{{if(x)x.onchange=apply;}}); fq.oninput=apply;
function reset(){{fs.value=fc.value=fe.value='';if(fl)fl.value='';fq.value='';apply();}}
const cl=$('#cl'),cq=$('#cq');
function applyCob(){{
  if(!cl)return; let n=0, rows=document.querySelectorAll('#cbody tr');
  rows.forEach(r=>{{
    const ok=(!cl.value||r.dataset.lote===cl.value)&&(!cq.value||r.dataset.txt.includes(cq.value.toLowerCase()));
    r.classList.toggle('hide',!ok); if(ok)n++;
  }});
  $('#ccnt').textContent=n+' de '+rows.length+' objetos';
}}
if(cl){{cl.onchange=applyCob; cq.oninput=applyCob;}}
function resetCob(){{cl.value='';cq.value='';applyCob();}}
const hc=$('#hc'),hq=$('#hq');
function applyHc(){{
  let n=0, rows=document.querySelectorAll('#hbody tr');
  rows.forEach(r=>{{
    const ok=(!hc.value||r.dataset.clas===hc.value)&&(!hq.value||r.dataset.txt.includes(hq.value.toLowerCase()));
    r.classList.toggle('hide',!ok); if(ok)n++;
  }});
  $('#hcnt').textContent=n+' de '+rows.length+' grupos';
}}
hc.onchange=applyHc; hq.oninput=applyHc;
function resetHc(){{hc.value='';hq.value='';applyHc();}}
apply();applyHc();applyCob();
</script>
</body></html>
"""


if __name__ == "__main__":
    src = Path(sys.argv[1] if len(sys.argv) > 1 else "lote1_hallazgos.json")
    out = Path(sys.argv[2] if len(sys.argv) > 2 else "01_lote1.html")
    data = json.loads(src.read_text(encoding="utf-8"))
    out.write_text(build(data), encoding="utf-8")
    print(f"{out} generado: {len(data['hallazgos'])} hallazgos, {len(data['hardcode'])} grupos de hardcodeo")
