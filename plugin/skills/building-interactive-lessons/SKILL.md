---
name: building-interactive-lessons
description: Builds an interactive, AI-powered lesson as one web page on any subject (a concept, rules, a policy, a formula) or from docs or a code repo. Plans first (discover the learner, verify the material, plan chapters that build on each other), then fills a ready page template from the plan, told as one story from a hook to a payoff, with predictions, pictures designed for each idea (stepped, animated or driven by the learner, with ready-to-use scenes), real code or text with recorded results, fill-in-the-blank exercises built on real mistakes, AI-graded explanations, an ask-the-tutor box, and quizzes on key ideas and pitfalls. Fresh reviewers check the finished lesson. Also revises a lesson it built from feedback. Use for "teach me this", "make a lesson", "turn this repo into a tutorial", "learning artifact", "interactive tutorial", "course for this lab", "fix this chapter of the lesson". Not for reference docs, slide decks, or a quick explanation in chat.
license: MIT
compatibility: Needs a code tool that runs Python 3 with PyYAML (and Node for a JavaScript slice), to record real results and fill the page template. Best in claude.ai, where the published page can ask Claude (tutor and grader) and keep progress; reviews by fresh agents need Claude Code or Cowork, and a browser or Playwright for the page checks. Elsewhere it produces one HTML file with the AI features hidden.
metadata:
  author: chayapol.par
  version: 0.5.0
---

# Building interactive lessons

Turns a topic, docs or a repo into a lesson the learner works through: predict, read real material, fill the blanks, see what each choice really leads to, explain, ask. The skill plans the learning as a **blueprint** (structured data), records every real result into it with your code tool, fills the ready page template from it, and has fresh reviewers check the result. Nobody writes the page by hand.

## Words used one way only

- **Blueprint:** the lesson as data (`references/blueprint-format.md`). **Page:** the HTML built from it.
- **Component:** a building block from the catalogue (`references/components/`): a block type, a figure kind, a scene recipe or a page part.
- **Picture:** any diagram block. **Moving picture:** animated frames, a play block or a scene; each needs the author's yes.
- **Self-check:** an item in `references/self-checks.md`. **Review:** a pass by a reviewer who did not write the lesson (`references/lesson-review.md`).
- **Author:** the person asking for the lesson. **Learner:** the person who will use it.

## Critical

1. **Plan before building.** Discover, verify and plan come first. The page is built only from a blueprint that passes every self-check.
2. **Every chapter states what the learner must get right and how we will know.** Each `must_get_right` item names a check, fill-the-blanks or explain block, placed after the teaching, that tests it. A prediction before the teaching never counts alone.
3. **Chapters connect, and only through what they show.** Each chapter lists what it `brings_in` and what it `carries_forward`, with the blocks that show each carried idea. Bridges and recaps name only concepts their linked blocks really show.
4. **The learner produces something in every chapter:** a prediction, a filled blank, or an answer in their own words. Reading alone does not count.
5. **Pick components by the idea.** Name the kind of topic, find the wrong belief, and pick the component that carries each beat (`references/topic-map.md`, `references/components/`). Write a diagram's brief before drawing; no clear brief means no diagram.
6. **Compare choices only where choices exist,** on the same input, naming the first step where they differ.
7. **Every result is real.** The page runs no code. Every code result, each wrong option's included, is recorded from a real run in your code tool. A text result is quoted from a named source or worked out in steps. Every number in a picture is printed by its `computed_by` code. Never type a result. If you cannot run code, stop and say so.
8. **Hints and solutions are the learner's choice.** Every exercise has Hint and Show solution, always available, plus a read-along mode. The tutor never hands over a solution.
9. **Real material, small.** A code slice is the real code that carries the idea, at most 15 code lines, with line comments and hidden `setup`. A text exercise is the real sentence, rule or formula. Never pad.
10. **Test the idea, not the example.** Explain an example before using it, and never ask for its details, such as a clause number.
11. **The page comes from the template.** Fill `assets/page-template.md` with the blueprint by following `references/building-the-page.md`. Never hand-write or hand-edit the page; change the blueprint and build again.
12. **One story, and nothing gives the answer early.** A big idea, chapters in beats from hook to payoff, each ending on an open question the next one answers. No answer shows before its guess, a "Spot the mistake" question comes before its card, and words stay inside the text budget (`references/chapter-design.md` sections 0 and 8).
13. **Design each picture from the idea, not from a menu.** Answer the five questions for every key idea and move a picture only where the manner of change is what must be learned (`references/visual-design.md`). Ready-made figures are cheap; when none carries the storyboard, start from a scene recipe. Moving pictures cost tokens: propose each with its reason and cost, and build it only once agreed.
14. **Checked by someone who did not write it.** Fresh reviewers check the content, the learner's path and every scene (`references/lesson-review.md`). Where you cannot start agents, run the same checklists yourself and tell the author it was self-checked, not reviewed.

## When to run or offer it (mode: suggest first)

It plans, builds and publishes a page, so offer it in one line, then wait.

**Signals:** the user wants to learn or teach a topic, a lab, a library or a codebase; says they ran code without understanding it; asks for a tutorial, a course, a learning artifact or an interactive explainer; gives feedback on a lesson this skill built.

**Offer:** "Want me to build an interactive lesson for this (plan the chapters first, then a page with real examples, pictures that move where it helps, fill-in-the-blank exercises, an AI tutor and grading)?"

## Time budget

| Step | At most |
|---|---|
| Plan (steps 1 to 3, blueprint passing the self-checks) | 20 min |
| First build (step 4) | 10 min |
| Review (step 5, reviewers in parallel) | 20 min |
| One revise round | 15 min |

If a step runs over, stop. Write one line in the work log: which step, how long, and why. Then go on or ask, but never spend the overrun silently.

## Steps

```
- [ ] 1. Discover: learner, source, goal, scope, motion, theme
- [ ] 2. Verify: facts, misconceptions, real material; record every result
- [ ] 3. Plan: arc, components per beat, blueprint; self-checks pass
- [ ] 4. Build: fill the page template from the blueprint
- [ ] 5. Review: content, learner, scenes and layout
- [ ] 6. Publish, and improve from use (the Revise path)
```

### 1. Discover
**Assume first, then confirm.** Never start from a blank profile, and never build on a guess nobody checked.

1. **Draft the learner profile** from what you already know: memory, this conversation, the user's files and past work. Cover `knows`, `new_to`, `wants_to` and `time_minutes`. With nothing to go on: new to the topic, no coding assumed.
2. **Draft the scope:** the source (a repo, docs, URLs or a topic; a source behind a connector needs that connector's read tool), the lesson's `role`, and 3 to 5 **objectives**, each starting "After this, you can…", with a verb a check can observe.
3. **Ask, in one round, at most 4 questions,** with the multiple-choice question tool when there is one:
   - **Confirm the profile:** what you assumed they know, each item with where it came from.
   - **Scope:** how deep, which topics are in or out, how long, and the style (picture-heavy or code-heavy).
   - **How much motion, with a suggestion and its cost** (`references/visual-design.md` section 7). Put your recommendation first, for example: "Moving pictures where they teach something a still can't (recommended: I'll propose each one in the plan, about 10–25k extra tokens per scene)", "Stepped pictures only (cheapest)", "Rich: scenes and trials wherever they fit".
   - **The theme:** one accent and its name, checked against `references/theme.md`. No organisation name or logo without a yes. This can share a question with the profile.
   - Never ask what you can find out yourself.
4. **Record the answers** in the blueprint and set `assumed: false`. If nobody answers (an unattended run), go on with `assumed: true` and an `assumption_note` naming who should confirm it.

**Scope rule:** `role` is `before-hands-on` (a primer before labs), `standalone` or `after-hands-on` (a review). One lesson holds at most 90 minutes of chapters, 5 to 15 minutes each; a longer source becomes several lessons. A before-hands-on chapter names its `source_section` and gets at least 10% of that section's hands-on minutes. For example, 7 labs of 30 to 90 minutes fit one primer of 7 chapters, about 9 to 12 minutes each.

### 2. Verify
- Read the sources. Write the **facts** in the blueprint, each `confirmed` (with its source) or `inferred`.
- Collect **misconceptions** learners really hold: docs' warnings, issue trackers, error messages, FAQs. Mark ones from your own knowledge as such.
- Pick the **real material**: code slices of at most 15 code lines with hidden `setup` and line comments, or the real sentences, rules and formulas.
- For each fill-the-blanks exercise, choose 1 to 3 key tokens to blank and 2 or 3 wrong options that are real misconceptions.
- For every picture with numbers, write `computed_by` code that prints them.
- **Record every result** with your code tool, following `references/building-the-page.md` section 2: every slice, every blank option, every `computed_by`. A step that needs a service gets `run_locally`; record it where the service is.

### 3. Plan
1. **The arc:** one `big_idea`, then chapters by beat (hook, intuition, proof, mechanism, boundary, transfer, payoff), each with a `milestone` and an `open_question` the next chapter answers (`references/chapter-design.md` section 0).
2. **The concept map:** order the chapters so each uses only what came before. Fill one chapter card per chapter (`references/chapter-design.md`).
3. **Components per beat:** name the kind of topic and its wrong belief, then pick the component that carries each beat from `references/topic-map.md`. Take each one's recipe and rules from `references/components/`:
   - `text-and-questions.md`: predict, held guess, idea, key check, spot the mistake and its card, recap, glossary
   - `exercises.md`: code slice, compare, fill-the-blanks (code and text), explain, stretch
   - `still-and-stepped.md`: flow, growing pipeline, tokens, bars, scatter, grid, tiles, frames, svg
   - `scenes.md`: strip and draws, travel along a path (anime.js or GSAP), pull, pour, and how to write your own
   - `trials.md`: play block, run control
   - `page-parts.md`: what the template builds around the chapters, and the fields that feed it
4. **Design each picture** (`references/visual-design.md`): the five questions, congruence, the change test, a learner role, a storyboard in words. Use a ready-made figure if it carries the storyboard; otherwise copy the nearest scene recipe and adapt it. Write the `motion` answer on every moving picture.
5. **Write exercises and quizzes** by `references/checks-and-quizzes.md`, inside the text budget (`chapter-design.md` section 8).
6. **Save the blueprint** (`references/blueprint-format.md`; `assets/example-blueprint.yaml` is complete).
7. **Self-check:** work through `references/self-checks.md`, counting with code, and fix every failure.
8. **Show the chapter map** if the author is present: titles, minutes, what each must get right, what carries forward, and each proposed moving picture with its moment, why a still would fail, the learner's role and its cost. Add what they keep to `lesson.agreed_extras`. If they said to just build, build only what Discover agreed and list the rest as proposals.

### 4. Build
- Fill the page template from the blueprint, following `references/building-the-page.md` section 3: the blueprint goes in as JSON, each scene as its own script element, with its motion library's tags.
- The template already follows `references/page-contract.md`, works out the theme (`references/theme.md`) and wires the tutor and grader (`references/ai-tutor-and-grader.md`). Change the template only to fix it for every lesson.
- In claude.ai, load the environment's artifact skills before publishing and check the page against their rules; their rules win.

### 5. Review
Follow `references/lesson-review.md`:
- **Where you can start agents** (Claude Code, Cowork): three fresh reviewers in parallel, each with its brief: content (every self-check, every result re-run, every fact against its source), learner (a persona at the stated level, phone width, ending in a teach-back), scenes and layout (every scene step and control, light and dark, with and without motion).
- **Where you cannot** (a plain claude.ai chat): run the three passes yourself, and tell the author the lesson was self-checked, not reviewed.
- **Grader:** try each explain exercise with a right, a wrong and a half-right answer; the verdicts must match. If the build environment cannot reach the AI, test on the published page.
- Fix every failure in the blueprint, build again, and send the changed chapters back to the reviewer that found it. Stop when all say ready, or after 3 rounds, and report what is open.

### 6. Publish and improve
- In claude.ai, publish `lesson.html` as an artifact with the capabilities in `references/page-contract.md`, and `lesson-blueprint.txt` beside it. Republish to the same path so the link stays.
- Tell the author how it was checked: by fresh reviewers or by a self-check, and what was not checked.
- When learners use it, revise first the blocks where most people fail or ask the most questions.

## Revise path (a feedback round)

For feedback on a lesson this skill built. Skip Discover and Verify; the blueprint already holds the facts.

1. **Edit the blueprint** for each point of feedback. Never edit the page.
2. **Record again** the results of the blocks whose code changed (`building-the-page.md` section 2).
3. **Build again** (`building-the-page.md` section 3), and list the chapters that changed.
4. **Review** only the changed chapters (`lesson-review.md`), with a fresh learner persona.
5. **Republish** to the same link. Report each point of feedback with what changed and how it was checked.

## Example

**User:** "Make a lesson on how text chunking works in my RAG repo, for someone who knows Python."

**Actions:**
1. Discover: knows Python, new to search; 30 minutes; `standalone`; an objective such as "After this, you can predict where chunks start for a size and overlap". Motion: stepped pictures recommended, since nothing here moves in a way a still can't show.
2. Verify: read `chunker.py`; slice the 10 lines that compute starts; misconceptions such as "overlap adds tokens to each chunk"; run the slice and every blank option, and record what each prints.
3. Plan: a process topic (`topic-map.md` section 1). Hook: a flow figure of the search pipeline. Mechanism: a code slice, then a blank on the stride expression with `chunk_size - overlap` right and `overlap` and `chunk_size + overlap` as real mistakes. Boundary: compare three overlaps on one page. The flow grows in chapter 2. Self-checks pass.
4. Build: fill the template. Review: three fresh reviewers; the learner persona's teach-back matches the big idea.

**Result:** a published lesson page, its blueprint beside it, a field guide at the end, and a line saying how it was reviewed.

## Troubleshooting

| Problem | Cause → fix |
|---|---|
| An unknown or empty field | A typo, an old field, or a YAML line split by an unquoted comma or colon → fix the name, or quote the value |
| A goal tested only by a prediction | → add a check, blank or explain after the idea |
| A recorded result differs from a fresh run | The code changed after recording → record that block again |
| A wrong option prints the same as the right one | Run cannot show the mistake → print the value the mistake changes, or pick another wrong option |
| A bridge or recap names something its blocks never show | → teach it in that chapter, or reword the bridge |
| A block promises in prose that a later chapter adds to a picture | → plan a growing diagram: `grows_in` on the first stage, `extends` in each named chapter |
| A moving picture that was not agreed | → propose it with its reason and cost, then add it to `lesson.agreed_extras`, or use a still or stepped picture |
| A moving picture with a thin `why_not_still` | → answer the five questions; if a still loses nothing, use a still |
| A scene shows a number not in its data | It was typed into the script → print it from `computed_by` and read it from `scene.data` |
| A scene step looks the same as the one before | → merge it, or make it show its one change |
| A scene lands somewhere else with motion than by a jump | Something changes outside `scene.move`, `scene.set` or `scene.play` → set every end value through them |
| A scene shows its steps as words | Its script threw, or its library could not load → read the console; offline, report "not checked" |
| The case weights do not add up to 1 | A trial can land in no case or two → fix the cases in `computed_by` and record again |
| A guess's answer shows earlier (title, objective, milestone, caption) | → reword that text, or move the picture after the guess |
| A blank's answer is written in the block just above | → reword the block above, or move the blank |
| The right option is the longest | → shorten it, or make a wrong option as full |
| Over the text budget | → keep the core, move detail to `more`, or let the picture say it |
| A quiz leans on an example detail | → explain the example and that detail earlier, or in brackets in the question |
| A diagram with too many boxes or highlights | → cut boxes that travel together, or split it; highlight only this chapter's point |
| The theme was refused (the page shows Ink blue) | The accent is too grey or too close to green, red or amber → pick a passing colour (`theme.md`) |
| Learners pass quizzes but fail blanks | Quizzes test recall → turn the quiz into an application question |
| Learners cannot follow | Missing bridge or prerequisite → check `brings_in` and the opening bridge |
| The tutor gives away the answer | The template's tutor rules were changed → restore them from `references/ai-tutor-and-grader.md` |

## References

- `references/principles.md`: why each rule exists, and the research behind it
- `references/topic-map.md`: for each kind of topic, the component that carries each beat of the story
- `references/components/`: the catalogue: what each component is for, its beat, the learner's role, a recipe, its rules, and when it is the wrong pick
- `references/visual-design.md`: designing a picture from the idea: five questions, congruence, the change test, roles, storyboards, the scene runtime, motion libraries, cost
- `references/diagrams.md`: the ready-made figures: brief, cut and draw them
- `references/chapter-design.md`: the arc, chapter cards, blocks, scope, the text budget
- `references/checks-and-quizzes.md`: fair tests, blanks, quizzes, hints and solutions, and the judgement calls
- `references/blueprint-format.md`: every blueprint field
- `references/self-checks.md`: every blueprint rule as a checklist
- `references/building-the-page.md`: recording every result and filling the page template
- `references/lesson-review.md`: the three reviewers, their briefs, and the report
- `references/theme.md`: one accent colour, and how the page works out and checks the rest
- `references/page-contract.md`: how the page behaves; the template implements it
- `references/ai-tutor-and-grader.md`: tutor and grader prompts and wiring
- `assets/page-template.md`: the page template, one html block with two placeholders
- `assets/example-blueprint.yaml`: a small code example (text chunking)
- `assets/example-monty-blueprint.yaml`: a 5-chapter example with no code (Stay or Switch?: tiles, animated steps, deal 100 games, case tables)
- `assets/example-concepts-blueprint.yaml`: an example with no code and two scenes (How LLMs Work: token chips, a word map, an attention grid, a strip of odds, a run-by-run scene in anime.js)

## Next

After learners have used the lesson, take the Revise path for the weakest blocks. For the next topic, start again at step 1 and reuse the learner profile.
