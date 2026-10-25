# Build the paper with tectonic (XeTeX engine, packages fetched on demand).
#   make          -> paper.pdf
#   make model    -> run the integration-fragment model and check its result
#   make clean
TECTONIC ?= tectonic

paper.pdf: paper.tex references.bib
	$(TECTONIC) -X compile paper.tex

model:
	python3 -I model/integration-fragment-model.py

clean:
	rm -f paper.pdf

.PHONY: model clean
