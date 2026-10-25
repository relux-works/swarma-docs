# Build the platform paper with tectonic (XeTeX engine, packages fetched on demand).
#   make -C paper/platform        -> paper/platform/platform.pdf
#   make -C paper/platform clean
TECTONIC ?= tectonic

platform.pdf: platform.tex references.bib
	$(TECTONIC) -X compile platform.tex

clean:
	rm -f platform.pdf

.PHONY: clean
