.PHONY: run test demo eval matje index peps index-peps eval-peps eval-peps-100 run-peps audit screenshots check demo-peps

run: arkiva/embeddings.json
	python3 -m src.app "$(Q)"

arkiva/embeddings.json:
	python3 src/embeddings.py   # one-off local index (≈$0.003 on Token Factory); without it `make run` would fall back to BM25

demo:
	python3 src/server.py

test:
	python3 -m unittest discover -s tests -v

check:   # preflight for a judge: the tests (no network, no key) + what each live part still needs — nothing is assumed
	@python3 -m unittest discover -s tests 2>&1 | grep -E "^(Ran|OK|FAILED)" | tr "\n" " "; echo
	@test -n "$$NEBIUS_API_KEY" && echo "NEBIUS_API_KEY  set     -> make run / demo / eval will call Token Factory" || echo "NEBIUS_API_KEY  missing -> make run / demo / eval need it; make test does not"
	@test -f arkiva-peps/embeddings.json && echo "public index    present (arkiva-peps/embeddings.json)" || echo "public index    missing -> make peps index-peps (one-off, about \$$0.003)"
	@test -f arkiva/embeddings.json && echo "private index   present" || echo "private index   missing -> make index (private corpus; the public one is enough for the demo)"
	@test -n "$$TAVILY_API_KEY" && echo "TAVILY_API_KEY  set     -> /web answers from live sources behind the privacy gate" || echo "TAVILY_API_KEY  missing -> /web refuses with 'pa_celes' (fail-closed); everything else works"
	@echo "public demo     ARK_ARKIVA=arkiva-peps ARK_RATE_PER_MIN=6 ARK_DAILY_CAP_USD=1 make demo   (per-IP rate limit + daily spend cap, see /buxheti)"

demo-peps:   # the public corpus on its own port, with the budget guard on — what the public demo URL runs
	ARK_ARKIVA=arkiva-peps ARK_PORT=$(or $(ARK_PORT),8079) ARK_RATE_PER_MIN=$(or $(ARK_RATE_PER_MIN),6) ARK_DAILY_CAP_USD=$(or $(ARK_DAILY_CAP_USD),1) python3 src/server.py

eval:
	python3 harness/eval.py

matje:
	python3 src/matje.py 5 $(or $(ETIKETA),dita1)

index:
	python3 src/embeddings.py

# Public example corpus (Python PEPs, public domain/CC0) — the same engine, a corpus anyone can rebuild.
PEPS ?= /tmp/peps/peps
peps:
	test -d $(PEPS) || git clone -q --depth 1 https://github.com/python/peps.git $(dir $(PEPS))
	python3 harness/ndaj_korpusin.py --burimi peps --nga $(PEPS) --dalja arkiva-peps
index-peps:
	ARK_ARKIVA=arkiva-peps python3 src/embeddings.py --mat
	ARK_ARKIVA=arkiva-peps python3 src/embeddings.py
eval-peps:
	ARK_ARKIVA=arkiva-peps ARK_PYETJE=pyetjet-peps.json ARK_RAPORT=report-peps.json python3 harness/eval.py
run-peps:
	ARK_ARKIVA=arkiva-peps python3 -m src.app "$(Q)"
eval-peps-100:   # 80 generated questions (ground truth by construction) + 20 traps; ≈$0.07
	ARK_ARKIVA=arkiva-peps ARK_PYETJE=pyetjet-peps-100.json ARK_RAPORT=report-peps-100.json python3 harness/eval.py
audit:   # memory-audit matrix for one unit: make audit ID=vendim-d-070  (ARK_ARKIVA=arkiva-peps make audit ID=pep-0008)
	python3 src/audit.py "$(ID)"
DEMO_URL ?= http://127.0.0.1:$(or $(ARK_PORT),8077)
screenshots:   # real screenshots of the running dashboard (run the demo on the PUBLIC corpus first: ARK_ARKIVA=arkiva-peps make demo)
	python3 tools/screenshots.py --url $(DEMO_URL) --out docs/screenshots
