# RTJT

Transcribes recorded thesis cluster reviews and labels who spoke when, so feedback can be tracked per student across review rounds.

Runs fully locally: [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (large-v3) for speech-to-text and [pyannote](https://github.com/pyannote/pyannote-audio) for speaker diarization.

**Privacy:** recordings, presentations and transcripts never leave the machine and are gitignored. Only code is in this repo.

## Requirements
- Windows/Linux with an NVIDIA GPU (8 GB VRAM is enough)
- [uv](https://docs.astral.sh/uv/) and [ffmpeg](https://ffmpeg.org/) on PATH
- A Hugging Face read token, with the terms accepted for
  [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1) and
  [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0)

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
- [ ] Speaker identification (voice profiles → real names)
- [ ] Transcript cleanup
- [ ] Review summaries + per-student progress tracking
