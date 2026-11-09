# Components: trials

Where a learner must believe a number, they make it: deal or draw many times, fresh and random each time, and see their counts beside the expected share. A sceptic distrusts a table they were shown and trusts a count they made.

## Contents

1. Play block (deal and count)
2. Run control in a scene
3. Which one

---

## 1. Play block

- **For:** a chance or an average the learner doubts ("it's 50/50"), when each trial is just an outcome. The page deals from a case table that code worked out, and shows the learner's counts beside the expected share.
- **Beats:** proof (the learner's own evidence), boundary (deal again under a changed rule and watch the counts change).
- **Learner role:** run.
- **Recipe:**

```yaml
- id: deal-games
  type: play
  prompt: "Back to 3 doors and a host who knows. Deal 100 games and count who would win: staying with door 1, or switching."
  unit: games
  deals: [10, 100]
  outcomes:
    - {id: stay-wins, label: Staying wins, short: St}
    - {id: switch-wins, label: Switching wins, short: Sw, hot: true}
  computed_by:
    language: python
    code: |
      import json
      from monty import knowing_host_cases, sample
      cases = knowing_host_cases()
      print(json.dumps({"cases": cases, "sample": sample(cases, ["stay-wins", "switch-wins"], seed=7)}))
  cases: []                            # filled from a real run: [{label, weight, outcome}], weights add up to 1
  sample: {games: 100, seed: 7, counts: {}}   # one seeded deal, for screenshots and read-along only
```

The `computed_by` code usually lives in a `shared_modules` entry (here `monty`), so the cases are worked out once and every play block and table uses the same ones.

- **Rules:** agreed first (`play` in `lesson.agreed_extras`); 2 to 4 outcomes, each with a 1 or 2 character `short` so a dealt game never relies on colour; one outcome hot at most; the weights add up to 1, every case leads to an outcome and every outcome has a case (`self-checks.md` section 14).
- **Wrong pick when:** the learner already believes the number (it adds time and nothing else), or a trial has a shape worth seeing (a draw landing in a slice, a ball rolling to a bin): use a scene with a run control.
- **Example:** `example-monty-blueprint.yaml`, `deal-games`; `deal-knowing` and `deal-guessing` deal the same game under two rules, side by side.

## 2. Run control in a scene

- **For:** trials whose shape teaches: where each one lands, and how they pile up. The learner sets a control, then runs 10 or 100 trials and reads a one-line summary.
- **Beats:** proof.
- **Learner role:** run (often with drive).
- **Recipe:** add a run control to a scene and set `scene.run` in its script; `scenes.md` section 2 is a complete one.

```yaml
controls:
  - {id: draw, kind: run, label: Draw, trials: [10, 100], unit: words}
```

```js
scene.run = (trials, settings) => {
  const counts = words.map(() => 0);
  for (let t = 0; t < trials; t += 1) counts[sliceAt(scene.random(), oddsAt(settings))] += 1;   // one draw per trial
  counts.forEach((count, i) => scene.move(bins[i], { width: binWidth * count / trials }, { delay: i * 120 }));
  return words.map((word, i) => `${word} ${counts[i]}`).join(" · ") + ` (of ${trials} draws)`;
};
```

- **Rules:** `trials` are whole numbers from 1 to 1000, one button each; `scene.run` returns one line; use `scene.random()` so read-along and screenshots are the same every time (`self-checks.md` section 14).

## 3. Which one

| The trial… | Use |
|---|---|
| is just an outcome to count (win or lose, yes or no) | a play block: no script, cheaper |
| lands somewhere the learner should see (a slice, a bin, a slot) | a scene with a run control |
| depends on a setting the learner changes | a scene with a slider and a run control |
| should be compared under two rules | two play blocks, side by side, the same deal sizes |
