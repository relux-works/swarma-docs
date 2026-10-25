# Build the paper with tectonic (XeTeX engine, packages fetched on demand).
#   make          -> paper.pdf
#   make appendix -> status-appendix.pdf (implementation state, a separate document)
#   make model    -> run the integration-fragment model and check its result
#   make clean
TECTONIC ?= tectonic

paper.pdf: paper.tex references.bib
	$(TECTONIC) -X compile paper.tex

appendix: status-appendix.pdf

status-appendix.pdf: status-appendix.tex
	$(TECTONIC) -X compile status-appendix.tex

model:
	python3 -I model/integration-fragment-model.py

clean:
	rm -f paper.pdf status-appendix.pdf

.PHONY: appendix model clean
