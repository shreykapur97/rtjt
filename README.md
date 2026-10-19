# RTJT

By **Shrey Kapur** ([@shreykapur97](https://github.com/shreykapur97))

Transcribes recorded thesis cluster reviews and labels who spoke when, so feedback can be tracked per student across review rounds.

Runs fully locally: [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (large-v3, batched) for speech-to-text and [pyannote](https://github.com/pyannote/pyannote-audio) community-1 (exclusive mode) for speaker diarization. Settings were chosen with the evaluation script below.

**Privacy:** recordings, transcripts, notes and voiceprints are gitignored; only code is in this repo. Recordings and voiceprints never leave the machine. Transcripts and flattened slides are copied to a separate reviews folder, and only faculty notes are published to the faculty's Google Drive.

## Requirements
- Windows/Linux with an NVIDIA GPU (8 GB VRAM is enough)
- [uv](https://docs.astral.sh/uv/) and [ffmpeg](https://ffmpeg.org/) on PATH
- A Hugging Face read token, with the terms accepted for
  [pyannote/speaker-diarization-community-1](https://huggingface.co/pyannote/speaker-diarization-community-1)

On Windows, pyannote prints a `torchcodec` warning at start-up. It is harmless: audio is decoded with ffmpeg and passed in memory.

## Setup
```
uv sync
copy .env.example .env   # then add HF_TOKEN=hf_...
```

## Each review round

**1. Add the recordings**, one file per student, named after the student:
```
data/raw_recordings/<YYYY-MM-DD>/<Name>.m4a
```

**2. Transcribe.** Only new recordings are processed; known voices are named automatically.
```
python -m pipeline.audio
```

**3. Check the names.** Open each `outputs/students/<Name>/<date>_transcript.md` and look at
the speaker table at the top.

- **All correct:** go to step 4.
- **Something wrong:** write the right names in `outputs/_work/<date>/speakers.yaml`
  (create it if it doesn't exist), then rebuild the transcripts (takes seconds, no re-transcribing):
  ```yaml
  <Name>:
    SPEAKER_00: <guide>
    SPEAKER_01: <Name>
  ```
  ```
  python -m pipeline.audio --render
  ```
  Names typed here always win over the automatic ones. Optionally, strengthen the voiceprints
  with the corrected round:
  ```
  python -m pipeline.audio.voices enroll
  ```

**4. Slides (separate, optional).** Ask students for a PDF, saved by date:
```
data/raw_presentations/<YYYY-MM-DD>/<Name>.pdf
```
(or point `paths.presentations` in `config.local.yaml` at a shared folder with the same layout;
Windows `.lnk` shortcuts don't work). Then:
```
python -m pipeline.slides
```
Each page is turned into an image and saved as `outputs/students/<Name>/<date>_slides.pdf`, so
hidden text, links and metadata never reach the notes session. Only new or changed PDFs are redone
(`--force` redoes all).

PDF only. Other formats are skipped and listed:
- Google Slides (`.gslides` in Drive for Desktop are cloud-only links that can't be read):
  in Drive, **File → Download → PDF**, and save it into the same date folder as `<Name>.pdf`.
- PowerPoint, Keynote etc.: export as PDF.

What a PDF loses (true of any PDF export, not caused by the flattening):
- animations and builds: each slide shows its final state, all objects at once, so
  items meant to appear in turn or disappear may overlap or cover each other
- videos and GIFs: one still frame (or an empty box), no link
- speaker notes

Slides are currently only used as reference (e.g. to check unclear words in transcripts), where
the static text is enough. Students can make a PDF more faithful by duplicating a slide per
animation step and adding a still and a link for each video.

**5. Export** to the reviews folder (`REVIEWS_DIR` in `.env`):
```
python -m pipeline.export            # transcripts and slides
python -m pipeline.export --audio    # transcripts only
python -m pipeline.export --slides   # slides only
```
Only new or changed files are copied. If you fix a name after exporting, run
`--render` and then `export` again: the corrected transcript replaces the old copy.

**6. Faculty notes** (in the reviews folder, not here). Start a separate Claude Code session
inside `REVIEWS_DIR` and run the `faculty-notes` skill:
```
cd <REVIEWS_DIR>
claude
/faculty-notes <YYYY-MM-DD>            # all students of that round
/faculty-notes <YYYY-MM-DD> <Name> ...  # some students (overwrites their notes)
```
This writes a short note per student to `<REVIEWS_DIR>/notes/<date>/faculty/<Name>.md`,
following general thesis research stages. The note rules are kept privately in the reviews
folder, and that session has restricted permissions with no access to this repo. Read the
notes and fix anything by hand before step 7.

**7. Publish** the faculty notes to Google Drive as `.docx` (`FACULTY_NOTES_DIR` in `.env`, a
Drive for Desktop path):
```
python -m pipeline.publish --date <YYYY-MM-DD>   # one round
python -m pipeline.publish                       # all rounds
```
Only `notes/<date>/faculty/` is read. A `.docx` is rebuilt only when its note is newer, and
nothing in Drive is deleted.

## Usage
Put recordings in a dated folder, one file per student:
```
data/raw_recordings/2026-10-08/<Name>.m4a
```
Then run:
```
python -m pipeline.audio                       # all new recordings
python -m pipeline.audio data\raw_recordings\2026-10-08   # one round
python -m pipeline.audio <file>.m4a --force    # redo one file
```
Recordings that already have a transcript are skipped. In VS Code: Run and Debug (Ctrl+Shift+D) → **Transcribe all**.

Other commands:
```
python -m pipeline.audio --render                 # rebuild .md from .json after changing render settings
python -m pipeline.audio.evaluate                 # score settings on hand-corrected clips in data/eval/
python -m pipeline.audio.rediarize <label>        # re-run speaker detection only, into outputs/_compare/<label>/
python -m pipeline.audio.voices enroll|test|identify   # voiceprints: build, check accuracy, label transcripts
```
Speaker names come from `outputs/_work/<date>/speakers.yaml` (manual, always wins) and from
voiceprints in `data/voiceprints/` (both gitignored). People to recognise in every recording are
listed under `voices.people` in `config.local.yaml`.
Ctrl+M markers from Windows Sound Recorder are highlighted in the transcript.

## Evaluation
`data/eval/<clip>.m4a` + `<clip>.txt` hold short clips with hand-corrected text (a line starting
with `-` marks a speaker change). `pipeline.audio.evaluate` reports word error rate and speaker-change
recall/precision/F1 for each preset in `config.yaml` → `eval.presets`.

## Layout
Inputs are organised by date, outputs by student.
```
pipeline/                    code
  audio/                     transcription pipeline     python -m pipeline.audio
  slides/                    presentation pipeline      python -m pipeline.slides
  export.py, config.py       shared
  publish.py                 faculty notes -> .docx     python -m pipeline.publish
config.yaml                  settings (override in config.local.yaml)
data/                        (ignored)
  raw_recordings/<date>/<Name>.m4a
  raw_presentations/<date>/<Name>.pdf
  eval/                                  hand-corrected test clips
  voiceprints/<Name>.npy
outputs/                     (ignored)
  students/<Name>/<date>_transcript.md   readable transcript
  students/<Name>/<date>_slides.pdf      flattened presentation
  _work/<date>/<Name>.json               word timings + speakers, for later steps
```

## Export
`python -m pipeline.export` is the only step that writes outside this repo. It copies the
transcripts and flattened slides, and nothing else, to a separate folder for downstream tools
(set `REVIEWS_DIR` in `.env`, outside this repo):
```
<REVIEWS_DIR>/transcripts/<date>/<Name>.md
<REVIEWS_DIR>/presentations/<date>/<Name>.pdf     image-only: no hidden text, links or metadata
```
`--audio` or `--slides` exports just one of the two.

`python -m pipeline.publish` is the only step that writes to Google Drive. It reads only the
faculty notes in the reviews folder and writes `.docx` copies to `FACULTY_NOTES_DIR`, which
must be outside this repo and outside the reviews folder.

## Roadmap
- [x] Transcription + speaker diarization
- [x] Evaluation on hand-corrected clips; batched Whisper, community-1 diarization
- [x] Readable transcripts: paragraphs, interjections, markers, ghost-speaker cleanup
- [x] Speaker identification: voiceprints for recurring people (`pipeline.audio.voices`), manual name map per round
- [x] Faculty review notes in a separate session, published to Drive as `.docx`
- [ ] Student notes, shared with each student
- [ ] Per-student progress tracking across rounds

## Quick commands
Run in the VS Code terminal with the venv active, after adding recordings to
`data/raw_recordings/<YYYY-MM-DD>/<Name>.m4a`:
```
python -m pipeline.audio                 # 1. transcribe new recordings + name speakers
python -m pipeline.audio --render        # 2. only if you fixed names in outputs/_work/<date>/speakers.yaml
python -m pipeline.audio.voices enroll   # 3. optional, after fixing names: improve voiceprints
python -m pipeline.slides               # 4. flatten slide PDFs (independent of 1-3)
python -m pipeline.export               # 5. copy transcripts + slides to the reviews folder
# 6. in a Claude Code session inside the reviews folder: /faculty-notes <YYYY-MM-DD>
python -m pipeline.publish --date <YYYY-MM-DD>   # 7. faculty notes -> .docx in Drive
```

## Author
Created and maintained by **Shrey Kapur** ([@shreykapur97](https://github.com/shreykapur97)).

## Disclaimer
The author accepts no liability for misuse of this software, including storing personal data beyond the consented period or any other unlawful use. Whoever runs it is responsible for consent, retention and legal compliance. See [DISCLAIMER.txt](DISCLAIMER.txt).

## License
Copyright (C) 2026 Shrey Kapur

Licensed under the GNU Affero General Public License v3.0 or later. See [LICENSE.txt](LICENSE.txt).
