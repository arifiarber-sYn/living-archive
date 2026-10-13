#!/usr/bin/env python3
"""screenshots.py — real screenshots of the running demo for README/Devpost (Design criterion).

Drives the actual UI (`src/ui.html`) against a live server: every answer, refusal and git line in the PNGs comes
from real calls to Nebius Token Factory / Tavily — nothing is mocked or edited. Run it against the PUBLIC corpus
only (ARK_ARKIVA=arkiva-peps), so no private text ends up in an image.

    ARK_ARKIVA=arkiva-peps ARK_PORT=8131 make demo &
    python3 tools/screenshots.py --url http://127.0.0.1:8131 [--out docs/screenshots] [--no-web]

Needs: playwright (python) + chromium. Writes 1280×800 PNGs + an index of what each shows (shots.json).
"""
from __future__ import annotations

import argparse
import json
import pathlib
import time

from playwright.sync_api import sync_playwright

SHOTS = [
    # (file, what the judge sees, action)
    ('01-ask-cited', 'answerable question → answer with a [pep-xxxx] citation, latency and cost', 'ask', 'Which PEP added assignment expressions?'),
    ('02-ask-refused', 'trap (non-existent PEP) → the model says «I don\'t know» instead of inventing', 'ask', 'What does PEP 9999 propose?'),
    ('03-memory-history', 'memory audit trail: git log of the memory directory, the agent\'s own `remember` commits on top', 'hist', None),
    ('04-web-gate', 'web layer WITHOUT permission → privacy gate refuses, 0 bytes leave the machine', 'web', False),
    ('05-web-cited', 'web layer WITH permission → archive units first, Tavily pages second; one answer citing [pep-0572] and [wN] side by side', 'web', True),
]
WEB_Q = 'Which PEP added assignment expressions and in which Python release did it ship?'  # memory knows the PEP, the web knows the release


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--url', default='http://127.0.0.1:8077')
    ap.add_argument('--out', default='docs/screenshots')
    ap.add_argument('--no-web', action='store_true', help='skip the Tavily shots (no key / no permission)')
    a = ap.parse_args()
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    indeksi = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': 1280, 'height': 800}, device_scale_factor=1)
        pg.goto(a.url, wait_until='networkidle')
        pg.wait_for_selector('#metrics .m')
        for emri, cka, lloji, arg in SHOTS:
            if lloji == 'web' and a.no_web:
                continue
            if lloji == 'ask':
                pg.fill('#q', arg)
                pg.click('#bq')
                pg.wait_for_function("document.getElementById('meta').textContent.length > 0", timeout=120000)
            elif lloji == 'hist':
                pg.click('text=Memory history')
                pg.wait_for_function("document.getElementById('mem').textContent.includes('git log')")
            elif lloji == 'web':
                pg.fill('#wq', WEB_Q)
                if pg.is_checked('#allow') != bool(arg):
                    pg.click('#allow')
                pg.click('#bw')
                pg.wait_for_function("document.getElementById('wmeta').textContent.length > 0", timeout=120000)
                pg.locator('#wout').scroll_into_view_if_needed()
            time.sleep(0.4)
            skedari = out / (emri + '.png')
            pg.screenshot(path=str(skedari), full_page=(lloji == 'web'))
            indeksi.append({'skedari': skedari.name, 'tregon': cka, 'hyrja': arg if isinstance(arg, str) else WEB_Q if lloji == 'web' else None,
                            'ora': time.strftime('%Y-%m-%dT%H:%M:%S')})
            print('✓', skedari, '—', cka)
        b.close()
    (out / 'shots.json').write_text(json.dumps({'url': a.url, 'shots': indeksi}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
