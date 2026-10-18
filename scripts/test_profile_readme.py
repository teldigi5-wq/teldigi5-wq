"""Regression checks for the public GitHub profile README and its local visual assets.

Only Python's standard library is used; no access token or network calls required.
"""
from pathlib import Path
import re
import unittest
from urllib.parse import urlparse
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
BRAND_ASSETS = ("assets/engineering-hero.svg", "assets/engineering-pulse.svg")
CHARTS = (
    "0-profile-details.svg",
    "1-repos-per-language.svg",
    "3-stats.svg",
)
RAW = "https://raw.githubusercontent.com/teldigi5-wq/teldigi5-wq/main/"


class ProfileReadmeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.readme = README.read_text(encoding="utf-8")

    def test_profile_is_a_profile_readme(self):
        self.assertIn("POOJANA", (ROOT / BRAND_ASSETS[0]).read_text(encoding="utf-8"))
        for token in (
            "SLIIT", "Open to", "Currently Building", "Engineering Evidence",
            "Technical Toolkit", "GitHub Activity",
            "https://poojana-portfolio.vercel.app/",
            "https://www.linkedin.com/in/poojana-kaveesh-3048b8387",
            "mailto:teldigi5@gmail.com",
        ):
            with self.subTest(token=token):
                self.assertIn(token, self.readme)

    def test_flagship_projects_remain_visible(self):
        start = self.readme.index("## 🔭 Currently Building")
        end = self.readme.index("### A closer look", start)
        shortlist = self.readme[start:end]
        for project in (
            "aetheris-platform", "sentinel-security-platform", "averis-ai",
            "finalforge", "floodguard-whatsapp-bot", "wayfarer-world-travel",
            "aetheris-ai-runtime",
        ):
            with self.subTest(project=project):
                self.assertIn("https://github.com/teldigi5-wq/" + project, shortlist)

    def test_presentation_does_not_claim_maturity_not_earned(self):
        self.assertIn("Pre-production", self.readme)
        self.assertIn("currently offline", self.readme)
        self.assertIn("not plagiarism", self.readme.lower())
        self.assertIn("Physical-machine validation remains pending", self.readme)
        self.assertIn("no confirmed booking inventory", self.readme)

    def test_animated_vector_banner_is_local_and_bounded(self):
        banner = ROOT / "assets/poojana-systems-3d-animated.svg"
        self.assertTrue(banner.is_file())
        self.assertLess(banner.stat().st_size, 18000)
        data = banner.read_text(encoding="utf-8")
        self.assertIn("@keyframes", data)
        self.assertNotIn("<script", data.lower())
        self.assertNotIn("<foreignObject", data)
        self.assertIn("prefers-reduced-motion", data)
        self.assertIn("assets/poojana-systems-3d-animated.svg?v=", self.readme)
        self.assertNotIn('src="' + RAW + 'assets/poojana-cinematic-hero.webp', self.readme)
        root = ET.fromstring(data)
        self.assertTrue(root.tag.endswith("svg"))

    def test_recent_toolkit_technologies_have_project_links(self):
        for skill in ("HMAC-SHA256", "SQLite", "Playwright", "GSAP / ScrollTrigger", "n8n"):
            self.assertIn(skill, self.readme)
        self.assertIn("Some integrations are experimental or disabled in production", self.readme)

    def test_svg_assets_parse_and_are_accessible(self):
        for name in BRAND_ASSETS:
            with self.subTest(asset=name):
                path = ROOT / name
                self.assertTrue(path.is_file())
                self.assertLess(path.stat().st_size, 16000)
                svg = ET.parse(path).getroot()
                self.assertTrue(svg.tag.endswith("svg"))
                ns = "{http://www.w3.org/2000/svg}"
                self.assertIsNotNone(svg.find(ns + "title"))
                self.assertIsNotNone(svg.find(ns + "desc"))

    def test_every_local_image_exists_and_has_alt(self):
        images = re.findall(r"<img\b[^>]*>", self.readme, flags=re.I)
        self.assertGreaterEqual(len(images), 7)
        for tag in images:
            with self.subTest(tag=tag[:100]):
                src = re.search(r'\bsrc="([^"]+)"', tag)
                alt = re.search(r'\balt="([^"]+)"', tag)
                self.assertIsNotNone(src)
                self.assertIsNotNone(alt)
                url = urlparse(src.group(1))
                self.assertEqual(url.scheme, "https")
                if src.group(1).startswith(RAW):
                    local_path = url.path.split("/main/", 1)[-1]
                    self.assertTrue((ROOT / local_path).is_file(), local_path)

    def test_original_skill_icons_and_focus_strip_are_restored(self):
        self.assertNotIn("assets/technical-toolkit.svg", self.readme)
        self.assertIn("Original animated engineering practice strip", self.readme)
        self.assertIn("## 🧰 Technical Toolkit", self.readme)
        self.assertIn("Technologies shown are tools used, studied or integrated in identifiable projects", self.readme)
        icon_groups = (
            "java,spring,python,fastapi,postgres,redis,rabbitmq,docker,kubernetes,linux",
            "nextjs,react,ts,js,nodejs,electron,flutter,dart,html,css",
            "aws,firebase,supabase,git,github,arduino,vite",
        )
        for icons in icon_groups:
            with self.subTest(icons=icons):
                self.assertIn("https://skillicons.dev/icons?i=" + icons, self.readme)
        strip = (ROOT / "assets/engineering-pulse.svg").read_text(encoding="utf-8")
        for area in ("BACKEND", "DISTRIBUTED", "CLOUD", "OBSERVABILITY", "IOT", "AI DIRECTION"):
            with self.subTest(area=area):
                self.assertIn(area, strip)
        for anchor in (
            "#-currently-building", "#-engineering-evidence",
            "#-technical-toolkit", "#-github-activity",
        ):
            with self.subTest(anchor=anchor):
                self.assertIn('href="' + anchor + '"', self.readme)

    def test_generated_chart_urls_are_cache_versioned(self):
        for name in CHARTS:
            pattern = re.compile(
                re.escape(RAW + "profile-summary-card-output/github_dark/" + name)
                + r"\?v=[a-zA-Z0-9]{8,16}"
            )
            with self.subTest(chart=name):
                self.assertEqual(len(pattern.findall(self.readme)), 1)
        self.assertIn("actions/workflows/profile-activity.yml", self.readme)

    def test_no_obvious_placeholder_links(self):
        self.assertNotIn("]()", self.readme)
        self.assertNotIn('href="#"', self.readme)
        self.assertNotIn("TODO: ADD", self.readme)
        self.assertLess(len(self.readme.encode("utf-8")), 24000)


if __name__ == "__main__":
    unittest.main()
