"""Construye el grafo de dependencias del repositorio: objeto -> tabla, objeto -> objeto y reporte .rdl -> procedimiento.

Salida: auditoria/dependencias_grafo.json
"""
from pathlib import Path
import os, re, json, collections, glob

BD = str(Path(__file__).resolve().parent.parent / 'BD')
RPT = str(Path(__file__).resolve().parent.parent / 'reportes')


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


objs = {}
for fn in sorted(os.listdir(BD)):
    if fn.endswith('.sql'):
        n, k = objname(fn)
        objs[n] = k

progs = {n for n, k in objs.items() if k in ('StoredProcedure', 'UserDefinedFunction')}
tables = {n for n, k in objs.items() if k == 'Table'}
up_prog = {n.upper(): n for n in progs}
up_tbl = {n.upper(): n for n in tables}
# nombre corto -> objeto (para referencias sin esquema)
short_tbl = collections.defaultdict(set)
for n in tables:
    short_tbl[n.split('.')[-1].upper()].add(n)
short_prog = collections.defaultdict(set)
for n in progs:
    short_prog[n.split('.')[-1].upper()].add(n)

pair = re.compile(r'(?=\[?([A-Za-z_][\w]*)\]?\.\[?([A-Za-z_][\w]*)\]?)')
word = re.compile(r'\b([A-Za-z_][\w]*)\b')

uses_tbl = collections.defaultdict(set)
used_by_tbl = collections.defaultdict(set)
calls = collections.defaultdict(set)
called_by = collections.defaultdict(set)

texts = {}
for fn in sorted(os.listdir(BD)):
    if fn.endswith('.sql'):
        n, k = objname(fn)
        texts[n] = read(os.path.join(BD, fn))

for p in sorted(progs):
    txt = texts[p]
    body = txt
    refs_t, refs_p = set(), set()
    for m in pair.finditer(body):
        cand = (m.group(1) + '.' + m.group(2)).upper()
        if cand in up_tbl:
            refs_t.add(up_tbl[cand])
        if cand in up_prog and up_prog[cand] != p:
            refs_p.add(up_prog[cand])
    # referencias sin esquema: solo para nombres cortos no ambiguos y distintivos
    for w in set(x.upper() for x in word.findall(body)):
        if w in short_tbl and len(short_tbl[w]) == 1:
            refs_t |= short_tbl[w]
        if w in short_prog and len(short_prog[w]) == 1:
            o = next(iter(short_prog[w]))
            if o != p:
                refs_p.add(o)
    uses_tbl[p] = refs_t
    calls[p] = refs_p
    for t in refs_t:
        used_by_tbl[t].add(p)
    for q in refs_p:
        called_by[q].add(p)

# rdl
rdl = {}
for fp in sorted(glob.glob(os.path.join(RPT, '*.rdl'))):
    t = read(fp)
    sps = set()
    for c in re.findall(r'<CommandText>(.*?)</CommandText>', t, re.S):
        for m in pair.finditer(c):
            cand = (m.group(1) + '.' + m.group(2)).upper()
            if cand in up_prog:
                sps.add(up_prog[cand])
        for w in set(x.upper() for x in word.findall(c)):
            if w in short_prog and len(short_prog[w]) == 1:
                sps |= short_prog[w]
    rdl[os.path.basename(fp)] = sorted(sps)

rdl_sps = set()
for v in rdl.values():
    rdl_sps |= set(v)

huerfanos = sorted(n for n in progs if not called_by[n] and n not in rdl_sps)
sin_uso = sorted(n for n in tables if not used_by_tbl[n])

out = {
    'n_prog': len(progs), 'n_tbl': len(tables),
    'top_tbl': sorted(((len(v), k) for k, v in used_by_tbl.items()), reverse=True)[:20],
    'top_prog': sorted(((len(v), k) for k, v in called_by.items()), reverse=True)[:20],
    'huerfanos': huerfanos, 'n_huerfanos': len(huerfanos),
    'sin_uso': sin_uso, 'n_sin_uso': len(sin_uso),
    'rdl': rdl, 'n_rdl_sps': len(rdl_sps),
    'used_by_tbl': {k: sorted(v) for k, v in used_by_tbl.items()},
    'calls': {k: sorted(v) for k, v in calls.items()},
}
json.dump(out, open(str(Path(__file__).resolve().parent / 'dependencias_grafo.json'), 'w'), indent=1, ensure_ascii=False)
print('progs', len(progs), 'tablas', len(tables))
print('top tbl', out['top_tbl'][:8])
print('top prog', out['top_prog'][:8])
print('huerfanos', len(huerfanos), '/ tablas sin uso', len(sin_uso), '/ sps en rdl', len(rdl_sps))
esq = collections.Counter(n.split('.')[0] for n in sin_uso)
print('tablas sin uso por esquema', esq.most_common())
esq2 = collections.Counter(n.split('.')[0] for n in huerfanos)
print('huerfanos por esquema', esq2.most_common())
