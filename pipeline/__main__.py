# Copyright (C) 2026 Shrey Kapur
# SPDX-License-Identifier: AGPL-3.0-or-later

print("""Run one of:
  python -m pipeline.audio     transcribe + speaker-label recordings  (--render, --force, ...)
  python -m pipeline.slides    flatten presentation PDFs
  python -m pipeline.export    copy results to the reviews folder    (--audio / --slides)""")
