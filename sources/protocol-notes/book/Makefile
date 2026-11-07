BOOK = main
all: $(BOOK).pdf
$(BOOK).pdf: $(BOOK).tex front.tex ch*.tex appendix.tex
	xelatex -interaction=nonstopmode -halt-on-error $(BOOK).tex
	xelatex -interaction=nonstopmode -halt-on-error $(BOOK).tex
	xelatex -interaction=nonstopmode -halt-on-error $(BOOK).tex
clean:
	rm -f *.aux *.log *.out *.toc *.pdf
.PHONY: all clean
