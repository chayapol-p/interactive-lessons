# Components: scenes

A scene is a picture written for one idea, with its own script, when no ready-made figure (`still-and-stepped.md`) carries the storyboard. Each recipe below is a pattern from `visual-design.md` section 6, built and checked on a real page: every step, every control value, light and dark, with motion and with reduced motion. Copy the one whose pattern fits, then change the layout, the data and the words for your idea.

A scene costs about 10–25k tokens. Propose it with its reason and cost, and build it only after a yes (`lesson.agreed_extras: [scene]`).

## Contents

1. The parts of every scene
2. Strip and draws: a setting drives the odds, then the learner runs trials
3. Travel along a path: each run reads everything (anime.js)
4. The same motion in GSAP
5. Pull: weights tug a point to their blend
6. Pour: a share leaves one place and fills another
7. Writing your own
8. Signs it is the wrong pick

---

## 1. The parts of every scene

```yaml
- id: SCENE-ID
  type: diagram
  shape: change-over-time          # the idea's shape
  brief: {understand: ..., how_it_helps: ..., clearer_than_text: ...}
  motion:                          # why it moves (visual-design.md section 1)
    changes: what moves or changes
    stays: the landmarks that never move
    why_not_still: what about the change a still picture cannot show, in 8 words or more
    learner_does: step             # step, bet, drive, run, puzzle or explore; it must match the controls
    breaks: a-misconception-id     # optional: the wrong belief the picture breaks
  figure:
    kind: scene
    height: 230                    # 120 to 480; the width is always 340
    library: anime                 # optional: anime or gsap; leave out to use scene.move only
    steps:                         # the storyboard, written before the script: one change per step
      - {label: Before, caption: Where to look in this step, about 25 words at most.}
    controls: []                   # optional, at most 2: slider, buttons, run
    computed_by: {language: python, code: "...prints {\"data\": ...}"}
    data: {}                       # filled from a real run of computed_by
    script: |
      // draws the scene; sets scene.show (and scene.run with a run control)
```

**The script's contract** (`visual-design.md` section 6 lists every helper):
- Build the elements once, at the top. Read every number from `scene.data`; never type one.
- `scene.show = (step, from, settings) => { ... }` draws the **whole state** of `step`, from any step: the learner can jump. Use `scene.move` (or `scene.play` with a library timeline) for anything that should move; it jumps when motion is reduced, on Back, and on the first draw.
- With a `run` control, `scene.run = (trials, settings) => { ... }` runs the trials with `scene.random()` and returns one line that sums them up.
- Every share or weight the end state uses is drawn. A blend whose parts do not add up on screen leaves the learner asking where the rest went.
- A share is never shown as 0% or 100% unless it is: show `<1%` and `>99%`, and store enough decimals in `computed_by` that a tiny share is not rounded to 0.
- Labels never sit on another dot or label: place each on its own dot's row, on the side away from the crowd, and move it down a row while it hits one. Give a label that a line may cross the `halo` class.
- Colour only through classes (`svg-box`, `svg-text`, `svg-line`, `svg-dot`, `svg-bar`, with `hot`, `dim`, `ghost`, `small`, and `halo` on text). A width that carries data goes in `element.style.strokeWidth`.

## 2. Strip and draws

- **Pattern:** one whole split into slices (a share or a chance); a slider sets the slices; a run button draws many times, and bins fill in proportion.
- **For:** a setting that reshapes odds (temperature, a threshold, a weight), then evidence the learner makes.
- **Beats:** intuition, proof. **Learner role:** run (with drive).
- **Breaks:** "it always gives the same answer", "a higher setting means smarter".
- **Blueprint:**

```yaml
steps:
  - {label: The strip, caption: "Each word gets a slice of the strip, as wide as its chance. Slide the temperature and watch the widths."}
  - {label: One draw, caption: "One reply is one draw: a random point on the strip. The word under it is the one written."}
  - {label: Many draws, caption: "Draw many times. Each word wins about as often as its slice is wide; the marks show where."}
controls:
  - {id: temperature, kind: slider, label: Temperature, values: ["0.2", "0.7", "1.0", "1.5"], start: 2}
  - {id: draw, kind: run, label: Draw, trials: [10, 100], unit: words}
computed_by:
  language: python
  code: |
    import json, random
    from toy_llm import NEXT_SCORES, softmax
    temperatures = ["0.2", "0.7", "1.0", "1.5"]
    # 6 decimals, so a tiny chance is never stored as 0
    odds = {t: [round(share, 6) for share in softmax(list(NEXT_SCORES.values()), float(t))] for t in temperatures}
    example_draw = round(random.Random(7).random() * 0.4, 3)   # lands in the top word's slice at every setting
    print(json.dumps({"data": {"words": list(NEXT_SCORES), "temperatures": temperatures, "odds": odds, "example_draw": example_draw}}))
```

- **Script:**

```js
// Layout: the strip on top, then one row per word with its share and a bin that fills with draws
const words = scene.data.words, temperatures = scene.data.temperatures;
const left = 20, right = 320, stripTop = 46, stripHeight = 34;
const rowsTop = 136, rowGap = 22, binLeft = 150, binWidth = 165;
const oddsAt = (settings) => scene.data.odds[temperatures[settings.temperature]];
// Which slice a point from 0 to 1 lands in
const sliceAt = (point, shares) => { let edge = 0; for (let i = 0; i < shares.length; i += 1) { edge += shares[i]; if (point < edge) return i; } return shares.length - 1; };

// A share as a percentage: a word that can still be drawn never shows 0%, and one that can still lose never shows 100%
function percentText(share) {
  if (share > 0 && share < 0.005) return "<1%";
  if (share < 1 && share > 0.995) return ">99%";
  return `${Math.round(share * 100)}%`;
}

// The strip: one slice per word; a label only where the slice is wide enough to hold it
scene.add("text", { x: left, y: stripTop - 10, class: "svg-text small" }, "All the odds, as one strip");
const slices = words.map((word, i) => scene.add("rect", { x: left, y: stripTop, width: 0, height: stripHeight, class: i === 0 ? "svg-box hot" : "svg-box" }));
const sliceLabels = words.map((word) => scene.add("text", { x: left, y: stripTop + 21, "text-anchor": "middle", class: "svg-text small", opacity: 0 }, word));
// The draw: a dot that drops onto the strip
const dot = scene.add("circle", { cx: left + (right - left) * scene.data.example_draw, cy: 14, r: 6, class: "svg-dot hot", opacity: 0 });

// One row per word: its name, its share, a bin for draws, and a mark where its share says draws should reach
const names = words.map((word, i) => scene.add("text", { x: left, y: rowsTop + i * rowGap, class: "svg-text" }, word));
const shareTexts = words.map((word, i) => scene.add("text", { x: 130, y: rowsTop + i * rowGap, "text-anchor": "end", class: "svg-text small" }, ""));
const bins = words.map((word, i) => scene.add("rect", { x: binLeft, y: rowsTop + i * rowGap - 11, width: 0, height: 12, class: "svg-bar" }));
const marks = words.map((word, i) => scene.add("line", { x1: binLeft, x2: binLeft, y1: rowsTop + i * rowGap - 14, y2: rowsTop + i * rowGap + 4, class: "svg-line hot", opacity: 0 }));

scene.show = (step, from, settings) => {
  const shares = oddsAt(settings);
  // The slices take their widths at this temperature; no word appears or disappears
  let x = left;
  shares.forEach((share, i) => {
    const width = (right - left) * share;
    scene.move(slices[i], { x, width });
    scene.move(sliceLabels[i], { x: x + width / 2, opacity: width >= 48 ? 1 : 0 });
    scene.write(shareTexts[i], percentText(share));
    x += width;
  });
  // Step 2: one draw lands in a slice, and that word lights up
  const hit = sliceAt(scene.data.example_draw, shares);
  scene.move(dot, { cy: step >= 1 ? stripTop + stripHeight / 2 : 14, opacity: step >= 1 ? 1 : 0 });
  names.forEach((name, i) => name.setAttribute("class", step >= 1 && i === hit ? "svg-text hot" : "svg-text"));
  // Step 3: the marks show where many draws should pile up; the bins empty for a fresh run
  marks.forEach((mark, i) => { const at = binLeft + binWidth * shares[i]; scene.move(mark, { x1: at, x2: at, opacity: step >= 2 ? 1 : 0 }); });
  bins.forEach((bin) => scene.move(bin, { width: 0 }, { duration: 300 }));
};

// Draw words: each draw is a random point on the strip; the bins fill with the share each word got
scene.run = (trials, settings) => {
  const shares = oddsAt(settings);
  const counts = words.map(() => 0);
  for (let t = 0; t < trials; t += 1) counts[sliceAt(scene.random(), shares)] += 1;
  counts.forEach((count, i) => scene.move(bins[i], { width: binWidth * count / trials }, { delay: i * 120 }));
  return words.map((word, i) => `${word} ${counts[i]}`).join(" · ") + ` (of ${trials} draws)`;
};
```

- **Example:** `example-concepts-blueprint.yaml`, `odds-bars`.

## 3. Travel along a path

- **Pattern:** travellers move along their own curves, staggered, into a place; a new thing rides a line that draws itself back. Uses anime.js (`svg.createMotionPath`, `svg.createDrawable`, `createTimeline`).
- **For:** information read, sent or fed back: tokens into a model, a request through services, a value through a loop.
- **Beats:** mechanism. **Learner role:** step.
- **Breaks:** "it plans the whole answer at once", "it remembers instead of re-reading".
- **Blueprint:** `library: anime`; steps "Text so far", "Run 1", "Run 2"; data `{prompt: [...], next: [...]}` from `computed_by`.
- **Script** (draw the whole state, then build a paused timeline for the move into this step and hand it to `scene.play`):

```js
// Layout: the text so far in a row at the top, the model below; each run reads every token and adds one
const { createTimeline, svg } = scene.anime;
const prompt = scene.data.prompt, next = scene.data.next;
const rowY = 32, model = { x: 120, y: 160, w: 100, h: 40 };
const chipWidth = (word) => Math.max(26, word.length * 6.6 + 12);
const centres = (words) => { const out = []; let x = 8; for (const w of words) { out.push(x + chipWidth(w) / 2); x += chipWidth(w) + 4; } return out; };
// A chip is drawn around (0, 0) inside a group, so it can travel by translate
function chip(word, isNew) {
  const group = scene.add("g", {});
  const width = chipWidth(word);
  group.append(scene.add("rect", { x: -width / 2, y: -11, width, height: 22, rx: 5, class: isNew ? "svg-box hot" : "svg-box" }));
  group.append(scene.add("text", { x: 0, y: 4, "text-anchor": "middle", class: "svg-text small" }, word));
  return group;
}

scene.show = (step) => {
  // The state after this step: the row holds the prompt plus one token per run so far
  scene.root.replaceChildren();
  scene.add("text", { x: 8, y: 12, class: "svg-text small" }, "Text so far");
  scene.add("rect", { x: model.x, y: model.y, width: model.w, height: model.h, rx: 8, class: "svg-box" });
  scene.add("text", { x: model.x + model.w / 2, y: model.y + 25, "text-anchor": "middle", class: "svg-text" }, "Model");
  const words = prompt.concat(next.slice(0, step));
  const read = words.slice(0, words.length - (step ? 1 : 0));
  const xs = centres(words);
  const target = { x: model.x + model.w / 2, y: model.y };
  const routes = step ? read.map((word, i) => scene.add("path", { d: `M ${xs[i]} ${rowY + 11} C ${xs[i]} ${rowY + 80}, ${target.x} ${target.y - 70}, ${target.x} ${target.y}`, class: "svg-line dim" })) : [];
  const chips = words.map((word, i) => scene.set(chip(word, step > 0 && i === words.length - 1), { transform: `translate(${xs[i]} ${rowY})` }));
  if (!step) return;
  // The last run, hidden until it plays: each token read travels its own curve in, then the new token rides back
  const end = { x: xs[xs.length - 1], y: rowY };
  const back = scene.add("path", { d: `M ${model.x + model.w} ${model.y + model.h / 2} C 330 ${model.y + model.h / 2}, ${end.x + 30} ${end.y + 70}, ${end.x} ${end.y}`, class: "svg-line hot", opacity: 0 });
  const dots = read.map(() => scene.add("circle", { cx: 0, cy: 0, r: 4, class: "svg-dot hot", opacity: 0 }));
  const newChip = scene.set(chips[chips.length - 1], { opacity: 0 });
  scene.root.append(newChip);
  // --- motion (anime.js) ---
  const timeline = createTimeline({ autoplay: false, defaults: { ease: "inOutQuad" } });
  dots.forEach((dot, i) => {
    const { translateX, translateY } = svg.createMotionPath(routes[i]);
    timeline.set(dot, { opacity: 1 }, i * 70);
    timeline.add(dot, { translateX, translateY, duration: 700 }, i * 70);
    timeline.add(dot, { opacity: 0, duration: 100 }, i * 70 + 600);
  });
  const way = svg.createMotionPath(back);
  timeline.set(back, { opacity: 1 }, "+=200");
  timeline.add(svg.createDrawable(back), { draw: ["0 0", "0 1"], duration: 900 }, "<<");
  timeline.set(newChip, { opacity: 1 }, "<<");
  timeline.add(newChip, { translateX: way.translateX, translateY: way.translateY, duration: 900 }, "<<");
  scene.play(timeline);
  // --- end motion ---
};
```

- **Example:** `example-concepts-blueprint.yaml`, `run-by-run`.

## 4. The same motion in GSAP

Pick GSAP when the author prefers its look or its eases. Set `library: gsap`, drop the first line that reads `scene.anime`, and swap the block between the motion markers:

```js
  // --- motion (GSAP) ---
  const timeline = scene.gsap.timeline({ paused: true, defaults: { ease: "power2.inOut" } });
  dots.forEach((dot, i) => {
    timeline.set(dot, { opacity: 1 }, i * 0.07);
    timeline.to(dot, { duration: 0.7, motionPath: { path: routes[i] } }, i * 0.07);
    timeline.to(dot, { opacity: 0, duration: 0.1 }, i * 0.07 + 0.6);
  });
  timeline.set(back, { opacity: 1 }, "+=0.2");
  timeline.fromTo(back, { drawSVG: "0%" }, { drawSVG: "100%", duration: 0.9 }, "<");
  timeline.set(newChip, { opacity: 1 }, "<");
  timeline.to(newChip, { duration: 0.9, motionPath: { path: back } }, "<");
  scene.play(timeline);
  // --- end motion ---
```

GSAP's MotionPathPlugin and DrawSVGPlugin load with it (`building-the-page.md` section 3). GSAP is free to use but not open source; anime.js is MIT.

## 5. Pull

- **Pattern:** lines from a point to several others, as thick as each one's weight; then the point slides to the weighted blend. Buttons switch the case.
- **For:** a weighted average, attention, a vote, a centre of mass.
- **Beats:** mechanism. **Learner role:** drive.
- **Breaks:** "a word has one fixed meaning", "every input counts the same".
- **Blueprint:** steps "Before", "The shares", "The pull"; a `buttons` control (here `sentence`) with one value per case. Data: `{name, control, start: [x, y], sentences: {<case>: {points: [{word, x, y, share}], self, end: [x, y]}}}`, where `self` is the point's share of itself (drawn as a ring, so every share the blend uses is on screen) and `end` is the weighted blend:

```yaml
computed_by:
  language: python
  code: |
    import json
    from toy_llm import MEANING, RIVER, MONEY, attention_row, after_attention
    sentences = {}
    for name, words in [("River", RIVER), ("Money", MONEY)]:
        shares = dict(zip(words, attention_row("bank", words)))
        # Words with meaning on the map get their own point; words about neither water nor money share one point
        content = [w for w in words if w != "bank" and max(MEANING[w][:2]) > 0]
        others = [w for w in words if w != "bank" and w not in content]
        points = [{"word": w, "x": MEANING[w][0], "y": MEANING[w][1], "share": round(shares[w], 2)} for w in content]
        points.append({"word": ", ".join(dict.fromkeys(o.lower() for o in others)), "x": 0.0, "y": 0.0,
                       "share": round(sum(shares[o] for o in others), 2)})
        end = after_attention("bank", words)
        sentences[name] = {"points": points, "self": round(shares["bank"], 2), "end": [round(end[0], 2), round(end[1], 2)]}
    print(json.dumps({"data": {"name": "bank", "control": "sentence", "start": MEANING["bank"][:2], "sentences": sentences}}))
```
- **Script:**

```js
// Pull: lines from one point to every other, as thick as its weight; then the point slides to the weighted blend
// The map: about water to the right, about money upwards, both from 0 to 1
const px = (x) => 50 + x * 240, py = (y) => 205 - y * 170;
scene.add("line", { x1: px(0), y1: py(0), x2: px(1.05), y2: py(0), class: "svg-line dim" });
scene.add("line", { x1: px(0), y1: py(0), x2: px(0), y2: py(1.08), class: "svg-line dim" });
scene.add("text", { x: px(1.05), y: py(0) + 34, "text-anchor": "end", class: "svg-text small" }, "about water →");
scene.add("text", { x: px(0) - 6, y: py(1.08) - 8, class: "svg-text small" }, "↑ about money");
const cases = Object.keys(scene.data.sentences);
const slots = Math.max(...cases.map((name) => scene.data.sentences[name].points.length));

// One line, dot and label per word, lines under dots; then the moving point, its own share as a ring, and its label
const lines = [...Array(slots)].map(() => scene.add("line", { x1: 0, y1: 0, x2: 0, y2: 0, class: "svg-line hot", "stroke-linecap": "round", opacity: 0 }));
const dots = [...Array(slots)].map(() => scene.add("circle", { cx: px(0), cy: py(0), r: 5, class: "svg-dot", opacity: 0 }));
const labels = [...Array(slots)].map(() => scene.add("text", { x: px(0), y: py(0), class: "svg-text small halo", opacity: 0 }, ""));
const start = { x: px(scene.data.start[0]), y: py(scene.data.start[1]) };
const selfRing = scene.add("circle", { cx: start.x, cy: start.y, r: 12, class: "svg-line hot", fill: "none", opacity: 0 });
const selfLabel = scene.add("text", { x: start.x, y: start.y + 28, "text-anchor": "middle", class: "svg-text small halo", opacity: 0 }, "");
const mover = scene.add("circle", { cx: start.x, cy: start.y, r: 7, class: "svg-dot hot" });
const moverLabel = scene.add("text", { x: start.x + 11, y: start.y + 4, class: "svg-text hot halo" }, scene.data.name);

// Two boxes overlap when neither is wholly left, right, above or below the other
function boxesOverlap(first, second) {
  const apart = first.x + first.width < second.x || second.x + second.width < first.x
    || first.y + first.height < second.y || second.y + second.height < first.y;
  return !apart;
}

// Place each label on its dot's row, on the side away from the map's middle; move it down a row while it hits
// a label already placed or another dot
function placeLabels(points) {
  const placed = points.map((point) => ({ x: px(point.x) - 6, y: py(point.y) - 6, width: 12, height: 12 }));
  points.forEach((point, i) => {
    const onLeft = point.x > 0.5;
    const x = px(point.x), y = py(point.y);
    scene.set(labels[i], { x: onLeft ? x - 9 : x + 9, y: y + 4, "text-anchor": onLeft ? "end" : "start" });
    for (const row of [0, 1, 2, 3]) {
      scene.set(labels[i], { y: y + 4 + row * 13 });
      const box = labels[i].getBBox();
      const hits = placed.filter((other, j) => j !== i && boxesOverlap(box, other));
      if (!hits.length) { placed.push(box); break; }
    }
  });
}

scene.show = (step, from, settings) => {
  // The case the learner picked, and where the point stands at this step
  const sentence = scene.data.sentences[cases[settings[scene.data.control]]];
  const where = step >= 2 ? sentence.end : scene.data.start;
  const moverX = px(where[0]), moverY = py(where[1]);
  scene.move(mover, { cx: moverX, cy: moverY }, { duration: 900 });
  scene.move(moverLabel, { x: moverX + 11, y: moverY + 4 }, { duration: 900 });

  // Every other word: its dot, its label, and a line from the point as thick as the word's share
  lines.forEach((line, i) => {
    const point = sentence.points[i];
    if (!point) { [line, dots[i], labels[i]].forEach((element) => scene.set(element, { opacity: 0 })); return; }
    scene.set(dots[i], { cx: px(point.x), cy: py(point.y), opacity: 1 });
    scene.write(labels[i], `${point.word} ${point.share}`);
    scene.set(labels[i], { opacity: 1 });
    line.style.strokeWidth = String(1.5 + point.share * 18);   // a style, so it wins over the class's width
    scene.move(line, { x1: moverX, y1: moverY, x2: px(point.x), y2: py(point.y), opacity: step >= 1 ? 0.55 : 0 }, { duration: 900 });
  });
  placeLabels(sentence.points);

  // The point's share of itself: a ring where it started, the part of its old meaning it keeps
  selfRing.style.strokeWidth = String(1.5 + sentence.self * 18);
  scene.write(selfLabel, `${scene.data.name} itself ${sentence.self}`);
  scene.move(selfRing, { opacity: step >= 1 ? 0.55 : 0 });
  scene.move(selfLabel, { opacity: step >= 1 ? 1 : 0 });
};
```

## 6. Pour

- **Pattern:** a place empties and its share pours into another; the outlines stay, and the total is shown as unchanged.
- **For:** a chance, a budget, a load or a probability mass moving between places.
- **Beats:** intuition, proof. **Learner role:** step.
- **Breaks:** "the two places left are now equal", "the opened place's share vanished".
- **Blueprint:**

```yaml
height: 220
steps:
  - {label: Before, caption: Each door holds a third of the chance.}
  - {label: The pour, caption: "The host opens door 3, and its share pours into door 2."}
  - {label: After, caption: "Door 2 now holds two thirds; the total never changed."}
computed_by:
  language: python
  code: |
    import json
    print(json.dumps({"data": {"places": ["Door 1", "Door 2", "Door 3"], "before": [0.333, 0.333, 0.333],
                                "after": [0.333, 0.667, 0], "flow": {"from": 2, "to": 1}, "total": 1}}))
```

- **Script:**

```js
// Pour: a share leaves one place and fills another, and the total stays visible
const places = scene.data.places, before = scene.data.before, after = scene.data.after, flow = scene.data.flow;
const cupWidth = 64, cupHeight = 120, cupTop = 40;
const gap = (scene.width - places.length * cupWidth) / (places.length + 1);
const cupLeft = (i) => gap + i * (cupWidth + gap);
const cupMiddle = (i) => cupLeft(i) + cupWidth / 2;
const fillTop = (share) => cupTop + cupHeight * (1 - share);

// Each place: an outline (the landmark), a fill as high as its share, its name, and its share above it
const cups = places.map((place, i) => scene.add("rect", { x: cupLeft(i), y: cupTop, width: cupWidth, height: cupHeight, rx: 4, class: "svg-box ghost" }));
const fills = places.map((place, i) => scene.add("rect", { x: cupLeft(i) + 3, y: fillTop(before[i]), width: cupWidth - 6, height: cupHeight * before[i], class: "svg-bar" }));
places.forEach((place, i) => scene.add("text", { x: cupMiddle(i), y: cupTop + cupHeight + 18, "text-anchor": "middle", class: "svg-text" }, place));
const shareTexts = places.map((place, i) => scene.add("text", { x: cupMiddle(i), y: cupTop - 10, "text-anchor": "middle", class: "svg-text small" }, ""));
const totalText = scene.add("text", { x: scene.width / 2, y: scene.height - 10, "text-anchor": "middle", class: "svg-text small", opacity: 0 }, "");

// The drop that carries the share from one place to the other
const drop = scene.add("circle", { cx: cupMiddle(flow.from), cy: fillTop(before[flow.from]), r: 7, class: "svg-dot hot", opacity: 0 });

scene.show = (step) => {
  // Step 1 pours: the drop travels across, then the fills settle at their new heights
  const shares = step >= 1 ? after : before;
  places.forEach((place, i) => {
    scene.move(fills[i], { y: fillTop(shares[i]), height: cupHeight * shares[i] }, { duration: 800, delay: step === 1 ? 600 : 0 });
    scene.write(shareTexts[i], `${Math.round(shares[i] * 100)}%`);
    cups[i].setAttribute("class", step >= 2 && shares[i] === 0 ? "svg-box dim" : "svg-box ghost");
  });
  const dropAt = step >= 1 ? flow.to : flow.from;
  scene.move(drop, { cx: cupMiddle(dropAt), cy: fillTop(shares[dropAt]) - 10, opacity: step === 1 ? 1 : 0 }, { duration: 700 });

  // Step 2: the total, which never changed
  scene.write(totalText, `All places together: ${Math.round(scene.data.total * 100)}%`);
  scene.move(totalText, { opacity: step >= 2 ? 1 : 0 });
  scene.say(`Shares: ${places.map((place, i) => `${place} ${Math.round(shares[i] * 100)}%`).join(", ")}`);
};
```

## 7. Writing your own

When no recipe fits, design it with `visual-design.md` (five questions, the change test, a role, a storyboard), then:
1. Write the steps' captions first; they must read well with no picture.
2. Write `computed_by` so every number comes from code.
3. Lay out the landmarks (what stays), then the actors (what moves).
4. Write `scene.show` as "the state of this step", then the move into it.
5. Build the page and have the scene reviewer check it (`lesson-review.md` section 5).

## 8. Signs it is the wrong pick

- A ready-made figure already carries the storyboard: frames for a few states, a play block for plain trials.
- The last frame alone teaches as much: use it as a still.
- More than about 4 things move at once, or it needs a control panel to make sense.
- The motion shows a process the real system does not have (steps that really happen together, memory it does not keep).
