"""Usage: python -m pipeline [files or folders...] [--force] [--no-diarize]

With no paths, processes every audio file under data/raw_recordings.
data/raw_recordings/<date>/<Name>.m4a ->
  outputs/students/<Name>/<date>_transcript.md   (shareable)
  outputs/_work/<date>/<Name>.json               (local working data)
"""
import argparse
import time
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

from .audio import AUDIO_EXTS, SAMPLE_RATE, load_audio  # noqa: E402
from .config import load_config  # noqa: E402


def find_audio(paths: list[Path]) -> list[Path]:
    files = []
    for p in paths:
        if p.is_dir():
            files += sorted(f for f in p.rglob("*") if f.suffix.lower() in AUDIO_EXTS)
        elif p.suffix.lower() in AUDIO_EXTS:
            files.append(p)
    return files


def main() -> None:
    parser = argparse.ArgumentParser(description="Transcribe and speaker-label review recordings")
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--force", action="store_true", help="redo files that already have outputs")
    parser.add_argument("--no-diarize", action="store_true", help="skip speaker labelling")
    args = parser.parse_args()

    cfg = load_config()
    recordings, outputs = cfg["paths"]["recordings"], cfg["paths"]["outputs"]
    files = find_audio([p.resolve() for p in args.paths] or [recordings])
    if not files:
        print(f"No audio found in {args.paths or recordings}")
        return

    from .diarize import diarize
    from .merge import build_utterances, write_outputs
    from .transcribe import load_model, transcribe

    diarize_on = cfg["diarization"]["enabled"] and not args.no_diarize
    model = None
    for i, f in enumerate(files, 1):
        rel = f.relative_to(recordings) if f.is_relative_to(recordings) else Path(f.name)
        student, date = f.stem, (rel.parent.name or "undated")
        md_path = outputs / "students" / student / f"{date}_transcript.md"
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

        utterances = build_utterances(words, turns)
        meta = {
            "student": student, "date": date, "source": str(rel),
            "language": language, "duration": duration, "whisper": cfg["whisper"]["model"],
        }
        write_outputs(utterances, meta, md_path, json_path)
        print(f"  done in {(time.time() - t0) / 60:.1f} min -> {md_path.relative_to(outputs.parent)}")


if __name__ == "__main__":
    main()
