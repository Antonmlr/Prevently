# ============================================================
#  Makefile – Prevently · Project for the Term Project
#  THGA Bochum · Stephan Bökelmann - edited by Anton Möller
#
#  Builds two PDFs and a PNG image into out/:
#    - proposal       the fill-in template (proposal-template/)
#    - documentation  the worked example (example-documentation/)
#
#  Requirement: TeX Live with latexmk (apt install latexmk texlive-full) & PlantUML (apt install plantuml)
# ============================================================

PLANTUML := plantuml
LATEXMK  := latexmk
OUTDIR   := ../out

SCHEMA_PUML := db/schema.puml
SCHEMA_PNG  := $(OUTDIR)/schema.png

# -cd: latexmk changes into the source file's directory before building,
#      so \input and the style search path resolve. The output directory
#      ../out is relative to the source file and therefore always lands in
#      the repository-level out/.
LMKFLAGS := -pdf -interaction=nonstopmode -halt-on-error \
            -cd -output-directory=../$(OUTDIR)

# The style package lives in style/ and is found via an absolute TEXINPUTS
# path, regardless of which subdirectory the source file sits in.
TEXENV   := TEXINPUTS="$(CURDIR)/style:.:$$TEXINPUTS"

STYLE    := style/thga-db.sty

# Let make find each .tex by its basename across the source directories.
vpath %.tex docs/proposal-template docs/example-documentation docs/User-manual

## All documents to build (basename without .tex):
DOCS     := proposal documentation userguide

ALL_PDF  := $(addprefix $(OUTDIR)/, $(addsuffix .pdf, $(DOCS)))

# ---- Main targets -------------------------------------------

.PHONY: all clean distclean help

all: $(ALL_PDF) $(SCHEMA_PNG)

$(OUTDIR):
	mkdir -p $(OUTDIR)

# Generic rule: <basename>.tex (found via vpath) → out/<basename>.pdf
$(OUTDIR)/%.pdf: %.tex $(STYLE) | $(OUTDIR)
	$(TEXENV) $(LATEXMK) $(LMKFLAGS) $<

$(SCHEMA_PNG): $(SCHEMA_PUML) | $(OUTDIR)
	$(PLANTUML) -tpng -o $(OUTDIR) $<

# ---- Clean up -----------------------------------------------

clean:
	rm -f $(addprefix $(OUTDIR)/, *.aux *.log *.fdb_latexmk *.fls *.out *.toc *.synctex.gz)

distclean:
	rm -rf $(OUTDIR)

# ---- Help ---------------------------------------------------

help:
	@echo "Available targets:"
	@echo "  all        – build all PDFs  (→ $(OUTDIR)/)"
	@echo "  clean      – remove auxiliary files, keep PDFs"
	@echo "  distclean  – remove everything including $(OUTDIR)/"
