"""ndaj_korpusin.py — nxjerr arkiven reale (perdore per matje).

Ndan DECISIONS.md / LESSONS.md ne njesi (nje vendim/mesim = nje skedar),
pastrojne sekretet dhe shkruajne ne nebius-gara/arkiva/.
"""
from __future__ import annotations

import pathlib
import re

BURIME = [
    (pathlib.Path.home() / 'openclaw-knowledge/docs/agent/DECISIONS.md', 'vendim', r'^##\s+(D-\d+)'),
    (pathlib.Path.home() / 'openclaw-knowledge/docs/agent/LESSONS.md', 'mesim', r'^##\s+(L-\d+)'),
]
DALJA = pathlib.Path.home() / 'nebius-gara/arkiva'
FSHEH = [(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+', '<email>'),
         (r'sk-[A-Za-z0-9_-]{12,}', '<sekret>'),
         (r'[0-9a-f]{32,}', '<hash>'),
         (r'(?:/home/[A-Za-z0-9_.-]+|/Users/[A-Za-z0-9]+)\S*', '<shteg>')]


def pastro(t: str) -> str:
    for pat, zev in FSHEH:
        t = re.sub(pat, zev, t)
    return t


# ---------------------------------------------------------------- public example corpus: Python PEPs
# Halim's condition (13.10, H6): a PUBLIC corpus for the public repo — never the private archive. Each unit carries
# `burimi` (canonical URL) and `licenca` (read from the PEP's own Copyright section), per document.
RX_PEP = re.compile(r'^pep-(\d{4})\.(rst|txt)$')
MAX_TRUPI = 8000  # chars kept per unit (repo size); the full text is one click away at `burimi`


def licenca_pep(teksti: str) -> str:
    fund = teksti[-1500:].lower()
    if 'cc0' in fund:
        return 'CC0-1.0 (per the PEP copyright section)'
    if 'public domain' in fund:
        return 'Public domain (per the PEP copyright section)'
    if 'open publication license' in fund:
        return 'Open Publication License (per the PEP copyright section)'
    return 'Public domain or CC0-1.0 per PEP 1 policy (no explicit copyright section in this PEP)'


def ndaj_pep(skedari: pathlib.Path) -> tuple[str, str] | None:
    m = RX_PEP.match(skedari.name)
    if not m:
        return None
    numri = int(m.group(1))
    teksti = skedari.read_text(encoding='utf-8', errors='replace')
    koka, _, trupi = teksti.partition(chr(10) + chr(10))
    fusha = {}
    for rr in koka.splitlines():
        if ':' in rr and not rr.startswith((' ', chr(9))):
            k, v = rr.split(':', 1)
            fusha[k.strip().lower()] = v.strip()
    titulli = fusha.get('title', 'PEP ' + str(numri))
    ident = 'pep-%04d' % numri
    trupi = trupi.strip()
    shkurtuar = len(trupi) > MAX_TRUPI
    if shkurtuar:
        trupi = trupi[:MAX_TRUPI].rsplit(chr(10), 1)[0] + chr(10) + chr(10) + '[… truncated; full text at the source URL …]'
    fm = ['---', 'id: ' + ident, 'burimi: https://peps.python.org/' + ident + '/', 'licenca: ' + licenca_pep(teksti),
          'titulli: ' + titulli.replace(chr(10), ' '), 'statusi: ' + fusha.get('status', '?'), 'lloji: ' + fusha.get('type', '?'),
          'krijuar: ' + fusha.get('created', '?'), 'shkurtuar: ' + ('po' if shkurtuar else 'jo'), '---', '']
    koka_lex = '# PEP %d — %s (Status: %s · Type: %s · Created: %s)' % (
        numri, titulli, fusha.get('status', '?'), fusha.get('type', '?'), fusha.get('created', '?'))
    return ident, chr(10).join(fm) + koka_lex + chr(10) + chr(10) + trupi + chr(10)


def main_peps(nga: pathlib.Path, dalja: pathlib.Path) -> int:
    dalja.mkdir(parents=True, exist_ok=True)
    n = 0
    for sk in sorted(nga.iterdir()):
        r = ndaj_pep(sk)
        if not r:
            continue
        ident, trupi = r
        (dalja / (ident + '.md')).write_text(trupi, encoding='utf-8')
        n += 1
    print('njesi te shkruara:', n)
    print('dosja:', dalja)
    return 0


def main() -> int:
    import argparse
    a = argparse.ArgumentParser()
    a.add_argument('--burimi', choices=['privat', 'peps'], default='privat')
    a.add_argument('--nga', type=pathlib.Path, help='peps: directory with pep-NNNN.rst')
    a.add_argument('--dalja', type=pathlib.Path, default=None)
    ns = a.parse_args()
    if ns.burimi == 'peps':
        if not ns.nga:
            raise SystemExit('--nga <dir me pep-NNNN.rst> kerkohet')
        return main_peps(ns.nga, ns.dalja or (DALJA.parent / 'arkiva-peps'))
    DALJA.mkdir(parents=True, exist_ok=True)
    n = 0
    for skedari, lloji, pat in BURIME:
        if not skedari.exists():
            print('mungon:', skedari)
            continue
        tekst = skedari.read_text(encoding='utf-8', errors='replace')
        pjese = re.split(r'(?m)^(?=##\s)', tekst)
        for p in pjese:
            m = re.match(pat, p.strip())
            if not m:
                continue
            ident = m.group(1).lower()
            trupi = pastro(p.strip())
            if len(trupi) < 120:
                continue
            (DALJA / (lloji + '-' + ident + '.md')).write_text(
                '---' + chr(10) + 'id: ' + ident + chr(10) + 'burimi: ' + skedari.name + chr(10) + '---' + chr(10) + chr(10) + trupi + chr(10),
                encoding='utf-8')
            n += 1
    print('njesi te shkruara:', n)
    print('dosja:', DALJA)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
