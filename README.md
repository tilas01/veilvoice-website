<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
# veilvoice-website

The source code of the VeilVoice website. It has two editions: the full one, which uses a little JavaScript for the live demos, the download checker and search, and a no-JavaScript edition built from plain HTML and CSS that works with scripts switched off. A small Python toolkit imports each release of the site, serves it on your own computer, and holds the nginx setup for running it on a server.

[![checks](https://github.com/tilas01/veilvoice-website/actions/workflows/checks.yml/badge.svg)](https://github.com/tilas01/veilvoice-website/actions/workflows/checks.yml)
[![CodeQL](https://github.com/tilas01/veilvoice-website/actions/workflows/codeql.yml/badge.svg)](https://github.com/tilas01/veilvoice-website/actions/workflows/codeql.yml)
[![zizmor](https://github.com/tilas01/veilvoice-website/actions/workflows/zizmor.yml/badge.svg)](https://github.com/tilas01/veilvoice-website/actions/workflows/zizmor.yml)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/tilas01/veilvoice-website/badge)](https://scorecard.dev/viewer/?uri=github.com/tilas01/veilvoice-website)
[![Licence: GPL-3.0-or-later](https://img.shields.io/badge/licence-GPL--3.0--or--later-blue)](LICENSE)

**The website:** [tilas01.github.io/veilvoice-website](https://tilas01.github.io/veilvoice-website/)

## Part of VeilVoice

[VeilVoice](https://github.com/tilas01/veilvoice) removes the voiceprint from a recording and keeps the words. Pitch, formants, timbre and accent are destroyed on your own machine, fully offline, so the speech can still be transcribed but not traced back to a voice. It is written in Rust with no `unsafe` code.

This repository holds only the website, so you can read, check or host it without downloading the whole program. The project lives in:

- [tilas01/veilvoice](https://github.com/tilas01/veilvoice): the program, its releases, the manual and the roadmap.
- **tilas01/veilvoice-website**: this repository, the website.
- **VeilVoice IPS** (Integrity Protection Service): an optional companion that watches for tampering. Its repository is being set up, and this list will link to it once it is public.

## What is in here

| Folder | What it holds |
| --- | --- |
| [`site/`](site) | The website itself, ready to serve. Every page, picture and script. |
| [`tools/import-site.py`](tools/import-site.py) | Copies the website from a VeilVoice release into `site/`, at this address. |
| [`hosting/local/`](hosting/local) | A small server for reading the site on your own computer. |
| [`hosting/nginx/`](hosting/nginx) | The configuration for serving the site from your own server with nginx. |
| [`tests/`](tests) | Checks run on every change. |

Only `site/` is published. The pages are generated from the VeilVoice sources, so to change what a page says, change its source in tilas01/veilvoice: an edit made directly in `site/` is replaced by the next import. The generators are moving into this repository next, and this section will say so when they have.

## Reading it on your own computer

You need Python 3.12 or later and nothing else.

```bash
git clone https://github.com/tilas01/veilvoice-website.git
cd veilvoice-website
python3 hosting/local/serve.py
```

Open the address it prints, normally <http://localhost:8000>. The server listens on your own computer only, so nothing else can reach it. It sends the same security headers as the real server, so a page that would break there breaks here first.

`python3 hosting/local/serve.py --check` fetches every page once and reports any that fail.

## Hosting it on a server

[`hosting/nginx/veilvoice.conf`](hosting/nginx/veilvoice.conf) serves `site/` over HTTPS behind Cloudflare, with a strict Content-Security-Policy, HSTS and the other security headers in [`veilvoice-headers.conf`](hosting/nginx/veilvoice-headers.conf). It keeps no access log, so the server holds no record of who visited. Replace `your.domain` with your domain and follow the comments at the top of each file.

## Importing a new release

```bash
python3 tools/import-site.py --from ../veilvoice                # the latest release
python3 tools/import-site.py --from ../veilvoice --ref v0.1.23  # a particular one
python3 tools/import-site.py --from ../veilvoice --check        # confirm site/ matches
```

It reads the release through git, so uncommitted work never reaches the site. It points every link at this website's address, keeps the 404 page out of the sitemap and adds the Google Search Console tag to the home page.

## The Search Console tag

The home page carries a `google-site-verification` tag. Google uses it to confirm that this site belongs to tilas01, and drops the site from Search Console the moment it disappears. It must stay on the home page for good. The importer adds it, the tests fail without it, and the publishing workflow refuses to publish a home page that lacks it.

## How this repository is kept safe

- **Every commit is signed** by tilas01.
- **CodeQL** scans the scripts and workflows.
- **zizmor** checks every workflow change. It is installed only if its hash matches the pinned one.
- **OpenSSF Scorecard** compares the repository's settings with good practice.
- **Dependabot** proposes updates to the pinned actions and to zizmor, each held back for seven days after release. Nothing merges by itself.

## Reporting a problem

- **Something wrong on the website**, such as a broken page or a dead link: [open an issue here](https://github.com/tilas01/veilvoice-website/issues).
- **Something wrong with the program**: [open an issue on tilas01/veilvoice](https://github.com/tilas01/veilvoice/issues).
- **A security problem with either**: report it privately, as [SECURITY.md](SECURITY.md) explains. Please don't open a public issue for it.

## Licence

GPL-3.0-or-later, copyright tilas01, the same as VeilVoice. The full text is in [LICENSE](LICENSE).
