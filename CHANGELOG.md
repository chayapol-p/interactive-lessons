# Changelog

## 0.4.0 · unreleased
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
