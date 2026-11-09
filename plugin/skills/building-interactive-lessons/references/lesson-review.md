# Lesson review: three fresh reviewers

Where the scripted edition runs check scripts, this edition has the finished lesson reviewed. Three reviewers each check one side of it. None of them wrote the lesson, so none of them grades their own work.

## Contents

1. Who reviews what
2. Fresh agents, or a self-check
3. The content reviewer
4. The learner reviewer
5. The scene and layout reviewer
6. The report
7. After the review

---

## 1. Who reviews what

| Reviewer | Checks | Needs |
|---|---|---|
| **Content** | every rule in `self-checks.md`, every result re-run, every fact against its source | the blueprint, a code tool, the sources |
| **Learner** | whether a person at the stated level gets the promise of the lesson | the published page (or the built file), a browser |
| **Scene and layout** | every scene step and control, light and dark, phone width | the built page, a browser |

The promise to review against (write it in each brief): the lesson's `big_idea` and objectives, for the learner in `lesson.learner`.

## 2. Fresh agents, or a self-check

- **Where you can start agents** (Claude Code, Cowork): start the three reviewers as fresh agents, in parallel, each with its brief below. Give them files and the promise, never your reasoning about the lesson. They report; you fix.
- **Where you cannot** (a plain claude.ai chat): do the three passes yourself, one after another, in the same order and with the same checklists. Then tell the author plainly: "This lesson was self-checked, not reviewed by fresh agents." Never call a self-check a review.
- **Browser:** the learner and layout passes need a page they can open and tap: a browser tool, or Playwright with Chromium in the code tool (`pip install playwright`, then `python -m playwright install chromium`). With neither, say which checks could not run.
- **Motion libraries offline:** if the browser cannot reach jsDelivr, a scene that names a library shows its steps as words. Report it as "not checked: library unreachable", not as a pass or a failure.

## 3. The content reviewer

**Brief:**
> You review a lesson blueprint before it is published. You did not write it. Files: `lesson-blueprint.yaml`, the skill's `references/self-checks.md`, `references/blueprint-format.md`, and the sources listed in its facts. Promise: [big idea and objectives] for [learner].
> 1. Work through `self-checks.md` sections 1 to 16, item by item. Count with code, not by eye.
> 2. Re-run every program (`building-the-page.md` section 2): every slice, every code blank option, every `computed_by`. Compare each with what the blueprint records.
> 3. Check every `confirmed` fact against its source, and every text option's `output_source`.
> 4. Read the rules in `checks-and-quizzes.md`, `chapter-design.md` and `diagrams.md` that are not marked (checked): they are judgement calls. Answer each against the blueprint.
> Report in the fixed format (section 6). Fix nothing.

## 4. The learner reviewer

Run with the `testing-with-real-users` skill when it is installed: it gives the persona, one new person per round, and the stop rule. Without it, use this brief.

**Brief:**
> You are [a persona at the lesson's learner level: what they know, what is new, what they want]. You have [time_minutes] minutes. Open the lesson page at phone width (390 px). Read-along stays off. Do the lesson as this person would: guess before reading on, pick blanks, write the explain answers in your own words.
> - Never open the page's source or the blueprint: you only see and tap what a learner sees.
> - Note every place you were stuck, confused, bored, or guessed without knowing.
> - At the end, without looking back, teach the big idea to a friend in 3 to 5 sentences (the teach-back), and say whether you would say "I get it".
> Report in the fixed format (section 6), with the teach-back word for word.

A teach-back that matches the big idea and an honest "I get it" is a pass. Anything else names the chapter that lost the learner.

## 5. The scene and layout reviewer

**Brief:**
> You check a built lesson page in a browser, at 390 px wide, in light and in dark (the page's theme switch, or `prefers-color-scheme`). Files: `lesson.html`, `lesson-blueprint.yaml` (for the data each scene should show), the skill's `references/page-contract.md` and `references/visual-design.md`.
>
> For the whole page:
> - No script error in the console, no sideways scroll, nothing cut off or overlapping, both themes readable.
> - If `document.documentElement.dataset.themeProblem` is set, the theme was refused: report the reason.
> - Click through one chapter: Check on a wrong blank shows its own output and reason; Show solution fills the blanks; a pitfall card opens after its question; Read-along opens every solution.
>
> For every scene, every step, and every value of every control:
> 1. It draws: no error, and not the word fallback (unless a library could not load).
> 2. Every number it shows is in its `data` (or is a step caption or control value).
> 3. Nothing is drawn outside its 340-wide box.
> 4. Each step changes something you can see.
> 5. Motion lands where a jump lands: reach a step with Next and screenshot it; then Next and Back to return to it by jump; screenshot again. The two must match.
> 6. Every run button gives a one-line summary.
> 7. With reduced motion (emulate `prefers-reduced-motion: reduce`), every step jumps straight to its end picture.
> 8. Play again visibly replays the move into the step: the picture leaves the step and moves back into it.
> 9. No label sits on another label or on a dot it does not name; every share the end picture uses is drawn; no share shows 0% or 100% unless it is.
> 10. Every button and control is at least 44 px tall.
>
> Save one screenshot per scene step and theme, and read them in order like a comic strip: does each step show one change, and does its caption say where to look?
> Report in the fixed format (section 6). Fix nothing.

## 6. The report

Every reviewer returns the same shape, so you can merge them:

```text
REVIEWER   content | learner | scene and layout
PROMISE    <the promise, one line>
PASSED     <what was checked and held, one line per group>
FAILED     <block or chapter id>: <what is wrong> → <what would fix it>
NOT CHECKED <what could not run, and why>
VERDICT    ready | fix first
```

The learner reviewer adds `TEACH-BACK` (word for word) and `STUCK AT` (chapter and block ids).

## 7. After the review

1. Fix every `FAILED` line in the blueprint, then rebuild (`building-the-page.md` section 5).
2. Send only the changed chapters back to the reviewer that found the problem. A fresh learner persona each round.
3. Stop when every reviewer says `ready`, or after 3 rounds; then report what is still open.
4. Tell the author what was reviewed, by whom (fresh agents or a self-check), and what was not checked.
