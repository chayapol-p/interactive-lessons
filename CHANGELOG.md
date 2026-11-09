# Changelog

## 0.5.0 · 9 Nov 2026
**Two editions.** `main` is the directory edition: the plugin holds only Markdown, YAML, JSON and images, and agents do what the scripts did. The scripted edition moves to the `full` branch, and the GitHub install points there. Both make the same lessons.

- **No scripts in the plugin.** Recording results, building the page and checking it become steps the agent follows: `references/building-the-page.md` (record every result with the agent's own code tool, fill the template), `references/self-checks.md` (every checker rule as a checklist) and `references/lesson-review.md` (three fresh reviewers: content, learner, scenes and layout; a self-check where agents cannot start, said plainly).
- **The page template is Markdown:** `assets/page-template.md`, one html block with two placeholders. The page now works out the theme's colours itself from `theme.accent`, with the same contrast checks, and keeps Ink blue if an accent fails (`references/theme.md`). `example-monty-cases.py` is gone; its tables stay in the Monty blueprint.
- **A component catalogue** in `references/components/`: every block, figure, scene recipe and page part, each with what it is for, its story beat, the learner's role, a recipe, its rules and when it is the wrong pick.
- **A topic map** (`references/topic-map.md`): for 11 kinds of topic, the component that carries each beat from hook to payoff, and the moving picture most worth proposing.
- **`references/principles.md`:** why each rule exists, with its sources.
- **Pictures are designed from the idea, not picked from a menu.** `references/visual-design.md`: five questions per key idea, congruence, the change test, six learner roles, storyboards, cost, and the research behind each rule.
- **Scenes:** a picture written for one idea, with learner-paced steps, up to 2 controls (slider, buttons, run), every number from `computed_by`, and a script that sets `scene.show`. A scene may name a motion library, anime.js (MIT) or GSAP, loaded from jsDelivr only when asked. `components/scenes.md` gives 5 ready scenes, each checked on a real page: strip and draws, travel along a path (anime.js and GSAP), pull, pour.
- **Motion is asked for with its cost:** Discover asks how much motion with a recommendation; the chapter map lists each proposed moving picture with its reason and token cost. `motion` is required on every moving picture.
- `play` gains `unit` ("Deal 100 replies"). The LLM example's temperature picture is a scene, and it adds a run-by-run scene in anime.js.

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
