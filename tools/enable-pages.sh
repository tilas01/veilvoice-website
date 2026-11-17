#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Switch GitHub Pages on for tilas01/veilvoice-website, published by the
# `pages` workflow rather than from a branch, then publish site/ once.
# Needs the GitHub CLI signed in as tilas01 (`gh auth status`).
set -euo pipefail
repo=tilas01/veilvoice-website

if gh api "repos/$repo/pages" >/dev/null 2>&1; then
  echo "Pages is already on; making sure it publishes from the workflow"
  gh api -X PUT "repos/$repo/pages" -f build_type=workflow >/dev/null
else
  echo "switching Pages on, published by the workflow"
  gh api -X POST "repos/$repo/pages" -f build_type=workflow >/dev/null
fi
gh api "repos/$repo/pages" --jq '"Pages: " + .html_url + " (" + .build_type + ")"'

gh workflow run pages.yml --repo "$repo" --ref main
echo "deploy started; follow it with: gh run watch --repo $repo"
