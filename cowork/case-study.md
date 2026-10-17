# Case study: how thesis review notes are recorded and structured

DRAFT, 2026-10-18. Background for designing `reviews/WORKFLOW.md`.
Not instructions for Cowork.

Question: is there an established way to (A) record and transcribe a review, and (B) structure
the notes of a thesis review, that RTJT should follow instead of inventing its own?

Short answer: no single standard exists for design/architecture thesis reviews. But several
neighbouring fields have settled formats, and they agree on a common core (see "Common core").

---

## Part A: recording and transcribing

### A1. Transcription styles (qualitative research)
- **Full verbatim:** every word, filler, false start, pause. Used for conversation/discourse
  analysis (Jefferson notation adds pauses, overlaps, intonation).
- **Intelligent / clean verbatim:** drops fillers and false starts, keeps the speaker's words
  and meaning. Standard for thematic and content analysis.
- **Edited / clean read:** smooths grammar so it reads like prepared text. Some sources say
  this is unsuitable for research because it adds interpretation too early.
- Common advice: keep the full version, since a cleaned transcript can't be un-cleaned without
  going back to the audio. AI transcripts need human review before quoting.
- Caveat: these sources are mostly transcription-vendor blogs.

**For RTJT:** already matches. Whisper transcript = raw record (close to full verbatim, with
timestamps); notes = intelligent verbatim. Keep both layers.

### A2. Lecture capture (Panopto)
- Speech recognition + OCR on slides/screen, synced to the video timeline. Search jumps to the
  moment; slide headings become a table of contents.
- Key limit (also in a 2006 slide-retrieval paper): the slide file alone doesn't say *when* a
  slide was shown. Syncing needs slide-change times captured during the session (screen or
  projector capture).

**For RTJT:** we record audio only, so "feedback per slide" means the slide for each moment has
to come from somewhere:
1. Ctrl+M marker at each slide change (already supported, but it overloads the "important
   moment" marker).
2. Students say "slide N" when they change slides.
3. Screen-record the review (gives exact slide timing; heavier).
4. Cowork infers the slide from content (no extra effort, can be wrong; must say so).

---

## Part B: how review notes are structured

### B1. PhD supervision meeting records (UK/Irish universities)
Galway, UCC, Roehampton, Queen Margaret, Nottingham, LSE PhD Log, Cambridge HPS.
- Fields: date, attendees, review of actions since last meeting, topics discussed,
  **action points (who, what, by when)**, next meeting, agenda for next time.
- Usually the **student writes it** after the meeting; supervisors add to it or confirm.
- QMU: the whole team must agree the record, especially action points. LSE: entries can't be
  edited once published, and the supervisor signs off.

**Takeaway:** the action list and the "since last time" check are the core. The record belongs
to the student as much as to the supervisor.

### B2. Thesis committee meeting reports (US graduate programmes)
Michigan EEB, Boston University, Johns Hopkins BME, Brown, Kentucky, Toronto, Maine, Andrews.
- **Student part first, sent before the meeting:** 1-2 page progress summary and plans
  (BU caps it at 300 words).
- **Previous goals vs outcome.**
- **What was presented / feedback given / expectations set** (Kentucky's wording).
- Committee rating (exceeds / meets / below; Toronto: satisfactory / concerns / unsatisfactory).
- Recommendations, split into research priorities and professional development.
- Next meeting date; signatures; student comment box.

**Takeaway:** a clear split between *what the student brought*, *what the committee said*, and
*what is expected next*. (RTJT drops the rating: guiding, not grading.)

### B3. PhD annual progress reviews
Western, Nottingham, Edinburgh, Portsmouth, GWU, IIT Guwahati, Portland State, Tor Vergata.
- Student: progress **measured against the objectives in the previous report**, outputs, plan
  for the next period.
- Assessor: comments **per element** (written report, presentation/viva); shortcomings need
  detailed comment.
- Outcome: acceptable progress or an agreed action plan.

**Takeaway:** each review is read against the previous one. This is the "how the thesis
evolves" layer.

### B4. Architecture / design thesis juries and crits
Melbourne MSD, KTH, Kerala and SPAV B.Arch syllabi, Gothenburg critique thesis, Georgia
Southern, ITU, Pakistan crit study.
- Format: short presentation (about 20-30 min with Q&A) to a panel; drawings, models, site
  analysis. Internal reviews during the term, external jury at the end.
- Documentation is weak: one study notes critique **lacks standardised guidance** and
  recommends documenting crits. Melbourne recommends giving students the rubric in advance as a
  feedback sheet.
- Closest practice: students keep **reflective reports** across the semester, showing how they
  take up critique over time.

**Takeaway:** no standard to copy. That is a gap RTJT can fill, borrowing from B1-B3.

### B5. Critical Response Process (Liz Lerman, 1990)
Feedback on work in progress, in order:
1. Statements of meaning (what was striking).
2. Artist as questioner (the maker asks what they want to know).
3. Neutral questions from responders. (Steps 3-4 from general knowledge; search results only
   confirmed steps 1-2.)
4. Opinions, with the artist's permission.

**Takeaway:** separate *observations*, *questions* and *opinions/advice*. In notes, this lets
you see what a guide actually advised versus what they only asked.

### B6. Design rationale: IBIS and QOC
- **IBIS** (Kunz & Rittel, 1970): Issue → Positions → Arguments for/against.
- **QOC:** Questions, Options, Criteria, Assessments, Arguments, Decisions.
- Tools (gIBIS, Compendium, DRed) used IBIS to capture meetings live and index meeting videos;
  DRed's issue/option/argument graphs were judged good for review meetings.
- Known problem: full rationale capture is too much effort, so people stop doing it. Informal,
  partial rationale that actually gets written is worth more.

**Takeaway:** a design review is a set of open issues with options and arguments, some of them
decided. Keep it light: issue, what was proposed, for/against, decided or open.

### B7. Feedback models (Hattie & Timperley, 2007)
- Feedback works at four levels: **task** (is it right), **process** (the approach),
  **self-regulation** (how the student steers their own work), **self** (personal praise;
  least useful).
- The same paper frames feedback as feed up (where am I going), feed back (how am I doing),
  feed forward (where next). Not covered by the search results; from the 2007 paper.

**Takeaway:** a useful lens for later analysis (what kind of feedback each student gets), not
necessarily a note heading.

---

## Comparison

| Case | Unit of the note | Before the review | Feedback | After the review | Across reviews |
|---|---|---|---|---|---|
| B1 Supervision record | meeting | actions since last time | topics discussed | action points (who/when) | next agenda |
| B2 Committee report | meeting | student summary | presented / feedback / expectations | recommendations | previous goals vs outcome |
| B3 Annual review | year | progress vs objectives | comments per element | action plan | yes, core |
| B4 Design jury | presentation | drawings, models | spoken critique, rarely recorded | rarely | reflective reports |
| B5 CRP | work in progress | - | meaning / questions / opinions | - | - |
| B6 IBIS / QOC | issue | - | options, arguments | decisions | open issues carry over |
| A2 Lecture capture | slide / moment | slides | transcript synced to slides | search | - |

## Common core
Almost every format has these, in this order:
1. **Context:** who, when, what was presented (the slides).
2. **Since last time:** what was asked last round and what happened.
3. **Discussion:** by topic or by slide/issue, with who said what.
4. **Decisions and open questions.**
5. **Actions:** who does what next.
6. **Carry-over:** feeds the next review.

## What this means for RTJT (to discuss)
Possible note structure, in layers. Nothing decided yet.

1. **Transcript** (exists): raw, timestamped.
2. **Per-review note** (exists, to extend):
   - Project as presented (from slides + talk).
   - Since last review: actions from the previous note, done / not mentioned. (Needs a previous
     note; from round 2 on.)
   - Discussion **by slide**, General section for the rest (from A2). Needs a slide-timing
     decision (A2 options 1-4).
   - Optional tag per point: observation / question / advice (B5).
   - Decisions and open issues (B6, kept light).
   - Actions: who, what (B1). Deadlines only if said.
   - Mentioned / Further reading / Marked moments / Unclear / Flagged (existing sections).
3. **Progress per student** (later): compares notes and slides across rounds (B3, B4
   reflective reports). Open issues and actions carry over.

Open decisions:
- Slide timing: Ctrl+M per slide, students say "slide N", screen recording, or Cowork infers?
- Does the student see or confirm their note (B1, B2)? Consent currently covers Claude/Cowork +
  Drive; sharing notes with students is a separate choice.
- Tag points (observation / question / advice) or keep plain?
- Keep it simple: which of these layers are actually worth it now?

---

## Sources
Transcription
- Looppanel, types of transcription: https://www.looppanel.com/blog/types-of-transcription-in-qualitative-research
- Looppanel, transcription in qualitative research: https://www.looppanel.com/blog/transcription-in-qualitative-research
- Subanana, verbatim vs clean read: https://subanana.com/en/blog/transcript-formats-verbatim-clean-read
- GMR Transcription, verbatim styles: https://www.gmrtranscription.com/blog/verbatim-style-for-interviews-or-qualitative-research

Lecture capture
- Panopto: https://panopto.com/record
- University of Richmond, Panopto search: https://blog.richmond.edu/lawlibrary/?p=5171
- Glasgow, slide retrieval paper: https://www.dcs.gla.ac.uk/~vincia/papers/slidesretrieval.pdf

Supervision records
- Galway sample record: https://ugal.ie/media/collegeofartssocialsciencescelticstudies/Sample_Supervision_Record_Form_Dec24.docx
- UCC research supervision record: https://www.ucc.ie/en/media/academic/appliedpsychology/dclin/ResearchSupervisionRecord.docx
- Roehampton supervision record: https://www.roehampton.ac.uk/globalassets/documents/graduate-school/current-students/supervision-record.doc
- Queen Margaret supervision record: https://www.qmu.ac.uk/media/jrejtnif/supervison-meeting-record-tagged.doc
- LSE PhD Log: https://info.lse.ac.uk/current-students/phd-academy/assets/documents/PhD-Log-instructions-Students.pdf
- Cambridge HPS PhD log: https://www.hps.cam.ac.uk/students/phd-guide/log

Committee reports
- Michigan EEB: https://prod.lsa.umich.edu/content/dam/eeb-assets/eeb-documents/EEB_PhDcommitteemtgform.pdf
- Boston University: https://www.bu.edu/eng/files/2022/09/PostProspectusCommitteeMeetingForm_03.2019_Fillable_PDF.pdf
- Johns Hopkins BME: https://www.bme.jhu.edu/wp-content/uploads/2022/02/JHU-BME-Thesis-Committee-Meeting-Report-Fillable.pdf
- Brown Pathobiology: https://pathobiology.biomed.brown.edu/sites/default/files/Pathobiology%20Annual%20Thesis%20Committee%20Meeting%20Report-25.pdf
- Kentucky Biology: https://bio.as.uky.edu/sites/default/files/Updated_COMMITTEE%20MEETING%20FORM.pdf
- Toronto Immunology: https://immunology.utoronto.ca/sites/default/files/inline-files/Committee%20Meeting%20Form%20Nov%202022%20update_fillable_final_0.pdf

Annual reviews
- Western Engineering: https://www.eng.uwo.ca/Electrical/pdf/graduate/PhD_Progress_Form.pdf
- Nottingham annual review: https://www.nottingham.ac.uk/academicservices/documents/qmdocuments/resannualreview.docx
- Edinburgh annual review questions: https://registryservices.ed.ac.uk/sites/default/files/2024-07/Annual%20Review%20Form%20questions_0.pdf
- GWU annual review: https://Publichealth.gwu.edu/sites/g/files/zaxdzs4586/files/2023-08/phd_annual_review_form_-_2023.pdf

Design crits and juries
- Georgia Southern, design critique reflections: https://digitalcommons.georgiasouthern.edu/ij-sotl/vol13/iss3/8
- Pakistan, factors affecting critique: https://ojs-orjss.gcwus.edu.pk/journal/article/view/73
- Gothenburg, the work of critique: https://gupea.ub.gu.se/handle/2077/22775
- Melbourne MSD studio assessment: https://msd.unimelb.edu.au/__data/assets/pdf_file/0010/4642318/230419_Studio-Assessment_formatted.pdf
- Melbourne M.Arch subject assessment: https://handbook.unimelb.edu.au/2019/subjects/abpl90285/assessment
- Sussex, collaborative note-taking in feedback: https://blogs.sussex.ac.uk/learning-matters/2025/02/20/collaborative-note-taking-in-formative-feedback/

Feedback methods
- Dance Exchange, Critical Response Process: https://www.danceexchange.org/crp
- ArtEZ, CRP: https://cft.artez.nl/?p=1758
- Wikipedia, design rationale (IBIS, QOC): https://en.wikipedia.org/wiki/Design_rationale
- Southampton, 15 years on from gIBIS and QOC: https://web-archive.southampton.ac.uk/eprints.aktors.org/513/index.html
- University of Twente, process feedback (Hattie & Timperley): https://www.utwente.nl/en/learning-teaching/assessment/toolbox/organize-process-feedback/
