"""Rebuild the README's lesson screenshot from a real build of the no-code Monty Hall example.

Usage (from the repo root):
    pip install pyyaml playwright
    python3 docs/diagram/capture_lesson_shot.py

It builds the Stay or Switch? example (the Monty Hall problem) with the skill's own scripts, opens chapter 1 at phone width,
picks a wrong option in the fill-the-blank exercise, presses See result and Check, and saves the
After bars as docs/images/lesson-bars(-dark).png, and the passage, its result and its reason as docs/images/lesson-shot.png (light) and docs/images/lesson-shot-dark.png (dark).
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL = Path(os.environ.get("SKILL_FOLDER", REPO / "skills" / "building-interactive-lessons"))
IMAGES = REPO / "docs" / "images"

# Build the example lesson with the skill's own build script
work_folder = Path(tempfile.mkdtemp())
page = work_folder / "lesson.html"
subprocess.run([sys.executable, str(SKILL / "scripts" / "build_page.py"), str(SKILL / "assets" / "example-monty-blueprint.yaml"),
                "--out", str(page)], check=True, capture_output=True)

from playwright.sync_api import sync_playwright  # noqa: E402

# Show the After bars, then pick the wrong option "1 in 2", then See result and Check, in each theme
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(args=["--no-sandbox"])
    for theme, file_name in [("light", "lesson-shot.png"), ("dark", "lesson-shot-dark.png")]:
        tab = browser.new_page(viewport={"width": 390, "height": 844}, color_scheme=theme, device_scale_factor=2)
        tab.goto(page.as_uri() + "#where-the-chance-goes")
        tab.locator("#before-after").get_by_role("button", name="After").click()  # the bars after the host opens door 3
        exercise = tab.locator("#after-chance")
        exercise.locator(".blank").first.click()
        exercise.locator(".chip").filter(has_text="1 in 2").click()
        exercise.get_by_role("button", name="See result").click()
        exercise.get_by_role("button", name="Check").click()
        tab.add_style_tag(content=".topbar { display: none !important; }")  # the sticky bar would cover the top
        # Two shots, shown side by side in the README: the After bars, then the wrong pick with its result and reason
        def page_box(selector_top, selector_bottom):
            return tab.evaluate("""([top, bottom]) => {
                const a = document.querySelector(top).getBoundingClientRect(), b = document.querySelector(bottom).getBoundingClientRect();
                return {x: Math.max(a.x - 12, 0), y: a.y - 12 + window.scrollY, width: Math.min(a.width + 24, 390), height: b.bottom - a.y + 24};
            }""", [selector_top, selector_bottom])
        bars_name = file_name.replace("lesson-shot", "lesson-bars")
        tab.screenshot(path=str(IMAGES / bars_name), full_page=True, clip=page_box("#before-after .switch", "#before-after figcaption"))
        tab.screenshot(path=str(IMAGES / file_name), full_page=True, clip=page_box("#after-chance .code-panel", "#after-chance .feedback.wrong"))
        print(f"Saved {IMAGES / bars_name}")
        print(f"Saved {IMAGES / file_name}")
    browser.close()
