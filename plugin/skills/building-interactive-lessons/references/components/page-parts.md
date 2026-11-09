# Components: page parts

The parts the template builds around the chapters by itself. You never add them as blocks; you feed them through blueprint fields, and their quality depends on those fields. `page-contract.md` has their full behaviour.

| Part | What the learner sees | Fed by | Make it strong |
|---|---|---|---|
| **Start page** | a first question from chapter 1, what they will be able to do, total time, the chapter list with times, who the lesson is for (folded) | `lesson.objectives`, `learner`, each chapter's `title`, `minutes`, `why_it_matters`, the first predict | objectives with observable verbs; `why_it_matters` one line, never the answer |
| **Journey strip** | one dot per chapter, "You are here. By the end: you can …" | each chapter's `milestone` | "I can" plus an action, never the answer to a guess |
| **Bridge line** | one muted line opening each chapter | `bridge_in.text` | recall one earlier idea by name, then pose this chapter's angle |
| **Still open** | the chapter's last line: the question the next chapter answers | `open_question` | a question the learner now wants answered; the next chapter's predict picks it up |
| **Field guide** | the big idea, every recap line, the confident-but-wrong list, `run_locally` commands | `big_idea`, every `recap`, the learner's own confident guesses | recaps written the way the learner would use them |
| **Glossary sheet** | tap a term to see its definition | `glossary` | every term used more than once, defined in one line |
| **Tutor** | "Ask" on every block, a chat that knows the block and never hands over a solution | the block, the chapter card, `context_note`, the rubric (`ai-tutor-and-grader.md`) | a full `context_note` on every code slice, so "Show the code around this" works without AI too |
| **Grader** | Submit on every explain and stretch | `rubric`, `reference_solution`, `common_wrong_answers` | one observable `passing` line per criterion |
| **Read-along** | a switch that opens every solution, fills every blank, shows every output | every solution, every option's output, seeded samples | nothing extra: it works when every result is recorded |
| **Theme** | the accent colour and fonts | `theme` | one accent agreed with the learner (`theme.md`) |
| **Mode line** | what is on (read-along, tutor off) and work solved | nothing | — |

**Where the tutor and grader run:** inside claude.ai, when the viewer allows the page to ask Claude. Anywhere else the page hides them, and the rest of the lesson works: blanks, checks, pictures, scenes and trials need no AI.
