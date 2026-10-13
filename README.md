# RTJT

Transcribes recorded thesis cluster reviews and labels who spoke when, so feedback can be tracked per student across review rounds.

Runs fully locally: [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (large-v3, batched) for speech-to-text and [pyannote](https://github.com/pyannote/pyannote-audio) community-1 (exclusive mode) for speaker diarization. Settings were chosen with the evaluation script below.

**Privacy:** recordings, transcripts and voiceprints never leave the machine and are gitignored. Only code is in this repo.

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
python -m pipeline
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
  python -m pipeline --render
  ```
  Names typed here always win over the automatic ones. Optionally, strengthen the voiceprints
  with the corrected round:
  ```
  python -m pipeline.voices enroll
  ```

**4. Export** the transcripts to the reviews folder (`REVIEWS_DIR` in `.env`):
```
python -m pipeline.export
```
Only new or changed transcripts are copied. If you fix a name after exporting, run
`--render` and then `export` again: the corrected transcript replaces the old copy.

**5. Slides (optional).** Ask students for a PDF and save it next to the recording's date:
```
data/raw_presentations/<YYYY-MM-DD>/<Name>.pdf
```
```
python -m pipeline.slides
```
Each page is turned into an image and the copy goes to the reviews folder, so hidden text,
links and metadata never reach Cowork. Other formats are skipped: export them as PDF first.
Only new or changed PDFs are copied (`--force` redoes all).

## Usage
Put recordings in a dated folder, one file per student:
```
data/raw_recordings/2026-10-08/<Name>.m4a
```
Then run:
```
python -m pipeline                       # all new recordings
python -m pipeline data\raw_recordings\2026-10-08   # one round
python -m pipeline <file>.m4a --force    # redo one file
```
Recordings that already have a transcript are skipped. In VS Code: Run and Debug (Ctrl+Shift+D) → **Transcribe all**.

Other commands:
```
python -m pipeline --render                 # rebuild .md from .json after changing render settings
python -m pipeline.evaluate                 # score settings on hand-corrected clips in data/eval/
python -m pipeline.rediarize <label>        # re-run speaker detection only, into outputs/_compare/<label>/
python -m pipeline.voices enroll|test|identify   # voiceprints: build, check accuracy, label transcripts
```
Speaker names come from `outputs/_work/<date>/speakers.yaml` (manual, always wins) and from
voiceprints in `data/voiceprints/` (both gitignored). People to recognise in every recording are
listed under `voices.people` in `config.local.yaml`.
Ctrl+M markers from Windows Sound Recorder are highlighted in the transcript.

## Evaluation
`data/eval/<clip>.m4a` + `<clip>.txt` hold short clips with hand-corrected text (a line starting
with `-` marks a speaker change). `pipeline.evaluate` reports word error rate and speaker-change
recall/precision/F1 for each preset in `config.yaml` → `eval.presets`.

## Layout
Inputs are organised by date, outputs by student.
```
pipeline/                    code
config.yaml                  settings (override in config.local.yaml)
data/                        (ignored)
  raw_recordings/<date>/<Name>.m4a
  raw_presentations/<date>/<Name>.pdf
  eval/                                  hand-corrected test clips
  voiceprints/<Name>.npy
outputs/                     (ignored)
  students/<Name>/<date>_transcript.md   readable transcript
  _work/<date>/<Name>.json               word timings + speakers, for later steps
```

## Export
`python -m pipeline.export` copies the transcripts, and nothing else, to a separate folder
for downstream tools (set `REVIEWS_DIR` in `.env`, outside this repo):
```
<REVIEWS_DIR>/transcripts/<date>/<Name>.md
```
`python -m pipeline.slides` copies the presentations (PDF only) to
`<REVIEWS_DIR>/presentations/<date>/<Name>.pdf`, flattened: every page is rendered to an image,
so hidden text, links, metadata and scripts never leave this folder.

## Roadmap
- [x] Transcription + speaker diarization
- [x] Evaluation on hand-corrected clips; batched Whisper, community-1 diarization
- [x] Readable transcripts: paragraphs, interjections, markers, ghost-speaker cleanup
- [x] Speaker identification: voiceprints for recurring people (`pipeline.voices`), manual name map per round
- [ ] Review summaries + per-student progress tracking

## Quick commands
Run in the VS Code terminal with the venv active, after adding recordings to
`data/raw_recordings/<YYYY-MM-DD>/<Name>.m4a`:
```
python -m pipeline                 # 1. transcribe new recordings + name speakers
python -m pipeline --render        # 2. only if you fixed names in outputs/_work/<date>/speakers.yaml
python -m pipeline.voices enroll   # 3. optional, after fixing names: improve voiceprints
python -m pipeline.export          # 4. copy transcripts to the reviews folder
python -m pipeline.slides          # 5. optional: flatten + copy slide PDFs to the reviews folder
```
