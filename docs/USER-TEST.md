# User test — Impact (N-2), 13.10.2026

**Pse:** juria e shënon **Impact 6.71/10** në 4 raunde radhazi: «audienca = autori», «harness-i vërteton retrieval-in, jo rezultatin te përdoruesit». Zgjidhja = **1 njeri i jashtëm (jo autori)** bën 10 pyetje reale + verdikt. 30 min.

## Procedura (për njerëzën testues)
1. Hap **http://127.0.0.1:8077/** (dashboard-i; demo-ja duhet ndezur — `make demo`).
2. Bëj pyetjet; për secilën shëno:
   - **a citoi?** (po/jo) · **a refuzoi?** (po/jo)
   - **verdikti yt:** saktë / i pjesshëm / gabim / s'e di
3. Regjistro në `harness/user-test.json` (skema më poshtë, ose ma dërgo listën dhe e shkruaj unë).

## 10 pyetje të propozuara (mix i vërtetë + kurthe)
1. Which PEP added the walrus operator (`:=`) to Python?
2. What does PEP 8 recommend as the maximum line length?
3. Which PEP defines the «Zen of Python»?
4. Which PEP added `match`/`case` structural pattern matching?
5. What does PEP 484 introduce?
6. **Kurthë:** What does PEP 9999 propose?
7. **Kurthë:** What is the best restaurant in Pristina?
8. Which PEP describes Python's release/version support cycle?
9. What does PEP 20 say about simplicity?
10. How do I pickle a lambda function? *(jashtë domenit → duhet refuzim i sinqertë)*

## Skema (`harness/user-test.json`)
```json
{
  "tester": "<emri, jo autori>",
  "data": "2026-10-13",
  "pyetje": [
    {"q": "...", "citoi": true, "refuzoi": false, "verdikti": "saktë", "koment": ""}
  ],
  "permbledhje": {"sakte": 0, "pjesshem": 0, "gabim": 0, "refuzime_te_sakta": 0}
}
```

## Pas testit
3 rreshta «Impact — measured» në README: *«An external tester asked 10 real questions: N cited correctly, M honest refusals, 0 confidently wrong.»* — kjo mbyll (a) dhe (b) e jurisë.
