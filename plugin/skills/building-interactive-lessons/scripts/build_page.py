#!/usr/bin/env python3
"""Build the lesson page from the blueprint. Never hand-write or hand-edit the page.

Usage:
    python scripts/build_page.py lesson-blueprint.yaml [--out lesson.html] [--template assets/template.html]

What it does:
    1. Checks the blueprint (the same rules as check_blueprint.py, without running code) and stops on any error.
    2. Fills the template with the blueprint as data and writes the page.
    3. Copies the blueprint beside the page as lesson-blueprint.txt, for publishing.
    4. Compares with the page it replaces and writes changed.json: the chapters and pages whose content changed.
       scripts/screenshot_chapters.py reads that file, so a revise round only re-checks what changed.
"""

import argparse
import hashlib
import html
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_blueprint import check_blueprint, load_blueprint  # noqa: E402
from theme import adjustment_note, css_for  # noqa: E402

SKILL_FOLDER = Path(__file__).resolve().parent.parent
DEFAULT_TEMPLATE = SKILL_FOLDER / "assets" / "template.html"
DATA_PLACEHOLDER = "/*__LESSON_DATA__*/null"
TITLE_PLACEHOLDER = "__LESSON_TITLE__"
THEME_PLACEHOLDER = "/*__THEME_TOKENS__*/"
FONT_PLACEHOLDER = "__FONT_QUERY__"
SCENE_PLACEHOLDER = "<!--__SCENE_SCRIPTS__-->"
SCENES_START = "<!--SCENES_START-->"
SCENES_END = "<!--SCENES_END-->"
EMBEDDED_SCENES = re.compile(re.escape(SCENES_START) + r".*?" + re.escape(SCENES_END), re.S)
DATA_START = "/*LESSON_DATA_START*/"
DATA_END = "/*LESSON_DATA_END*/"
EMBEDDED_DATA = re.compile(re.escape(DATA_START) + r"(.*?)" + re.escape(DATA_END), re.S)


def lesson_json(blueprint):
    """The blueprint as JSON that is safe inside a <script> element."""
    text = json.dumps(blueprint, ensure_ascii=False, separators=(",", ":"), default=str)
    # "</" would close the script element early; U+2028 and U+2029 end a line in older JavaScript
    return text.replace("</", "<\\/").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")


# Motion libraries a scene may name (figure.library), pinned, loaded from jsDelivr only when a scene uses them
LIBRARY_SCRIPTS = {
    "anime": ["https://cdn.jsdelivr.net/npm/animejs@4.5.0/dist/bundles/anime.umd.min.js"],
    "gsap": ["https://cdn.jsdelivr.net/npm/gsap@3.15.1/dist/gsap.min.js",
             "https://cdn.jsdelivr.net/npm/gsap@3.15.1/dist/MotionPathPlugin.min.js",
             "https://cdn.jsdelivr.net/npm/gsap@3.15.1/dist/DrawSVGPlugin.min.js"],
}


def scene_scripts(blueprint):
    """One <script> element per scene, so a scene with a bug cannot stop the page or another scene.
    Each registers a function that the page calls with the scene's `scene` object (references/visual-design.md section 6)."""
    parts = []
    libraries = []
    for chapter in blueprint.get("chapters") or []:
        for block in chapter.get("blocks") or []:
            figure = block.get("figure") if block.get("type") == "diagram" else None
            if isinstance(figure, dict) and figure.get("kind") == "scene" and figure.get("library") in LIBRARY_SCRIPTS \
                    and figure["library"] not in libraries:
                libraries.append(figure["library"])
    for library in libraries:
        parts += [f'<script src="{url}"></script>' for url in LIBRARY_SCRIPTS[library]]
    for chapter in blueprint.get("chapters") or []:
        for block in chapter.get("blocks") or []:
            figure = block.get("figure") if block.get("type") == "diagram" else None
            if isinstance(figure, dict) and figure.get("kind") == "scene":
                key = json.dumps(block["id"])
                parts.append(f"<script>\n\"use strict\";\n(window.LESSON_SCENES = window.LESSON_SCENES || {{}})[{key}] = function (scene) {{\n"
                             f"{figure['script']}\n}};\n</script>")
    return SCENES_START + "\n".join(parts) + SCENES_END


def embedded_blueprint(page_path):
    """The blueprint data inside a page this script built earlier, or None."""
    if not page_path.exists():
        return None
    found = EMBEDDED_DATA.search(page_path.read_text(encoding="utf-8"))
    return json.loads(found.group(1)) if found else None


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, default=str)


def changed_views(old, new):
    """Which chapters and pages show something different in the new blueprint."""
    if old is None:
        return {"chapters": [chapter["id"] for chapter in new["chapters"]], "pages": ["start", "field-guide"], "first_build": True}
    old_chapters = {chapter.get("id"): chapter for chapter in old.get("chapters") or []}
    old_order = [chapter.get("id") for chapter in old.get("chapters") or []]
    new_chapters = new["chapters"]
    new_order = [chapter["id"] for chapter in new_chapters]
    changed = set()
    for position, chapter in enumerate(new_chapters):
        before = old_chapters.get(chapter["id"])
        # A chapter shows its number and its neighbours' titles, so a move or a renamed neighbour changes it too
        neighbours = lambda order, i: order[max(i - 1, 0):i + 2]
        moved = before is None or neighbours(old_order, old_order.index(chapter["id"])) != neighbours(new_order, position) \
            or old_order.index(chapter["id"]) != position
        renamed_next = position + 1 < len(new_chapters) and canonical((old_chapters.get(new_order[position + 1]) or {}).get("title")) != canonical(new_chapters[position + 1]["title"])
        if moved or renamed_next or canonical(before) != canonical(chapter):
            changed.add(chapter["id"])

    # Shared data shows inside chapters too
    old_misconceptions = {m.get("id"): m for m in old.get("misconceptions") or []}
    for misconception in new.get("misconceptions") or []:
        if canonical(old_misconceptions.get(misconception["id"])) != canonical(misconception):
            changed.update(c["id"] for c in new_chapters if misconception["id"] in (c.get("misconceptions") or []))
    if canonical(old.get("glossary")) != canonical(new.get("glossary")):
        changed.update(c["id"] for c in new_chapters)
    diagrams_changed = {block["id"] for c in new_chapters if c["id"] in changed for block in c["blocks"] if block.get("type") == "diagram"}
    for chapter in new_chapters:  # a later diagram stage redraws the stages it extends
        if any((block.get("extends") or {}).get("diagram") in diagrams_changed for block in chapter["blocks"]):
            changed.add(chapter["id"])

    pages = []
    chapter_list_changed = [(c.get("id"), c.get("title"), c.get("minutes"), c.get("source_section"), c.get("why_it_matters")) for c in old.get("chapters") or []] != \
        [(c.get("id"), c.get("title"), c.get("minutes"), c.get("source_section"), c.get("why_it_matters")) for c in new_chapters]
    if chapter_list_changed or canonical(old.get("lesson")) != canonical(new.get("lesson")):
        pages.append("start")
    if canonical(field_guide_content(old)) != canonical(field_guide_content(new)):
        pages.append("field-guide")
    return {"chapters": [c["id"] for c in new_chapters if c["id"] in changed], "pages": pages, "first_build": False}


def field_guide_content(blueprint):
    """What the field guide page shows: recaps, exercises, local runs, glossary, facts, the last bridge."""
    shown = []
    for chapter in blueprint.get("chapters") or []:
        for block in chapter.get("blocks") or []:
            if block.get("type") in ("recap", "fill_blanks", "explain", "predict", "check"):
                shown.append([block.get("id"), block.get("text"), (block.get("instructions") or [None])[0], block.get("question")])
            run_locally = (block.get("slice") or {}).get("run_locally") or block.get("run_locally")
            if run_locally:
                shown.append(run_locally)
        shown.append([chapter.get("id"), chapter.get("title")])
    last_bridge = ((blueprint.get("chapters") or [{}])[-1].get("bridge_out") or {}).get("text")
    return [shown, last_bridge, blueprint.get("glossary"), blueprint.get("facts")]


def main():
    parser = argparse.ArgumentParser(description="Build the lesson page from the blueprint.")
    parser.add_argument("blueprint", help="path to lesson-blueprint.yaml")
    parser.add_argument("--out", default="lesson.html", help="page to write (default: lesson.html)")
    parser.add_argument("--template", default=str(DEFAULT_TEMPLATE), help="page template (default: the skill's assets/template.html)")
    arguments = parser.parse_args()

    blueprint_path = Path(arguments.blueprint)
    page_path = Path(arguments.out)
    blueprint = load_blueprint(blueprint_path)
    problems = check_blueprint(blueprint)
    if problems.errors:
        for error in problems.errors:
            print(f"ERROR    {error}")
        print(f"\nNot built: {len(problems.errors)} errors. Fix the blueprint, then run check_blueprint.py --run-tests.")
        sys.exit(1)

    template = Path(arguments.template).read_text(encoding="utf-8")
    for placeholder in [DATA_PLACEHOLDER, TITLE_PLACEHOLDER, THEME_PLACEHOLDER, FONT_PLACEHOLDER, SCENE_PLACEHOLDER]:
        if template.count(placeholder) != 1:
            sys.exit(f"The template must contain {placeholder} exactly once.")

    theme_css, font_query = css_for(blueprint.get("theme"))
    page = template.replace(TITLE_PLACEHOLDER, html.escape(blueprint["lesson"]["title"]))
    page = page.replace(THEME_PLACEHOLDER, theme_css).replace(FONT_PLACEHOLDER, font_query)
    page = page.replace(SCENE_PLACEHOLDER, scene_scripts(blueprint))
    page = page.replace(DATA_PLACEHOLDER, DATA_START + lesson_json(blueprint) + DATA_END)
    old_page = page_path.read_text(encoding="utf-8") if page_path.exists() else None
    # Scene scripts are lesson content, like the data: a changed scene changes only its chapter
    without_data = lambda text: EMBEDDED_SCENES.sub("", EMBEDDED_DATA.sub("", text))
    if old_page is not None and without_data(old_page) != without_data(page):
        # The template itself changed, so every view may look different
        changes = changed_views(None, json.loads(canonical(blueprint)))
        changes["first_build"] = False
        changes["template_changed"] = True
    else:
        changes = changed_views(embedded_blueprint(page_path), json.loads(canonical(blueprint)))
    page_path.parent.mkdir(parents=True, exist_ok=True)
    page_path.write_text(page, encoding="utf-8")
    shutil.copyfile(blueprint_path, page_path.with_name("lesson-blueprint.txt"))
    changed_path = page_path.with_name("changed.json")
    changes["page_sha256"] = hashlib.sha256(page.encode("utf-8")).hexdigest()
    changed_path.write_text(json.dumps(changes, indent=2) + "\n", encoding="utf-8")

    print(f"Built {page_path} ({len(page) // 1024} KB) and {page_path.with_name('lesson-blueprint.txt')}.")
    if blueprint.get("theme"):
        print(f"Theme '{blueprint['theme'].get('name', 'unnamed')}': {adjustment_note(blueprint['theme'])}.")
    if changes["first_build"]:
        print("First build: every chapter is new.")
    elif changes.get("template_changed"):
        print("The template changed since the last build: every chapter and page is listed as changed.")
    elif not changes["chapters"] and not changes["pages"]:
        print("Nothing changed since the last build.")
    else:
        print(f"Changed chapters: {', '.join(changes['chapters']) or 'none'}")
        print(f"Changed pages: {', '.join(changes['pages']) or 'none'}")
    print(f"Wrote {changed_path}.")


if __name__ == "__main__":
    main()
