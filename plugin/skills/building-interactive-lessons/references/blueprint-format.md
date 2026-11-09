# Blueprint format

The blueprint is the lesson as data. The page is built from it, the checker reads it, and later edits start from it. Write it in YAML (or JSON with the same fields). `assets/example-blueprint.yaml` is a complete example that passes every check.

Any field not listed here is an **error**. That catches typos, and it catches YAML lines that an unquoted comma split into junk fields. Quote any value that contains a comma or a colon.

## Contents

1. Field list (required and optional)
2. Recorded outputs: how they are recorded and checked
3. Block fields, by type
4. Id rules

---

## 1. Field list

`R` = required, `o` = optional.

**Top level**
- `lesson` R · `known_ideas` R · `facts` R · `misconceptions` R · `chapters` R
- `glossary` o: list of `{term, definition}`. The page turns each term into a tappable definition card. Every term must appear somewhere in the chapters.
- `theme` o: `{name, accent, fonts, why}`. The learner's colour and type. `accent` R is one hex colour; `fonts` o is `schibsted-source` (default), `plex`, `work-newsreader` or `noto-thai`; `why` o is one line on where the colour came from. `scripts/theme.py` builds every other colour from the accent and refuses one too close to the right, wrong or answer colours (green, red, amber) or too grey. Without `theme`, the page uses Ink blue `#1d5ca8`. See `page-contract.md` section 1a.
- `shared_modules` o: `{module_name: python source}`. Helper modules (a toy corpus, a stub library) that every Python run can `import` when outputs are recorded.

**`lesson`**
- `title` R
- `big_idea` R: one sentence, the idea the learner should still hold a month later. Shown on the field guide only (`chapter-design.md` section 0).
- `role` R: `before-hands-on` (a primer for labs the learner does next), `standalone` (the lesson is the whole learning), or `after-hands-on` (a review). See the scope rule in SKILL.md step 1.
- `learner` R:
  - `knows` R (list), `new_to` R, `wants_to` R
  - `time_minutes` R: minutes the learner can give this lesson. The chapters must fit in it.
  - `assumed` R (`true`/`false`): `false` once the user confirmed the drafted profile (SKILL.md step 1); `true` when nobody did
  - `assumption_note` (R when `assumed: true`): who should confirm it, and when
- `objectives` R: 3 to 5 items of `{id, text}`. Text starts "After this, you can…" and never uses "understand".
- `source` o: where the material comes from.
- `agreed_extras` o: the moving pictures the author agreed to, after you proposed them with a reason and a cost: `animation`, `play`, `scene`. An animated figure, a play block or a scene without its agreement is an error (`visual-design.md` section 7).

**`known_ideas`**: `{id, idea}`. Ids start with `known-`. These are the specific ideas the first chapters bring in. `learner.knows` is the short profile line; `known_ideas` are the pieces a chapter can name in `brings_in`.

**`facts`**: `{id, statement, status, source}`. `status` is `confirmed` or `inferred`. A confirmed fact needs a `source`. The blueprint is the only place facts live; keep no separate fact sheet. The field guide page lists them with their status.

**`misconceptions`**: `{id, wrong_idea, why_people_believe_it, what_is_true, source}`, all required. Every misconception must be listed by some chapter.

**Chapter**
- `id`, `title`, `why_it_matters` R (shown on the start page only)
- `beat` R: one beat or a list of beats, from `hook`, `intuition`, `proof`, `mechanism`, `boundary`, `transfer`, `payoff`, in arc order across the lesson; the first chapter has `hook`, the last `payoff`
- `milestone` R: "I can …", what the learner can do at the chapter's end
- `open_question` R (every chapter but the last; never on the last): the question the chapter leaves open, ending with "?"
- `bridge_in` R: `{text, recalls}`. `recalls` lists the `brings_in` ideas the sentence reminds the learner of.
- `bridge_out` R: `{text, points_to}`. `points_to` is the later chapter the sentence previews, or `beyond` (last chapter only).
- `minutes` R: 5 to 15
- `source_section` o (R when the role is `before-hands-on`): the lab or section this chapter prepares for
- `source_minutes` o: hands-on minutes of that section. Used by the scope rule.
- `must_know` R: 1 to 3 ideas
- `must_get_right` R: items `{id, can_do, evidence, objective, tested_by}`
- `brings_in` R (list of idea ids), `misconceptions` R (list of ids)
- `carries_forward` R: items `{id, idea, used_in, shown_by}`. `shown_by` lists the blocks in this chapter that show the idea.

**Named concepts must be shown (checked).** A concept is a `glossary` term or a code name (`backticked`, snake_case or `call()`). Every concept named in:
- a carried idea appears in its `shown_by` blocks;
- a `bridge_in` appears in its recalled ideas, or in the blocks that showed them;
- a `bridge_out` appears in the blocks of its `points_to` chapter;
- a `recap` appears in its `sums_up` blocks.

Ids and link fields do not count as showing anything. Put every key concept in the `glossary`, so the checker can follow it.
- `blocks` R

## 2. Recorded outputs

The lesson page runs no code. Every Run button shows an output that was recorded from a real run at build time. Never invent an output.

**What is run, at build time**
- A code slice: `slice.setup`, then `slice.code`.
- A fill-in-the-blanks exercise, once per option: `setup`, then `code` with that option in its blank and every other blank set to its right option.

**What is recorded**
- Everything the program prints. If it fails, add the last error line (for example `NameError: name 'stride' is not defined`), as the checker does.
- The text itself, never a file path.

**How it is recorded**
- Write `""` for every `recorded_output` and option `output`, then run `python scripts/record_outputs.py lesson-blueprint.yaml`. It runs every program above with the real interpreter (`python`, or `node` for JavaScript) and writes what each prints into the blueprint, keeping its comments and layout.
- After changing a block's code, re-record only that block: `--only <block-id>`.

**How it is checked**
- `python scripts/check_blueprint.py lesson-blueprint.yaml --run-tests` runs every program again and compares the output with the recorded one. On a mismatch it prints the real output.
- A slice or exercise that needs a database, a network service or a key gets `run_locally: {command, why}`. Record its outputs on a machine that has the service; the checker skips running it. The page shows the command so a learner can run it too.
- Helper code the slice needs goes in `setup` or `shared_modules`, never in the lines the learner reads.

## 3. Block fields, by type

Every block has `id` and `type`. `R` = required, `o` = optional.

**predict**: `question` R; `options` (2 to 4) or `answer`; `hold` o (`true`, options only): the guess is noted, not marked, and the last chapter brings it back with its answer. Use it for the hook's opening guess, so the lesson's question stays open until the lesson answers it.
```yaml
- id: predict-count
  type: predict
  question: A 1,200-token page, size 500, overlap 50. How many chunks?
  options:
    - {text: "2", correct: false, why_wrong: "The short last chunk still counts."}
    - {text: "3", correct: true, why_right: "Starts at 0, 450 and 900."}
```

**idea**: `text` R (at most 2 sentences and about 45 words), `key` o (`true` when a later chapter or the field guide depends on it), `more` o.

**diagram**: `shape` R (`flow`, `structure`, `change-over-time`, `space`, `comparison`, `quantity`), `brief` R with `understand`, `how_it_helps`, `clearer_than_text`, and `figure` R: what the template draws.
- `motion` (R on a picture that moves: a `scene`, or `frames` with `animate: true`; an error anywhere else): the answers to the five questions in `visual-design.md` section 1. `changes` R (what moves or changes), `stays` R (the landmarks that never move), `why_not_still` R (at least 8 words: what about the change, its order, path, timing or amount, a still picture would hide), `learner_does` R (`step`, `bet`, `drive`, `run`, `puzzle` or `explore`; `drive` needs a slider or buttons, `run` a run control, `step` at least 2 steps), `breaks` o (the misconception the motion breaks).
- `figure.kind` R: `tiles` (`tiles` of `{label, state, inside, note, group}`, `state` one of closed, open, picked, hot), `flow` (`parts` of `{id, label, row, note}`, `links` of `{from, to, label}`, `highlight` o), `bars` (`bars` of `{label, value, note}`, `max` o, `mark_below` o), `tokens` (`rows` of `{label, tokens: [{text, id, hot}]}`), `scatter` (`points` of `{label, x, y}`, `highlight`, `x_label`, `y_label`), `grid` (`rows`, `columns`, `values` from 0 to 1, `highlight_row`), `frames` (`frames` of `{label, figure, caption}`, where `caption` o is one line shown under that step, `control: slider | buttons`, `control_label`, `animate` o: `true` moves between steps on a tap, needs `animation` in `lesson.agreed_extras`; a frame may hold bars, tokens, scatter, grid or tiles) `svg` (`svg`: full markup), or `scene` (a picture written for one idea; below). See `diagrams.md` section 7 and `visual-design.md` section 6.
- **`figure.kind: scene`** fields:
  - `steps` R: 1 to 8 items of `{label, caption}`, the storyboard. A label is at most 24 characters; a caption is about 25 words and says where to look.
  - `script` R: JavaScript that sets `scene.show(step, from, settings)`, and `scene.run(trials, settings)` when there is a run control. See `visual-design.md` section 6 for the `scene` object. It cannot contain `</script`.
  - `data` o: every number the scene shows, printed by `computed_by` as `{"data": {...}}`. Write `data: {}` before recording.
  - `controls` o: at most 2 items of `{id, kind, label, …}`. `kind: slider` (an ordered setting) or `buttons` (at most 3 separate cases, each at most 12 characters) need `values` (2 to 8 labels) and `start` o (an index, default 0); `kind: run` needs `trials` (whole numbers from 1 to 1000, one button each) and `unit` o ("words", "games"), shown as "Draw 100 words".
  - `height` o: a whole number from 120 to 480 (default 240); the scene is 340 wide.
  - `library` o: `anime` or `gsap`, a motion library loaded from jsDelivr for this page; the script must use `scene.anime` or `scene.gsap`. See `visual-design.md` section 6.
  - A scene cannot grow across chapters; it needs `scene` in `lesson.agreed_extras` and a `motion` answer.
- `figure.toy` o (`true`): the numbers are made up to show the idea. The page puts "Toy numbers." before the caption. Use it on every figure whose data is a sketch, not a measurement.
- `figure.computed_by` (R for scatter, grid, frames, and a scene with `data`; o for bars, tokens and tiles): `{language: python, code, run_locally}`. The code prints the figure's data as one JSON object; `record_outputs.py` writes it in, and `--run-tests` proves it. `run_locally` skips a run that needs a file or service the lesson does not ship.
- A diagram that grows across chapters is written as stages, never as a promise in prose:
  - `grows_in` o (first stage only): the later chapters that add to it. Each named chapter must have a stage that extends it.
  - `extends` o (later stages only): `{diagram, adds}`. `diagram` names the earlier stage (in an earlier chapter); `adds` says what this stage draws on top. Its `figure` lists only the parts and links it adds, and keeps the first stage's kind.
- A sentence such as "later chapters add one box each" anywhere in a block is an error unless the chapter's first-stage diagram has `grows_in`.
```yaml
# Chapter 1
- id: search-pipeline
  type: diagram
  shape: flow
  brief: {understand: "...", how_it_helps: "...", clearer_than_text: "..."}
  figure:
    kind: flow
    parts:
      - {id: page, label: Page, row: 0}
      - {id: chunks, label: Chunks, row: 1}
    links:
      - {from: page, to: chunks, label: cut}
  grows_in: [size-and-overlap]
# Chapter 2
- id: search-pipeline-settings
  type: diagram
  shape: flow
  brief: {understand: "...", how_it_helps: "...", clearer_than_text: "..."}
  figure:
    kind: flow
    parts:
      - {id: settings, label: "Size, overlap", row: 1}
    links:
      - {from: settings, to: chunks, label: dials}
  extends: {diagram: search-pipeline, adds: "Size and overlap dials on the chunks box."}
```

**code**: `slice` R, `notice` R (1 to 3 prompts).
- `slice.language` R (`python` or `javascript`), `slice.source` R, `slice.context_note` R, `slice.depends_on` o
- `slice.setup` o: runnable hidden setup (imports, fixtures, stubs)
- `slice.code` R: at most 15 code lines (blank and comment lines do not count), with a short comment at least every 4 code lines
- `slice.recorded_output` R
- `slice.run_locally` o: `{command, why}`

**compare**: `input` R, `options` R (2 or more `{name, steps}`), `differs_at` R (the number of the first step where the options differ; earlier steps must be the same), `explanation` R.

**fill_blanks**: the default exercise, for code or for text.
- `instructions` R (1 to 4 lines), `language` R (`python`, `javascript` or `text`), `source` R, `context_note` R, `hints` R (1 or 2 levels)
- Code: `code` R, the real slice with its line comments, and `setup` o, runnable hidden setup. Mark 1 to 3 blanks as `{{blank-id}}` on the lines that carry the idea.
- Text (`language: text`): `text` R, the sentence, rule or formula, with its blanks marked the same way. No `code`, `setup` or `run_locally`. Each option adds `output_from` R (`source`: quoted from a named source, or `worked`: worked out step by step) and `output_source` R (the source with its section, or the steps). The page shows the result under "What this choice leads to".
- `blanks` R: one item per blank, `{id, options}`. Each blank has 3 or 4 options, exactly one right:
  - right option: `{text, correct: true, why_right, output}`
  - wrong option: `{text, correct: false, why_wrong, misconception, output}`. `why_wrong` is one line; `misconception` names a real misconception.
  - `output` is what the program prints with that option, recorded from a real run. A wrong option must print something different from the right one, so Run shows the learner what goes wrong.
- `run_locally` o: `{command, why}`
- The solution the page shows is the code with every right option filled in.
```yaml
- id: fix-stride
  type: fill_blanks
  instructions: ["Fill the blank so each chunk shares 50 tokens with the one before it."]
  language: python
  source: the chunker above
  context_note: The same chunker, with the line that sets the step left blank.
  setup: |
    tokens = [f"word{i}" for i in range(1200)]
  code: |
    stride = {{stride}}                              # how far each new chunk moves
    starts = list(range(0, len(tokens), stride))    # one start per stride
    print("starts:", starts[:3])
  blanks:
    - id: stride
      options:
        - {text: "chunk_size - overlap", correct: true, why_right: "...", output: "starts: [0, 450, 900]"}
        - {text: "overlap", correct: false, why_wrong: "...", misconception: overlap-adds-tokens, output: "starts: [0, 50, 100]"}
        - {text: "chunk_size + overlap", correct: false, why_wrong: "...", misconception: overlap-adds-tokens, output: "starts: [0, 550, 1100]"}
  hints: ["Should the shared part make the step longer or shorter?"]
```

**explain**: a short answer in the learner's words, graded by AI.
- `instructions` R, `reference_solution` R, `rubric` R (items `{criterion, passing}`), `hints` R
- `common_wrong_answers` o: `{answer, misconception, hint}`

**stretch**: the optional "write it yourself" exercise, collapsed by default. At most 1 per chapter, and never in `tested_by`.
- `kind` R (`code` or `explain`), `instructions` R, `reference_solution` R (code: commented, at most 15 code lines), `rubric` R, `hints` R
- `language` (R when `kind: code`)

**pitfall**: `misconception` R. It must be listed in the chapter's `misconceptions`.

**check**: `purpose` R (`key` or `pitfall`), `tests` R, `question` R, `options` R (3 or 4).
- `purpose: key` → `tests` names a `key: true` idea block in the same chapter.
- `purpose: pitfall` → `tests` names a misconception.

**recap**: `text` R, `sums_up` R (the teaching blocks of this chapter it summarises).

**play**: the learner deals trials and counts them (a ready-made "run trials" picture; needs `play` in `lesson.agreed_extras`). When a single trial has a shape worth seeing, write a scene with a run control instead.
- `unit` o: what one deal makes, plural and lower case (default `games`; for example `replies`, `draws`). The buttons read "Deal 100 replies".
- `prompt` R: what to deal and count, in one or two sentences.
- `deals` R: the deal sizes offered as buttons, `[10]`, `[100]` or `[10, 100]`.
- `outcomes` R: 2 to 4 items of `{id, label, short, hot}`. `short` R is 1 or 2 characters drawn in each dealt game, so a game never reads by colour alone; at most one outcome is `hot` (the one the lesson is about).
- `computed_by` R: python that prints one JSON object with `cases` and `sample`. `record_outputs.py` writes both in, and `--run-tests` proves them. Write `cases: []` and `sample: {games: 100, seed: 7, counts: {}}` before recording.
- `cases` (recorded): 2 to 12 items of `{label, weight, outcome}`: each way a game can go, its chance, and what it counts as. The weights add up to 1 (checked).
- `sample` (recorded): `{games, seed, counts}`, one deal made with a fixed seed. Read-along, screenshots and tests show it; a learner's own deals are fresh and random.
```yaml
- id: deal-games
  type: play
  prompt: Deal 100 games with a host who knows, and count who would win.
  deals: [10, 100]
  outcomes:
    - {id: stay-wins, label: Staying wins, short: St}
    - {id: switch-wins, label: Switching wins, short: Sw, hot: true}
  computed_by:
    language: python
    code: |
      import json, random
      cases = [{"label": f"Car behind door {car}", "weight": 1 / 3, "outcome": "stay-wins" if car == 1 else "switch-wins"} for car in [1, 2, 3]]
      dealt = random.Random(7).choices([c["outcome"] for c in cases], weights=[c["weight"] for c in cases], k=100)
      print(json.dumps({"cases": cases, "sample": {"games": 100, "seed": 7, "counts": {o: dealt.count(o) for o in ["stay-wins", "switch-wins"]}}}))
  cases: []
  sample: {games: 100, seed: 7, counts: {}}
```

## 4. Id rules

- Ids are lowercase words joined by hyphens, and unique across the whole blueprint.
- Use plain descriptive words (`fix-stride`), never codes (`c2-b4`).
- `known_ideas` ids start with `known-`.
