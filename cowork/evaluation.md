# DRAFT: criteria evaluation workflow

Work in progress. Rules are drafted here and copied into the reviews folder's
`WORKFLOW.md` once they are ready. Not instructions for Claude Code, and not live yet.

Runs after the post-processing step, on its notes (`notes/<date>/<Name>.md`).

## Criteria
Algorithmic Design II thesis cluster: applied research on parametric and data-driven design
in the built environment. Students identify a problem, justify it, experiment with data and
tools, build a prototype, and present their findings. They are not writing a thesis yet.

| # | Phase | Criterion | Look for |
|---|---|---|---|
| 1 | Problem | Problem statement | A specific built-environment / AEC challenge, with its scale |
| 2 | Problem | State of the art | Existing research, tools and projects, and what they miss |
| 3 | Problem | Rationale | Why a parametric or data-driven approach is needed here |
| 4 | Problem | Research question | One answerable question: problem, method, what is measured |
| 5 | Proposal | Aim | What the project will produce |
| 6 | Proposal | Workflow diagram | Inputs → computation → design output, and who uses it |
| 7 | Proposal | Scope and limitations | Typology, scale, stakeholder, case study; what is left out |
| 8 | Proposal | Methodology / roadmap | Tools, models and data, in order |
| 9 | Proposal | Timeline | Dated plan up to the final presentation |
| 10 | Data and experimentation | Datasets identified | Sources, or a plan to generate data |
| 11 | Data and experimentation | Dataset collected / generated | The data exists and is shown |
| 12 | Data and experimentation | Data validity | Quality, coverage and bias checked |
| 13 | Data and experimentation | Data interpreted | Analysis or visualisation that shows patterns or insights |
| 14 | Data and experimentation | Tools and models identified | Named tools / ML models and why they were chosen |
| 15 | Data and experimentation | Tools tested | Existing tools or models run on the student's own case |
| 16 | Data and experimentation | Experiment design and metrics | What is tested, against what, how success is measured |
| 17 | Prototype | Building blocks | The system split into components |
| 18 | Prototype | Pseudocode | The logic written out before coding |
| 19 | Prototype | Parametric / generative model | Scripts that generate design options, running independently |
| 20 | Prototype | Predictive model training | Training / tuning results (Not Applicable if no ML) |
| 21 | Prototype | Optimisation / design exploration | Options searched, compared or optimised against criteria |
| 22 | Prototype | Back end | Workflow runs end to end, debugged |
| 23 | Prototype | Front end mockup | The interface a designer or user would see |
| 24 | Prototype | Integrated prototype | Back end and front end working together |
| 25 | Presentation | Findings and evaluation | Results against the metrics: does it improve the design outcome? |
| 26 | Presentation | Narrative and slides | A clear story from problem to findings |
| 27 | Presentation | Diagrams and visuals | Clear, consistent diagrams of the system and results |
| 28 | Presentation | Demo video | The prototype shown working |
| 29 | Presentation | Result videos | Design outputs, iterations, experiments |
| 30 | Presentation | Final prototype | Finished digital (or physical) prototype |

## Marks
| Mark | Use when |
|---|---|
| Not Applicable | Does not apply to this project (e.g. training when there is no ML) |
| Not Started | Not shown or only mentioned as for later |
| Started | An idea or intention, nothing concrete yet |
| Progressed | Concrete work shown, but incomplete or challenged by the guides |
| Stagnant | Discussed, but no change since the previous review |
| Stable | Clear and accepted by the guides |
| Closed | Done, no further work needed |

Mark only the criteria the review actually covered, based on what was shown, not promised.

## Output (draft)
```markdown
## Criteria
| # | Criterion | Mark | Evidence |
|---|---|---|---|
| 4 | Research question | Progressed | <short reason> (`HH:MM:SS`) |
```

## Open decisions
- Merge 4 Research question and 5 Aim into one criterion? If merged, either drop to 29 or add
  "Case study / site".
- Where the marks go: inside each note, or a separate file per student.
