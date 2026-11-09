# Components: still and stepped pictures

The ready-made figures the template draws: cheap to write, already tested, both themes, phone width. Use one whenever it carries the storyboard; write a scene (`scenes.md`) only when none does. `diagrams.md` section 7 has every field; this file says which to pick and gives a recipe.

Every diagram block wraps its figure the same way:

```yaml
- id: search-pipeline
  type: diagram
  shape: flow            # flow, structure, change-over-time, space, comparison or quantity
  brief:
    understand: One sentence: what the learner should see after looking.
    how_it_helps: What is drawn, and what is highlighted.
    clearer_than_text: What the picture shows that a sentence would hide.
  figure: { ... }        # one of the cards below
```

## Contents

1. Flow (a process or a structure)
2. Growing pipeline (a system built up across chapters)
3. Tokens (pieces of text with their numbers)
4. Bars (how much)
5. Scatter (similarity as distance)
6. Grid (a table of shares)
7. Tiles (cases, doors, slots)
8. Frames, stepped (a few computed states)
9. Frames, animated (a move between computed states)
10. Svg: sequence, paired traces, a table of cases

---

## 1. Flow

- **For:** steps in order, or parts and how they connect.
- **Beats:** hook (the whole system at a glance), mechanism (the step this chapter is about, highlighted).
- **Learner role:** none; it frames the chapter.
- **Recipe:**

```yaml
figure:
  kind: flow
  parts:
    - {id: page, label: Page, row: 0}
    - {id: chunks, label: Chunks, note: cut from the page, row: 1}
    - {id: match, label: Match, row: 2}
    - {id: question, label: Question, row: 2}
  links:
    - {from: page, to: chunks, label: cut}
    - {from: chunks, to: match}
    - {from: question, to: match}
  highlight: [chunks]
```

- **Rules:** at most 9 boxes and 10 arrows, 2 highlighted; labels of 1 or 2 words, at most 3 parts per row (`self-checks.md` section 11).
- **Wrong pick when:** the point is how much, or how something moves (bars, frames, a scene).
- **Example:** `example-blueprint.yaml`, `search-pipeline`.

## 2. Growing pipeline

- **For:** a system the lesson builds one part per chapter. The learner sees it grow and always knows where the current part sits.
- **Beats:** across the mechanism chapters, from hook to payoff.
- **Recipe:** the first stage lists `grows_in`; each later chapter has its own diagram block with `extends` and only the parts it adds.

```yaml
# Chapter 1
- id: pipeline-tokens
  type: diagram
  grows_in: [tokens-to-meaning, attention]
  figure: {kind: flow, parts: [{id: text, label: Text, row: 0}, {id: tokens, label: Tokens, row: 1}], links: [{from: text, to: tokens}], highlight: [tokens]}
# Chapter 2
- id: pipeline-meaning
  type: diagram
  extends: {diagram: pipeline-tokens, adds: "Added: meaning vectors, one per token, so similar tokens sit close."}
  figure: {kind: flow, parts: [{id: vectors, label: Vectors, row: 2}], links: [{from: tokens, to: vectors}]}
```

- **Rules:** only flow figures grow; boxes never move between stages; `adds` names the change; the grown picture keeps the flow budget (`self-checks.md` section 13).
- **Wrong pick when:** the lesson is not about one system. Never promise a growing picture in prose.
- **Example:** `example-concepts-blueprint.yaml`, `pipeline-tokens` and the stages that extend it.

## 3. Tokens

- **For:** what a model or parser really receives: pieces with their numbers.
- **Beats:** hook, intuition.
- **Recipe:** `kind: tokens`, `rows` of `{label, tokens: [{text, id, hot}]}`, printed by `computed_by` from the real tokenizer (with `run_locally` when the tokenizer is not in the sandbox).
- **Rules:** at most 2 tokens hot (`self-checks.md` section 12).
- **Example:** `example-concepts-blueprint.yaml`, `real-tokens`.

## 4. Bars

- **For:** how much: a score, a share, a count, on one scale.
- **Beats:** proof, boundary.
- **Recipe:**

```yaml
figure:
  kind: bars
  max: 1
  bars:
    - {label: Your door, value: 0.33, note: 1 in 3}
    - {label: Door 2, value: 0.67, note: 2 in 3}
```

- **Rules:** number values; cannot grow; numbers from `computed_by` when the learner reads them (`self-checks.md` sections 11, 12).
- **Wrong pick when:** the shares must visibly move between bars as something happens (frames, animated; or a pour scene).

## 5. Scatter

- **For:** similarity as distance; clusters; where one thing sits among others.
- **Beats:** intuition, mechanism.
- **Recipe:** `kind: scatter`, `points` of `{label, x, y, group}`, axis labels for what each direction means, `toy: true` for a sketch, at most 2 highlighted.
- **Rules:** 2 to 12 points; `computed_by` required (`self-checks.md` section 12).
- **Wrong pick when:** the point moves because of other points (a pull scene).
- **Example:** `example-concepts-blueprint.yaml`, `meaning-map`.

## 6. Grid

- **For:** a table of shares from 0 to 1: attention, a confusion matrix, a correlation table.
- **Beats:** mechanism, proof.
- **Recipe:** `kind: grid`, `rows`, `columns`, `values` (one row per row label), `highlight_row`.
- **Rules:** at most 8 by 8; values from 0 to 1; `computed_by` required (`self-checks.md` section 12).
- **Example:** `example-concepts-blueprint.yaml`, inside `attention-grid`.

## 7. Tiles

- **For:** a row of cases in a state: doors, cups, cards, slots, servers. Groups frame "yours" against "the others".
- **Beats:** hook (the setup of a puzzle), transfer.
- **Recipe:**

```yaml
figure:
  kind: tiles
  tiles:
    - {label: Door 1, state: picked, note: yours, group: your pick}
    - {label: Door 2, state: closed, group: the others}
    - {label: Door 3, state: open, inside: goat, group: the others}
```

- **Rules:** at most 12 tiles; labels at most 10 characters; at most 2 hot (`self-checks.md` section 12).
- **Example:** `example-monty-blueprint.yaml`, `game-picture`.

## 8. Frames, stepped

- **For:** a change told by 2 to 8 computed states: a setting the learner slides (temperature, size, time) or separate cases the learner switches (two sentences).
- **Beats:** intuition, mechanism, boundary.
- **Learner role:** drive (slider or buttons).
- **Recipe:**

```yaml
figure:
  kind: frames
  control: slider            # slider for an ordered setting; buttons (at most 3) for separate cases
  control_label: Temperature
  computed_by:
    language: python
    code: |
      import json
      from toy_llm import NEXT_SCORES, softmax
      frames = [{"label": str(t), "figure": {"kind": "bars", "max": 1, "bars": [
                  {"label": w, "value": round(p, 2)} for w, p in zip(NEXT_SCORES, softmax(list(NEXT_SCORES.values()), t))]}}
                for t in [0.2, 0.7, 1.0, 1.5]]
      print(json.dumps({"frames": frames}))
  frames: []                 # filled from a real run
```

- **Rules:** 2 to 8 frames of one data kind; labels at most 12 characters; `computed_by` required (`self-checks.md` section 12).
- **Wrong pick when:** the learner must see how the change happens between states (animate it, or a scene).
- **Example:** `example-concepts-blueprint.yaml`, `attention-grid` (buttons).

## 9. Frames, animated

- **For:** a change whose movement is the point, between computed states: bars grow or shrink, tiles change state one after another.
- **Beats:** intuition, proof.
- **Learner role:** step.
- **Recipe:** a frames figure with `animate: true`, plus a `motion` answer on the block, and `animation` in `lesson.agreed_extras`.

```yaml
motion:
  changes: The other doors open one by one, and their chance gathers on the one door left.
  stays: Your door and its 1 in 10.
  why_not_still: A before and after shows where the chance ends up, but not that it comes from the doors the host opened.
  learner_does: step
```

- **Rules:** agreed first; the motion answer; `why_not_still` at least 8 words (`self-checks.md` section 14).
- **Example:** `example-monty-blueprint.yaml`, `ten-doors`.

## 10. Svg

Full `<svg viewBox="0 0 340 …" role="img" aria-label="…">` markup in the blueprint, drawn with the template's classes (`diagrams.md` section 7). Use it for three patterns:

- **Sequence** (actors passing messages over time: an agent and a tool, a server streaming): actors in a row, dashed lifelines down, solid calls, dashed replies, a frame for a loop. At most 4 actors and about 8 messages (`diagrams.md` section 5.3).
- **Paired traces** (two options on the same input, branching in space): exactly 2 traces, the same steps in the same order, one first-divergence marker in words (`diagrams.md` section 5.2).
- **A table of cases** (every way a game or rule can go, equally likely): one row per case, a column per outcome, ticks to count. **Example:** `example-monty-blueprint.yaml`, `cases-table`.

- **Rules:** `role="img"` and an `aria-label`; about 340 wide; classes only, never a colour by hand; cannot grow (`self-checks.md` section 11).
- **Wrong pick when:** a ready-made kind above draws it; the svg's numbers would be typed by hand (use a data kind with `computed_by`).
