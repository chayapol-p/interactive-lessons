"""Break the example blueprints one way at a time, and check that the checker catches each break.

Run from the repo root: python3 tests/check_catches_breaks.py
Each break is written to a temporary folder; the script exits with an error if any break is missed.
"""
import subprocess
import sys
from pathlib import Path

import tempfile

K = Path(__file__).resolve().parent.parent / "plugin" / "skills" / "building-interactive-lessons"
here = Path(tempfile.mkdtemp())
missed = []
example = (K / "assets/example-blueprint.yaml").read_text()


def case(name, old, new, run_tests=False, expect="", then=()):
    """Replace old with new (each found exactly once), then each (old, new) pair in `then`, and run the checker."""
    broken = example
    for find, put in [(old, new), *then]:
        assert broken.count(find) == 1, f"{name}: text to break not found once"
        broken = broken.replace(find, put)
    path = here / f"{name}.yaml"
    path.write_text(broken)
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

CARD = "      - id: page-vs-chunk-pitfall\n        type: pitfall\n        misconception: whole-page-is-fine\n"
case("card-before-question", CARD, "", expect="comes right before the pitfall card",
     then=[("      - id: page-vs-chunk-check\n", CARD + "      - id: page-vs-chunk-check\n")])

# The lesson arc and the text budget
case("idea-too-long", "        text: Search compares your question with pieces of text, and",
     "        text: Search, the part of the system that looks through everything you stored to find the passages that best answer a question, compares your question with pieces of text, and",
     expect="keep it to about 45")
case("feedback-two-sentences", 'why_wrong: "Fewer entries is usually faster; the problem is match quality."',
     'why_wrong: "Fewer entries is usually faster. The problem is match quality."', expect="more than one sentence")
case("caption-too-long", "          understand: Search never sees a page, only the chunks cut from it,",
     "          understand: Search never sees a page as a whole, from its first word to its last, only the chunks that the cutting step made from it,",
     expect="keep it to about 25")
case("copied-blank", "        explanation: Overlap does not change a chunk's size.",
     "        explanation: Overlap does not change a chunk's size; the step is chunk_size - overlap.", expect="word for word")
case("long-right-option", '{text: "One chunk per question and its answer", correct: true',
     '{text: "One chunk for each question together with the full answer that goes with it", correct: true', expect="guess it by length")
case("beat-out-of-order", "    beat: [mechanism]", "    beat: [hook]", expect="keep the arc in order")
case("no-open-question", '    open_question: "Which size suits the questions your users ask?"\n', "", expect="needs open_question")

# Design rules, broken in the concepts example
example = (K / "assets/example-concepts-blueprint.yaml").read_text()
case("theme-clash-green", 'accent: "#5b3cc4"', 'accent: "#2a9d4a"', expect="too close in hue")
case("theme-too-grey", 'accent: "#5b3cc4"', 'accent: "#777777"', expect="grey")
case("frame-label-long", "            - label: Before\n", "            - label: Before attention runs\n", expect="12")

# Moving pictures: a scene says why it moves, is agreed, and draws from computed data
WHY = "          why_not_still: A still picture shows the odds, but not that a reply is a draw that can land in any slice, nor how draws pile up in proportion to width.\n"
case("scene-not-agreed", "  agreed_extras: [scene]\n", "", expect="a scene is built only after the author agrees")
case("scene-without-motion", WHY, "", expect="motion")
case("scene-reason-thin", WHY, "          why_not_still: It looks nicer.\n", expect="at least 8 words")
case("scene-role-unknown", "          learner_does: run\n", "          learner_does: watch\n", expect="must be one of")
case("scene-no-show", "            scene.show = (step, from, settings) => {", "            scene.draw = (step, from, settings) => {", expect="must set scene.show")
case("scene-data-typed", "            example_draw: 0.13", "            example_draw: 0.5", run_tests=True, expect="not what computed_by prints")

# Picture ladder rules, broken in the Monty Hall example
example = (K / "assets/example-monty-blueprint.yaml").read_text()
LAST_CASE = "weight: 0.3333333333333333\n            outcome: switch-wins\n        sample:\n          games: 100\n          seed: 7\n"
case("play-weights-off", LAST_CASE, LAST_CASE.replace("0.3333333333333333", "0.5"), expect="add up to")
case("play-typed-by-hand", "seed: 7\n          counts:\n            stay-wins: 37\n            switch-wins: 63",
     "seed: 7\n          counts:\n            stay-wins: 33\n            switch-wins: 67", run_tests=True, expect="not what computed_by prints")
case("play-not-agreed", "  agreed_extras: [animation, play]", "  agreed_extras: [animation]", expect="a play block is built only after a yes")
case("animation-not-agreed", "  agreed_extras: [animation, play]", "  agreed_extras: [play]", expect="an animated picture is built only after a yes")
case("answer-in-milestone", 'milestone: "I can say the puzzle, its three rules, and a first guess."',
     'milestone: "I can show why you switch to door 2."', expect="before the guess")
case("tile-unknown-state", "{label: Door 1, state: picked, note: yours}", "{label: Door 1, state: chosen, note: yours}", expect="needs state")

if missed:
    sys.exit(f"Missed {len(missed)} breaks: {', '.join(missed)}")
print("Every break was caught.")
