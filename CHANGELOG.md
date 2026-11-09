# Changelog

## 0.5.0 · 9 Nov 2026
- Pictures are designed from the idea, not picked from a menu. New `references/visual-design.md`: five questions for every key idea (what is hidden, what changes and what stays, why a still would fail, which wrong belief it breaks, what the learner does), congruence between the picture and the idea, the change test (motion only where the manner of change must be learned), six learner roles (step, bet, drive, run, puzzle, explore), storyboards, and the research behind each rule (Tversky; Höffler and Leutner; Berney and Bétrancourt; Ploetzner; Mayer; Heer and Robertson; Bret Victor; Nicky Case; 3Blue1Brown; Kurzgesagt; Transformer Explainer).
- New figure kind `scene`: a picture written for one idea, with learner-paced steps, up to 2 controls (slider, buttons, or run for trials), every number in `data` printed by `computed_by`, and a script that sets `scene.show` (and `scene.run`). `scene.move` eases attributes, slow in and slow out, and jumps when motion is reduced. Each scene is its own `<script>`, and a scene that throws shows its steps as words.
- New `motion` field, required on every moving picture: what changes, what stays, why a still would fail (at least 8 words), what the learner does, and the misconception it breaks. The checker matches the role to the controls.
- New `scripts/check_scenes.py`: taps through every step and control of every scene, light and dark, with and without motion; fails a scene that throws, draws outside its box, shows a number its data does not hold, repeats a step, or lands somewhere else with motion than without; saves one image per step. `tests/check_scene_breaks.py` proves it catches each break.
- Asking about motion now comes with a suggestion and its token cost: Discover asks how much motion, and the chapter map lists each proposed moving picture with its reason and cost. `lesson.agreed_extras` gains `scene`.
- Scenes may name a motion library: `library: anime` (anime.js 4, MIT) or `library: gsap` (GSAP 3 with MotionPath and DrawSVG). The page loads it from jsDelivr only when a scene asks; `scene.play(timeline)` plays a timeline learner-paced and jumps to the end when motion is reduced, on the first draw and on Back. A scene whose library cannot load shows its steps as words. `visual-design.md` adds motion patterns: travel along a path, draw a line, pour, pull, stagger, hold.
- The LLM example adds "Run by run" (anime.js): every token travels into the model on each run, and the new one rides a curve back. `tests/check_scene_breaks.py` proves the same scene written in GSAP passes too. `check_scenes.py` and `screenshot_chapters.py` take `--libraries` to serve the libraries locally.
- `play` gains `unit` ("Deal 100 replies").
- The LLM example's temperature picture is now a scene: a strip of odds, one draw, then the learner sets the temperature and draws 10 or 100 words.
- The Monty Hall example's two animated pictures carry their motion answers.

## 0.4.1 · 8 Nov 2026
- The plugin now lives in its own folder, `plugin/`. The marketplace file at the repo root points there, so the install command is unchanged, and the README's picture tools in `docs/` are no longer part of the plugin.
- The plugin has an icon: a filled-in blank, ticked in red pen.
- The word-piece picture in the template calls each piece `piece`, so no name inside the page's code looks like a credential.

## 0.4.0 · 6 Nov 2026
- One Check button on fill-the-blanks: the verdict and where each pick leads, together.
- Stepped pictures keep their tallest step's height, so the page never jumps.
- Test, then reveal: a "Spot the mistake" question comes before its common-mistake card, which opens once it is answered (the checker's order rule is flipped).
- The key idea after "Your guess" stays folded until the guess is made, with a Skip button.
- The picture ladder: words, still, stepped (the default for a change), animated and play. Animated and play are offered in Discover for named moments and built only on a yes (`lesson.agreed_extras`).
- New `tiles` figure: labelled boxes that are closed, open, picked or hot (doors, cups, cards), alone or as steps.
- `animate: true` on frames: a tap moves between computed steps in 0.7 s, with Play again; reduced motion steps instead.
- New `play` block: deal 10 or 100 games from a computed case table and see your counts beside the expected share. The checker proves the cases and a seeded sample, and that the weights add up to 1.
- The lesson arc: `lesson.big_idea`, and per chapter a `beat` (hook, intuition, proof, mechanism, boundary, transfer, payoff), a `milestone` and an `open_question` the next chapter answers.
- The page shows a journey strip with "You are here", ends each chapter on its open question, keeps "Why it matters" to the start page, and opens the field guide with the big idea.
- New checks: the text budget (ideas 2 sentences and about 45 words, one-sentence feedback, captions about 25 words), no early answers, no copying into a blank, and fair option lengths. The three examples were trimmed to pass.
- Stay or Switch? rebuilt as one story in 5 chapters (about 25 minutes): The game · Feel it · Why · When it fails · Use it. Doors as tiles, 100 doors, Deal 100 games (both hosts), the 67 sliding onto door 2, and a 4-answer quiz to carry the idea to a new case; it ends by answering the first question.
- A chapter with no exercises shows as done only when its quizzes are answered right.
- From the first user-test round: a phone viewport tag (a phone opened the file at desktop width), glossary words that keep their comma, a key above dealt games, a self-check that counts as done without the tutor, and tiles that change one at a time (10 doors opening in turn).
- From the second round: `hold: true` keeps the opening guess unmarked until the last chapter brings it back; a deal shows how far a fair deal wanders (most deals 57 to 76); hover styles only with a mouse; punctuation stays with a glossary word.
- From the third round: the first guess comes back only after the last written answer; "You can now…" only after a goal's last test; the progress bar follows the work as it happens; a group that runs onto a second row is one outline; plainer spread wording ("usually between 57 and 76").
- `scripts/phone_driver.py`: the user-test access path (a phone page kept open per tester).
- `tests/check_page_clicks.py` clicks through the examples (blanks, two wrong blanks, folded cards, steady steps, tutor).

## 0.3.1 · 5 Nov 2026
- VISION and SKILL now say the same thing: any subject, the default learner, checks after teaching, bridges, diagram limits.
- The skill's description names any subject, so non-code requests trigger it.
- The repo installs as a Claude Code plugin marketplace.
- A small 3-chapter example, Stay or Switch? (the Monty Hall problem). It teaches why switching wins 2 in 3: every case listed, the chance moving onto one door, and what the host knows.

## 0.3.0 · 5 Nov 2026
- A colour per learner, built by `scripts/theme.py`; right, wrong and answer-shown colours stay fixed.
- A calmer page: plain labels, one box per action, right and wrong shown by mark and word, not colour alone.
- Phone-proof pictures: slanted grid labels, frame buttons on one row, nested loop arrows.

## 0.2.0 · Nov 2026
- Any subject: text blanks, and data pictures (tokens, scatter, grid, frames) computed by code.
- Test the idea, not the example; assume, then confirm.
- The tutor sends on Enter and renders Markdown.
