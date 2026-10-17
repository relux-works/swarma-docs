# Agent instructions for this repository

This repository holds the Swarma paper and book. The Russian text is the source of truth.

- Read `editorial/style.ru.md`, `editorial/names.ru.md` and `editorial/sources.ru.md` before writing. The plans are `editorial/paper-outline.ru.md` and `editorial/book-outline.ru.md`.
- Write only what the sources in `sources/` and the `editorial/` files support. Never invent formats, fields, refusal codes or numbers. Never raise a status above what the source says.
- The text is for an external reader: no internal identifiers, no session, seat, machine or people names (except the authors), no local paths, no private repository links.
- Edit Markdown and LaTeX sources only. Do not rebuild `book/swarma-book.ru.pdf` or render diagrams; the orchestrator does that after review.
- Run `sh scripts/check.sh` before handing off; it must pass.
- Commits are signed with the configured identity.
