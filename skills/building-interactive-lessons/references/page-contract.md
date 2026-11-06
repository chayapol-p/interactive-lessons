# Page contract

How the lesson page looks and behaves. `assets/template.html` implements all of it, and `scripts/build_page.py` fills the template from the blueprint. Change the template only to fix behaviour for every lesson; a lesson's content lives in its blueprint.

## Contents

1. Layout
1a. Look: colour, type, labels
2. Components and their behaviour
3. Exercises: blanks, hints, solutions, read-along mode
4. Run: recorded outputs only
5. Saving progress
6. Capabilities to declare in claude.ai
7. Publishing
8. Fallbacks
9. Before publishing

---

## 1. Layout

- **One chapter per page.** Previous and Next buttons at the bottom. Each chapter has its own address (`#chapter-id`), so a link opens it.
- **Slim top bar:** lesson title, "Chapter N of M", a Chapters menu, a thin progress bar, and the **Read-along** switch (section 3). No row of chips that wraps or scrolls sideways.
- **Start page:** who the lesson is for (say so when the learner profile is assumed), what they will be able to do, total time, and the chapter list with times.
- **Last page:** the field guide (every recap line), the "confident but wrong" list with links back, and the `run_locally` commands for learners who want to run the real thing.
- **Phone first:** one column, 16px side margins, no sideways scrolling. Code wraps or scrolls inside its own box.
- **Light and dark themes** from colour tokens, with readable contrast in both.
- **Calm by default:** no animation unless it explains something; respect reduced-motion settings.
- **Start page leads with work:** a first question from chapter 1 sits above the chapter list. The learner profile is folded under "Who this lesson is for".
- **One mode line** under the top bar says what is on (Read-along, tutor off). Progress counts work solved, not pages opened.

## 1a. Look: colour, type, labels

**Two colour layers** (`scripts/theme.py` builds both; never write a colour by hand)
- **Brand layer, per learner:** one accent from `theme.accent`. It sets buttons, links, the hot box in a picture, the shade ramp of grids and bars, and neutrals tinted towards it. The accent is adjusted per theme so text on it stays readable; the build prints the original and the adjusted colour.
- **Meaning layer, fixed for everyone:** right (green), wrong (red), answer shown (amber). A theme never changes these, so "right" looks the same in every lesson. An accent within 40° of one of them is refused.
- **No colours of your own** and no see-through colours. Each soft fill is its own token, checked for contrast in both themes.

**Choosing the theme** (SKILL.md step 1): draft it from what you know: a colour the learner named, their organisation's colour (marked "check me"), the topic's world, or the default. Show the learner the name, the original and the adjusted colour, and the reason. Never put an organisation's name or logo on the page without a yes.

**Right and wrong never by colour alone:** a ✓ or ✗ mark and the words "Right" or "Not quite" go with every colour. Screen readers hear the result.

**Labels:** sentence case, plain words, one per block: Your guess, Key idea, Real code, Try it, Apply it, Spot the mistake, In your own words, Common mistake, Remember. No capitals, no letter-spaced badges.

**One box per action:** an exercise is one card; its result, hint and solution sit inside it, not in boxes of their own. Pictures sit on the page with no frame.

**Phone-proof:** taps at least 44 px; frame buttons share one row and their labels fit in 12 characters; grid and bar values below 0.01 show as `<0.01`, never 0.00; code wraps.

**Access:** sheets (tutor, glossary, chapter menu) keep focus inside, close on Escape and return focus to the button that opened them; feedback is announced; the page behind is inert.

## 2. Components and their behaviour

**Bridge line** (top of each chapter): the chapter's `bridge_in`, in a muted style.

**Predict**: the question, options or an input, and a 3-step confidence choice (unsure, fairly sure, certain).
- **The answer waits for the guess:** the first `idea` block after the predict (the key idea that answers it) stays folded behind "Answer to see why" until the guess is made. A **Skip** button opens it without a guess, and the choice is kept. Only that one block folds; everything else stays open. Read-along opens it.
- Why: in every test round, learners read the answer while scrolling to the guess, so the guess stopped being a guess.

**Idea**: at most 3 sentences. Every `glossary` term in the text is tappable and opens its definition card at the bottom of the screen. A "More" panel holds optional depth.

**Diagram**: drawn from its `figure` (see `diagrams.md`). A stepped picture (`frames`) draws every step once and keeps the tallest step's height, so tapping through steps never moves the page. With `animate: true`, a tap moves from the last step to the new one in 0.7 s and a "Play again" button (always in place, so nothing jumps) replays it; reduced motion turns the movement off. A `toy` figure starts its caption with "Toy numbers." A caption under it states the brief's `understand` sentence.
- A stage with `extends` redraws the earlier stages muted, in the same positions, and highlights what it adds, under a line saying what was added to which chapter's picture. A first stage with `grows_in` notes under it which chapters add to it.

**Code**
- The slice, read-only, with its line comments, and a Run button that shows `recorded_output` (section 4).
- Notice prompts under the output.
- "Show the code around this" opens the tutor with that request filled in, or shows `context_note` and `setup` when AI is unavailable.
- A slice with `run_locally` also shows its command.

**Compare**: a switch between options. Below it, each option's steps, with step `differs_at` marked and the explanation shown.

**Play** (label "Play it"): the prompt, one button per deal size, then the dealt games as a grid of small cells (each with its outcome's short mark; the hot outcome filled with the accent), and a table: each outcome's count beside the expected share ("you: 64 of 100 · expected about 67"). Each deal is fresh and random; after two or more deals, a line adds up all of them. Read-along shows the seeded sample deal instead, so screenshots repeat.

**Fill the blanks, explain, stretch**: see section 3.

**Pitfall**: a card with the wrong idea ("People often think: …", never struck through, so a learner who just got it right never reads it as a mark against them), why people believe it, and what is true.
- **Test, then reveal:** when a "Spot the mistake" check tests the card's misconception, the check comes first and the card stays folded until the check is answered; then it opens as feedback. An "Open it now" button opens it early. Read-along opens it, and so does a "See the common mistake" link from a wrong blank.

**Check**: the question and options. On click: mark right or wrong, reveal the correct option, show the explanation of the option picked, then the correct one's.

**Recap**: the recap line and the `bridge_out` sentence.

**Glossary terms**: the first use of each `glossary` term in an idea, a question or a recap is tappable and opens its definition in a bottom sheet.

**Ask the tutor**: a button on every block opens a chat panel (a bottom sheet on phones). It sends the context packet for that block. Stop button while answering.

## 3. Exercises

**Fill the blanks** (the default exercise)
- The real code with its line comments. Each blank is a small picker showing its 3 or 4 options.
- **One Check button** does both jobs at once: it marks each blank right or wrong, shows each wrong pick's one-line `why_wrong` with a link to its misconception's card, and shows the recorded output for the chosen options (section 4). Picking again clears the marks and the output; checking again is free.
- Why one button: with a separate Run and Check, learners pressed only one of them and missed half the feedback.

**Explain**
- A text box. **Submit** sends the answer to the AI grader with the rubric (see `ai-tutor-and-grader.md`). Feedback names the first unmet criterion only.

**Stretch: write it yourself** (optional)
- At most one per chapter, collapsed under "Stretch: write it yourself".
- An editor for code or text. **Compare with solution** shows the learner's answer beside the reference solution. **Grade it** sends both, with the rubric, to the AI grader when it is available.

**Buttons every exercise has, always visible and independent**
- **Hint**: shows the next hint level, about half way to the answer.
- **Show solution**: the commented solution. For fill the blanks, it is the code with every right option filled in, and **Use this** fills the pickers. For explain and stretch, it is the reference solution.

**Read-along mode**
- A switch in the top bar. When on, every exercise opens with its solution shown, every blank filled, and every Run output visible. Opening the page with `?read-along=on` turns it on for that load only (the screenshot script uses this).
- For learners who want to read first and practise later. The choice is kept per viewer.

**Recording**
- Progress records whether the learner got each exercise right, and whether they opened the solution. The field guide shows "solved", "solved after reading the solution" or "read the solution", never a penalty.

Why the buttons are always there: a learner who is stuck and cannot see the answer stops learning. The tutor still never hands over a solution; the learner decides when to open it.

## 4. Run: recorded outputs only

The page never runs code. Every output comes from a real run at build time (see `blueprint-format.md` section 2).

- **Code slice:** Run shows `recorded_output`.
- **Fill the blanks** (Check shows it; blanks are numbered in the order they appear in the code):
  - every blank right → the right output;
  - one blank wrong → that option's recorded output, marked "What this choice prints";
  - two or more blanks wrong → no combined output exists, so show the output for the first wrong blank and say "Fix one blank at a time: this is what happens with only this blank changed". Never invent a combined output.
- Show error outputs in plain words first ("NameError: `stride` is used before it is set"), then the recorded line.
- Label each output "Recorded from a real run".

## 5. Saving progress

- In claude.ai, with `db` and `user` declared: save each learner's answers, confidence and solution views under `data/users/<their id>/progress`. This path is private to that learner.
- Write only when something changes; one write at a time per document.
- Without `db`: keep progress in browser storage, wrapped in try/catch, so the page still works if storage is blocked.
- Never store anything secret, and never store a learner's name; store ids only.

## 6. Capabilities to declare in claude.ai

```
capabilities: { sample: {}, db: {}, user: {} }
```

- `sample`: the tutor and the grader. `db` and `user`: private per-learner progress.
- Load the environment's `artifact-capabilities` skill before writing runtime code; its rules on consent, errors and access win over this file.

## 7. Publishing

- The page is one HTML file; the blueprint, with its recorded outputs, lives in it as data.
- `build_page.py` writes `lesson-blueprint.txt` beside the page. Publish it with the page (`.yaml` is not a served type), and keep the `.yaml` with your build files.
- Republish to the same page path so the link stays.

## 8. Fallbacks

The page must teach fully with any of these missing:

- **No `sample`:** tutor hidden. Fill the blanks, hints and solutions work as normal. Explain and stretch show the rubric as a self-check beside the reference solution.
- **No `db`:** progress kept in browser storage.
- **Opened as a local file:** everything above that does not need claude.ai still works.

## 9. Before publishing

- `check_blueprint.py lesson-blueprint.yaml --run-tests --page lesson.html` passes: every script check, and the page carries this blueprint.
- `screenshot_chapters.py lesson.html` reports no sideways scroll and no page errors for the changed chapters (all chapters on a first build).
- The screenshots read well at phone width in both themes, diagrams included.
- On a first build, click through one chapter: Check on a wrong blank shows its own output and its reason, Show solution and Use this fill the blanks, a common-mistake card opens after its question, and Read-along opens every solution. `tests/check_page_clicks.py` in the skill's repo runs these clicks on the examples.
