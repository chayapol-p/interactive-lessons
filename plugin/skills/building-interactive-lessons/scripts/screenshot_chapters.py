#!/usr/bin/env python3
"""Screenshot the changed chapters at phone width, in light and dark themes.

Usage:
    pip install playwright   (or use a Playwright that is already installed)
    python scripts/screenshot_chapters.py lesson.html [--chapters id ...] [--all] [--out shots]

By default it reads changed.json, which build_page.py writes beside the page, and shoots only the
chapters and pages listed there. Each view is shot twice (light, dark) at 390 px wide, full page,
with read-along on so every solution and output is open. It also reports any sideways scroll and any
error the page logged, so the agent looks at the images only for what a script cannot judge.
"""

import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

PHONE_WIDTH = 390
PHONE_HEIGHT = 844


def serve_libraries_from(context, folder):
    """Answer the page's jsDelivr requests from a local folder (npm package folders such as animejs/ and gsap/), for
    machines that cannot reach the CDN. https://cdn.jsdelivr.net/npm/gsap@3.15.1/dist/gsap.min.js -> folder/gsap/dist/gsap.min.js"""
    root = Path(folder).resolve()

    def answer(route):
        path = route.request.url.split("/npm/", 1)[-1]
        package, _, rest = path.partition("/")
        local = root / re.sub(r"@[^/]+$", "", package) / rest
        if local.is_file():
            route.fulfill(path=str(local), content_type="application/javascript")
        else:
            route.abort()
    context.route("https://cdn.jsdelivr.net/npm/**", answer)


def find_browser():
    """Playwright's own Chromium if installed, else a system Chrome."""
    for name in ["google-chrome", "chromium", "chromium-browser"]:
        found = shutil.which(name)
        if found:
            return found
    return None


def main():
    parser = argparse.ArgumentParser(description="Screenshot changed chapters at phone width, light and dark.")
    parser.add_argument("page", help="the built lesson.html")
    parser.add_argument("--chapters", nargs="+", metavar="ID", help="shoot these chapters instead of changed.json")
    parser.add_argument("--all", action="store_true", help="shoot every chapter and page")
    parser.add_argument("--libraries", metavar="FOLDER", help="serve motion libraries from this folder instead of jsDelivr (for machines without the CDN)")
    parser.add_argument("--out", default="shots", help="folder for the images (default: shots)")
    arguments = parser.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("screenshot_chapters.py needs Playwright: pip install playwright")

    page_path = Path(arguments.page).resolve()
    changed_path = page_path.with_name("changed.json")
    if arguments.chapters:
        views = list(arguments.chapters)
    elif arguments.all or not changed_path.exists():
        views = None  # every view, read from the page below
    else:
        changes = json.loads(changed_path.read_text(encoding="utf-8"))
        if changes.get("page_sha256") != hashlib.sha256(page_path.read_bytes()).hexdigest():
            sys.exit("changed.json belongs to another build of the page (did the last build fail?). "
                     "Rebuild with build_page.py, or pass --chapters or --all.")
        views = changes["chapters"] + changes["pages"]
        if not views:
            print("changed.json lists nothing to shoot. Use --all to shoot every view.")
            return

    out_folder = Path(arguments.out)
    out_folder.mkdir(parents=True, exist_ok=True)
    problems = []
    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(args=["--no-sandbox"])
        except Exception:
            browser = playwright.chromium.launch(executable_path=find_browser(), args=["--no-sandbox"])
        for theme in ["light", "dark"]:
            context = browser.new_context(viewport={"width": PHONE_WIDTH, "height": PHONE_HEIGHT}, color_scheme=theme, device_scale_factor=2)
            if arguments.libraries:
                serve_libraries_from(context, arguments.libraries)
            tab = context.new_page()
            logged = []
            tab.on("pageerror", lambda error, logged=logged: logged.append(str(error)))
            tab.on("console", lambda message, logged=logged: logged.append(message.text) if message.type == "error" else None)
            # ?read-along=on opens every solution and recorded output for the shot
            tab.goto(page_path.as_uri() + "?read-along=on")
            every_view = tab.evaluate("() => [...LESSON.chapters.map(c => c.id), 'start', 'field-guide']")
            for view in views or every_view:
                if view not in every_view:
                    problems.append(f"{view}: no such chapter or page")
                    continue
                tab.goto(page_path.as_uri() + "?read-along=on#" + view)
                tab.wait_for_timeout(300)
                image_path = out_folder / f"{view}-{theme}.png"
                tab.screenshot(path=str(image_path), full_page=True)
                sideways = tab.evaluate("() => document.documentElement.scrollWidth - document.documentElement.clientWidth")
                if sideways > 0:
                    problems.append(f"{view} ({theme}): the page scrolls sideways by {sideways} px")
                print(f"SHOT     {image_path}")
            for message in logged:
                if message.startswith("Failed to load resource"):
                    # Web fonts blocked by this machine's network: the page falls back to system fonts
                    print(f"NOTE     ({theme}) {message} (fonts fall back to system fonts)")
                else:
                    problems.append(f"page error ({theme}): {message}")
            context.close()
        browser.close()

    for problem in problems:
        print(f"PROBLEM  {problem}")
    print(f"\n{len(problems)} problems. Look at each image for what a script cannot judge: layout, contrast, a diagram that reads well.")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
