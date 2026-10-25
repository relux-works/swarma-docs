# Build the Swarma Chain paper with tectonic (XeTeX engine, packages fetched on demand).
#   make -C paper/chain   -> paper/chain/chain.pdf
#   make -C paper/chain clean
TECTONIC ?= tectonic

chain.pdf: chain.tex references.bib
	$(TECTONIC) -X compile chain.tex

clean:
	rm -f chain.pdf

.PHONY: clean
