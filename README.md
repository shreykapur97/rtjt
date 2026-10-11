# RTPM

Transcribes recorded thesis cluster student reviews and labels speakers.

**Privacy:** audio and transcripts stay local. Only code is in this repo.

## Setup
```
uv sync
copy .env.example .env   # add HF_TOKEN
```

## Layout
- `pipeline/` — code
- `config.yaml` — settings (override in `config.local.yaml`)
- `data/raw_recordings/<date>/` — review audio (ignored)
- `data/presentations/<date>/` — presentation PDFs (ignored)
- `outputs/` — transcripts (ignored)
