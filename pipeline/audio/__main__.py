# Copyright (C) 2026 Shrey Kapur
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Usage: python -m pipeline.audio [files or folders...] [--force] [--no-diarize] [--render]

With no paths, processes every audio file under data/raw_recordings.
data/raw_recordings/<date>/<Name>.m4a ->
  outputs/students/<Name>/<date>_transcript.md   (shareable)
  outputs/_work/<date>/<Name>.json               (local working data)

--render rebuilds every .md from the existing .json without re-transcribing
(use after changing formatting settings).
"""
import argparse
import json
import time
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

from .decode import AUDIO_EXTS, SAMPLE_RATE, load_audio, read_markers  # noqa: E402
from ..config import load_config  # noqa: E402
from .names import names_for  # noqa: E402
from .render import save, write_markdown  # noqa: E402


def find_audio(paths: list[Path]) -> list[Path]:
    files = []
    for p in paths:
        if p.is_dir():
            files += sorted(f for f in p.rglob("*") if f.suffix.lower() in AUDIO_EXTS)
        elif p.suffix.lower() in AUDIO_EXTS:
            files.append(p)
    return files


def md_path_for(outputs: Path, student: str, date: str) -> Path:
    return outputs / "students" / student / f"{date}_transcript.md"


def render_all(cfg: dict) -> None:
    outputs = cfg["paths"]["outputs"]
    for json_path in sorted((outputs / "_work").rglob("*.json")):
        data = json.loads(json_path.read_text(encoding="utf-8"))
        if "words" not in data["utterances"][0]:
            print(f"skip {json_path.relative_to(outputs)} (old format, re-transcribe with --force)")
            continue
        if "markers" not in data["meta"]:
            # Older outputs: read markers from the recording and store them
            recording = cfg["paths"]["recordings"] / data["meta"]["source"]
            data["meta"]["markers"] = read_markers(recording) if recording.exists() else []
            json_path.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
        md_path = md_path_for(outputs, data["meta"]["student"], data["meta"]["date"])
        write_markdown(data, cfg["render"], md_path, names_for(data, outputs), cfg["voices"]["label_student"])
        print(f"rendered {md_path.relative_to(outputs.parent)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Transcribe and speaker-label review recordings")
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--force", action="store_true", help="redo files that already have outputs")
    parser.add_argument("--no-diarize", action="store_true", help="skip speaker labelling")
    parser.add_argument("--render", action="store_true", help="rebuild .md files from existing .json only")
    args = parser.parse_args()

    cfg = load_config()
    if args.render:
        render_all(cfg)
        return

    recordings, outputs = cfg["paths"]["recordings"], cfg["paths"]["outputs"]
    files = find_audio([p.resolve() for p in args.paths] or [recordings])
    if not files:
        print(f"No audio found in {args.paths or recordings}")
        return

    from .diarize import diarize
    from .merge import build_utterances
    from .transcribe import load_model, transcribe
    from .voices import candidates, load_profiles, match, speaker_embeddings

    diarize_on = cfg["diarization"]["enabled"] and not args.no_diarize
    model = None
    for i, f in enumerate(files, 1):
        rel = f.relative_to(recordings) if f.is_relative_to(recordings) else Path(f.name)
        student, date = f.stem, (rel.parent.name or "undated")
        md_path = md_path_for(outputs, student, date)
        json_path = outputs / "_work" / date / f"{student}.json"
        if md_path.exists() and not args.force:
            print(f"[{i}/{len(files)}] skip {rel} (exists, use --force)")
            continue

        print(f"[{i}/{len(files)}] {rel}")
        t0 = time.time()
        audio = load_audio(f)
        duration = len(audio) / SAMPLE_RATE

        turns = []
        if diarize_on:
            print("  diarizing...")
            turns = diarize(audio, cfg["diarization"])
            print(f"  {len({s for _, _, s in turns})} speakers found")

        if model is None:
            print("  loading whisper...")
            model = load_model(cfg["whisper"])
        words, language = transcribe(model, audio, cfg["whisper"])

        data = {
            "meta": {
                "student": student, "date": date, "source": str(rel),
                "language": language, "duration": duration, "whisper": cfg["whisper"]["model"],
                "markers": read_markers(f),
            },
            "utterances": build_utterances(words, turns),
        }
        if turns and (profiles := load_profiles(cfg)):
            print("  recognising voices...")
            embs = speaker_embeddings(audio, data["utterances"], cfg)
            names, scores = match(embs, candidates(profiles, cfg, student), cfg["voices"]["threshold"])
            data["meta"].update(speaker_embeddings=embs, speaker_names=names, speaker_scores=scores)
            print(f"  {', '.join(f'{s}={n}' for s, n in sorted(names.items())) or 'nobody recognised'}")
        save(data, cfg["render"], md_path, json_path, names_for(data, outputs), cfg["voices"]["label_student"])
        print(f"  done in {(time.time() - t0) / 60:.1f} min -> {md_path.relative_to(outputs.parent)}")


if __name__ == "__main__":
    main()
