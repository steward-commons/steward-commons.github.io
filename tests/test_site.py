"""Checks for the Steward Commons front-porch homepage."""

from __future__ import annotations

import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
STYLE = ROOT / "style.css"
PUBLIC = ROOT.parent
COMMONS = PUBLIC.parent

EXPECTED_REPOS = [
    "card-deck",
    "injection-scanner",
    "house-defense",
    "the-range",
    "medical",
    "hang-up",
    "pixel-pet",
    "tongue",
    "pride",
    "proving-ground",
    "debate-loops",
    "gemini-consultant",
    "voice-box",
    "visitor-guide",
    "clubhouse",
]

VOID = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}

GITHUB_REPO = re.compile(
    r"https://github.com/steward-commons/([A-Za-z0-9._-]+)",
    re.IGNORECASE,
)


def staged_dir(name: str) -> Path | None:
    if name == "injection-scanner":
        path = COMMONS / name
        return path if path.is_dir() else None
    path = PUBLIC / name
    if path.is_dir() and path.resolve() != ROOT.resolve():
        return path
    return None


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.errors: list[str] = []
        self.tags: list[str] = []
        self.ids: set[str] = set()
        self.hrefs: list[str] = []
        self.src: list[str] = []
        self.img_missing_alt = 0
        self.lang = ""
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append(tag)
        ad = {k: v or "" for k, v in attrs}
        if tag == "html":
            self.lang = ad.get("lang", "")
        if "id" in ad:
            self.ids.add(ad["id"])
        if "href" in ad:
            self.hrefs.append(ad["href"])
        if "src" in ad:
            self.src.append(ad["src"])
        if tag == "img" and "alt" not in ad:
            self.img_missing_alt += 1
        if tag == "title":
            self._in_title = True
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag: str) -> None:
        if tag in VOID:
            return
        if self._in_title and tag == "title":
            self._in_title = False
        if not self.stack:
            self.errors.append(f"unexpected closing </{tag}>")
            return
        if tag not in self.stack:
            self.errors.append(f"closing </{tag}> with no open tag")
            return
        while self.stack:
            opened = self.stack.pop()
            if opened == tag:
                break
            if opened not in {"p", "li", "dt", "dd"}:
                self.errors.append(f"expected </{opened}> before </{tag}>")
                break

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data

    def close(self) -> None:
        super().close()
        if self.stack:
            self.errors.append("unclosed tags: " + ", ".join(self.stack))


def forbidden_needles() -> list[str]:
    return [
        "work" + "space",
        "/" + "home",
        "Kay" + "lea",
        "Toms" + "ello",
        "Ru" + "gen",
        "Rapun" + "zel",
        "Her" + "ington",
        "pass" + "word",
        "key" + "=",
        "arm" + "ory",
        "qu" + "al",
        "39" + "/40",
        "40" + "/40",
    ]


def iter_text_files(folder: Path):
    skip_names = {".git"}
    for path in folder.rglob("*"):
        if not path.is_file():
            continue
        if any(part in skip_names or part == "__pycache__" for part in path.parts):
            continue
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".woff", ".woff2"}:
            continue
        yield path


def same(a, b) -> bool:
    return a == b


class TestHomepage(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = INDEX.read_text(encoding="utf-8")
        cls.parser = PageParser()
        cls.parser.feed(cls.html)
        cls.parser.close()

    def test_required_files_exist(self) -> None:
        self.assertTrue(INDEX.is_file(), "index.html is missing")
        self.assertTrue(STYLE.is_file(), "style.css is missing")
        self.assertTrue((ROOT / "LICENSE").is_file(), "LICENSE is missing")
        self.assertTrue((ROOT / "README.md").is_file(), "README.md is missing")
        self.assertTrue((ROOT / "llms.txt").is_file(), "llms.txt is missing")

    def test_html_parses(self) -> None:
        self.assertFalse(self.parser.errors, self.parser.errors)
        self.assertIn("html", self.parser.tags)
        self.assertIn("head", self.parser.tags)
        self.assertIn("body", self.parser.tags)
        self.assertIn("main", self.parser.tags)
        self.assertIn("header", self.parser.tags)
        self.assertIn("footer", self.parser.tags)
        self.assertTrue(same(self.parser.tags.count("h1"), 1), "need exactly one h1")
        self.assertTrue(same(self.parser.lang, "en"), "html lang should be en")
        self.assertTrue(self.parser.title.strip())
        self.assertIn("main", self.parser.ids)
        self.assertTrue(same(self.parser.img_missing_alt, 0), "img tags need alt text")

    def test_stylesheet_and_icon_resolve(self) -> None:
        local = [
            h for h in self.parser.hrefs
            if "://" not in h and not h.startswith("#") and not h.startswith("mailto:")
        ]
        root_resolved = str(ROOT.resolve())
        for href in local:
            target = (ROOT / href).resolve()
            self.assertTrue(
                str(target).startswith(root_resolved),
                f"path leaves the site: {href}",
            )
            self.assertTrue(target.is_file(), f"missing linked file: {href}")
        self.assertTrue(STYLE.is_file())

    def test_repo_links_match_staged_folders(self) -> None:
        llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
        names = GITHUB_REPO.findall(self.html) + GITHUB_REPO.findall(llms)
        self.assertTrue(names, "no GitHub repo links found")
        unknown = []
        for name in names:
            if name == "steward-commons":
                # The organization itself, not a tool repo.
                continue
            if staged_dir(name) is None:
                unknown.append(name)
        self.assertFalse(unknown, f"link does not match a staged repo folder: {unknown}")

    def test_expected_tools_are_linked(self) -> None:
        names = set(GITHUB_REPO.findall(self.html))
        missing = [name for name in EXPECTED_REPOS if name not in names]
        self.assertFalse(missing, f"tool shed is missing: {missing}")

    def test_scrub_is_clean(self) -> None:
        needles = forbidden_needles()
        hits = []
        for path in iter_text_files(ROOT):
            text = path.read_text(encoding="utf-8", errors="replace")
            lowered = text.lower()
            for needle in needles:
                if needle.lower() in lowered:
                    hits.append(f"{path.relative_to(ROOT)}: {needle}")
        self.assertFalse(hits, "scrub found banned text:\n" + "\n".join(hits))

    def test_no_outside_assets(self) -> None:
        banned_hosts = ("fonts.google", "cdn.", "googletag", "analytics", "facebook.net")
        blob = self.html.lower() + "\n" + STYLE.read_text(encoding="utf-8").lower()
        for host in banned_hosts:
            self.assertNotIn(host, blob, f"outside asset host present: {host}")
        self.assertIn("href=\"style.css\"", self.html)

    def test_llms_txt_covers_the_tools(self) -> None:
        llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
        names = set(GITHUB_REPO.findall(llms))
        missing = [name for name in EXPECTED_REPOS if name not in names]
        self.assertFalse(missing, f"llms.txt is missing: {missing}")
        self.assertIn("llms.txt", self.parser.hrefs)

    def test_section_order(self) -> None:
        labels = re.findall(
            r'<h3 class="group-label"[^>]*>([^<]+)</h3>',
            self.html,
        )
        wanted = [
            "Start here",
            "The Clubhouse",
            "Helpers",
            "Growing up",
            "Defense",
        ]
        self.assertTrue(same(labels, wanted), f"section order was {labels}")
        # Card Deck, then Clubhouse, then remaining helpers, then growing up, then defense.
        shed_start = self.html.find('id="shed-heading"')
        shed = self.html[shed_start:]
        first = {}
        for i, name in enumerate(GITHUB_REPO.findall(shed)):
            first.setdefault(name, i)
        self.assertTrue(first["card-deck"] < first["clubhouse"])
        self.assertTrue(first["clubhouse"] < first["gemini-consultant"])
        self.assertTrue(first["visitor-guide"] < first["pixel-pet"])
        self.assertTrue(first["debate-loops"] < first["injection-scanner"])

    def test_defense_note_anchor(self) -> None:
        self.assertIn("defense", self.parser.ids)
        self.assertIn("#defense", self.parser.hrefs)
        # The note itself should be visible in the tool shed, not hidden.
        self.assertIn("Looking for security tools?", self.html)
        self.assertNotIn("visually-hidden", self.html[self.html.find("Looking for security tools?"):self.html.find("Looking for security tools?") + 200])



if __name__ == "__main__":
    unittest.main()
