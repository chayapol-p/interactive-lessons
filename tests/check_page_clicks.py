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
SKILL = ROOT / "plugin" / "skills" / "building-interactive-lessons"
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

    def offline(context):
        """Only the page's own file loads: web fonts and anything else outside are refused, so every run behaves the same."""
        context.route("**/*", lambda route: route.continue_() if route.request.url.startswith("file:") else route.abort())
        return context

    def new_context(**settings):
        return offline(browser.new_context(**settings))

    def new_tab(url, fake_claude=False):
        context = new_context(viewport={"width": 390, "height": 844})
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

    # ---- The arc on the page: journey strip, open question, why-it-matters only on the start page, big idea at the end
    tab = new_tab(chunking + "#size-and-overlap")
    strip = tab.locator(".journey")
    expect("the journey strip marks this chapter", strip.locator("[aria-current=step]").inner_text() == "2" and "You are here" in strip.inner_text())
    milestones = tab.evaluate("() => LESSON.chapters.map(c => c.milestone.replace(/^I can /, ''))")
    expect("the strip shows this milestone only, never a later one", milestones[1] in strip.inner_text() and milestones[2] not in tab.locator("main").inner_text())
    expect("the chapter ends on its open question", "Still open" in tab.locator("#stride-recap").inner_text() and "Chapter 3 answers it" in tab.locator("#stride-recap").inner_text())
    expect("why it matters is not in the chapter", "Why it matters" not in tab.locator("main").inner_text())
    tab.goto(chunking + "#start"); tab.wait_for_timeout(100)
    why = tab.evaluate("() => LESSON.chapters[1].why_it_matters")
    expect("why it matters is on the start page", why in tab.locator("main").inner_text())
    tab.goto(chunking + "#field-guide"); tab.wait_for_timeout(100)
    expect("the field guide opens with the big idea", "The big idea" in tab.locator("main").inner_text())
    tab.goto(chunking + "#choosing-a-size"); tab.wait_for_timeout(100)
    expect("the last chapter ends on its bridge, no open question", "Still open" not in tab.locator("main").inner_text())

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
                            (build("example-monty-blueprint") + "#why-it-works", "before-after")]:
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
    tab = new_tab(monty + "#feel-it")
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
    sample = block(new_tab(monty + "?read-along=on#feel-it"), "deal-games").inner_text()
    expect("read-along shows the seeded sample deal", "you: 63 of 100" in sample and "you: 37 of 100" in sample, sample[:300])

    # ---- Tiles, animated: a tap moves between computed steps, replayable; reduced motion steps instead
    tab = new_tab(monty + "#feel-it")
    doors = block(tab, "ten-doors")
    doors.locator(".switch.frames button").nth(2).click()
    expect("the tapped step button shows as pressed", doors.locator(".switch.frames button").nth(2).get_attribute("aria-pressed") == "true"
           and doors.get_by_role("button", name="Play again").get_attribute("aria-pressed") is None)
    doors.locator(".switch.frames button").nth(0).click(); tab.wait_for_timeout(1500)
    expect("tiles draw one box per door", doors.locator(".frame-layer.current rect.svg-box").count() == 10)
    doors.locator(".switch.frames button").nth(1).click()
    tab.wait_for_timeout(60)
    expect("a tap animates from the last step", doors.locator("[data-tile-ghost]").count() == 8)
    tab.wait_for_timeout(1500)
    expect("the animation ends within 2 seconds", doors.locator("[data-tile-ghost]").count() == 0)
    doors.get_by_role("button", name="Play again").click()
    tab.wait_for_timeout(60)
    expect("Play again replays the step", doors.locator("[data-tile-ghost]").count() == 8)
    tab = new_tab(monty + "#why-it-works")
    bars = block(tab, "before-after")
    bars.locator(".switch.frames button").nth(2).click()
    tab.wait_for_timeout(150)
    expect("bars move to the new step", bars.locator(".frame-layer.current rect.svg-bar").count() == 3)
    calm = new_context(viewport={"width": 390, "height": 844}, reduced_motion="reduce").new_page()
    calm.goto(monty + "#feel-it"); calm.wait_for_timeout(150)
    calm.locator("#ten-doors .switch.frames button").nth(1).click(); calm.wait_for_timeout(60)
    expect("reduced motion steps without moving", calm.locator("#ten-doors [data-tile-ghost]").count() == 0
           and not calm.locator("#ten-doors").get_by_role("button", name="Play again").is_visible())

    # ---- Ten doors: the host's goats open one at a time, all within 2 seconds
    tab = new_tab(monty + "#feel-it")
    ten = block(tab, "ten-doors")
    ten.locator(".switch.frames button").nth(1).click()
    tab.wait_for_timeout(60)
    early = ten.locator("[data-tile-ghost]").count()
    tab.wait_for_timeout(560)
    middle = ten.locator("[data-tile-ghost]").count()
    tab.wait_for_timeout(1400)
    expect("the doors open one after another", early == 8 and 0 < middle < 8, f"{early} then {middle} doors still closing")
    expect("all of them open within 2 seconds", ten.locator("[data-tile-ghost]").count() == 0)
    expect("ten tiles sit in two rows of five", len(set(ten.locator(".frame-layer.current rect.svg-box").evaluate_all("els => els.map(e => e.getAttribute('y'))"))) == 2)
    expect("the deal names its marks before any deal", "sw switching wins" in block(tab, "deal-games").inner_text().lower())

    # ---- A chapter with no exercises is done only when its quizzes are answered right
    tab = new_tab(monty + "#use-it")
    expect("a chapter with no exercises is not done at the start", tab.locator(".journey-steps li").nth(0).inner_text() == "1")
    tab.goto(monty + "#the-game"); tab.wait_for_timeout(100)
    block(tab, "rules-key-check").locator(".option", has_text="He no longer knows").click()
    tab.goto(monty + "#use-it"); tab.wait_for_timeout(100)
    expect("answering its quiz right marks it done", tab.locator(".journey-steps li").nth(0).inner_text() == "✓")
    order = block(new_tab(monty + "?read-along=on#feel-it"), "deal-games").locator(".deal-cell").all_inner_texts()
    expect("the sample deal is laid out in a mixed order", order[:37] != ["St"] * 37, str(order[:12]))

    # ---- A held guess is noted, not marked, and the last chapter brings it back with its answer
    tab = new_tab(monty + "#the-game")
    first = block(tab, "predict-game")
    first.locator(".option", has_text="Stay with door 1").click()
    text = first.inner_text()
    expect("a held guess is noted, not marked", "Noted" in text and "Not quite" not in text and first.locator(".option.wrong, .option.right").count() == 0, text[:200])
    tab.goto(monty + "#use-it"); tab.wait_for_timeout(100)
    expect("the first guess waits until the last answer is written", "Your first guess" not in block(tab, "use-recap").inner_text())
    answer = block(tab, "payoff-explain")
    answer.locator("textarea").fill("Switch, because the host knows.")
    answer.get_by_role("button", name="Submit").click()
    tab.wait_for_timeout(100)
    recap = block(tab, "use-recap").inner_text()
    expect("the last chapter brings the first guess back", "you said: Stay with door 1" in recap and "Switch to door 2" in recap, recap[:200])
    expect("the deal says how far a fair deal wanders", "usually between" in block(new_tab(monty + "?read-along=on#feel-it"), "deal-games").inner_text())
    expect("a comma stays with its glossary word", tab.evaluate("() => [...document.querySelectorAll('.term-wrap')].some(w => w.textContent.endsWith(','))") or
           new_tab(monty + "#feel-it").evaluate("() => [...document.querySelectorAll('.term-wrap')].some(w => w.textContent.endsWith(','))"))

    # ---- "You can now" only after a goal's last test; a group over two rows is one outline; progress keeps pace
    tab = new_tab(monty + "#use-it")
    count = block(tab, "quiz-count")
    count.locator(".blank").first.click(); count.locator(".chip").filter(has_text=re.compile("^3$")).click()
    check(tab, "quiz-count")
    expect("no 'You can now' before the goal's last test", "You can now" not in count.inner_text(), count.inner_text()[-200:])
    groups = block(new_tab(monty + "#feel-it"), "ten-doors")
    expect("the other 9 are one outline across two rows", groups.locator(".frame-layer.current path.svg-group").count() == 1
           and groups.locator(".frame-layer.current rect.svg-group").count() == 1)
    tab = new_tab(monty + "#the-game")
    block(tab, "rules-key-check").locator(".option", has_text="He no longer knows").click()
    width = tab.evaluate("() => parseFloat(document.querySelector('.progress-fill').style.width)")
    expect("a quiz answered right moves the progress bar", width > 0, str(width))

    # ---- With the tutor off, ticking every point of the self-check counts the answer as done
    tab = new_tab(monty + "#use-it")
    answer = block(tab, "payoff-explain")
    answer.locator("textarea").fill("Switch: my pick was right 1 in 3 and the host had to leave the car behind door 2.")
    answer.get_by_role("button", name="Submit").click()
    for box in answer.locator(".self-check label span").all():
        box.click()
    tab.goto(monty + "#field-guide"); tab.wait_for_timeout(100)
    expect("ticking every point counts as done", "checked yourself" in tab.locator("main").inner_text())

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

    # ---- On a real phone (mobile viewport rules), the page lays out at phone width, not shrunk desktop width
    phone = new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, device_scale_factor=2).new_page()
    phone.goto(monty + "#the-game"); phone.wait_for_timeout(150)
    expect("a phone lays the page out at its own width", phone.evaluate("document.documentElement.clientWidth") == 390,
           str(phone.evaluate("document.documentElement.clientWidth")))

    # ---- Offline, a scene whose motion library cannot load shows its steps as words, and the page still works
    fallback = block(new_tab(concepts + "#next-token"), "run-by-run")
    expect("a scene without its library falls back to its steps as words", "could not be drawn" in fallback.inner_text() and fallback.locator("ol li").count() == 3,
           fallback.inner_text()[:160])

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
