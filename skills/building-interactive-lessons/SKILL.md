---
name: building-interactive-lessons
description: Builds an interactive, AI-powered lesson as one web page on any subject (a concept, rules, a policy, a formula) or from docs or a code repo. Plans first (discover the learner, verify the material, plan chapters that build on each other), then fills a ready page template from the plan, with predictions, real code or text with recorded results, fill-in-the-blank exercises built on real mistakes, AI-graded explanations, an ask-the-tutor box, quizzes on key ideas and pitfalls, and diagrams only where they have a stated purpose. Also revises a lesson it built from feedback. Use for "teach me this", "make a lesson", "turn this repo into a tutorial", "learning artifact", "interactive tutorial", "course for this lab", "fix this chapter of the lesson". Not for reference docs, slide decks, or a quick explanation in chat.
license: MIT
compatibility: Needs Python 3 with PyYAML (checker and build) and ruamel.yaml (recording outputs), node for JavaScript slices, and Playwright with Chromium or Chrome for phone screenshots. Best in claude.ai, where a published artifact can ask Claude (tutor and grader) and keep progress. Elsewhere it produces one HTML file with the AI features hidden.
metadata:
  author: chayapol.par
  version: 0.3.1
---

# Building interactive lessons

Turns a topic, docs or a repo into a lesson the learner works through: predict, read real code, fill the blanks, see what each choice really prints, explain, ask. The skill plans the learning as a **blueprint** (structured data). Scripts record the real outputs into it, check it, and fill the page template from it. Nobody writes the page by hand.

## Critical

1. **Plan before building.** Discover, verify and plan come first. The page is built only from a blueprint that passes `scripts/check_blueprint.py --run-tests`.
2. **Every chapter states what the learner must get right and how we will know.** Each `must_get_right` item names a check, fill-the-blanks or explain block, placed after the teaching, that tests it. A prediction before the teaching never counts alone.
3. **Chapters connect, and only through what they show.** Each chapter lists what it `brings_in` and what it `carries_forward`, with the blocks that show each carried idea. It opens with a bridge that recalls earlier ideas and closes with one that points to the chapter using them next. Bridges and recaps name only concepts their linked blocks really show.
4. **The learner produces something in every chapter:** a prediction, a filled blank, or an answer in their own words. Reading alone does not count.
5. **Diagrams need a purpose first.** Write the diagram brief (what it should make clear, how, and what is clearer than words) before drawing. No clear brief means no diagram.
6. **Compare choices only where choices exist.** When a chapter compares options, show them on the same input and name the first step where they differ.
7. **Every result is real.** The page runs no code. A code result is recorded from a real run by `scripts/record_outputs.py`, including every wrong option's. A text result is quoted from a named source or worked out in steps. The numbers in a picture are printed by its `computed_by` code. Never type a result.
8. **Hints and solutions are the learner's choice.** Every exercise has a Hint button and a Show solution button, always available, plus a read-along mode that opens all solutions. The **tutor** never hands over a solution; it hints and points to Show solution.
9. **Real material, small.** Any subject works: code, rules, formulas, concepts. A code slice is the real code that carries the idea, at most 15 code lines, with short line comments, and hidden `setup`; the tutor can show the code around it. A text exercise is the real sentence, rule or formula. No minimum length: never pad.
10. **Test the idea, not the example.** Explain an example (a lab, a codebase, a rule book) before using it, and never ask the learner to recall its details, such as a clause number. A quiz must be answerable by someone who learned the idea but has never seen the example.
11. **The page comes from the template.** `scripts/build_page.py` fills `assets/template.html` with the blueprint. Never hand-write or hand-edit the page; change the blueprint and rebuild.

## When to run or offer it (mode: suggest first)

It plans, builds and publishes a page, so offer it in one line, then wait.

**Signals:** the user wants to learn or teach a topic, a lab, a library or a codebase; says they ran code without understanding it; asks for a tutorial, a course, a learning artifact or an interactive explainer; gives feedback on a lesson this skill built.

**Offer:** "Want me to build an interactive lesson for this (plan the chapters first, then a page with real code, fill-in-the-blank exercises, an AI tutor and grading)?"

## Time budget

| Step | At most |
|---|---|
| Plan (steps 1 to 3, blueprint passing the checker) | 15 min |
| First build (steps 4 and 5, from the template) | 20 min |
| One revise round | 10 min |

If a step runs over, stop. Write one line in the work log: which step, how long, and why (for example "plan: 25 min, the source had 12 labs, split into 2 lessons"). Then go on or ask, but never spend the overrun silently.

## Steps

```
- [ ] 1. Discover: learner, source, goal, scope
- [ ] 2. Verify: facts, misconceptions, slices; record the real outputs
- [ ] 3. Plan: concept map, chapters, blueprint; the checker passes
- [ ] 4. Build: fill the template from the blueprint
- [ ] 5. Check: one command for the script checks; screenshots; judgement calls
- [ ] 6. Publish, and improve from use (the Revise path)
```

### 1. Discover
**Assume first, then confirm.** Never start from a blank profile, and never build on a guess nobody checked.

1. **Draft the learner profile** from what you already know: memory, this conversation, the user's files and past work. Cover what they know (`knows`), what is new (`new_to`), what they want to do afterwards (`wants_to`) and their minutes (`time_minutes`). With nothing to go on, use the default: new to the topic, no coding assumed.
2. **Draft the scope:** the source (a repo, docs, URLs or a topic; a source behind a connector needs that connector's read tool), the lesson's `role`, and 3 to 5 **objectives**, each starting "After this, you can…". Use verbs a check can observe (predict, choose, write, fix, explain), never "understand".
3. **Ask, in one round, at most 4 questions,** with the environment's multiple-choice question tool when there is one:
   - **Confirm the profile:** show what you assumed they know, each item with where it came from, and let them tick or correct it.
   - **Scope questions** whose answers change the chapters: how deep (intuition only, light maths, full mechanics), which topics are in or out, how long, and the style (for example, picture-heavy or code-heavy).
   - **Offer the higher picture steps, only where a named moment needs them** (`references/diagrams.md` section 0): an animation when the motion is the idea, a play block when the learner needs to believe a number. Name the moment and the extra build time, for example "Chapter 2: let you deal 100 games and count the wins yourself (about 10 more minutes to build)?". Build them only on a yes, and record it in `lesson.agreed_extras`.
   - **Confirm the theme:** draft one accent and its name from a colour they named, their organisation's colour (say "check me"), the topic's world, or the default Ink blue. Run `python scripts/theme.py '#hex'` and show the original and adjusted colour. No organisation name or logo goes on the page without a yes. This can share a question with the profile.
   - Put your recommended answer first. Never ask what you can find out yourself.
4. **Record the answers** in the blueprint and set `assumed: false`. If nobody answers (an unattended run), go on with `assumed: true` and an `assumption_note` naming who should confirm it.

**Scope rule** (enforced by the checker)
- Choose the lesson's `role`:
  - `before-hands-on`: a primer the learner reads before doing the labs themselves;
  - `standalone`: the lesson is the whole learning;
  - `after-hands-on`: a review after the labs.
- One lesson holds at most 90 minutes of chapters, 5 to 15 minutes each. A longer source becomes several lessons, one per part.
- `before-hands-on`: each chapter names its `source_section` and gets at least 10% of that section's hands-on minutes. A chapter teaches at most 3 ideas, so a section with more ideas gets more chapters.
- Example: 7 labs of 30 to 90 minutes each fit one before-hands-on lesson of 7 chapters, about 9 to 12 minutes each.

### 2. Verify
- Read the sources. Write the **facts** in the blueprint's `facts` list, each marked `confirmed` (with its source) or `inferred`. The blueprint is the only place facts live; keep no separate fact sheet.
- Collect **misconceptions**: wrong ideas learners really hold. Look in the docs' warnings, issue trackers, error messages and FAQs. Mark ones from your own knowledge as such.
- Pick the **code slices**: the real lines that carry each idea, at most 15 code lines. Write hidden `setup` for imports and stubs, and add short line comments.
- For each fill-the-blanks exercise, choose 1 to 3 key words or tokens to blank, and 2 or 3 wrong options that are real misconceptions. With no code (`language: text`), each option's result names its source or its worked steps.
- For a picture with numbers (a map, a grid, bars, a slider), write `computed_by` code that prints them; `record_outputs.py` fills them in.
- **Record the outputs.** Leave every `recorded_output` and option `output` empty (`""`), then run:
  ```bash
  pip install pyyaml ruamel.yaml
  python scripts/record_outputs.py lesson-blueprint.yaml
  ```
  It runs every slice and every blank option with the real interpreter and writes what each prints into the blueprint, keeping its comments. A step that needs a service gets `run_locally`; record it on a machine that has the service.

### 3. Plan
- Map the concepts and what each depends on. Order the chapters so each uses only what came before.
- Fill one **chapter card** per chapter. See `references/chapter-design.md` for every field and the reason it exists.
- Choose blocks: predict, idea, then the exercise after the teaching. See `references/chapter-design.md`.
- Write exercises and quizzes by the rules in `references/checks-and-quizzes.md`.
- Pick each picture's step on the ladder (words, still, stepped, animated, play; `references/diagrams.md` section 0). Stepped is the default for a change; animated and play only with a yes from Discover.
- Write a brief for every diagram first, cut it to the fewest boxes, pick its pattern (growing pipeline, paired traces or sequence), then write its `figure` (flow, bars, tiles, frames or svg). See `references/diagrams.md`. Borrow from the diagram-design skill here if it is installed, never during a build.
- Save the blueprint in the format in `references/blueprint-format.md`. `assets/example-blueprint.yaml` is a complete example.
- Run the checker and fix every error:
  ```bash
  python scripts/check_blueprint.py lesson-blueprint.yaml --run-tests
  ```
- If the author is present, show the chapter map on one screen (chapter titles, minutes, what each must get right, what carries forward) and wait for a go. If they said to just build, build.

### 4. Build
- Fill the template from the blueprint:
  ```bash
  python scripts/build_page.py lesson-blueprint.yaml --out lesson.html
  ```
  It refuses a blueprint with errors. It writes `lesson.html`, a copy of the blueprint as `lesson-blueprint.txt`, and `changed.json` (the chapters that differ from the last build).
- The template already follows `references/page-contract.md` and wires the tutor and grader as in `references/ai-tutor-and-grader.md`. Change the template only to fix it for every lesson, never for one lesson's content.
- In claude.ai: load the environment's `artifact-design` and `artifact-capabilities` skills before publishing, and check the template against their current rules. Their rules win over the template.

### 5. Check
- **Every script check, in one command.** It checks the blueprint's shape (strict: unknown fields are errors), that each goal is tested after the teaching, that every blank has exactly one right option and a recorded output for each option, that every promise and bridge resolves, slice lengths, and that every recorded output is what the code really prints. `--page` adds that the page was built from this blueprint:
  ```bash
  python scripts/check_blueprint.py lesson-blueprint.yaml --run-tests --page lesson.html
  ```
- **Phone screenshots, changed chapters only:**
  ```bash
  python scripts/screenshot_chapters.py lesson.html --out shots
  ```
  It shoots each chapter in `changed.json` at 390 px wide, light and dark, with every solution open, and reports sideways scroll and page errors. Use `--all` on a first build.
- **Look at the screenshots** for what a script cannot judge: a diagram that reads well, contrast, crowded text.
- **Judgement calls:** read the list in `references/checks-and-quizzes.md` against the blueprint.
- **Grader:** try each explain exercise with a right, a wrong and a half-right answer; the verdicts must match. If the build environment cannot reach the AI, publish first, run this test on the live page, and report it.

### 6. Publish and improve
- In claude.ai, publish `lesson.html` as an artifact with the capabilities in `references/page-contract.md`, and `lesson-blueprint.txt` beside it. Republish to the same file path so the link stays.
- When learners use it, revise the blocks where most people fail or ask the most questions first, with the Revise path below.

## Revise path (a feedback round)

For feedback on a lesson this skill built. Skip Discover and Verify; the blueprint already holds the facts.

1. **Edit the blueprint** for each point of feedback. Never edit the page.
2. **Re-record** the outputs of the blocks whose code changed: `python scripts/record_outputs.py lesson-blueprint.yaml --only <block-id> ...`
3. **Rebuild**: `python scripts/build_page.py lesson-blueprint.yaml --out lesson.html`. It prints the chapters that changed.
4. **Check**: the one-command check with `--run-tests --page lesson.html`, then `screenshot_chapters.py`, which shoots only the changed chapters. Look at those images.
5. **Republish** to the same artifact link. Report each point of feedback with what changed and the check output that shows it.

## Example

**User:** "Make a lesson on how text chunking works in my RAG repo, for someone who knows Python."

**Actions:**
1. Discover: learner knows Python, new to search; 30 minutes; role `standalone`; objectives such as "After this, you can predict where chunks start for a size and overlap".
2. Verify: read `chunker.py`; slice the 10 lines that compute starts; misconceptions such as "overlap adds tokens to each chunk"; `record_outputs.py` records what the slice and each blank option print.
3. Plan: 3 chapters (why chunk, size and overlap, choosing a size). Chapter 2 blanks the stride expression, with `chunk_size - overlap` right and `overlap` and `chunk_size + overlap` as real mistakes. A flow figure in chapter 1 grows in chapter 2. The checker passes with `--run-tests`.
4. Build: `build_page.py` fills the template. The one-command check passes with `--page`; screenshots of 3 chapters, light and dark.

**Result:** a published lesson page, its blueprint beside it, and a field guide at the end.

## Troubleshooting

| Error | Cause → fix |
|---|---|
| "unknown field" | A typo, a field from an older version, or a YAML line split by an unquoted comma → fix the name, or quote the value |
| "needs a check, fill_blanks or explain after the teaching" | The only test is a prediction → add an exercise or quiz after the idea |
| "the recorded output is not what the code prints" | The code changed after recording → run `record_outputs.py --only <block-id>` |
| "prints the same as the right option" | Run cannot show the mistake → print the value the mistake changes, or choose another wrong option |
| "minutes cannot prepare … minutes of hands-on work" | A long lab got a thin chapter → give it more minutes or split it into 2 chapters |
| "bridge_out names 'X', but chapter 'Y' never shows it" | A bridge or recap promises more than the lesson teaches → teach X in that chapter, or reword the bridge |
| "promises something for later chapters in prose" | A growing diagram was described, not planned → add `grows_in` to the first stage and a diagram with `extends` in each named chapter |
| "figure link … is not a part of this figure" | A later stage links to a part no stage defines → add the part, or fix the id |
| "page … is stale" | The blueprint changed after the build → rebuild with `build_page.py` |
| "changed.json belongs to another build" | The last build failed → fix the blueprint and rebuild |
| "built only after a yes in Discover" | An animation or play block was added without asking → ask the author, then add `animation` or `play` to `lesson.agreed_extras`, or use a stepped picture |
| "the case weights add up to …, not 1" | A game can land in no case or two → fix the cases in `computed_by` and re-record |
| "a pitfall check comes right before the pitfall card" | The card sits before its question, so it gives the answer away → move the check above the card |
| "the question names 'X', which no earlier block explains" | A quiz leans on a detail of the example → explain the example and that detail earlier, or explain it in brackets in the question |
| "option 'X' is only a detail of the example" | An answer is a clause number or file name → write what that choice means |
| "the picture has … boxes" or "highlights … boxes" | The diagram says too much → cut boxes that travel together, or split it; highlight only what this chapter is about |
| A diagram reads badly in the screenshot | Parts crowd one row, or an arrow crosses a box → move parts to other rows, or put a joining input in the same row as its target |
| Learners pass quizzes but fail blanks | Quizzes test recall, not use → turn the quiz into an application question |
| Learners say they cannot follow | Missing bridge or prerequisite → check `brings_in` and the opening bridge |
| Tutor gives away the answer | The template's tutor rules were changed → restore them from `references/ai-tutor-and-grader.md` |

## References

- `references/blueprint-format.md`: every blueprint field, required and optional, figures, and how outputs are recorded
- `references/chapter-design.md`: chapter cards, blocks, scope, and the reason for each part
- `references/checks-and-quizzes.md`: fair tests, blanks, quizzes, hints and solutions, and the judgement calls
- `references/diagrams.md`: when a diagram helps, how to brief it, and how to write its figure
- `references/ai-tutor-and-grader.md`: tutor and grader prompts and wiring
- `references/page-contract.md`: how the page behaves; the template implements it
- `scripts/record_outputs.py`: runs every slice and blank option, and writes the real outputs into the blueprint
- `scripts/check_blueprint.py`: every script check in one command (`--run-tests`, `--page`)
- `scripts/build_page.py`: fills the template from the blueprint, and lists the changed chapters
- `scripts/theme.py`: builds both themes' colours from one accent, checks contrast, and refuses a clash with right, wrong or answer colours
- `scripts/screenshot_chapters.py`: phone screenshots of the changed chapters, light and dark
- `assets/template.html`: the page template
- `assets/example-blueprint.yaml`: a complete small code example (text chunking)
- `assets/example-monty-blueprint.yaml`: a small 3-chapter example with no code (Stay or Switch?: case tables, Before and After bars, a door-count slider; every chance worked out by code)
- `assets/example-concepts-blueprint.yaml`: a complete example with no code (How LLMs Work: text blanks, token chips, a word map, an attention grid, a temperature slider)

## Next

After learners have used the lesson, take the Revise path for the weakest blocks. For the next topic, start again at step 1 and reuse the learner profile.
