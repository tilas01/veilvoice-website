<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
# veilvoice-website

The VeilVoice website: downloads and how to verify them, the full manual, and live demos of the app and command line.

[![CodeQL](https://github.com/tilas01/veilvoice-website/actions/workflows/codeql.yml/badge.svg)](https://github.com/tilas01/veilvoice-website/actions/workflows/codeql.yml)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/tilas01/veilvoice-website/badge)](https://scorecard.dev/viewer/?uri=github.com/tilas01/veilvoice-website)
[![Licence: GPL-3.0-or-later](https://img.shields.io/badge/licence-GPL--3.0--or--later-blue)](LICENSE)

## What VeilVoice is

[VeilVoice](https://github.com/tilas01/veilvoice) removes the voiceprint from a recording and keeps the words. Pitch, formants, timbre and accent are destroyed on your own machine, fully offline, so the speech can still be transcribed but not traced back to a voice. It is written in Rust with no `unsafe` code.

Everything about the program lives in [tilas01/veilvoice](https://github.com/tilas01/veilvoice):

- [The code](https://github.com/tilas01/veilvoice/tree/main/crates) and its [README](https://github.com/tilas01/veilvoice#readme)
- [Releases](https://github.com/tilas01/veilvoice/releases), with checksums and signatures
- [The manual and guides](https://github.com/tilas01/veilvoice/tree/main/docs), and the [wiki](https://github.com/tilas01/veilvoice/wiki)
- [The roadmap](https://github.com/tilas01/veilvoice/blob/main/ROADMAP.md) and [the changelog](https://github.com/tilas01/veilvoice/blob/main/CHANGELOG.md)

The [`veilvoice`](veilvoice) folder in this repository is a link to that repository, pinned to the commit the site was built from.

## How this repository is made

The site is moving here from tilas01/veilvoice. Until the move is finished, it is still served at [tilas01.github.io/veilvoice](https://tilas01.github.io/veilvoice/), and that address will keep working afterwards.

Every page here is generated. The generators are in tilas01/veilvoice, under [`tools/site/`](https://github.com/tilas01/veilvoice/tree/main/tools/site) and [`tools/docs/`](https://github.com/tilas01/veilvoice/tree/main/tools/docs). Once the move is done, each VeilVoice release rebuilds the site from the released commit and commits the result here, signed by the project key, so the site always describes a version you can download.

To change what a page says, change its source in tilas01/veilvoice. An edit made directly here is overwritten by the next release.

To look at the site on your own machine, clone tilas01/veilvoice and run `python tools/site/serve.py`. Every page also works with JavaScript switched off.

## Reporting a problem

- **Something wrong on the website**, such as a broken page, a dead link or a download that does not match its checksum: [open an issue here](https://github.com/tilas01/veilvoice-website/issues).
- **Something wrong with the program**: [open an issue on tilas01/veilvoice](https://github.com/tilas01/veilvoice/issues).
- **A security problem with either**: report it privately, as [SECURITY.md](SECURITY.md) explains. Please do not open a public issue for it.

## Maintainers

tilas01. Questions and reports go to the issue trackers above.

## Licence

GPL-3.0-or-later © tilas01, the same as VeilVoice. See [LICENSE](LICENSE).
