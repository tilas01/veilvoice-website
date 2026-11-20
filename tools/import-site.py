#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Copy the website out of a VeilVoice release into site/.

    python3 tools/import-site.py --from ../veilvoice            # latest release
    python3 tools/import-site.py --from ../veilvoice --ref v0.1.23
    python3 tools/import-site.py --from ../veilvoice --check    # changes nothing

Until the generators move into this repository, the pages are still built in
tilas01/veilvoice and committed there under website/. This takes that folder
exactly as it was at a release tag, so the site always describes a version
you can download, and makes the three changes the new address needs:

1. Every link to the old address, tilas01.github.io/veilvoice, now names this
   site instead. The old address keeps working, because it redirects here,
   but canonical links, the sitemap and social previews should name the page
   people are meant to land on.
2. The home page carries the Google Search Console verification tag. Search
   Console drops the site the moment the tag is gone, so this refuses to write
   a home page without it.
3. The "not found" page is taken out of the sitemap, which should list only
   pages worth finding.
4. Nothing else. Every other byte is copied unchanged, so a diff of site/
   against the release shows only the address.

It reads the release with `git archive`, so uncommitted edits in the veilvoice
checkout never reach the site, and it unpacks with the "data" filter, which
refuses absolute paths, links that point outside the folder and device files.
Standard library only.
"""

import argparse
import io
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE = os.path.join(ROOT, "site")

NEW = "https://tilas01.github.io/veilvoice-website"

# The old address, with or without its scheme (link text often leaves it
# off), but not this repository's own address, which starts with the same
# letters: `(?![\w-])` stops "veilvoice" matching "veilvoice-website".
OLD = re.compile(r"(https?://)?tilas01\.github\.io/veilvoice(?![\w-])")


def _moved(match):
    return NEW if match.group(1) else NEW.split("://", 1)[1]

# The token proves to Google that tilas01 controls the site. It is not a
# secret: it grants nothing to anyone who copies it.
VERIFICATION = (
    '<meta name="google-site-verification" '
    'content="PrXwNiHGNWIM2txx_q0gUkifC33DUK5qk3cMkXYangc" />'
)

# Files whose text may name the old address. Everything else (pictures, fonts,
# the signing key) is copied byte for byte.
TEXT = (".html", ".xml", ".txt", ".json", ".js", ".css", ".md", ".svg")

# The signing key and its fingerprint are evidence, so they are never
# rewritten even though they are text.
NEVER_REWRITE = {"assets/veilvoice-signing-key.asc", "assets/fingerprint.txt"}


def git(repo, *args, binary=False):
    out = subprocess.run(
        ["git", "-C", repo, *args],
        check=True,
        capture_output=True,
    ).stdout
    return out if binary else out.decode("utf-8").strip()


def latest_release(repo):
    """The newest tag that names a release, skipping prereleases like v1.0-rc1."""
    tags = git(repo, "tag", "--list", "v*", "--sort=-v:refname").splitlines()
    for tag in tags:
        if "-" not in tag:
            return tag
    sys.exit("error: the veilvoice checkout has no release tags; fetch them with git fetch --tags")


def unpack(repo, ref, into):
    archive = git(repo, "archive", "--format=tar", ref, "website", binary=True)
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(into, filter="data")
    return os.path.join(into, "website")


def add_verification(html):
    """Put the tag in the head, straight after the viewport line."""
    if "google-site-verification" in html:
        return html
    marker = '<meta name="viewport"'
    at = html.find(marker)
    if at < 0:
        sys.exit("error: the home page has no viewport line to place the Search Console tag after")
    end = html.index(">", at) + 1
    note = (
        "\n<!-- Google Search Console reads this tag to confirm that tilas01"
        " controls this site.\n     It must stay on the home page for as long"
        " as the site is listed there. -->\n"
    )
    return html[:end] + note + VERIFICATION + html[end:]


def clean_sitemap(xml):
    """Drop the 404 page's entry: a sitemap lists pages meant to be found."""
    return "".join(line for line in xml.splitlines(keepends=True)
                   if not line.strip().endswith("/404.html</loc></url>"))


def rewrite(tree):
    """Point every old address at the new one. Returns how many were changed."""
    changed = 0
    for base, _dirs, files in os.walk(tree):
        for name in files:
            path = os.path.join(base, name)
            rel = os.path.relpath(path, tree).replace(os.sep, "/")
            if not name.endswith(TEXT) or rel in NEVER_REWRITE:
                continue
            with open(path, encoding="utf-8", newline="") as handle:
                text = handle.read()
            new, count = OLD.subn(_moved, text)
            if rel == "index.html":
                new = add_verification(new)
            if rel == "sitemap.xml":
                new = clean_sitemap(new)
            if new != text:
                with open(path, "w", encoding="utf-8", newline="") as handle:
                    handle.write(new)
                changed += count
    return changed


def same_tree(a, b):
    """True when the two folders hold the same files with the same bytes."""
    def listing(top):
        found = {}
        for base, _dirs, files in os.walk(top):
            for name in files:
                path = os.path.join(base, name)
                with open(path, "rb") as handle:
                    found[os.path.relpath(path, top)] = handle.read()
        return found
    return listing(a) == listing(b)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--from", dest="repo", required=True,
                        help="a checkout of tilas01/veilvoice with its tags")
    parser.add_argument("--ref", help="the release tag to copy (default: the latest)")
    parser.add_argument("--check", action="store_true",
                        help="fail if site/ differs from what this would write")
    args = parser.parse_args()

    repo = os.path.abspath(args.repo)
    ref = args.ref or latest_release(repo)

    with tempfile.TemporaryDirectory() as work:
        tree = unpack(repo, ref, work)
        changed = rewrite(tree)
        index = os.path.join(tree, "index.html")
        with open(index, encoding="utf-8") as handle:
            if VERIFICATION not in handle.read():
                sys.exit("error: the home page would be written without the Search Console tag")

        if args.check:
            if os.path.isdir(SITE) and same_tree(tree, SITE):
                print(f"site/ matches {ref}")
                return
            sys.exit(f"error: site/ does not match {ref}; run tools/import-site.py --from {args.repo} --ref {ref}")

        if os.path.isdir(SITE):
            shutil.rmtree(SITE)
        shutil.copytree(tree, SITE)

    print(f"site/ now holds the website from {ref} ({changed} links moved to the new address)")


if __name__ == "__main__":
    main()
