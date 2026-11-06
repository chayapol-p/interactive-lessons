# Diagrams

A diagram earns its place only when it makes something clearer than words can. Decide that before drawing.

## Contents

0. The picture ladder: how much picture a moment needs
1. Write the brief first
2. Shapes that suit a diagram
3. Skip the diagram for
4. Cut first: density and highlights
5. Three patterns: growing pipeline, paired traces, sequence
6. Drawing rules
7. The figure: what the template draws
8. Where these rules come from

---

## 0. The picture ladder

Pick the lowest step that carries the idea. Each step up costs build time and the learner's attention, so it must buy understanding that the step below cannot.

| Step | Use it when |
|---|---|
| 0. Words | a definition or a single rule: a `glossary` entry or an `idea` |
| 1. Still | a structure or a list of cases: `flow`, `grid`, `svg`, `tiles` |
| 2. Stepped | a change the learner taps through: `frames`. **The default for any change.** |
| 3. Animated | the motion itself is the idea (a share sliding onto one door): `frames` with `animate: true` |
| 4. Play | the learner must believe a number, and only evidence they make will do: a `play` block |

**Steps 3 and 4 are asked for, never assumed.** In Discover (SKILL.md step 1), offer them for the named moments that need them, with the extra build time, and build them only on a yes. Record each yes in `lesson.agreed_extras` (`animation`, `play`); the checker refuses an animated picture or a play block without it.

- **Animated** (`animate: true` on a `frames` figure): a tap on a step moves from the last step to the new one: bars with the same label grow or shrink (0.7 s); tiles that change state change one after another, left to right, all within 2 s, so the eye can follow each door opening; anything else fades out, then in. Nothing plays by itself, "Play again" replays the last move, and with reduced motion the picture simply steps. Every number shown is a computed step's; only the motion between steps is drawn.
- **Play** (a `play` block): the learner deals 10 or 100 games from a case table that `computed_by` worked out, and sees their counts beside the expected share ("you: 64 of 100 · expected about 67"). Every deal is fresh and random, so the evidence is theirs; a seeded sample deal from the same code is kept for read-along, screenshots and tests. See `blueprint-format.md` section 3.
- Why ask first: an animation or a game that is not needed is decoration that costs the learner's time. When it is needed (a sceptic who will not believe 2 in 3 until they see it), nothing else will do.

## 1. Write the brief first

Every `diagram` block starts with three answers. Write them in the blueprint before any drawing. The checker requires all three, a `shape` from section 2 and a `figure` (section 7). It also checks growing diagrams and the budgets in section 4. The other drawing rules are judgement calls for step 5.

- **`understand`**: what the learner should understand after looking. One sentence.
  - Example: "Each chunk starts one stride after the previous one, so the shared part is the overlap."
- **`how_it_helps`**: how the picture produces that understanding. What is shown, and what is highlighted.
  - Example: "Chunks drawn as bars on alternating lanes along the page; the shared stretch is coloured."
- **`clearer_than_text`**: what the learner sees that a sentence would hide.
  - Example: "That the window moves less when overlap grows, and that the last chunk is short."

If any answer is vague ("shows the system", "makes it visual"), there is no diagram yet. Rewrite or drop it.

## 2. Shapes that suit a diagram

**Flow:** steps in order.
- Examples: a pipeline, the path of one request.
- Draw: boxes and arrows; highlight the step the chapter is about.

**Structure:** parts and how they connect.
- Examples: an architecture, a data model, a class hierarchy.
- Draw: grouped boxes; show only the parts this chapter needs.

**Change over time:** a state that moves.
- Examples: a sliding window, a pointer walking a list, a cache filling, an agent loop, a stream of tokens.
- Draw: one picture of a telling moment, or a sequence (section 5.3) when actors pass messages.

**Space:** distance, angle or position.
- Examples: embeddings, nearest neighbours, clusters.
- Draw: points or arrows in 2D, labelled as a simplified sketch.

**Comparison:** two choices on the same input.
- Examples: keyword vs vector search, two cleaning rules.
- Draw: paired traces with the first divergence marked (section 5.2).

**Quantity:** how numbers relate.
- Examples: a score built from parts, a trade-off.
- Draw: a simple bar chart.

## 3. Skip the diagram for

- Definitions and single rules: a sentence is faster.
- Syntax: show the code.
- Text transformations: a `compare` block with marked steps works better.
- Lists of things: a list.
- One-box "diagrams": write the sentence.
- Anything where the brief's `clearer_than_text` is empty.

## 4. Cut first: density and highlights

**The best edit to a diagram is usually a deletion.**

- Every box is a distinct idea. Two boxes that always travel together are one box.
- Every arrow carries information. If the layout already shows the relation, remove the arrow.
- A diagram is done when nothing more can be removed, not when everything is added.

**Target density: about 4 out of 10.** Complete enough to be true, sparse enough to read without a guide.

**Budgets** (checked for flow figures)
- At most **9 boxes** in the whole picture, counting every stage of a growing diagram. More than 9 is two diagrams.
- At most **10 arrows** in the whole picture.
- At most **2 highlighted boxes** per stage: the `highlight` list plus, on a later stage, the boxes it adds. If you want to highlight 4 things, you have not yet decided what this chapter is about.

## 5. Three patterns

Pick the pattern that matches the brief before you write the figure.

### 5.1 Growing pipeline (architecture delta)

**Use when:** several chapters each add one part to the same system.

**How**
- Draw the first stage in the first chapter that needs it, with `grows_in`. Each later chapter adds a stage with `extends: {diagram, adds}` and lists only the boxes and arrows it adds.
- **Keep the mental map stable.** A box never moves between stages; only new boxes appear. The template fixes every box's place from all stages, so the first stage leaves room for later ones.
- **Name the change.** `adds` is the change note: begin with what was added and say what it does ("Added: a cache in front of search, so a repeated question skips retrieval"). Never just "updated".
- Earlier boxes are muted; the boxes this stage adds are highlighted. That is the only colour signal.
- Budget: the grown picture stays within section 4 (9 boxes, 10 arrows). A bigger system is split into named parts, each its own diagram.

**Avoid:** redrawing each stage from scratch (boxes drift and seem to move); adding more than 2 boxes in one stage; a stage that only restyles.

### 5.2 Paired traces with the first divergence (compare choices)

**Use when:** two similar inputs or options reach different outcomes, and the point is where they first part ways.

**How**
- Usually a `compare` block, not a diagram: the same ordered steps for each option, with `differs_at` naming the first step that differs. Draw a diagram only when the steps branch in space (an `svg` figure).
- **Exactly 2 traces** is best; 3 to 6 steps each.
- Both traces list the same steps in the same order. Mark each step's state in words, not colour alone (for example "kept", "dropped", "not reached").
- **One first-divergence marker**, labelled. Do not highlight every later difference.
- If a trace stops early, the steps after it are "not reached". Never draw them as if they ran.

**Avoid:** two flows ordered differently; green and red dots without words.

### 5.3 Sequence (loops and streams)

**Use when:** actors pass messages over time: an agent calling a tool and reading its result, a server streaming tokens to a page, a retry.

**How** (an `svg` figure)
- Actors are boxes in one row at the top, each with a dashed lifeline running down. Time flows down.
- A call is a solid arrow between lifelines. Its reply is a **dashed** arrow back. A one-way event (a streamed piece, a fire-and-forget) is dashed with an open arrowhead.
- A loop or a branch is a frame around the messages it repeats, with a small label tab at the top left: `LOOP up to 4 steps`, `ALT tool error`.
- Highlight 1 or 2 messages: the one the chapter is about.
- Budget: at most 4 actors and about 8 messages. A longer exchange shows one pass of the loop inside the frame.

**Avoid:** free-floating if/else arrows instead of a frame; solid reply arrows; every message highlighted.

## 6. Drawing rules

- **One idea per picture.** If the brief needs two `understand` sentences, make two diagrams or cut one idea.
- **Labels sit on the parts they name,** not in a legend far away. Arrow labels are short (at most about 14 characters).
- **No arrow through a box it does not connect.** Move the box or the row instead.
- **No shadows, no glow, no colours of your own.** The template's tokens give both themes.
- **Say when it is a sketch.** Set `toy: true` on a figure whose numbers are made up; the caption then starts "Toy numbers." Simplified pictures of real data ("2D sketch; real embeddings have hundreds of numbers") say so in the caption.
- **Works in both themes,** and stays readable at phone width.

## 7. The figure: what the template draws

The page template draws every diagram from its `figure`. Pick the simplest kind that carries the brief.

**`kind: flow`** (flow, structure, growing pipeline): boxes in rows, joined by arrows.
- `parts`: `{id, label, row, note}`. `row` is 0 at the top; parts in one row spread evenly across it. Keep labels to 1 or 2 words and at most 3 parts per row, so it reads at phone width.
- `links`: `{from, to, label}`. The template draws every arrow at right angles with rounded corners: sideways within a row; otherwise out of one box's bottom (or top, for an arrow back up, such as a tool result), across a gap between rows, and into the other box.
  - Several arrows on one box edge each get their own attach point.
  - An arrow that crosses another arrow hops over it.
  - An arrow that cannot avoid a box it does not connect is drawn dashed. Treat that as a layout fault: move a part to another row.
  - A label (at most about 14 characters) sits on a small mask beside its arrow, clear of boxes, other arrows and other labels.
  - An arrow back up to an earlier row (a layer repeating, a token fed back in) runs dashed in a lane at the right edge. Several loops nest: the shortest loop takes the lane nearest the boxes, so loops never cross. Its label sits on the run into the box it returns to.
- `highlight` o: the part ids this chapter is about (at most 2, section 4).
- Growing: a later stage lists only the parts and links it adds (section 5.1).
- Avoid an arrow that crosses a box: put an input that joins a step (a question meeting a search) in the same row as that step.

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

**`kind: bars`** (quantity): horizontal bars with their values.
- `bars`: `{label, value, note}`; `max` o sets the scale (default: the largest value). `mark_below` o marks bars below that value in a second colour. A bars figure cannot grow.

**Data pictures** (numbers that a learner reads): their numbers come from `computed_by` code, never from hand (checked for scatter, grid and frames).
- **`kind: tokens`**: rows of chips, one per piece, each with its number. A leading space shows as a dot. Mark at most 2 chips `hot`.
- **`kind: scatter`** (space): labelled points on a plain 2D map, at most 12. Label the axes for what they mean, and say "toy" when the map is a sketch. The template places each label clear of the others.
- **`kind: grid`** (comparison, quantity): a shaded table, at most 8 by 8, each cell's shade and number its value from 0 to 1, with one row outlined (`highlight_row`). Shades come from the theme's checked ramp, so the number in every cell stays readable; values under 0.01 show as `<.01`. Column labels slant, so keep them to one short word. Suits attention, a confusion matrix, a correlation table.
- **`kind: frames`** (change over time): a `slider` for an ordered setting (temperature, size, time) or `buttons` for separate cases (two sentences), stepping through 2 to 8 saved states of one data kind. Button labels share one row: at most 3 buttons, each at most 12 characters. Every state is computed, so the picture never interpolates or invents a value. The page draws every step once and keeps the tallest one's height, so stepping never makes the page jump; keep step captions similar in length anyway.

```yaml
figure:
  kind: frames
  control: slider
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
  frames: []   # record_outputs.py fills this in
```

**`kind: tiles`** (structure, a list of cases; also a step inside `frames`): a row of labelled boxes, each in a state, for doors, cups, cards or slots.
- `tiles`: `{label, state, inside, note, group}`. `state` R is `closed`, `open` (dashed, its `inside` shown dim), `picked` (thick accent outline: the learner's choice) or `hot` (accent fill, at most 2). `label` R (at most 10 characters) sits at the top of the tile; `inside` o is the big word in the middle (default `?`, or empty when open); `note` o is a short word under it.
- Tiles with the same `group`, next to each other, share a dashed frame with the group's name above it (for "your door" against "the other two").
- At most 12 tiles: up to 6 sit in one row, and 7 to 12 sit in two even rows (10 tiles: two rows of 5). A group that runs onto the second row keeps one name, on its first frame. Inside `frames`, every step is a computed tiles figure, so a door opening is a new step, not a drawn effect.
- To show a big version of a small case (10 doors for 3), group "yours" against "the other 9" and open the other group's tiles in one animated step: the learner watches the whole group's chance gather on the one tile left.

```yaml
figure:
  kind: tiles
  tiles:
    - {label: Door 1, state: picked, note: yours}
    - {label: Door 2, state: closed}
    - {label: Door 3, state: open, inside: goat, note: opened}
```

**`kind: svg`** (sequence, paired traces, change over time, space): full `<svg viewBox=...>` markup written in the blueprint.
- Use the template's classes so both themes work: `svg-box` (with `hot`, `dim`, `ghost`), `svg-text` (with `small`, `dim`, `hot`), `svg-line` (with `hot`, `dim`), `svg-arrowhead`, `svg-bar`, `svg-grid`, `svg-overlap`, `svg-group` (a dashed frame, for a sequence's loop). For a dashed reply or lifeline, add `stroke-dasharray="5 4"` to the line.
- Give the `<svg>` a `role="img"` and an `aria-label` that says what it shows. Keep the `viewBox` about 340 wide. An svg figure cannot grow; use a flow figure for a diagram that grows.

Check every figure in the phone screenshots, light and dark (SKILL.md step 5).

## 8. Where these rules come from

Sections 4 and 5 are adapted from the **diagram-design** skill: its deletion-first philosophy and density target, and its architecture delta, paired policy-evaluation traces and sequence types.

**Borrow from it at design time, never at build time.**
- At design time (step 3, Plan), you may read diagram-design's references for a pattern this file does not cover, then write the figure in this skill's format.
- During a build, never call diagram-design. Its first-run style check stops to ask the user a question, which halts an unattended build. Its output is a separate HTML page, not inline SVG that uses this template's theme classes.
