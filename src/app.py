"""Hyrja e projektit — pyet arkivën e gjalle nga rreshti i komandave.

Përdorimi:
  export NEBIUS_API_KEY=...        # ose çelësi nga thesari lokal
  python3 -m src.app "Pyetja"

Nje komande nga klon i paster:  make run Q="Which decision grants unlimited autonomy?"
"""
from __future__ import annotations

import json
import sys

from src.know import Arkiva, pergjigju


def main() -> int:
    pyetja = ' '.join(sys.argv[1:]).strip() or 'Which decision grants unlimited autonomy to the agent?'
    ark = Arkiva()
    r = pergjigju(ark, pyetja)
    print('arkiva:', ark.N, 'njesi | semantike:', ark.vec is not None)
    print('pyetja:', pyetja)
    print('-' * 60)
    print(r['pergjigja'] or '(pa pergjigje)')
    print('-' * 60)
    print('citime:', r['citime'] or '(asnje)', '| refuzim:', r['refuzim'])
    print('gjetjet:', r['gjetjet'][:4])
    print('kohe: %ss | kosto: $%s' % (r['sekonda'], r['kosto_usd']))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())