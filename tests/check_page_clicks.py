"""Click through the built example pages and check how they behave, the way a learner would use them.

Run from the repo root: python3 tests/check_page_clicks.py
Needs Playwright with Chromium (pip install playwright; python -m playwright install chromium).
Each example is built into a temporary folder; the script exits with an error if any check fails.
The tutor test replaces Claude with a stand-in that answers at once, so it needs no network.
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "building-interactive-lessons"
BUILD_FOLDER = Path(tempfile.mkdtemp())
failures = []


def build(example):
    page_path = BUILD_FOLDER / example / "lesson.html"
    subprocess.run([sys.executable, str(SKILL / "scripts/build_page.py"), str(SKILL / f"assets/{example}.yaml"), "--out", str(page_path)],
                   check=True, capture_output=True)
    return page_path.as_uri()


def expect(name, passed, detail=""):
    print(f"{'PASS' if passed else 'FAIL'}     {name}{'' if passed else ': ' + detail}")
    if not passed:
        failures.append(name)


# A stand-in for Claude: the tutor streams one short Markdown answer, and every request is kept for the test to read
FAKE_CLAUDE = """
window.__tutorRequests = [];
const fakeSample = async (turns, options) => {
  window.__tutorRequests.push(turns);
  if (options && options.onText) options.onText({ text: "**Hint:** think" });
  return { text: "**Hint:** think about how far each chunk moves." };
};
fakeSample.json = async () => ({ verdict: "pass", criteria: [], first_problem: "", hint: "", misconception: "", insight: "Well put." });
window.claude = { use: async (capability) => (capability === "sample" ? fakeSample : null) };
"""


def block(tab, block_id):
    return tab.locator(f"#{block_id}")


def pick(tab, block_id, blank_number, option_text):
    """Tap a blank, then the option with this text."""
    exercise = block(tab, block_id)
    exercise.locator(".blank").nth(blank_number).click()
    exercise.locator(".chip").filter(has_text=re.compile("^" + re.escape(option_text) + "$")).first.click()


def check(tab, block_id):
    block(tab, block_id).get_by_role("button", name="Check", exact=True).click()


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(args=["--no-sandbox"])
    errors = []

    def new_tab(url, fake_claude=False):
        context = browser.new_context(viewport={"width": 390, "height": 844})
        if fake_claude:
            context.add_init_script(FAKE_CLAUDE)
        tab = context.new_page()
        tab.on("pageerror", lambda error: errors.append(str(error)))
        tab.goto(url)
        tab.wait_for_timeout(150)
        return tab

    # ---- Code blanks: one Check shows where the pick leads and the verdict together
    chunking = build("example-blueprint")
    tab = new_tab(chunking + "#size-and-overlap")
    exercise = block(tab, "fix-stride")
    expect("fill the blanks has no separate Run button", exercise.get_by_role("button", name="Run", exact=True).count() == 0)
    pick(tab, "fix-stride", 0, "overlap")
    check(tab, "fix-stride")
    text = exercise.inner_text()
    expect("a wrong pick shows its verdict", "Not quite" in text, text[:200])
    expect("a wrong pick shows what it prints", "What this choice prints" in text and "starts: [0, 50, 100]" in text, text[:300])
    pick(tab, "fix-stride", 0, "chunk_size - overlap")
    expect("picking again clears the old result", "starts: [0, 50, 100]" not in exercise.inner_text())
    check(tab, "fix-stride")
    text = exercise.inner_text()
    expect("checking again is free and shows the right output", "Correct." in text and "starts: [0, 450, 900]" in text, text[:300])

    # ---- Test, then reveal: the common-mistake card opens once its question is answered
    tab = new_tab(chunking + "#why-chunk")
    card = block(tab, "page-vs-chunk-pitfall")
    expect("the card is folded before its question", "People often think" not in card.inner_text() and "Answer the question above" in card.inner_text(), card.inner_text())
    question_box = block(tab, "page-vs-chunk-check")
    expect("the question comes before its card", question_box.bounding_box()["y"] < card.bounding_box()["y"])
    question_box.locator(".option").first.click()
    expect("answering the question opens the card", "People often think" in card.inner_text(), card.inner_text())

    # ---- The key idea folds under the guess, with Skip
    idea = block(tab, "chunk-idea")
    expect("the key idea is folded before the guess", "Answer to see why" in idea.inner_text(), idea.inner_text())
    block(tab, "predict-page-match").locator(".option").first.click()
    expect("answering the guess opens the key idea", "Search compares your question" in idea.inner_text(), idea.inner_text())
    tab = new_tab(chunking + "#size-and-overlap")
    idea = block(tab, "stride-idea")
    idea.get_by_role("button", name="Skip").click()
    expect("Skip opens the key idea without a guess", "Each new chunk starts one stride" in idea.inner_text(), idea.inner_text())
    tab.reload()
    tab.wait_for_timeout(150)
    expect("a skipped idea stays open after a reload", "Each new chunk starts one stride" in block(tab, "stride-idea").inner_text())

    # ---- Read-along opens everything
    for chapter in ["why-chunk", "size-and-overlap", "choosing-a-size"]:
        tab = new_tab(chunking + "?read-along=on#" + chapter)
        expect(f"read-along leaves nothing folded ({chapter})", tab.locator(".folded").count() == 0)
    expect("read-along shows each blank's output", "starts: [0, 450, 900]" in block(new_tab(chunking + "?read-along=on#size-and-overlap"), "fix-stride").inner_text())

    # ---- Two blanks, both wrong: the first wrong blank's own output, and the note
    concepts = build("example-concepts-blueprint")
    tab = new_tab(concepts + "#attention")
    exercise = block(tab, "bank-attends")
    for blank_number in range(2):
        exercise.locator(".blank").nth(blank_number).click()
        right = tab.evaluate(f"() => BLOCKS['bank-attends'].blanks.map(b => b.options.find(o => !o.correct).text)[{blank_number}]")
        exercise.locator(".chip").filter(has_text=re.compile("^" + re.escape(right) + "$")).first.click()
    check(tab, "bank-attends")
    text = exercise.inner_text()
    expect("two wrong blanks: both are marked", text.count("✗") >= 2 or exercise.locator(".blank.wrong").count() == 2, text[:200])
    expect("two wrong blanks: one blank at a time note", "Fix one blank at a time" in text, text[:400])

    # ---- Stepped pictures keep one height, so the page never jumps
    for url, diagram_id in [(concepts + "#attention", "attention-grid"), (concepts + "#next-token", "odds-bars"),
                            (build("example-monty-blueprint") + "#where-the-chance-goes", "before-after")]:
        tab = new_tab(url)
        figure = block(tab, diagram_id)
        heights = []
        buttons = figure.locator(".switch.frames button")
        slider = figure.locator("input[type=range]")
        steps = buttons.count() or int(slider.get_attribute("max")) + 1
        for step in range(steps):
            if buttons.count():
                buttons.nth(step).click()
            else:
                slider.fill(str(step))
            tab.wait_for_timeout(50)
            heights.append(round(figure.bounding_box()["height"]))
        expect(f"{diagram_id} keeps one height over {steps} steps", len(set(heights)) == 1, str(heights))

    # ---- Play: fresh random deals, counts beside the expected share; read-along shows the seeded sample
    monty = build("example-monty-blueprint")
    tab = new_tab(monty + "#every-case")
    play = block(tab, "deal-games")
    expect("play shows nothing before a deal", play.locator(".deal-cell").count() == 0)
    switch_counts = []
    for _ in range(5):
        play.get_by_role("button", name="Deal 100 games").click()
        switch_counts.append(play.locator(".deal-cell.hot").count())
    expect("a deal of 100 shows 100 games", play.locator(".deal-cell").count() == 100)
    expect("each deal is fresh, not a fixed list", len(set(switch_counts)) > 1, str(switch_counts))
    expect("counts sit beside the expected share", "expected about 67" in play.inner_text() and "All your deals together" in play.inner_text())
    play.get_by_role("button", name="Deal 10 games").click()
    expect("a deal of 10 shows 10 games", play.locator(".deal-cell").count() == 10)
    sample = block(new_tab(monty + "?read-along=on#every-case"), "deal-games").inner_text()
    expect("read-along shows the seeded sample deal", "you: 63 of 100" in sample and "you: 37 of 100" in sample, sample[:300])

    # ---- Tiles, animated: a tap moves between computed steps, replayable; reduced motion steps instead
    tab = new_tab(monty + "#where-the-chance-goes")
    doors = block(tab, "doors-open")
    expect("tiles draw one box per door", doors.locator(".frame-layer.current rect.svg-box").count() == 3)
    doors.locator(".switch.frames button").nth(1).click()
    tab.wait_for_timeout(200)
    expect("a tap animates from the last step", doors.locator(".frame-layer.leaving").count() == 1)
    tab.wait_for_timeout(800)
    expect("the animation ends within a second", doors.locator(".frame-layer.leaving").count() == 0)
    doors.get_by_role("button", name="Play again").click()
    tab.wait_for_timeout(200)
    expect("Play again replays the step", doors.locator(".frame-layer.leaving").count() == 1)
    calm = browser.new_context(viewport={"width": 390, "height": 844}, reduced_motion="reduce").new_page()
    calm.goto(monty + "#where-the-chance-goes"); calm.wait_for_timeout(150)
    calm.locator("#doors-open .switch.frames button").nth(1).click(); calm.wait_for_timeout(100)
    expect("reduced motion steps without moving", calm.locator("#doors-open .frame-layer.leaving").count() == 0
           and not calm.locator("#doors-open").get_by_role("button", name="Play again").is_visible())

    # ---- Tutor: opens with the block's context, sends on Enter, renders Markdown, keeps the answer back
    tab = new_tab(chunking + "#size-and-overlap", fake_claude=True)
    tab.wait_for_timeout(200)
    exercise = block(tab, "fix-stride")
    exercise.get_by_role("button", name="Ask the tutor").first.click()
    box = tab.locator("#tutor-input")
    box.fill("just tell me what goes in the stride blank")
    box.press("Enter")
    tab.wait_for_timeout(200)
    sheet = tab.locator(".sheet")
    expect("the tutor renders Markdown", sheet.locator("strong", has_text="Hint:").count() >= 1, sheet.inner_text()[:200])
    request = tab.evaluate("() => window.__tutorRequests[0][0].content")
    expect("the tutor gets the rules and this block", "Never give an exercise's solution" in request and "fill-the-blanks exercise (OPEN" in request, request[:200])
    tab.keyboard.press("Escape")
    expect("Escape closes the tutor", tab.locator(".sheet").count() == 0)

    # ---- Every view of every example loads with no page error
    for example in ["example-blueprint", "example-concepts-blueprint", "example-monty-blueprint"]:
        url = build(example)
        tab = new_tab(url)
        views = tab.evaluate("() => ['start', ...LESSON.chapters.map(c => c.id), 'field-guide']")
        for view in views:
            tab.goto(url + "#" + view)
            tab.wait_for_timeout(80)
    expect("no page errors on any view", not errors, "; ".join(errors[:3]))
    browser.close()

if failures:
    sys.exit(f"\n{len(failures)} click checks failed: {', '.join(failures)}")
print("\nEvery click check passed.")
