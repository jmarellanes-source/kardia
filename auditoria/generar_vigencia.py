"""Insumo para la lista limpia de objetos vigentes en CIERRE / SAF / PO / cobranza.

Solo lectura sobre el repositorio: no toca SQL Server. Cruza, por objeto:
  - presencia en el export de BD_prod
  - quien lo invoca (grafo de llamadas) y si algun .rdl lo usa
  - fechas de creacion/modificacion declaradas en el encabezado del script
  - si escribe o solo lee
  - hermanos por nombre (sufijos _MOD, _V2, _OLD, _BK, _2 ...)
  - declaraciones del cliente (objetos que dijo que no estan en uso)
"""
import os, re, json, collections, glob

ROOT = '/home/ubuntu/kardia'
BD = os.path.join(ROOT, 'BD')
PROD = os.path.join(ROOT, 'BD_prod')
RPT = os.path.join(ROOT, 'reportes')
OUT = '/home/ubuntu/kardia/auditoria/vigencia_objetos.json'

FOCO = ('CIERRE', 'SAF', 'PO')
FOCO_DBO = {'dbo.REPORTE_COBRANZA_INTEGRACION'}

# Declaraciones textuales del cliente (attachment de respuestas Q01/Q15/Q28/Q29)
DECLARADO = {
    'CIERRE.SP_IND_GEN_MES_MOD': 'El cliente declara que no esta en uso; el ejemplo vigente de ballon es CIERRE.SP_SAF_SALDOS linea 90.',
    'CIERRE.SP_SND_COBRANZA': 'El cliente lo senala como implementacion de referencia (COVID en columna propia y separacion balance/cuentas de orden en OBSERVACIONES, linea 47).',
    'CIERRE.SP_SAF_SALDOS': 'El cliente lo senala como implementacion de referencia del concepto ballon (linea 90).',
}
DECLARADO_BAJA_PATRON = 'primera version de la poliza, no se utiliza y sera borrada de la base'


def read(p):
    b = open(p, 'rb').read()
    if b[:2] == b'\xff\xfe':
        return b.decode('utf-16-le', errors='replace')
    if b[:2] == b'\xfe\xff':
        return b.decode('utf-16-be', errors='replace')
    return b.decode('utf-8-sig', errors='replace')


def objname(fn):
    parts = fn[:-4].split('.')
    return '.'.join(parts[:-1]), parts[-1]


def cargar(d):
    objs, txt = {}, {}
    for fn in sorted(os.listdir(d)):
        if fn.endswith('.sql'):
            n, k = objname(fn)
            objs[n] = k
            txt[n] = read(os.path.join(d, fn))
    return objs, txt


objs, texts = cargar(BD)
pobjs, ptexts = cargar(PROD)

progs = {n for n, k in objs.items() if k in ('StoredProcedure', 'UserDefinedFunction')}
pprogs = {n for n, k in pobjs.items() if k in ('StoredProcedure', 'UserDefinedFunction')}
up_prog = {n.upper(): n for n in progs}
short_prog = collections.defaultdict(set)
for n in progs:
    short_prog[n.split('.')[-1].upper()].add(n)

pair = re.compile(r'(?=\[?([A-Za-z_][\w]*)\]?\.\[?([A-Za-z_][\w]*)\]?)')
word = re.compile(r'\b([A-Za-z_][\w]*)\b')

called_by = collections.defaultdict(set)
for p in sorted(progs):
    body = texts[p]
    refs = set()
    for m in pair.finditer(body):
        cand = (m.group(1) + '.' + m.group(2)).upper()
        if cand in up_prog and up_prog[cand] != p:
            refs.add(up_prog[cand])
    for w in set(x.upper() for x in word.findall(body)):
        if w in short_prog and len(short_prog[w]) == 1:
            o = next(iter(short_prog[w]))
            if o != p:
                refs.add(o)
    for q in refs:
        called_by[q].add(p)

# .rdl -> objetos referenciados
rdl_usa = collections.defaultdict(set)
for fp in sorted(glob.glob(os.path.join(RPT, '*.rdl'))):
    body = read(fp)
    up = body.upper()
    for n in progs:
        corto = n.split('.')[-1].upper()
        if re.search(r'\b' + re.escape(corto) + r'\b', up):
            rdl_usa[n].add(os.path.basename(fp))

# fechas declaradas en el encabezado
re_crea = re.compile(r'(?im)^\s*--\s*creaci[oó]n\s*:?\s*[\t ]*([0-9/\-]{6,12})')
re_mod = re.compile(r'(?im)^\s*--\s*(?:modificaci[oó]n|actualizaci[oó]n|modific[oó])\s*:?\s*[\t ]*([0-9/\-]{6,12})')


def fechas(t):
    c = re_crea.search(t)
    ms = re_mod.findall(t)
    return (c.group(1).strip() if c else ''), (max(ms).strip() if ms else '')


ESCRIBE = re.compile(r'(?is)\b(insert\s+into|insert\s+\[|update\s+|delete\s+from|truncate\s+table|merge\s+)')
JOB = re.compile(r'(?i)\b(sp_start_job|sp_add_jobstep|xp_cmdshell)\b')
SUFIJO = re.compile(r'(?i)_(MOD|V2|V3|OLD|BK|BAK|BACKUP|TMP|TEMP|COPIA|COPY|PRUEBA|TEST|NEW|NUEVO|2|3)$')

filas = []
for n in sorted(progs):
    esq = n.split('.')[0]
    if esq.upper() not in FOCO and n not in FOCO_DBO:
        continue
    t = texts[n]
    crea, mod = fechas(t)
    pcrea, pmod = fechas(ptexts.get(n, '')) if n in pprogs else ('', '')
    corto = n.split('.')[-1]
    base = SUFIJO.sub('', corto)
    hermanos = sorted(m for m in progs
                      if m != n and m.split('.')[-1].upper().startswith(base.upper())
                      and m.split('.')[0] == esq)
    lee_qa = bool(re.search(r'(?i)\b\w+_QA\b\s*\.', t))
    lee_shadow = bool(re.search(r'(?i)\bQuiero_Confianza_Shadow\b', t))
    filas.append(dict(
        obj=n, tipo=objs[n], esquema=esq,
        lineas=t.count('\n') + 1,
        en_prod=n in pprogs,
        lineas_prod=(ptexts[n].count('\n') + 1) if n in pprogs else 0,
        llamadores=sorted(called_by.get(n, ())),
        llamadores_prod=sorted(x for x in called_by.get(n, ()) if x in pprogs),
        rdl=sorted(rdl_usa.get(n, ())),
        crea=crea, mod=mod, crea_prod=pcrea, mod_prod=pmod,
        escribe=bool(ESCRIBE.search(t)),
        agenda=bool(JOB.search(t)),
        sufijo=bool(SUFIJO.search(corto)),
        hermanos=hermanos,
        lee_qa=lee_qa, lee_shadow=lee_shadow,
        declarado=DECLARADO.get(n, ''),
    ))


def clasificar(f):
    """Devuelve (estado, motivo). Estado es una hipotesis con evidencia, no un hecho."""
    if f['obj'] in DECLARADO and 'no esta en uso' in DECLARADO[f['obj']]:
        return 'Fuera de uso (declarado)', 'El cliente lo declara sin uso.'
    if f['obj'] in DECLARADO:
        return 'Vigente de referencia', 'El cliente lo senala como implementacion correcta.'
    if f['lee_qa']:
        return 'Fuera de uso (declarado)', ('Lee la base Quiero_Confianza_CreditoPuente_QA: el cliente declaro que estos '
                                            'cuatro objetos son la primera version de la poliza y seran borrados.')
    ev = []
    if f['en_prod']:
        ev.append('existe en el export de BD_prod')
    if f['llamadores_prod']:
        ev.append('lo invocan %d objetos que tambien estan en produccion' % len(f['llamadores_prod']))
    elif f['llamadores']:
        ev.append('lo invocan %d objetos del repositorio' % len(f['llamadores']))
    if f['rdl']:
        ev.append('lo usan %d reportes .rdl' % len(f['rdl']))
    motivo = '; '.join(ev) if ev else 'sin ninguna evidencia de uso en el repositorio'
    if f['en_prod'] and (f['llamadores_prod'] or f['rdl'] or f['agenda']):
        return 'Vigente', motivo
    if f['en_prod']:
        return 'Vigente sin invocador conocido', (motivo + '; nadie lo invoca dentro del repositorio, '
                                                  'asi que su disparo tiene que estar fuera (job, CAS o ejecucion manual)')
    if f['sufijo'] and f['hermanos']:
        return 'Candidato a baja', ('nombre con sufijo de version y convive con %s; %s'
                                    % (', '.join(h.split('.')[-1] for h in f['hermanos']), motivo))
    if re.search(r'(?i)(QA_PROD|PROD_QA)', f['obj']):
        return 'Candidato a baja', ('es una herramienta de promocion entre ambientes, fuera del camino contable; '
                                    + motivo)
    if f['llamadores'] or f['rdl']:
        return 'Solo en el repositorio', (motivo + '; no aparece en el export de BD_prod')
    return 'Ausente del export (indeterminado)', ('no esta en el export de BD_prod y ' + motivo
                                                  + '; hay que verificarlo contra los metadatos de la instancia')


for f in filas:
    f['estado'], f['motivo'] = clasificar(f)

json.dump(filas, open(OUT, 'w'), ensure_ascii=False, indent=1)
c = collections.Counter(f['estado'] for f in filas)
print('objetos en foco:', len(filas))
for k, v in c.most_common():
    print(' ', k, v)
print('con sufijo de version:', sum(1 for f in filas if f['sufijo']))
print('sin fecha de encabezado:', sum(1 for f in filas if not f['crea'] and not f['mod']))
print('escriben:', sum(1 for f in filas if f['escribe']))
