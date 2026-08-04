from __future__ import annotations

import importlib.util
import json
import os
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent
SPEC = importlib.util.spec_from_file_location("site_build", ROOT / "scripts/build.py")
assert SPEC and SPEC.loader
SITE_BUILD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SITE_BUILD)


class BuildTests(unittest.TestCase):
    def test_home_project_link_stays_on_current_origin(self) -> None:
        home = (REPO_ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn('href="/ai_free_quota/"', home)
        self.assertNotIn('href="https://yoyoworks.github.io/ai_free_quota/"', home)

    def test_dataset_is_valid(self) -> None:
        data = json.loads((ROOT / "data/ai-free-quotas.json").read_text(encoding="utf-8"))
        SITE_BUILD.validate(data)
        self.assertEqual(30, len(data["entries"]))

    def test_build_produces_complete_static_site(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "dist"
            SITE_BUILD.build(output)
            expected = {
                "index.html",
                "zh/index.html",
                "us/index.html",
                "assets/site.css",
                "data/ai-free-quotas.json",
                "robots.txt",
                "sitemap.xml",
                "llms.txt",
            }
            self.assertEqual(expected, {str(path.relative_to(output)) for path in output.rglob("*") if path.is_file()})
            zh = (output / "zh/index.html").read_text(encoding="utf-8")
            en = (output / "us/index.html").read_text(encoding="utf-8")
            root = (output / "index.html").read_text(encoding="utf-8")
            self.assertNotIn("{{", root + zh + en)
            self.assertIn("application/ld+json", zh)
            self.assertIn('rel="noopener noreferrer sponsored"', zh)
            self.assertNotIn("智谱 BigModel", en)
            self.assertIn("navigator.languages", root)
            self.assertIn('localStorage.getItem("ai-free-quota-language")', root)
            self.assertIn('data-language-panel="zh"', root)
            self.assertIn('data-language-panel="en"', root)
            self.assertNotIn("Choose a language", root)
            self.assertIn('href="/assets/theme.css"', root)
            self.assertIn('src="/assets/site.js"', root)
            self.assertIn('class="site-nav"', root)
            self.assertIn('class="brand"', zh)
            ids = re.findall(r'\sid="([^"]+)"', root)
            self.assertEqual(len(ids), len(set(ids)))

    def test_shared_theme_contract(self) -> None:
        theme = (REPO_ROOT / "assets/theme.css").read_text(encoding="utf-8")
        expected = {
            "--yw-paper": "#f8f6f1",
            "--yw-surface": "#fcfbf7",
            "--yw-surface-glass": "rgba(252, 251, 247, 0.88)",
            "--yw-ink": "#18243b",
            "--yw-muted": "#6c7380",
            "--yw-navy": "#243b68",
            "--yw-blue": "#416b96",
            "--yw-teal": "#438f8c",
            "--yw-coral": "#d86c48",
            "--yw-gold": "#ddb24c",
        }
        for name, value in expected.items():
            self.assertIn(f"{name}: {value};", theme)

    def test_shared_control_contract(self) -> None:
        theme = (REPO_ROOT / "assets/theme.css").read_text(encoding="utf-8")
        master = (REPO_ROOT / "design-system/MASTER.md").read_text(encoding="utf-8")
        skill = (REPO_ROOT / ".agents/skills/yoyoworks-ui/SKILL.md").read_text(encoding="utf-8")
        row = (ROOT / "src/templates/row.html").read_text(encoding="utf-8")
        panel = (ROOT / "src/templates/panel.html").read_text(encoding="utf-8")
        build_script = (ROOT / "scripts/build.py").read_text(encoding="utf-8")

        for selector in (
            ".yw-button",
            ".yw-button--secondary",
            ".yw-language-switch",
            ".yw-text-link",
            ".yw-disclosure",
        ):
            self.assertIn(selector, theme)

        self.assertIn("assets/theme.css", master)
        self.assertIn("design-system/MASTER.md", skill)
        self.assertIn("yw-button yw-button--secondary", row)
        self.assertIn("yw-text-link yw-text-link--external", row)
        self.assertIn("yw-disclosure quota-toggle", build_script)
        self.assertNotIn("quota-actions", panel)

    def test_mobile_layout_uses_cards_without_horizontal_table_width(self) -> None:
        css = (ROOT / "src/static/site.css").read_text(encoding="utf-8")
        self.assertIn("@media (max-width: 720px)", css)
        self.assertIn("content: attr(data-label)", css)
        self.assertIn("-webkit-line-clamp: var(--yw-directory-clamp-lines)", css)
        self.assertNotIn("min-width: 900px", css)

    def test_long_mobile_descriptions_have_localized_disclosure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "dist"
            SITE_BUILD.build(output)
            zh = (output / "zh/index.html").read_text(encoding="utf-8")
            en = (output / "us/index.html").read_text(encoding="utf-8")

            self.assertIn('data-expand-label="展开详情"', zh)
            self.assertIn('data-collapse-label="收起"', zh)
            self.assertIn('data-expand-label="Expand details"', en)
            self.assertIn('data-collapse-label="Collapse"', en)
            self.assertIn('type="button" hidden data-quota-toggle', zh)
            self.assertNotIn('data-label="免费额度说明"', zh)

    def test_mobile_disclosure_uses_rendered_overflow(self) -> None:
        site_script = (REPO_ROOT / "assets/site.js").read_text(encoding="utf-8")
        build_script = (ROOT / "scripts/build.py").read_text(encoding="utf-8")

        self.assertIn("details.scrollHeight <= details.clientHeight + 1", site_script)
        self.assertIn("getComputedStyle(details).webkitLineClamp", site_script)
        self.assertNotIn("len(quota)", build_script)

    def test_mirror_host_does_not_override_canonical_origin(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "dist"
            with patch.dict(os.environ, {"SITE_URL": "https://mirror.example/"}, clear=False):
                SITE_BUILD.build(output)
            zh = (output / "zh/index.html").read_text(encoding="utf-8")
            self.assertIn(
                '<link rel="canonical" href="https://yoyoworks.github.io/ai_free_quota/zh/">',
                zh,
            )
            self.assertNotIn("https://mirror.example/", zh)


if __name__ == "__main__":
    unittest.main()
