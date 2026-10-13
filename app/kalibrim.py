#!/usr/bin/env python3
"""Kalibrim i pragut te refuzimit — matet, nuk hamendet.

Xhiron nje grup pyetjesh qe arkivi I Mbulon dhe nje grup qe NUK i mbulon;
afishon skorin me te larte te seciles, pastaj propozon pragun midis tyre.

Perdorimi:  python3 app/kalibrim.py
"""
import sys, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import reja  # noqa: E402

Mbulon = [
    'Cilat jane taksat vjetore te biznesit per 2026?',
    'Sa eshte buxheti i planifikuar per vitin e ardhshem?',
    'Cfare rregullon rregullorja e transparences?',
    'Cfare permban raporti i auditimit te 2025?',
]
Nuk_mbulon = [
    'Kush fitoi Kupen e Botes 2010?',
    'Cfare eshte fotosinteza?',
    'Sa kushton bileta e trenit ne Japoni?',
    'Kush e shkroi romanin Lumi i vdekur?',
]


def main() -> int:
    te_mbuluara, pa_mbulim = [], []
    print('--- pyetje qe arkivi I MBULON (skori me i larte) ---')
    for q in Mbulon:
        s = reja.kerko(q, 1)[0]['skor']
        te_mbuluara.append(s)
        print('  %.4f  %s' % (s, q[:60]))
    print('--- pyetje PA mbulim (skori me i larte) ---')
    for q in Nuk_mbulon:
        s = reja.kerko(q, 1)[0]['skor']
        pa_mbulim.append(s)
        print('  %.4f  %s' % (s, q[:60]))
    poshte, siper = max(pa_mbulim), min(te_mbuluara)
    print('---')
    print('me i larti PA mbulim : %.4f' % poshte)
    print('me i uleti ME mbulim : %.4f' % siper)
    if poshte < siper:
        prag = round((poshte + siper) / 2, 3)
        print('PRAG i propozuar      : %.3f  (ndarje e paster)' % prag)
    else:
        print('PA ndarje te paster — zonat mbivendosen; duhet korpus me i madh.')
        prag = round(sum(te_mbuluara) / len(te_mbuluara) * 0.85, 3)
        print('PRAG i propozuar (i kujdesshem): %.3f' % prag)
    print('vendos:  export ARK_PRAG=%s' % prag)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
