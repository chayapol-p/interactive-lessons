"""Break the example blueprints one way at a time, and check that the checker catches each break.

Run from the repo root: python3 tests/check_catches_breaks.py
Each break is written to a temporary folder; the script exits with an error if any break is missed.
"""
import subprocess
import sys
from pathlib import Path

import tempfile

K = Path(__file__).resolve().parent.parent / "skills" / "building-interactive-lessons"
here = Path(tempfile.mkdtemp())
missed = []
example = (K / "assets/example-blueprint.yaml").read_text()


def case(name, old, new, run_tests=False, expect=""):
    assert example.count(old) == 1, f"{name}: text to break not found once"
    path = here / f"{name}.yaml"
    path.write_text(example.replace(old, new))
    command = [sys.executable, str(K / "scripts/check_blueprint.py"), str(path)] + (["--run-tests"] if run_tests else [])
    output = subprocess.run(command, capture_output=True, text=True).stdout
    errors = [line for line in output.splitlines() if line.startswith("ERROR")]
    caught = any(expect in line for line in errors)
    print(f"{'CAUGHT ' if caught else 'MISSED '} {name}: {len(errors)} errors")
    if not caught:
        missed.append(name)
    for line in errors[:3]:
        print("        ", line[:190])


case("comma-split",
     "          - Fill the blank so each chunk shares 50 tokens with the one before it.",
     "          - Fill the blank, so each chunk shares 50 tokens: with the one before it.",
     expect="should be plain text")
case("typed-output",
     'output: "starts: [0, 50, 100]"', 'output: "starts: [0, 50, 150]"', run_tests=True, expect="recorded output is not what the code prints")
case("two-right-options",
     "                correct: false\n                why_wrong: That moves only 50 tokens",
     "                correct: true\n                why_wrong: That moves only 50 tokens", expect="exactly 1 is needed")
case("missing-output",
     '                output: "starts: [0, 550, 1100]"\n', "", expect="output")
case("wrong-prints-same",
     'output: "starts: [0, 50, 100]"', 'output: "starts: [0, 450, 900]"', expect="prints the same as the right option")
case("unknown-field",
     "        type: fill_blanks\n", "        type: fill_blanks\n        lab_minutes: 30\n", expect="unknown field")
case("prose-promise",
     "        grows_in: [size-and-overlap]\n", "", expect="grows_in")
case("bridge-names-unseen",
     "Next you will decide how big each slice is and how much neighbouring slices share.",
     "Next you will decide how big each slice is, how much neighbouring slices share, and how `embed_chunks()` stores them.", expect="never shows it")
case("slice-too-long",
     '          print("starts:", starts[:3])                    # the first three starts',
     "\n".join(['          x = 1  # filler'] * 12) + '\n          print("starts:", starts[:3])                    # the first three starts',
     expect="code lines")

# Design rules, broken in the concepts example
example = (K / "assets/example-concepts-blueprint.yaml").read_text()
case("theme-clash-green", 'accent: "#5b3cc4"', 'accent: "#2a9d4a"', expect="too close in hue")
case("theme-too-grey", 'accent: "#5b3cc4"', 'accent: "#777777"', expect="grey")
case("frame-label-long", "            - label: Before\n", "            - label: Before attention runs\n", expect="12")

if missed:
    sys.exit(f"Missed {len(missed)} breaks: {', '.join(missed)}")
print("Every break was caught.")
