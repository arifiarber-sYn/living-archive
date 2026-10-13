#!/usr/bin/env bash
# pergatit_publik.sh — builds the PUBLIC tree of this repo in a fresh git history, without the private archive.
#   bash tools/pergatit_publik.sh [/tmp/nebius-gara-publik]
# Halim's condition #2 / K-C: `arkiva/` (derived from private notes) must never be published; the public corpus is arkiva-peps/.
# Nothing is pushed by this script. Output = local repo with ONE commit; remote = living-archive (K-C = A-lite, decided 13.10).
set -euo pipefail
SRC="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${1:-/tmp/nebius-gara-publik}"
rm -rf "$OUT"; mkdir -p "$OUT"
# 1. copy tracked files only (no logs, no .git, no private archive, no embeddings binaries)
( cd "$SRC" && git ls-files -z | grep -zv '^arkiva/' | grep -zv '^emb\.log$' | grep -zv '^eval[0-9]*\.log$' \
  | tar --null -T - -cf - ) | tar -C "$OUT" -xf -
# 2. public default corpus + ignore the private one if someone recreates it locally
sed -i "s#(_RRENJA / 'arkiva'))#(_RRENJA / 'arkiva-peps'))#" "$OUT/src/know.py" "$OUT/src/embeddings.py"
sed -i 's#Path(os.environ.get("ARK_ARKIVA") or (KETU / "arkiva"))#Path(os.environ.get("ARK_ARKIVA") or (KETU / "arkiva-peps"))#' "$OUT/src/remember.py"
sed -i "s#(RRENJA / 'arkiva'))#(RRENJA / 'arkiva-peps'))#" "$OUT/src/audit.py"
printf '\n# private archive (never published) — see README «Public example corpus»\narkiva/\n' >> "$OUT/.gitignore"
# 2b. the private question set's answer rows quote private text → keep only the summaries; the public transcript replaces the private one
python3 - "$OUT" <<'PY'
import json, pathlib, sys
out = pathlib.Path(sys.argv[1])
for p in out.glob('harness/report*.json'):
    if 'peps' in p.name:
        continue
    d = json.loads(p.read_text(encoding='utf-8'))
    if isinstance(d, dict) and 'rreshtat' in d:
        d['rreshtat'] = 'redacted in the public tree — the private corpus is never published; per-row data lives in report-peps*.json'
        p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
# human-review notes quote private answers in their free text → keep structure/verdicts, drop the quotes
for name in ('harness/vleresim-njerezor.json', 'harness/audit-toka.json'):
    q = out / name
    if q.exists():
        d = json.loads(q.read_text(encoding='utf-8'))
        for r in d.get('rastet', []):
            for k in ('arsyeja', 'prova', 'pyetja'):
                if k in r:
                    r[k] = 'redacted in the public tree (quotes the private corpus)'
        q.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
tp = out / 'demo/transcript-peps.md'
if not tp.exists():
    sys.exit('NDAL: demo/transcript-peps.md mungon (i pagjurmuar?) — transkripti privat do të dilte publik')
(out / 'demo/transcript.md').write_text(tp.read_text(encoding='utf-8'), encoding='utf-8')
PY
# 2c. private-marker scan OUTSIDE the public corpus: text of private units must not appear anywhere (fail-closed)
if ( cd "$OUT" && grep -rIlE 'Halimi has|autonomi pa limite|full digital autonomy|securevault/secrets/[a-z-]+\.key.*=' --exclude-dir=arkiva-peps --exclude-dir=.git . | grep -v '^./tools/pergatit_publik.sh$' | grep . ); then
  echo "NDAL: tekst privat në pemën publike (shih skedarët më lart)"; exit 4; fi
# 3. fresh history
( cd "$OUT" && git init -q -b main && git add -A && git -c user.name="Living Archive" -c user.email="noreply@example.invalid" \
  commit -qm "The Living Archive — public tree (Nebius x NVIDIA Global AI Hackathon, Personal AI track)" )
# 4. proofs: no private unit, tests green, no secrets
if ( cd "$OUT" && git ls-files | grep -q '^arkiva/' ); then echo "NDAL: arkiva/ u gjurmua"; exit 2; fi
TESTI=$( cd "$OUT" && ARK_ARKIVA=arkiva-peps python3 -m unittest discover -s tests 2>&1 | grep -E '^(OK|FAILED)' | tail -1 )
echo "teste: ${TESTI:-?}"; case "$TESTI" in OK*) ;; *) echo "NDAL: testet në pemën publike nuk janë të gjelbra"; exit 5;; esac
if command -v gitleaks >/dev/null; then ( cd "$OUT" && gitleaks detect --source . --no-banner --exit-code 9 >/dev/null 2>&1 && echo "gitleaks: 0" || { echo "NDAL: gitleaks gjeti diçka"; exit 3; } ); fi
echo "GATI: $OUT  ($(cd "$OUT" && git ls-files | wc -l) skedarë, $(du -sh "$OUT" | cut -f1)) — push: cd $OUT && git remote add origin git@github.com:arifiarber-sYn/living-archive.git && git push -f origin main (A-lite, histori 1-commit; L-261: kurrë arkiva/)."
