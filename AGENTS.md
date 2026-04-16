# AGENTS.md

Project-level rules for AI agents working in this repository.

## Purpose

This repo hosts the **complementary website** plus **source components, figures, and text blocks** for printed conference posters. The repo is deployed via GitHub Pages; posters link to it via QR codes.

The user compiles printed posters themselves in PowerPoint. Do not add PPTX files, `build_poster.py`, `export_pdf.py`, or similar compilation scripts unless explicitly asked. The repo's job is the website + raw source material; the poster artifact itself lives outside the repo.

## Source of in-progress materials

Drafts and working files for each conference live in Box, under:

```
C:\Users\wilso\Box\Causal Methods Spring 2026\Sessions\Special projects\<conference-slug>\
```

When porting a conference into the repo, copy only what the website needs — typically `dashboard/index.html` (flatten the `dashboard/` wrapper on the way in), the `figures/` folder, and any `.drawio` sources the user is actively editing. Leave internal docs (HANDOFF, CONTENT_MAP, tour scripts, poster drafts, acceptance letters) in Box unless the user asks otherwise.

## Conference folder convention

Each conference lives in a top-level folder named `<conference>-<year>-<method-slug>/` (method-centric, not disease-centric — matches existing ACIC and ISPOR entries). Inside each:

- `index.html` — single-file React+CDN dashboard, no build step.
- `figures/` — SVG, PNG, and `.drawio` sources. The dashboard's `./figures/...` relative paths must resolve here. Drawio is the preferred format for figures the user iterates on — they edit in draw.io and export SVG back into this folder. When creating new figures, provide both a `.drawio` source and an SVG export.
- `components/` — reusable HTML/JSX snippets for dashboard + poster.
- `text/` — Markdown fragments (one per poster section).

The root `index.html` landing page links to each conference; the root `README.md` documents the convention.

## Deploy URL

The site is published at `https://andystats.github.io/conference-materials/`. Use this as the base URL when generating QR codes for printed posters — e.g. `https://andystats.github.io/conference-materials/<conference-slug>/`.

## Git hygiene

The repo is public. Before committing, confirm no secrets or patient-level data made it in. Don't stage `.claude/` or other local tooling state.
