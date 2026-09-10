import difflib
import pathlib
import re
import sys

OLD = pathlib.Path('/home/ubuntu/kardia')
NEW = pathlib.Path('/home/ubuntu/sept10')


def leer(p):
    b = p.read_bytes()
    if b[:2] in (b'\xff\xfe', b'\xfe\xff'):
        t = b.decode('utf-16')
    elif b[:3] == b'\xef\xbb\xbf':
        t = b[3:].decode('utf-8', 'replace')
    else:
        t = b.decode('utf-8', 'replace')
    return [l.rstrip() for l in t.replace('\r\n', '\n').replace('\r', '\n').split('\n')]


def sustantivo(l):
    s = l.strip()
    return bool(s) and not s.startswith('--')


def comparar():
    res = []
    for p in sorted(NEW.rglob('*')):
        if not p.is_file() or p.suffix.lower() != '.sql':
            continue
        rel = p.relative_to(NEW)
        o = OLD / rel
        if not o.exists():
            res.append((str(rel), 'nuevo', [], []))
            continue
        a, b = leer(o), leer(p)
        d = list(difflib.unified_diff(a, b, n=2, lineterm=''))
        add = [l[1:] for l in d if l.startswith('+') and not l.startswith('+++')]
        rem = [l[1:] for l in d if l.startswith('-') and not l.startswith('---')]
        if any(map(sustantivo, add + rem)):
            res.append((str(rel), 'modificado', add, rem))
    return res


if __name__ == '__main__':
    r = comparar()
    print('archivos sql con cambio sustantivo:', len(r))
    for rel, k, add, rem in sorted(r, key=lambda x: -(len(x[2]) + len(x[3]))):
        print('%-70s %-11s +%-5d -%d' % (rel, k, len(add), len(rem)))
    if len(sys.argv) > 1:
        pat = re.compile(sys.argv[1], re.I)
        for rel, k, add, rem in r:
            if not pat.search(rel):
                continue
            print('\n===', rel, k)
            for l in rem:
                print('  -', l.strip()[:160])
            for l in add:
                print('  +', l.strip()[:160])
