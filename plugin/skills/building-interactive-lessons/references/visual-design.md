# Visual design: find what moves, then build the picture for it

How to decide what a key idea should look like, whether it should move, and what the learner does with it. This is a way of thinking, not a menu. The figure kinds in `diagrams.md` are ready-made parts that are cheap to use; when none of them carries the idea, write a **scene** (section 6): a picture made for this one idea.

## Contents

0. Why a method, not a menu
1. Five questions for every key idea
2. Match the picture to the idea (congruence)
3. Does it need to move? The change test
4. What does the learner do? Pick a role
5. Storyboard before code
6. Build it: a ready-made figure, or a scene
7. Cost, and asking the author
8. Rules every moving picture keeps
9. Signs a picture is not working
10. Where these rules come from

---

## 0. Why a method, not a menu

A fixed list of picture types makes every lesson look the same, and it pushes an idea into whatever shape the list has. A card deal suits a game of chance; it does not suit a model choosing its next word, even though both are about chance.

Research gives a sober starting point: across three meta-analyses, animation beats still pictures only a little on average (about g = 0.23). The gain is large in one case: when the learner must learn **how** something changes (its order, its path, its timing, how much goes where). When only the start and the end matter, still pictures do as well. So the question is never "can this move?" but "**what about this change must the learner see?**"

## 1. Five questions for every key idea

Answer these for every `key: true` idea before choosing a picture. Write the answers in the diagram's `brief`, and, for anything that moves, in its `motion` field (`blueprint-format.md` section 3).

1. **What is hidden?** The process, state or quantity that words cannot show at once. Examples: a share flowing from several sources into one place; the order in which steps happen; every case of a game at once; a setting and the outcome it drives.
2. **What changes, and what stays?** Name the **actors** (the things that move or change) and the **landmarks** (the things that never move: an axis, a frame, the input text). The learner reads change against what stays.
3. **Why would a still picture fail?** Apply the change test (section 3). If a still picture would do, use one.
4. **Which wrong belief does the picture break?** Name the misconception. The best picture shows the moment where the wrong belief predicts one thing and the picture shows another.
5. **What does the learner do?** Pick a role (section 4). Watching alone is the weakest role; use it only when the order of events is the whole point.

## 2. Match the picture to the idea (congruence)

The structure of the picture should match the structure of the idea. Before drawing, say which of these the idea is, and use the matching visual language:

| The idea is about… | Show it as… |
|---|---|
| order of events | left to right or top to bottom, one event per step |
| how much | length or area, on one shared scale |
| a share or a chance | one whole split into parts (a bar, a strip, a pie of fixed size) |
| similarity | distance |
| flow of information or material | paths, with the moving thing travelling along them |
| something fed back | a loop that returns to an earlier place |
| a choice and its result | a branch, with the path not taken still visible |
| many cases at once | small copies side by side, the same in every way except the case |

- **Start concrete.** Show the lesson's own example first, then the general case (a single sentence before "any sentence"; three doors before n doors).
- **A metaphor must carry the mechanism.** A good one keeps the cause-and-effect of the real thing: water pouring into cups for shares, a magnet pulling a point. A metaphor that looks nice but moves differently from the real process teaches the wrong process.
- **Never imply a process that is not there.** If things happen at the same time, they move at the same time; if the real system has no memory, the picture shows nothing carried over.

## 3. Does it need to move? The change test

Ask what the learner must take away about the change:

- **Only the before and the after** → a still picture, or two states side by side. Motion adds little here.
- **The manner of the change** (what moves where, in what order, how much, how fast, continuous or in jumps) → motion, in learner-paced steps.
- **How an outcome depends on a setting** → let the learner drive the setting and watch the outcome react at once.
- **A number the learner will not believe from a table** → let them make the evidence: run trials and count.
- **A whole space of behaviour** → go up the ladder of abstraction: one concrete case, then sweep one setting, then show many cases at once.

When in doubt, choose the still picture and say in the brief what motion would add. The author can ask for it.

## 4. What does the learner do? Pick a role

Every interaction comes with a question the learner answers by doing it. Activity without a question teaches nothing.

| Role | Use it when | The learner's question |
|---|---|---|
| **Step through** | the order of events is the idea | "What happens next?" |
| **Bet, then see** | the idea has a clear right answer that surprises | "Where will it land?" (they guess, then the picture moves) |
| **Drive** | the idea is a relation between a setting and an outcome | "What happens if I turn this up?" |
| **Run trials** | the idea is a chance or an average | "Is it really about 60 in 100?" |
| **Puzzle** | the topic can be modelled exactly | "Can I make it reach this target?" |
| **Explore** | last, after every part has been taught | the learner's own questions |

- A role can grow across a chapter: step through it once, then drive it.
- An open sandbox is never the explanation. It comes after the pieces, if at all.
- In "bet, then see", the guess is a `predict` block just above the picture, or a control the learner sets before pressing a button.

## 5. Storyboard before code

Write the steps first, as words, in the figure's `steps`. Draw only once the words read well on their own.

- **One change per step.** 2 to 8 steps. A step that changes nothing is cut.
- **Each step has a caption** that says where to look (about 25 words). The caption is the signal; the picture is the evidence.
- **Learner-paced.** Back and Next, never autoplay. A "Play again" replays the last move.
- **Stage a complex change.** Move first, then recolour, then relabel. Do not move and rescale at the same time.
- **Keep identity.** An actor keeps its shape, colour and label across steps, so the eye can track it. Never morph one thing into an unrelated thing: the eye reads it as "this became that".
- **Few movers.** At most about 4 things move at once; dim the rest. When many must move, stagger them so the eye can follow each one.
- **Slow in, slow out.** Each move eases in and out, about 0.4 to 1.2 s.
- **Every state is computed.** The numbers in each step come from `computed_by`; only the motion between steps is drawn.

## 6. Build it: a ready-made figure, or a scene

**Ready-made figures** (`diagrams.md`): flow, bars, tokens, scatter, grid, tiles, frames. Cheap to write and already tested. Use one when it carries the storyboard as it is.

**A scene** (`figure.kind: scene`): a picture written for this idea, with its own script. Use it when the storyboard needs something no ready-made figure does: an actor that travels along a path, a share that pours from several places into one, a token that drops into its bin after a draw, a point pulled by several weights.

How a scene works (`blueprint-format.md` section 3 has every field):
- `steps` hold the storyboard: a label and a caption per step.
- `data` holds every number the scene shows, printed by `computed_by`.
- `controls` (optional) are a slider or buttons the learner sets, and a `run` button for trials.
- `script` is JavaScript that draws the scene. It gets one object, `scene`, and sets `scene.show`:

```js
// scene.root: an empty <svg> 340 wide and scene.height tall; scene.data: the recorded data
const words = scene.data.words;
const dots = words.map((word, i) => scene.add("circle", { cx: 40 + i * 60, cy: 120, r: 8, class: "svg-dot" }));
scene.show = (step, from, settings) => {
  // Draw the state of `step`. It must work from any step (the learner can jump), and it must end in the same
  // picture with or without motion: scene.move animates when allowed and jumps when motion is reduced.
  dots.forEach((dot, i) => scene.move(dot, { cy: step >= 1 && i === 2 ? 60 : 120 }, { delay: i * 120 }));
};
```

What `scene` gives the script:
- `scene.root`, `scene.width` (340), `scene.height`, `scene.data`
- `scene.add(tag, attributes, text)`: adds an SVG element to the root and returns it
- `scene.move(element, attributes, {duration, delay})`: eases numeric attributes (x, y, cx, cy, r, width, height, opacity, x1…y2) to new values; jumps when motion is reduced
- `scene.write(element, text)`: sets a label's text
- `scene.set(element, attributes)`: sets attributes at once, with no motion
- `scene.random()`: a random number; seeded in read-along, so screenshots are the same every time
- `scene.say(text)`: tells a screen reader what just changed
- `scene.show(step, from, settings)` (you set it): draw the step; `from` is the step before (undefined on first draw); `settings` maps each control id to its chosen index
- `scene.run(trials, settings)` (you set it, only with a `run` control): run trials and return one line that sums them up

Classes for colour (both themes work): `svg-box` (with `hot`, `dim`, `ghost`), `svg-text` (with `small`, `big`, `dim`, `hot`), `svg-line` (with `hot`, `dim`), `svg-dot` (with `hot`, `dim`), `svg-bar`, `svg-group`. Never set a colour by hand. A class also sets a stroke width, which beats a `stroke-width` attribute; to make a width carry data (a line as thick as a share), set `element.style.strokeWidth`.

`scripts/check_scenes.py` opens each scene, steps through every step and every control value, light and dark, with and without motion. It fails a scene that throws, draws outside its box, shows a number its data does not hold, has two steps that look the same, or ends a step in a different picture with motion than without. It also saves one image per step, so you can read the scene like a comic strip.

## 7. Cost, and asking the author

Moving pictures cost the author tokens and time. Rough guide (an estimate; it varies with the idea):

| Picture | Extra cost on top of a plain lesson |
|---|---|
| still or stepped, ready-made | small: part of the normal plan |
| animated frames (`animate: true`) | about 2–5k tokens |
| a play block (deal and count) | about 3–6k tokens |
| a scene | about 10–25k tokens and 10–20 minutes each, with checks and fixes |

**Ask with a suggestion, never silently.**
- **Discover** asks one question about motion, with your recommended answer first. For example: "Moving pictures where they teach something a still picture can't (recommended; I'll suggest them in the plan, about 10–25k extra tokens each)", "Stepped pictures only (cheapest)", or "Rich: scenes and trials wherever they fit".
- **Plan** lists each proposed moving picture in the chapter map: the moment, the change test answer (why a still picture fails), the learner's role, and its cost. The author keeps or drops each one.
- Record what was agreed in `lesson.agreed_extras` (`animation`, `play`, `scene`). The checker refuses a moving picture that was not agreed.
- **Unattended run:** build stepped pictures only, and list the proposed scenes with their reasons in the work log.

## 8. Rules every moving picture keeps

Checked by `check_blueprint.py` or `check_scenes.py` where marked.
- It has a `motion` answer: what changes, what stays, why a still picture fails, and what the learner does **(checked)**.
- It was agreed in Discover or Plan **(checked)**.
- Every number it shows comes from its data **(checked by check_scenes.py)**.
- Steps are learner-paced and nothing plays by itself; reduced motion jumps to the same end picture **(checked by check_scenes.py)**.
- It fits 340 by its height, readable at phone width, in both themes **(checked by check_scenes.py)**.
- Each step changes something visible **(checked by check_scenes.py)**.
- Its caption names where to look, within the text budget **(checked)**.

## 9. Signs a picture is not working

- **Motion as decoration.** Things move, but the learner learns nothing they could not get from the last frame. Use the last frame as a still.
- **Too much at once.** More than about 4 things move together, or the move and the relabel happen together. Stage it.
- **A process that is not there.** The picture shows steps happening one after another when they really happen together, or shows memory the system does not have.
- **The sandbox dump.** A rich control panel with no question. Add the question, or cut the panel.
- **Typed numbers.** A number written into the script instead of read from `scene.data`.
- **A drift in identity.** The same thing changes colour or shape between steps for no reason, so the learner loses track of it.

## 10. Where these rules come from

- Tversky, Morrison and Bétrancourt (2002), *Animation: can it facilitate?*: the congruence principle (the picture's structure matches the idea's) and the apprehension principle (it must be perceived accurately: slow, clear, in steps).
- Höffler and Leutner (2007), Berney and Bétrancourt (2016), Castro-Alonso et al. (2019): small average gains for animation; Ploetzner, Berney and Bétrancourt (2020, 2021): large gains when the specifics of a change must be learned, none when only simple change is involved.
- Mayer, *Multimedia Learning*: the segmenting principle (learner-paced steps), signaling (cue where to look), coherence (cut what does not teach).
- Heer and Robertson (2007), *Animated Transitions in Statistical Data Graphics*: object constancy, staged transitions, keep landmarks, avoid rescaling mid-move, slow in and slow out.
- Bret Victor (2011), *Explorable Explanations* and *Up and Down the Ladder of Abstraction*: reactive documents, explorable examples, one case → a sweep → the whole space.
- Nicky Case (2018), *Explorable Explanations: 4 More Design Patterns*: puzzle it out, place your bets, role play, sandbox; activity alone does not teach.
- Grant Sanderson (3Blue1Brown): start with a motivating concrete example before the general idea; precise, programmatic pictures.
- Kurzgesagt, *How to Make a Kurzgesagt Video*: choose a visual metaphor and the transitions between ideas per scene, and decide which scenes need the most attention.
- Cho et al. (2025), *Transformer Explainer*: follow one input through the system, and let the learner change the input and settings and see the result.
