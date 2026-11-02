"""Controlla che ogni testo dell'interfaccia sia tradotto in tutte le lingue, con gli stessi segnaposto.

Esecuzione:  .venv\\Scripts\\python -m unittest discover -s tests -v
Elenco delle frasi:  .venv\\Scripts\\python tests\\test_i18n.py
"""

import ast
import string
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from gtd.locales import en, es, fr  # noqa: E402

CATALOGS = {"en": en.STRINGS, "fr": fr.STRINGS, "es": es.STRINGS}


def _is_status_call(func: ast.expr) -> bool:
    """login_page.info("…") / .error("…"): ricevono il testo italiano e lo traducono loro."""
    if not (isinstance(func, ast.Attribute) and func.attr in ("info", "error")):
        return False
    target = func.value
    return (isinstance(target, ast.Name) and target.id == "self") or \
           (isinstance(target, ast.Attribute) and target.attr == "login_page")


def source_strings() -> set[str]:
    found: set[str] = set()
    for path in (ROOT / "gtd").rglob("*.py"):
        if "locales" in path.parts:
            continue
        tree = ast.parse(path.read_text("utf-8"))
        status_file = path.name in ("login_page.py", "main_window.py")
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not node.args:
                continue
            func = node.func
            name = func.id if isinstance(func, ast.Name) else None
            attr = func.attr if isinstance(func, ast.Attribute) else None
            # DownloadPage._t(setter, "testo") e DownloadPage._label("testo") registrano scritte statiche
            arg = node.args[1] if attr == "_t" and len(node.args) > 1 else node.args[0]
            if not (isinstance(arg, ast.Constant) and isinstance(arg.value, str)):
                continue
            if name in ("tr", "N_") or attr in ("_t", "_label") or (status_file and _is_status_call(func)):
                found.add(arg.value)
    return found


def placeholders(text: str) -> set[str]:
    return {field for _, field, _, _ in string.Formatter().parse(text) if field}


class TranslationsTest(unittest.TestCase):
    def test_every_string_is_translated(self):
        keys = source_strings()
        self.assertGreater(len(keys), 100)
        for code, catalog in CATALOGS.items():
            missing = sorted(keys - catalog.keys())
            self.assertEqual(missing, [], f"{code}: mancano {len(missing)} traduzioni")

    def test_no_leftover_translations(self):
        keys = source_strings()
        for code, catalog in CATALOGS.items():
            unused = sorted(catalog.keys() - keys)
            self.assertEqual(unused, [], f"{code}: traduzioni di testi che non esistono più")

    def test_placeholders_match(self):
        for code, catalog in CATALOGS.items():
            for key, value in catalog.items():
                self.assertEqual(placeholders(key), placeholders(value), f"{code}: {key!r}")

    def test_html_tags_preserved(self):
        for code, catalog in CATALOGS.items():
            for key, value in catalog.items():
                for tag in ("<b>", "<br>", "<a ", "<i>"):
                    self.assertEqual(key.count(tag), value.count(tag), f"{code} {tag}: {key!r}")


if __name__ == "__main__":
    for text in sorted(source_strings()):
        print(repr(text))
