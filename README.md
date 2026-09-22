# Community Partners Initiatives — cpinitiatives.org

Fully static, front-end-only website for CPI, built to host on GitHub Pages with
zero backend. Admin/CMS and real data intake are a later phase — this is the
public-facing site.

## Stack

Plain HTML/CSS/JS. No build step is required to *serve* the site — every file
in this repo is already the deployable output. A small Python generator
(`scripts/build.py`) is the single source of truth for shared chrome (nav,
footer) and placeholder content, so editing content means editing that script
and re-running it rather than hand-editing 20 HTML files:

```bash
python3 scripts/build.py
```

## Structure

```
index.html                     Homepage
find-support.html              Public "find a partner" search
about.html                     Mission, model, founding thesis
donate.html                    Giving page (embed slot — see below)
join.html                      Partner application wizard (client-side)
get-involved.html              Audience router
contact.html
portal.html                    "Coming soon" placeholder for the partner portal
partners/                      Partner directory + one static page per partner
initiatives/                   Initiative directory + one static page per initiative
needs/                         Public needs board
resources/                     Resource library
assets/css/style.css           Design system (tokens, components)
assets/js/*.js                 Nav, search/filter, and the join wizard
scripts/build.py               Generator — data + templates live here
```

Partner and initiative detail pages are pre-rendered to real folders
(`/partners/<slug>/`, `/initiatives/<slug>/`) so URLs are stable and
crawlable — no client-side routing required.

## Placeholder content

**All partner organizations, initiatives, and needs in this build are
fictional placeholders** (`scripts/build.py`, `PARTNERS` / `INITIATIVES` /
`NEEDS`), sized to match the PRD's "launch slice" (6 partners, 3 initiatives,
5 needs, 4 categories). Replace them with real, verified partner data before
this goes live — do not launch with placeholder orgs presented as real. The
`resources/` page links to real public resources (211 LA, EDD, DPSS, etc.);
verify those are still current before launch.

## Donations

`donate.html` ships with a clearly-labeled embed slot instead of a fake
"Donate" button, because a static site can't process payments on its own.
Once you have a processor account, drop its embeddable widget in:

- **Donorbox** — embeddable campaign iframe/script, no backend needed.
- **Give Lively** — embeddable donation form.
- **PayPal Giving Fund / PayPal donate button** — hosted button, pure HTML.

All three are client-side embeds and work fine on GitHub Pages. Until one is
wired up, the page offers a `mailto:` fallback for direct gifts.

## Deploying to free GitHub Pages

This site is intentionally static and requires no paid hosting, server, database, or build service.

1. In repo **Settings → Pages**, choose **Deploy from a branch**.
2. Select branch `main` and folder `/ (root)`.
3. Keep the root `.nojekyll` file so GitHub serves every static asset directly.
4. `CNAME` is present with `cpinitiatives.org`.
5. At Squarespace DNS, use four A records for `@`: `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`.
6. Add a CNAME for `www` pointing to `ghettoeinstein.github.io`.
7. Wait for GitHub TLS certificate provisioning, then enable **Enforce HTTPS**.

The public MVP works without a backend: Homepage → Find Support/Partners → Initiative → Join CPI. Forms use static-friendly fallbacks until a hosted form service or backend is added.

## Known repo issue (unrelated to this build)

`/Users/emperorpierre` itself is a git repository (`.git` lives at the home
directory root, not inside `cpi/`). That means a `git add`/`commit` run from
`~/cpi` operates on your entire home folder unless you're careful. This repo
was initialized separately, scoped to `cpi/` only, to avoid that risk — but
the home-directory repo still exists and is worth cleaning up separately.
# cpinitiatives
# cpinitiatives
# cpinitiatives
# cpinitiatives
