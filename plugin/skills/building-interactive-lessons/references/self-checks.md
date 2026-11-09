# Self-checks: every blueprint rule as a checklist

Every rule the blueprint must keep, one line each, grouped by part of the blueprint. Rules marked **(checked)** in the other references are all here.

**Who uses it:**
- **The author (Claude)** works through it at the end of Plan (step 3), before building.
- **The content reviewer** works through it again on the finished blueprint (`lesson-review.md`).

**How to use it:**
- Go group by group. For each item, find every place in the blueprint it applies to.
- Count with code, never by eye: words, sentences, lines, characters, options, minutes. Use your own code tool for this.
- Write each failure as `block-or-chapter id: what is wrong` and fix it before building.

The numbers below are the limits. "About" means a soft limit: a few words over is a judgement call, many is a failure.

## Contents

1. Shape and ids
2. Lesson, learner and scope
3. Facts, misconceptions, glossary
4. The story arc
5. Chapter links and bridges
6. Teaching and testing in each chapter
7. Blocks: predict, idea, check, recap, compare, code
8. Fill-the-blanks
9. Explain and stretch
10. Text budget and fair questions
11. Diagrams and figures
12. Data figures
13. Growing diagrams
14. Moving pictures: motion, scenes, play
15. Real results
16. Theme

---

## 1. Shape and ids

- [ ] The blueprint starts with a `lesson` section, and has `known_ideas`, `facts`, `misconceptions` and `chapters`.
- [ ] Every item has only the fields `blueprint-format.md` lists for it, and every field marked R. An unknown field is usually a typo, an old field, or a YAML line split by an unquoted comma or colon: quote that value.
- [ ] No required field is empty.
- [ ] Every block `type` is one of: predict, idea, diagram, code, compare, fill_blanks, explain, stretch, pitfall, check, recap, play. (`your_turn` is retired: use `fill_blanks`, `stretch` or `explain`.)
- [ ] Every id is lowercase words joined by hyphens (`chunk-size`), and no id is used twice anywhere in the blueprint.
- [ ] Known idea ids start with `known-`.
- [ ] Lists of sentences (`instructions`, `hints`, `must_know`, `notice`, `knows`, `steps` in a compare, `beat`) hold plain text, never a mapping: a colon in an unquoted line turns it into one.
- [ ] YAML has no duplicate keys.

## 2. Lesson, learner and scope

- [ ] `lesson.role` is `before-hands-on`, `standalone` or `after-hands-on`.
- [ ] `learner.assumed` is true or false. When true, `assumption_note` says who should confirm the profile.
- [ ] `learner.time_minutes` is a number.
- [ ] 3 to 5 objectives. Each starts "After this, you can", and none uses "understand": use a verb a check can observe (predict, choose, write, fix, explain).
- [ ] Every objective is served by at least one chapter's `must_get_right` item, and every item names an objective that exists.
- [ ] Each chapter takes 5 to 15 minutes.
- [ ] The chapters add up to at most 90 minutes, and to no more than `learner.time_minutes`. A longer source becomes several lessons.
- [ ] `before-hands-on`: every chapter names its `source_section`, and when it gives `source_minutes`, the chapter's minutes are at least 10% of them.

## 3. Facts, misconceptions, glossary

- [ ] Every fact's `status` is `confirmed` or `inferred`. A confirmed fact names its `source`.
- [ ] Every misconception is listed by some chapter, and every chapter's listed misconception exists.
- [ ] Every glossary term appears somewhere in the lesson's text.

## 4. The story arc

- [ ] `big_idea` is one sentence: what the learner should still say a month later.
- [ ] Every chapter has a `beat` from: hook, intuition, proof, mechanism, boundary, transfer, payoff. Beats keep that order (a beat may repeat, never come back after a later one).
- [ ] The first chapter is the hook; the last is the payoff.
- [ ] Every `milestone` starts "I can ".
- [ ] Every chapter but the last has an `open_question` ending in "?"; the last chapter has none.

## 5. Chapter links and bridges

- [ ] Every chapter has 1 to 3 `must_know` ideas.
- [ ] Every `brings_in` id is carried forward by an earlier chapter, or is a known idea.
- [ ] Every chapter carries at least one idea forward. Each carried idea has `used_in` (later chapter ids, or `beyond`), and only later chapters.
- [ ] The last chapter carries at least one idea forward with `used_in: [beyond]`.
- [ ] Every carried idea has `shown_by`: blocks in its own chapter (not the recap) that show it. Every concept it names appears in those blocks.
- [ ] `bridge_in.recalls` lists only ids from `brings_in`, and every concept the bridge names appears in a recalled idea or in the blocks that showed it.
- [ ] `bridge_out.points_to` is a later chapter, or `beyond` (last chapter only). Every concept the bridge names appears in that chapter.
- [ ] A recap's `sums_up` names teaching blocks of its own chapter, and every concept the recap names appears in them.

**What "names a concept" means:** a glossary term, or a code name (`backticked`, snake_case, or `call()`). A plural counts as the same term. Ids and link fields never count as showing anything.

## 6. Teaching and testing in each chapter

- [ ] The first block is a `predict`.
- [ ] There is at least one `idea` block.
- [ ] After the first `idea`, there is at least one `check`, `fill_blanks` or `explain`.
- [ ] A chapter that shows code (a `code` block) has a `fill_blanks` exercise.
- [ ] There is a `recap` block.
- [ ] At most 2 `check` blocks and 1 `stretch`.
- [ ] Every `must_get_right` item's `tested_by` names blocks of its own chapter, at least one of them a `check`, `fill_blanks` or `explain` placed after the first `idea`. A `predict` may be listed too, never alone; a `stretch` never; a teaching block cannot test.
- [ ] Every `idea` with `key: true` has a `check` with `purpose: key` and `tests:` that idea's id. `key` is true or false.
- [ ] Every listed misconception has a `pitfall` block in the chapter; every pitfall's misconception is listed by the chapter.
- [ ] No two `check` blocks and no two `pitfall` blocks sit side by side.
- [ ] A `check` with `purpose: pitfall` sits right before the pitfall card for the misconception it tests (test, then reveal).

## 7. Blocks: predict, idea, check, recap, compare, code

- [ ] `predict`: 2 to 4 options with exactly one correct, or an `answer`. `hold: true` (keep the guess unmarked until the last chapter) only on a predict with options.
- [ ] `check`: 3 or 4 options, exactly one correct. `purpose` is `key` or `pitfall`; a pitfall check `tests` a defined misconception; a key check tests a key idea in this chapter.
- [ ] Every correct option has `why_right` (the insight, not praise); every wrong option has `why_wrong` (the specific mistake).
- [ ] `idea`: at most 2 sentences.
- [ ] `diagram`: `shape` is flow, structure, change-over-time, space, comparison or quantity.
- [ ] `code`: slice `language` is python or javascript; 1 to 3 `notice` prompts saying what to look at.
- [ ] `compare`: at least 2 options; `differs_at` is a step number (1 is the first), every option has at least that many steps, the options are the same before it and differ at it.
- [ ] `explain` and `stretch` have a `rubric`; `stretch.kind` is `code` or `explain`; a code stretch names its language.
- [ ] Every `common_wrong_answers` entry names a defined misconception.
- [ ] Exercises have 1 or 2 hint levels and 1 to 4 instruction lines.

## 8. Fill-the-blanks

- [ ] `language` is python, javascript or text.
- [ ] Code exercises hold their passage in `code`; text exercises in `text`, with no `code`, `setup` or `run_locally`.
- [ ] 1 to 3 blanks, each marked exactly once as `{{blank-id}}`, and every marked id is a blank.
- [ ] Each blank has 3 or 4 options and exactly one right option.
- [ ] Every right option has `why_right`; every wrong option has `why_wrong` and names a defined misconception.
- [ ] Code options: every option has a recorded `output`, and no `output_from` or `output_source`.
- [ ] Text options: every option has its result in `output`, plus `output_from` (`source` or `worked`) and `output_source` (the source with its section, or the steps).
- [ ] Every wrong option leads to a different result from the right one. If it prints the same, Run cannot show the mistake: print the value the mistake changes, or pick another wrong option.
- [ ] With several blanks, the right options of every blank record the same output (with every blank right, the program prints one thing).
- [ ] The code is at most 15 code lines (blank and comment-only lines do not count), with at least one comment per 4 code lines.
- [ ] No recorded output looks like a file path: paste the printed text itself.

## 9. Explain and stretch

- [ ] A code stretch's reference solution keeps the code limits in section 8.
- [ ] A rubric line has `criterion` and `passing`.

## 10. Text budget and fair questions

- [ ] An `idea` has at most about 45 words; detail goes in `more`.
- [ ] Each `why_right` and `why_wrong` is one sentence.
- [ ] A diagram's caption (`brief.understand`) and every step caption have at most about 25 words.
- [ ] **No early answers.** A predict's right answer never shows before the guess: not in a chapter title, an objective, a milestone up to this chapter, nor in a picture above it in the chapter (caption, step captions, tile words, text drawn in an svg). The giveaway is a chance or count in the right option ("2 in 3", "60%") that no wrong option shares, or the whole right option when it is 3 words or more.
- [ ] **No copying.** A blank's right option (4 characters or more) is not written word for word in the block just above the exercise.
- [ ] **Fair length.** The right option is not more than 1.5 times as long as the longest wrong option and 12 or more characters longer.
- [ ] **Test the idea, not the example.** A predict or check question names an example detail (a section number such as 9.1.6, "Law 13", "clause 2", a file name such as `chunker.py`, a lab number) only if an earlier block showed it, or the question explains it in brackets right after it. No option is only an example detail.
- [ ] **No promises in prose.** No block says that a later chapter adds to, extends or redraws something ("the next chapter adds…", "this grows across the chapters"). Plan it as a growing diagram (section 13) instead.

## 11. Diagrams and figures

- [ ] Every diagram has a `brief` with `understand`, `how_it_helps` and `clearer_than_text`, and a `figure`.
- [ ] `figure.kind` is flow, bars, svg, tokens, scatter, grid, frames, tiles or scene.
- [ ] **flow:** has parts; every part has a `row` (a whole number, 0 at the top); every link's ends and every highlight are parts of this figure or its earlier stages.
- [ ] **flow budget:** at most 9 boxes and 10 arrows across all stages, and at most 2 highlighted boxes per stage (the `highlight` list plus the boxes a later stage adds).
- [ ] **bars:** has bars, each with a number value. A bars figure cannot grow.
- [ ] **svg:** has full `<svg ...>` markup. It cannot grow.
- [ ] `animate` is true or false, and only on a `frames` figure.
- [ ] `steps`, `controls`, `script`, `data`, `height` and `library` appear only on a scene.

## 12. Data figures

- [ ] **tokens:** has rows, each a list of tokens; at most 2 tokens `hot`.
- [ ] **scatter:** 2 to 12 points, each with number x and y; highlights are point labels, at most 2.
- [ ] **grid:** 1 to 8 rows and columns; one row of values per row label and one number per column label; every value from 0 to 1; `highlight_row` is a row label.
- [ ] **tiles:** 1 to 12 tiles; each `state` is closed, open, picked or hot; labels at most 10 characters; at most 2 tiles hot.
- [ ] **frames:** 2 to 8 frames, all holding the same kind of figure (bars, tokens, scatter, grid or tiles), never another frames figure. `control` is `slider` or `buttons`, with a `control_label`. Frame labels at most 12 characters. More than 3 frames use a slider.
- [ ] **computed_by:** scatter, grid and frames figures need it (bars, tokens and tiles may have it). It is python, prints one JSON object, and the figure's numbers are exactly what it prints.

## 13. Growing diagrams

- [ ] A first stage lists `grows_in`: later chapters, each holding a diagram with `extends: {diagram: <this id>, adds: ...}`. Only a first stage lists `grows_in`.
- [ ] Every `extends` points to a diagram block in an earlier chapter whose `grows_in` names this chapter, says what it `adds`, and never loops back.
- [ ] A later stage keeps the first stage's figure kind and adds at least one part or link; no part id is defined twice across stages.
- [ ] Only flow figures grow. A changing bars, tokens, scatter, grid or tiles picture is a `frames` figure; a changing scene is a new scene.

## 14. Moving pictures: motion, scenes, play

**Agreed first**
- [ ] `lesson.agreed_extras` lists only `animation`, `play` and `scene`.
- [ ] Frames with `animate: true` need `animation` agreed; a scene needs `scene`; a play block needs `play`.

**Motion answer**
- [ ] A moving picture (a scene, or frames with `animate: true`) has `motion` with `changes`, `stays`, `why_not_still` and `learner_does`, each a full phrase. Nothing else has `motion`.
- [ ] `why_not_still` has at least 8 words.
- [ ] `learner_does` is step, bet, drive, run, puzzle or explore, and matches the controls: `drive` needs a slider or buttons; `run` needs a run control; `step` needs at least 2 steps.
- [ ] `breaks`, when given, is a defined misconception.

**Scene**
- [ ] A scene does not grow across chapters.
- [ ] 1 to 8 steps, each with a label (at most 24 characters) and a caption.
- [ ] `height` is a whole number from 120 to 480 (the width is always 340).
- [ ] `script` sets `scene.show = (step, from, settings) => { ... }`, and never contains `</script`.
- [ ] `library`, when given, is `anime` or `gsap`, and the script uses `scene.anime` or `scene.gsap`.
- [ ] At most 2 controls, with unique ids. Each is `slider`, `buttons` or `run`.
- [ ] A slider or buttons control has 2 to 8 values and a `start` that is the index of one of them. Buttons: at most 3 values, each at most 12 characters.
- [ ] A run control has `trials` (whole numbers from 1 to 1000, one button each), and the script sets `scene.run(trials, settings)`, which returns one line summing up the trials.
- [ ] A scene with `data` has `computed_by` (python that prints `{"data": ...}`), and `data` is exactly what it prints.

**Play block**
- [ ] `unit` is what one deal makes, plural and lower case ("games", "replies").
- [ ] `deals` is 10, 100 or both.
- [ ] 2 to 4 outcomes with unique ids, each with a 1 or 2 character `short`; at most one `hot`.
- [ ] `computed_by` prints the `cases` and a seeded `sample` deal. 2 to 12 cases, each with a weight above 0 and an outcome that exists; the weights add up to 1; every outcome has a case.
- [ ] `sample.games` is one of the deal sizes; `sample.counts` counts every outcome and adds up to `sample.games`.

## 15. Real results

These need code to run. Run each program yourself (`building-the-page.md` section 2 says how), then compare.

- [ ] Every code slice's `recorded_output` is exactly what its `setup` plus `code` prints, ignoring trailing spaces and blank lines at the ends. A program that fails records its last error line too.
- [ ] Every code option's `output` is exactly what the exercise prints with that option filled in.
- [ ] Every `computed_by` prints one JSON object, and the figure's numbers (or a play block's cases and sample) are exactly what it prints.
- [ ] A step marked `run_locally` was recorded on a machine with the service; the review says it was not re-run.

## 16. Theme

- [ ] `theme` has only `name`, `accent`, `fonts`, `why`, and `accent` is one hex colour like `#1d5ca8`.
- [ ] `fonts`, when given, is `schibsted-source`, `plex`, `work-newsreader` or `noto-thai`.
- [ ] The accent passes `theme.md`: strong enough, far enough in hue from right, wrong and answer-shown, and every colour pair readable. The built page also checks it, and keeps the default theme if it fails.
