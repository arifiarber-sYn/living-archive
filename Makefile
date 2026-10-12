# Nje skedar, dy motorë. Vendos me: ARK_ENGINE=reja (ose lere bosh per vendorin).
ENGINE ?= vendor
Q ?= Sa eshte buxheti total i miratuar per vitin 2027?

ifeq ($(ENGINE),reja)
  SKRIPT := app/reja.py
  HARNESS := app/harness_reja.py
else
  SKRIPT := app/arkivi.py
  HARNESS := app/harness.py
endif

.PHONY: gelltit pyet ui harness kalibrim kosto

gelltit:
	python3 $(SKRIPT) gelltit

pyet:
	@if [ "$(ENGINE)" = "reja" ]; then python3 $(SKRIPT) pyet "$(Q)"; else python3 $(SKRIPT) pyet "$(Q)"; fi

harness:
	python3 $(HARNESS)

kalibrim:
	python3 app/kalibrim.py

kosto:
	python3 app/reja.py kosto

ui:
	python3 app/ui.py
