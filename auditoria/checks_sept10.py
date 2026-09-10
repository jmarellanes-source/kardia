import pathlib
import re
import sys

PATS = {
    'literal OPI VALOR (con espacio)': r"OPI VALOR",
    'literal OPI_VALOR': r"OPI_VALOR",
    'literal PRINCIPAL_VENCIDO': r"PRINCIPAL_VENCIDO",
    'literal INTERES_NO_EXIGIBLES': r"INTERES_NO_EXIGIBLES",
    'lee Quiero_Confianza_CreditoPuente_QA': r"Quiero_Confianza_CreditoPuente_QA",
    'lee Quiero_Confianza_shadow': r"Quiero_Confianza_shadow",
    'usa dbo.FN_ES_COVID': r"FN_ES_COVID",
    'usa columna IND_COVID': r"IND_COVID",
    'umbral 6051': r"6051",
    'umbral 6086': r"6086",
    "IN ('008','031')": r"IN\s*\(\s*'008'\s*,\s*'031'\s*\)",
    "IN ('008','031','046')": r"IN\s*\(\s*'008'\s*,\s*'031'\s*,\s*'046'\s*\)",
    'NOT IN (22,23,28,35)': r"NOT\s+IN\s*\(\s*22\s*,\s*23\s*,\s*28\s*,\s*35\s*\)",
    'WITH (NOLOCK)': r"WITH\s*\(\s*NOLOCK\s*\)",
    "OBSERVACION LIKE '%CUENTAS DE ORDEN%'": r"CUENTAS DE ORDEN",
    'filtros NUM_DESC_TIPO_CREDITO': r"NUM_DESC_TIPO_CREDITO\s*(IN|=|<>|NOT\s+IN)",
    'getdate() en logica de fecha': r"getdate\s*\(\s*\)",
}


def leer(p):
    b = p.read_bytes()
    if b[:2] in (b'\xff\xfe', b'\xfe\xff'):
        return b.decode('utf-16', 'replace')
    if b[:3] == b'\xef\xbb\xbf':
        return b[3:].decode('utf-8', 'replace')
    return b.decode('utf-8', 'replace')


def sin_comentarios(t):
    t = re.sub(r'/\*.*?\*/', ' ', t, flags=re.S)
    return '\n'.join(re.sub(r'--.*$', '', l) for l in t.split('\n'))


def escanear(raiz, sub):
    d = pathlib.Path(raiz) / sub
    res = {k: [0, 0] for k in PATS}
    for p in sorted(d.glob('*.sql')):
        t = sin_comentarios(leer(p))
        for k, pat in PATS.items():
            n = len(re.findall(pat, t, re.I))
            if n:
                res[k][0] += 1
                res[k][1] += n
    return res


if __name__ == '__main__':
    sub = sys.argv[1] if len(sys.argv) > 1 else 'BD_prod'
    a = escanear('/home/ubuntu/kardia', sub)
    b = escanear('/home/ubuntu/sept10', sub)
    print('%-40s %18s %18s' % (sub, 'auditado (obj/ocur)', 'Sept10 (obj/ocur)'))
    for k in PATS:
        print('%-40s %8d /%-8d %8d /%-8d' % (k, a[k][0], a[k][1], b[k][0], b[k][1]))
