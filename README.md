# Conference Materials Site

Static site hosting companion dashboards, posters, and supplementary material for conference presentations. Designed to be linked from printed posters via QR code.

## Structure

```
site/
├── index.html                                   # Landing page (list of all conferences)
├── acic-2026-causal-shap/
│   ├── index.html                               # Interactive dashboard for the ACIC 2026 poster
│   ├── figures/                                 # Source figures (SVG, PNG, .drawio where applicable)
│   ├── components/                              # Reusable HTML/JSX snippets for dashboard + poster
│   └── text/                                    # Markdown fragments for poster sections
├── ispor-2026-causal-discovery/
│   ├── index.html                               # Interactive dashboard for the ISPOR 2026 poster
│   ├── figures/                                 # Source figures (SVG, PNG, .drawio where applicable)
│   ├── components/                              # Reusable HTML/JSX snippets for dashboard + poster
│   └── text/                                    # Markdown fragments for poster sections
└── README.md                                    # This file
```

Each conference/poster gets its own subdirectory. The landing page at `/` lists them. QR codes on the posters point to the subdirectory URL (e.g., `https://<user>.github.io/<repo>/acic-2026-causal-shap/`).

## Per-conference scaffolding

Each conference folder follows the same three-subfolder convention so the repo is the canonical home for the website *and* the source material for the printed poster (which is compiled separately in PowerPoint):

- **`figures/`** — Source figures. SVG + PNG rasters for anything the dashboard embeds; `.drawio` files for figures under active iteration so they can be edited directly in draw.io and re-exported as SVG. Both ACIC and ISPOR conferences carry `.drawio` sources alongside their SVG/PNG exports.
- **`components/`** — Reusable HTML/JSX snippets that can be pasted into the dashboard or lifted into PowerPoint shapes. See the folder's `README.md` for filename convention.
- **`text/`** — Plain Markdown fragments, one per poster section (headline, abstract, column copy, captions). Feed these into PowerPoint when composing the printed poster.

New folders start empty with a `README.md` stub describing the convention. Real poster work drives the first entries.

## Dependencies

All pages are single-file HTML with CDN-loaded dependencies:

- React 18, ReactDOM 18 (unpkg)
- Recharts 2.15 (unpkg)
- KaTeX 0.16 (jsdelivr)
- Google Fonts (Playfair Display, Source Sans 3)
- Babel standalone (for in-browser JSX transform)

No build step. Just push and it works. Requires the viewer to be online.

## Deploying to GitHub Pages

1. Create a repository (suggested name: `conference-materials`).
2. Copy the contents of this `site/` folder into the repo root (or keep them under `site/` and configure Pages to serve from that folder).
3. Enable GitHub Pages: repo `Settings` → `Pages` → Source: `main` branch, folder `/` (or `/site` if you kept the structure).
4. Wait for the deploy action to finish. The URL will be `https://<user>.github.io/<repo>/`.

### Deploying from root

If you'd like the site URL to be just `https://<user>.github.io/<repo>/`, copy the files from `site/` to the repo root:

```bash
git clone https://github.com/<user>/conference-materials.git
cd conference-materials
cp -R /path/to/site/* .
git add .
git commit -m "Add conference materials site"
git push
```

### Deploying from `site/`

If you want to keep the repo clean and have Pages serve from a subfolder, after push:

- `Settings` → `Pages` → `Source: main / site`

The URL stays the same.

## Updating a dashboard

Each dashboard is a single self-contained HTML file. Edit the file, commit, push. Changes go live within a minute.

## Custom domain (optional)

Add a `CNAME` file containing your custom domain, then point a CNAME DNS record to `<user>.github.io`.

## Local preview

```bash
# From this directory, run any static server:
python -m http.server 8000
# Then open http://localhost:8000
```
