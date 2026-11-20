# SPDX-License-Identifier: GPL-3.0-or-later
"""Checks for the site and the tools that build and serve it.

    python3 -m unittest discover -s tests

Standard library only, so they run anywhere Python 3.12 or later does.
"""

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# The exact tag Google Search Console verified. It must never leave the home
# page, so this checks the whole tag rather than only its name.
VERIFICATION = (
    '<meta name="google-site-verification" '
    'content="PrXwNiHGNWIM2txx_q0gUkifC33DUK5qk3cMkXYangc" />'
)


def load(relative, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


importer = load("tools/import-site.py", "import_site")
serve = load("hosting/local/serve.py", "serve")


class SearchConsoleTag(unittest.TestCase):
    def test_the_home_page_carries_the_tag(self):
        html = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
        head = html.split("</head>", 1)[0]
        self.assertIn(VERIFICATION, head)

    def test_the_importer_writes_the_same_tag(self):
        self.assertEqual(importer.VERIFICATION, VERIFICATION)

    def test_the_tag_goes_in_after_the_viewport_line(self):
        page = '<head>\n<meta name="viewport" content="x">\n<title>t</title>\n</head>'
        out = importer.add_verification(page)
        self.assertLess(out.index("viewport"), out.index(VERIFICATION))
        self.assertLess(out.index(VERIFICATION), out.index("<title>"))

    def test_adding_it_twice_changes_nothing(self):
        page = importer.add_verification('<meta name="viewport" content="x">')
        self.assertEqual(importer.add_verification(page), page)


class Sitemap(unittest.TestCase):
    def test_the_not_found_page_is_left_out(self):
        xml = ("<urlset>\n  <url><loc>https://x/404.html</loc></url>\n"
               "  <url><loc>https://x/faq.html</loc></url>\n</urlset>\n")
        out = importer.clean_sitemap(xml)
        self.assertNotIn("404.html", out)
        self.assertIn("faq.html", out)

    def test_the_published_sitemap_lists_the_home_page_and_not_404(self):
        xml = (ROOT / "site" / "sitemap.xml").read_text(encoding="utf-8")
        self.assertIn("<loc>https://tilas01.github.io/veilvoice-website/</loc>", xml)
        self.assertNotIn("404.html", xml)

    def test_robots_names_the_sitemap(self):
        robots = (ROOT / "site" / "robots.txt").read_text(encoding="utf-8")
        self.assertIn("Sitemap: https://tilas01.github.io/veilvoice-website/sitemap.xml", robots)


class NewAddress(unittest.TestCase):
    def moved(self, text):
        return importer.OLD.sub(importer._moved, text)

    def test_links_move(self):
        self.assertEqual(
            self.moved('href="https://tilas01.github.io/veilvoice/faq.html"'),
            'href="https://tilas01.github.io/veilvoice-website/faq.html"',
        )

    def test_the_bare_address_moves(self):
        self.assertEqual(self.moved("https://tilas01.github.io/veilvoice"),
                         "https://tilas01.github.io/veilvoice-website")

    def test_link_text_without_a_scheme_moves(self):
        self.assertEqual(self.moved("[tilas01.github.io/veilvoice](x)"),
                         "[tilas01.github.io/veilvoice-website](x)")

    def test_the_new_address_is_left_alone(self):
        text = "https://tilas01.github.io/veilvoice-website/ and tilas01.github.io/veilvoice-website"
        self.assertEqual(self.moved(text), text)

    def test_the_source_repository_is_left_alone(self):
        text = "https://github.com/tilas01/veilvoice"
        self.assertEqual(self.moved(text), text)


class LocalServer(unittest.TestCase):
    def test_it_sends_the_real_servers_policy(self):
        names = {name.lower(): value for name, value in serve.security_headers()}
        self.assertIn("content-security-policy", names)
        self.assertIn("script-src 'self'", names["content-security-policy"])
        self.assertIn("frame-ancestors 'none'", names["content-security-policy"])
        self.assertIn("x-content-type-options", names)

    def test_it_drops_what_only_works_over_https(self):
        names = {name.lower(): value for name, value in serve.security_headers()}
        self.assertNotIn("strict-transport-security", names)
        self.assertNotIn("upgrade-insecure-requests", names["content-security-policy"])


if __name__ == "__main__":
    unittest.main()
