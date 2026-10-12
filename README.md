# RTJT

Transcribes recorded thesis cluster reviews and labels who spoke when, so feedback can be tracked per student across review rounds.

Runs fully locally: [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (large-v3, batched) for speech-to-text and [pyannote](https://github.com/pyannote/pyannote-audio) community-1 (exclusive mode) for speaker diarization. Settings were chosen with the evaluation script below.

**Privacy:** recordings, presentations and transcripts never leave the machine and are gitignored. Only code is in this repo.

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
  presentations/<date>/<Name>.pdf
outputs/                     (ignored)
  students/<Name>/<date>_transcript.md   readable transcript
  _work/<date>/<Name>.json               word timings + speakers, for later steps
```

## Roadmap
- [x] Transcription + speaker diarization
- [x] Evaluation on hand-corrected clips; batched Whisper, community-1 diarization
- [x] Readable transcripts: paragraphs, interjections, markers, ghost-speaker cleanup
- [x] Speaker identification: voiceprints for recurring people (`pipeline.voices`), manual name map per round
- [ ] Review summaries + per-student progress tracking
