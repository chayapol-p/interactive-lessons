# Interactive Lessons: concept, vision and principles

This file is the source for the README. It records what the project is, why it exists, and the rules every lesson follows, with the reason behind each rule.

Status: v0.4. Revised after the first real tests (a 7-chapter RAG workshop lesson, a no-code How LLMs Work lesson), a design review of the page, and rounds of user tests with fresh personas on the Monty Hall lesson.

---

## 1. Concept

An agent skill that turns any topic, some docs or a code repo into an **interactive lesson**: one web page that a learner works through chapter by chapter. Code is one kind of material it can teach; rules, formulas and concepts work too.

The learner does not only read. In every chapter they predict, read a small piece of real material (a code slice with its real output, or a real sentence, rule or formula), fill in the blanks on the words that carry the idea, and see where each choice really leads. An AI tutor sits beside every step, so a learner who is stuck can ask in their own words. An AI grader checks written explanations against a rubric and names the first problem.

The skill plans before it builds. It finds out who the learner is, checks the facts and the code, and lays out chapters that build on each other like blocks. Only then does it write the page.

## 2. Vision

Anyone who understands something well can turn it into a lesson that teaches as well as a patient tutor sitting next to the learner.

- **For authors:** point the skill at a repo or a topic and get a lesson plan you can review, then a working page.
- **For learners:** a lesson that asks you to think and do, answers your questions in context, and tells you where your understanding is still shaky.

## 3. Who it is for

- **Authors:** engineers, teachers and team leads who want to teach a system, a library, a lab or an idea.
- **Default learner:** new to the topic, no coding assumed. The skill drafts a profile from what it knows and the learner confirms it (4.17).

## 4. Principles

Each principle has a rule, the reason for it, and where it comes from.

### 4.1 Learners produce, not only read
- **Rule:** every chapter asks the learner to predict, fill in blanks in real material, or explain something in their own words.
- **Why:** in our first lab guides, learners read and tapped through demos and still could not explain the ideas. Making something forces the learner to build their own model of the idea.
- **From:** PRIMM (Predict, Run, Investigate, Modify, Make), a method for teaching programming that outperformed normal lessons in a 13-school study; Mayer's "generative activity" principle; DataCamp's hands-on exercises.

### 4.2 Plan the learning before building the page
- **Rule:** discover the learner, verify the material, then plan chapters as data (a blueprint). The page comes last, and a script fills a shared page template from the blueprint. Nobody writes the page by hand.
- **Why:** most weak lessons fail in their structure, not their styling. A blueprint can be checked by a script before any page exists. A shared template means every lesson gets the same tested behaviour, and a revision changes only the blueprint.
- **From:** make-it-learnable's "a spec, not a template" design for the plan; the first real test, where hand-building the page cost the most time, for the template.

### 4.3 Every chapter states what the learner must get right, and how we will know
- **Rule:** each chapter lists what the learner must know, what they must get right, and the exact check that proves each one. The check comes after the teaching; a prediction before it never counts alone.
- **Why:** a quiz that tests recall cannot show that a learner can apply an idea. The check must match the claim. If we cannot name how to test something, the chapter is not ready.
- **From:** standard instructional design (aligning objectives and assessment); our own Lab 1 lessons.

### 4.4 Chapters connect the dots
- **Rule:** each chapter names what it brings in from earlier chapters and what it carries forward, with the blocks that show each idea. It opens with a bridge from the last chapter and closes with a pointer to where the idea is used next. A bridge or recap names only ideas its blocks really show.
- **Why:** learners forget why a chapter exists when it floats alone. Naming the links turns separate facts into one connected picture.
- **From:** Mayer's pre-training principle; lucas-ataides/teach's "build from what the learner already knows".

### 4.5 One idea per block, in short steps
- **Rule:** a block holds one idea, explained in at most 2 sentences and about 45 words, tied to something the learner already knows. Feedback is one sentence; a caption is about 25 words. A script checks the budget.
- **Why:** short, learner-paced segments are easier to absorb than a long stream.
- **From:** Mayer's segmenting and coherence principles; DataCamp's one objective per lesson; ape-teach's one milestone at a time.

### 4.6 Predict first, with confidence
- **Rule:** a chapter opens with a prediction and asks how sure the learner is.
- **Why:** a wrong prediction made with confidence is the moment a learner is most ready to change their mind. Confidence also shows where an understanding is shaky but feels solid.
- **From:** make-it-learnable; PRIMM's predict step.

### 4.7 Wrong answers teach
- **Rule:** every wrong quiz option and every wrong blank option is a real misconception, with its own one-line explanation. A wrong blank option shows what the code really prints with it. The grader names the first problem.
- **Why:** a bare "wrong" teaches nothing. Naming the specific mistake repairs the specific misunderstanding.
- **From:** DataCamp's feedback rules (first error only, hints about 50% of the way); make-it-learnable's wrong-answer explanations.

### 4.8 Quizzes only where they earn their place
- **Rule:** quiz the key concepts and the pitfalls, at most 2 per chapter. A key concept gets an application question. A pitfall gets a "spot the mistake" question built from a real misconception.
- **Why:** quizzes on trivia train trivia. Quizzes on the ideas and traps that matter train judgement.

### 4.9 Diagrams start with a purpose
- **Rule:** before drawing, write what the diagram should help the learner understand, how it helps, and what becomes clearer than in words. No clear answer means no diagram. Then cut it to the fewest boxes (at most 9, 1 or 2 highlighted) and pick one of three patterns: a growing pipeline, paired traces, or a sequence.
- **Why:** a decorative diagram costs attention and teaches nothing. A diagram with a purpose shows a mechanism that text explains badly: flow, structure, change over time, space, or a comparison.
- **From:** Mayer's multimedia principle; the "build it up one part at a time" practice from several open teach skills.

### 4.10 Show what makes choices different
- **Rule:** when a lesson compares options (two rules, two settings, two methods), show them side by side on the same input and point to the exact step where they part ways.
- **Why:** a before and after shows that something changed. It does not show why one choice behaves differently from another. Learners need the difference itself.
- **From:** our own Lab 1 lessons, where learners saw outputs differ but could not tell what caused it.

### 4.11 Real code, small and commented, with context on demand
- **Rule:** a lesson shows only the real material that carries the idea: a code slice of at most 15 code lines with short line comments and hidden setup, or the real sentence, rule or formula. The default exercise turns 1 to 3 key words or tokens of it into blanks. A learner can ask the tutor for the context around it.
- **Why:** a whole repo buries the idea under setup and plumbing. Comments let a learner read a slice alone. Blanks on the key tokens test the idea itself, and a minimum length would only invite padding.
- **From:** ape-teach's minimal code; code-learn-skill's staged code; Claude Code's Learning style, where the learner writes the small strategic piece.

### 4.12 Every output is real, and the lesson works without AI
- **Rule:** the page runs no code. Every result it shows is real: a code result, including each wrong option's, is recorded from a real run; a text result is quoted from a named source or worked out in steps; the numbers in a picture are printed by code at build time. A script proves each run before publishing. Fill-in-the-blank exercises need no AI. The AI tutor and the grader for written answers add depth when the viewer allows them.
- **Why:** an invented output teaches a false lesson. Running code inside the page proved fragile in the first test, and recorded real outputs show the same truth with nothing to break. AI calls can be declined or unavailable, so the core of the lesson must not depend on them.

### 4.13 The learner decides when to see the answer; the tutor never hands it over
- **Rule:** every exercise has a Hint button and a Show solution button, always available, and a read-along mode opens every solution. The tutor answers inside the lesson's scope, explains from a new angle when the learner is stuck, and never gives a solution itself: it hints and points to Show solution.
- **Why:** a learner who is stuck and cannot see the answer stops learning, and some learners want to read first and practise later. The choice belongs to the learner. A tutor that hands over answers unasked would take that choice away.
- **From:** lucas-ataides/teach ("repair from a different angle, never a louder repeat").

### 4.14 Separate what is confirmed from what is inferred
- **Rule:** while verifying, the skill marks each fact as confirmed (from a source or a run) or inferred. Lessons state inferred points as such.
- **Why:** a lesson that teaches a wrong fact with confidence does lasting damage.
- **From:** udayanwalvekar/teach.

### 4.15 End with a field guide
- **Rule:** each block ends with a one-line recap. The lesson collects them into a one-page field guide, plus a list of places where the learner was confident but wrong.
- **Why:** the field guide is what the learner keeps. The confidence list tells them what to revisit.
- **From:** ape-teach's field guide; make-it-learnable's calibration readout.

### 4.16 Test the idea, not the example
- **Rule:** explain an example (a lab, a codebase, a rule book) before using it, and never ask the learner to recall its details, such as a clause number. A script flags quiz questions that lean on unexplained example details.
- **Why:** in the first badminton-rules lessons, quizzes asked for rule numbers the learner had never been shown. They tested memory of the example, not the idea.
- **From:** the author's own use of the skill.

### 4.17 Assume, then confirm
- **Rule:** draft the learner profile from what is already known (memory, the conversation, past work), show where each assumption came from, and confirm it with at most 4 questions that also settle the scope (depth, topics, length, style).
- **Why:** starting from a blank profile wastes the learner's time; building on an unchecked guess teaches the wrong level.
- **From:** the author's own use of the skill.

### 4.18 The learner's colour, the lesson's meaning
- **Rule:** each lesson takes one accent colour chosen with the learner (a colour they like, their organisation's, or the topic's world). Right, wrong and answer-shown colours stay fixed for everyone, and are never shown by colour alone. A script builds every other colour from the accent and checks contrast in both themes.
- **Why:** a page that feels like theirs invites the learner in; a "right" that changes colour between lessons teaches nothing but confusion.
- **From:** a six-seat design review of the template, led by the author.

### 4.19 Design each picture from the idea
- **Rule:** the skill designs a picture by reasoning about the idea, not by picking from a menu. For each key idea it answers five questions (what is hidden, what changes and what stays, why a still picture would fail, which wrong belief the picture breaks, what the learner does), matches the picture's structure to the idea's, and moves it only where the manner of change is what must be learned. Ready-made figures are cheap parts; when none carries the storyboard, it writes a scene for that idea: learner-paced steps, optional controls and trials, every number from computed data. Moving pictures cost tokens, so each is proposed with its reason and cost and built only once the author agrees.
- **Why:** a fixed set of picture types made every lesson look alike: a deal of cards built for Monty Hall came back for a model choosing its next word. Research is sober about motion (three meta-analyses find a small average gain, about g = 0.23) but clear about when it pays: when the learner must learn how something changes, its order, path or amount. In testing, the picture a tester named as the best part was one where a share visibly moved from one door to another.
- **From:** Mayer's multimedia and signalling principles; the author's test rounds.

### 4.20 One story, with milestones
- **Rule:** a lesson is one story with a big idea, told in beats: hook, intuition, proof, mechanism, boundary, transfer, payoff. Each chapter names its milestone ("I can…") and ends on an open question that the next chapter answers; the last chapter answers the first question. A journey strip shows where the learner is.
- **Why:** learners who follow one question from puzzle to answer keep both the answer and the reason; chapters read as separate topics are forgotten as separate topics. An open question at every chapter end keeps a question in the learner's hands.
- **From:** the author's story-deck (big idea, "Next →" questions), attention-principles (curiosity loops) and personal-storytelling (problem, pursuit, payoff) skills, borrowed at design time.

### 4.21 Nothing gives the answer early
- **Rule:** a guess's answer never appears before the guess: not in a title, a goal, a milestone, a caption or a totals row. The idea that answers a guess stays folded until the guess is made (with a Skip button). A blank's answer is never written in the block just above it, and the right option is never the longest. Scripts check each of these.
- **Why:** in every early test round, learners read the answer while scrolling to the question, and the guess stopped being a guess. A prediction only works when the learner commits before they know.

### 4.22 Learners make the evidence
- **Rule:** where a learner needs to believe a number, let them make it: deal 10 or 100 games from a computed case table, fresh and random each time, and show their counts beside the expected share. A seeded sample deal is kept only for screenshots and read-along.
- **Why:** a sceptic distrusts a table they were shown and trusts a count they made. In testing, a persona sure of "50/50" said "That's not 50/50, is it" at her own deal, not at any paragraph; a fixed deal looks staged.

### 4.23 Test, then reveal
- **Rule:** a "Spot the mistake" question comes before the common-mistake card it tests; the card stays folded until the question is answered, then opens as feedback. A learner may open it early, and read-along opens everything.
- **Why:** a card read first hands over the question's answer; a card read after a try explains the learner's own choice, right or wrong. The same reason folds the key idea under each guess (4.21).

### 4.24 Test with real users, then fix
- **Rule:** before release, fresh persona agents, a different person each round, use the lesson only the way a learner does (phone screenshots and taps, no answers mode, no files) and report in a fixed shape: moments, lost spots, a teach-back, a verdict, top fixes, bugs. Fix, then test with a new person. Stop on a correct teach-back with "I get it", or after two rounds with nothing new (then ask the author).
- **Why:** an author cannot unsee what they know. The test rounds found what no script did: a caption that contradicted its picture, an ending that showed the answer before the learner wrote theirs, and a fair dealer that a numbers-minded learner distrusted because the page never said how far a fair deal wanders. Setting up the phone access path found one more: the page had no phone viewport tag.
- **From:** the author's own rounds; the testing-with-real-users skill holds the method for any artifact a person uses.

## 5. How it works

1. **Discover:** who the learner is, what they know, what they should be able to do afterwards, and how big one lesson can be.
2. **Verify:** read the sources, list facts as confirmed or inferred, collect common misconceptions; a script runs every slice and every blank option and records the outputs.
3. **Plan:** map the concepts, order chapters so each uses only what came before, and write the blueprint. A script checks it.
4. **Build:** a script fills the page template from the blueprint, one chapter per page.
5. **Check:** one command runs every check a script can; phone screenshots, light and dark, show the rest; try the grader with right, wrong and half-right answers; test with fresh personas until one gets it (4.24).
6. **Publish and improve:** learners' progress shows which blocks need work. A revise round edits the blueprint, rebuilds, and re-checks only the chapters that changed.

Time budget: plan in 15 minutes, first build in 20, a revise round in 10. A step that runs over stops and logs why.

## 6. What a chapter looks like

- A journey strip: where this chapter sits, and its milestone
- A bridge from the last chapter
- **Predict**, with a confidence rating
- **Idea**, in at most 2 sentences, folded until the guess is made
- **Picture**, only when its purpose is written down, designed from the idea: still, stepped, moving, driven or run by the learner
- **Play or a scene with trials** (when agreed): make the evidence and count it
- **Real material:** a code slice with line comments and its recorded output, or a real sentence, rule or formula
- **Compare choices**, when the chapter has options to compare
- **Fill the blanks** on the words that carry the idea, with Hint and Show solution
- **Explain** in your own words, graded by AI
- **Stretch** (optional): write it yourself
- **Spot the mistake**, then the common-mistake card it opens
- **Recap** line, and the open question the next chapter answers
- **Ask the tutor** beside every step

## 7. Non-goals

- Not a course platform: no accounts, catalogues or certificates.
- Not a code runner: the page shows outputs recorded from real runs, and code slices are small on purpose.
- Not a slide deck or reference doc.
- Not a replacement for running the real project. Steps that need a database or a key show a recorded output and the command to run it locally.

## 8. Influences and credits

- **make-it-learnable** (Web Reactiva): prediction with confidence, wrong-answer explanations, one growing diagram, lessons planned as a spec. https://www.webreactiva.com/skills/make-it-learnable
- **teach** by lucas-ataides: find the level, one-line answer first, check by application. https://www.skills.sh/lucas-ataides/skills/teach
- **ape-teach** by arpitbbhayani: one milestone at a time, minimal code, a closing field guide. https://skills.sh/arpitbbhayani/ape-skills/ape-teach
- **teach** by udayanwalvekar: follow one real action through a system; confirmed vs inferred. https://www.skills.sh/udayanwalvekar/teach/teach
- **explain-diff** by yogan: background, intuition, walkthrough, quiz. https://github.com/yogan/agent-skills
- **code-learn-skill** by yumeiriowl: staged learning code beside its explanation. https://github.com/yumeiriowl/code-learn-skill
- **pyodide-exercise**: editable browser Python with tests and progressive hints. https://claudskills.com/skills/pyodide-exercise/
- **Claude Code's Learning output style**: the learner writes small strategic pieces marked `TODO(human)`. https://code.claude.com/docs/en/output-styles
- **DataCamp**: short lessons with one objective, scaffolded exercises, hints and first-error feedback. https://instructor-support.datacamp.com/courses/course-development/coding-exercise-anatomy
- **Claude Academy**: lessons labelled with time, alternating lessons, exercises and quizzes.
- **PRIMM**: Sentance, Waite and Kallia (2019), "Teaching computer programming with PRIMM: a sociocultural perspective", Computer Science Education.
- **Mayer's principles of multimedia learning**: Mayer (2020), Multimedia Learning, 3rd edition.
