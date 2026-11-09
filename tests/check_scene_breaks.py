"""Break the example scene one way at a time, and check that check_scenes.py catches each break.

Run from the repo root: python3 tests/check_scene_breaks.py
Needs Playwright with Chromium. Each break is built into a temporary page; the script exits with an error if any is missed.
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

K = Path(__file__).resolve().parent.parent / "plugin" / "skills" / "building-interactive-lessons"
here = Path(tempfile.mkdtemp())
example = (K / "assets/example-concepts-blueprint.yaml").read_text()
SHOW = "            scene.show = (step, from, settings) => {\n"
missed = []
ONLY = os.environ.get("ONLY")   # ONLY=<case name> runs one case


def case(name, old, new, expect):
    """Replace old with new (found exactly once), build the page, run check_scenes.py, and look for the expected problem."""
    if ONLY and ONLY != name:
        return
    assert example.count(old) == 1, f"{name}: text to break not found once"
    folder = here / name
    folder.mkdir()
    (folder / "lesson-blueprint.yaml").write_text(example.replace(old, new))
    subprocess.run([sys.executable, str(K / "scripts/build_page.py"), str(folder / "lesson-blueprint.yaml"), "--out", str(folder / "lesson.html")],
                   check=True, capture_output=True)
    output = subprocess.run([sys.executable, str(K / "scripts/check_scenes.py"), str(folder / "lesson.html"), "--out", str(folder / "shots")],
                            capture_output=True, text=True).stdout
    problems = [line for line in output.splitlines() if line.startswith("PROBLEM")]
    caught = any(expect in line for line in problems)
    print(f"{'CAUGHT ' if caught else 'MISSED '} {name}: {len(problems)} problems")
    if not caught:
        missed.append(name)
    for line in problems[:2]:
        print("        ", line[:180])


case("typed-number", SHOW, '            scene.add("text", { x: 200, y: 20, class: "svg-text small" }, "73%");\n' + SHOW,
     expect="which is not in its data")
case("drawn-outside", SHOW, '            scene.add("rect", { x: 330, y: 20, width: 40, height: 10, class: "svg-box" });\n' + SHOW,
     expect="drawn outside the box")
case("step-changes-nothing", "scene.move(mark, { x1: at, x2: at, opacity: step >= 2 ? 1 : 0 });",
     "scene.move(mark, { x1: at, x2: at, opacity: step >= 1 ? 1 : 0 });", expect="looks the same as step")
case("motion-lands-elsewhere", SHOW,
     '            requestAnimationFrame(() => dot.setAttribute("r", matchMedia("(prefers-reduced-motion: reduce)").matches ? 6 : 9));\n' + SHOW,
     expect="different picture with motion than without")
case("script-throws", SHOW, '            throw new Error("a bug in the scene");\n' + SHOW, expect="could not draw")
case("run-says-nothing", "              return words.map((word, i) => `${word} ${counts[i]}`).join(\" · \") + ` (of ${trials} draws)`;",
     "              return \"\";", expect="gives no summary line")

if missed:
    sys.exit(f"Missed {len(missed)} scene breaks: {', '.join(missed)}")
print("Every scene break was caught.")
