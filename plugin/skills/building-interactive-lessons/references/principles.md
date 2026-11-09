# Principles: why a lesson is built this way

The rules behind every step, each with the reason and where it comes from. Read this when a rule seems to get in the way: the reason says what the rule protects, so you can tell a real exception from a shortcut.

## Contents

1. The learner does the thinking
2. Plan before building
3. Tests that match the claim
4. One story, connected
5. Short steps, nothing given away
6. Pictures from the idea
7. Everything real
8. The learner's choice, the lesson's care
9. Checked by someone who did not write it
10. Sources

---

## 1. The learner does the thinking

- **Learners produce, not only read.** Every chapter asks for a prediction, a filled blank or an answer in the learner's own words. *Why:* learners who only read and tap through demos cannot explain the idea afterwards; making something forces them to build their own model. *From:* PRIMM (a 13-school study), Mayer's generative activity principle.
- **Predict first, with confidence.** A chapter opens with a guess and asks how sure the learner is. *Why:* a confident wrong guess is the moment a learner is most ready to change their mind, and confidence shows where a shaky idea feels solid.
- **Wrong answers teach.** Every wrong option is a real misconception with its own one-line reason; a wrong blank shows what it really leads to. *Why:* a bare "wrong" teaches nothing; naming the specific mistake repairs the specific misunderstanding.
- **Learners make the evidence.** Where a learner must believe a number, they make it: deal 10 or 100 trials and count. *Why:* a sceptic distrusts a table they were shown and trusts a count they made.

## 2. Plan before building

- **Assume, then confirm.** Draft the learner from what is known (memory, the conversation, past work), show where each guess came from, and confirm it with at most 4 questions. *Why:* a blank profile wastes the learner's time; an unchecked guess teaches the wrong level.
- **The plan is data.** Discover the learner, verify the material, then plan the chapters as a blueprint. The page is filled from a shared template, never written by hand. *Why:* most weak lessons fail in their structure, not their styling; a blueprint can be checked before any page exists, and a shared template gives every lesson the same tested behaviour.
- **Separate confirmed from inferred.** Every fact says whether a source or a run confirms it. *Why:* a lesson that teaches a wrong fact with confidence does lasting damage.

## 3. Tests that match the claim

- **Every chapter states what the learner must get right, and how we will know.** Each goal names the check, blank or explain exercise that tests it, placed after the teaching. *Why:* a recall quiz cannot show that a learner can apply an idea; if you cannot name the test, the chapter is not ready.
- **Quizzes only where they earn their place.** Quiz key ideas and pitfalls, at most 2 per chapter. *Why:* quizzes on trivia train trivia.
- **Test the idea, not the example.** Explain an example before using it, and never ask for its details, such as a clause number. *Why:* a question about a rule number tests memory of the example, not the idea.
- **Test, then reveal.** A "spot the mistake" question comes before the card that explains the mistake. *Why:* a card read first hands over the answer; a card read after a try explains the learner's own choice.

## 4. One story, connected

- **One story, with milestones.** A big idea, told in beats from hook to payoff; each chapter ends on an open question the next one answers. *Why:* learners who follow one question keep the answer and the reason; chapters read as separate topics are forgotten as separate topics.
- **Chapters connect the dots.** Each chapter names what it brings in and what it carries forward, with the blocks that show each idea. A bridge names only what its blocks really show. *Why:* a chapter that floats alone loses its reason to exist.
- **End with a field guide.** Every chapter's recap goes into a one-page field guide, with the places the learner was confident but wrong. *Why:* the field guide is what the learner keeps.

## 5. Short steps, nothing given away

- **One idea per block.** At most 2 sentences and about 45 words; feedback one sentence; a caption about 25 words. *Why:* short, learner-paced segments are easier to absorb than a long stream.
- **Nothing gives the answer early.** No title, goal, milestone or caption shows a guess's answer; a blank's answer is not in the block above it; the right option is never the longest. *Why:* in early tests, learners read the answer while scrolling to the question, and the guess stopped being a guess.
- **Real material, small.** A code slice is the real code that carries the idea, at most 15 lines, with line comments; a text exercise is the real sentence, rule or formula. Never pad. *Why:* a whole repo buries the idea; blanks on the key tokens test the idea itself.
- **Show what makes choices different.** Compare options on the same input and name the first step where they part ways. *Why:* a before and after shows that something changed, not why one choice behaves differently.

## 6. Pictures from the idea

- **A diagram needs a purpose first.** Say what it makes clear, how, and what a sentence would hide; then cut it to the fewest boxes. *Why:* a decorative diagram costs attention and teaches nothing.
- **Design each picture from the idea.** Five questions per key idea (what is hidden, what changes and what stays, why a still would fail, which wrong belief it breaks, what the learner does); move it only when the manner of change is what must be learned. *Why:* animation beats still pictures only a little on average (about g = 0.23), but a lot when the learner must learn how something changes. A fixed menu of pictures makes every lesson look alike.
- **Ask before it costs.** Moving pictures cost the author tokens and time, so each is proposed with its reason and cost, and built only after a yes.

All of this is worked out in `visual-design.md`.

## 7. Everything real

- **Every result is real.** The page runs no code. Every code result, each wrong option's included, is recorded from a real run; a text result is quoted from a named source or worked out in steps; every number in a picture is printed by code. *Why:* an invented output teaches a false lesson.
- **The lesson works without AI.** Blanks, checks and pictures need no AI; the tutor and grader add depth where the page can call Claude. *Why:* AI calls can be declined or unavailable.

## 8. The learner's choice, the lesson's care

- **The learner decides when to see the answer.** Every exercise has Hint and Show solution, always available, plus a read-along mode. The tutor never hands over a solution. *Why:* a stuck learner who cannot see the answer stops learning, and some want to read first and practise later.
- **The learner's colour, the lesson's meaning.** One accent colour chosen with the learner; right, wrong and answer-shown colours stay fixed and never rely on colour alone. *Why:* a page that feels like theirs invites the learner in; a "right" that changes colour teaches confusion.

## 9. Checked by someone who did not write it

- **Review with fresh eyes.** Every rule in `self-checks.md` is checked again, every result re-run, and the page used by a fresh learner persona, by reviewers who did not write the lesson (`lesson-review.md`). *Why:* an author cannot unsee what they know. Test rounds found what no rule did: a caption that contradicted its picture, an ending that showed the answer before the learner wrote theirs.
- **Say how it was checked.** Without agents, the author runs the same checklists and says the lesson was self-checked. *Why:* a self-check is weaker than a review, and the author deserves to know which they got.

## 10. Sources

- PRIMM: Sentance, Waite and Kallia (2019), "Teaching computer programming with PRIMM", *Computer Science Education*.
- Mayer (2020), *Multimedia Learning*, 3rd edition: segmenting, signalling, coherence, pre-training, generative activity.
- DataCamp's exercise rules: one objective per lesson, hints about half way, first-error feedback.
- Tversky, Morrison and Bétrancourt (2002); Höffler and Leutner (2007); Ploetzner, Berney and Bétrancourt (2020, 2021): when animation helps.
- Open teaching skills this one grew from: make-it-learnable (prediction with confidence, a plan as a spec), teach by lucas-ataides (repair from a new angle), ape-teach (one milestone at a time, a field guide), teach by udayanwalvekar (confirmed vs inferred).
