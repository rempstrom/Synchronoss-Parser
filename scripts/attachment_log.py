#!/usr/bin/env python3
"""
Attachment logger utility.

Scans an attachments folder and records metadata while generating
thumbnails for each file.  The thumbnail creation is handled by
``create_thumbnail`` which tries to open files using ``PIL.Image`` and
converts them to a small PNG image.  Non-image files or files that PIL
cannot handle are silently skipped.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional

try:  # pragma: no cover - used for graceful fallback when Pillow missing
    from PIL import Image
except Exception:  # pragma: no cover
    Image = None  # type: ignore

THUMB_SIZE = (150, 150)


def create_thumbnail(src_path: Path, dest_path: Path, size: tuple[int, int] = THUMB_SIZE) -> Optional[Path]:
    """Create a thumbnail for ``src_path`` and save to ``dest_path``.

    ``dest_path``'s parent directory is created automatically.  The
    resulting thumbnail is always saved in PNG format regardless of the
    source.  Any failure to open or process the image results in
    ``None`` being returned.
    """
    if Image is None:
        return None

    try:
        with Image.open(src_path) as img:
            img = img.convert("RGBA")  # ensure a consistent mode
            img.thumbnail(size)
            dest_path = dest_path.with_suffix(".png")
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            img.save(dest_path, format="PNG")
            return dest_path
    except Exception:
        return None


def iter_attachments(root: Path) -> Iterable[Path]:
    """Yield all files under ``root`` recursively."""
    for path in sorted(root.rglob("*")):
        if path.is_file():
            yield path


def log_attachments(root: Path, thumb_dir: Path) -> List[dict]:
    """Iterate ``root`` creating thumbnails in ``thumb_dir``.

    Returns a list of dictionaries with ``file`` and ``thumbnail`` keys
    for each processed attachment.  Files that cannot be opened by PIL
    are skipped entirely.
    """
    records: List[dict] = []
    thumb_dir.mkdir(parents=True, exist_ok=True)

    for f in iter_attachments(root):
        thumb_path = create_thumbnail(f, thumb_dir / f"{f.stem}_thumb.png")
        if thumb_path is None:
            continue
        records.append({"file": str(f), "thumbnail": str(thumb_path)})

    return records


if __name__ == "__main__":  # pragma: no cover - simple CLI usage
    import argparse
    import csv

    ap = argparse.ArgumentParser(description="Log attachments with thumbnails")
    ap.add_argument("--attachments", required=True, help="Root folder containing attachments")
    ap.add_argument("--log", required=True, help="Path to output CSV log")
    ap.add_argument("--thumb-dir", default="thumbnails", help="Directory to store generated thumbnails")
    args = ap.parse_args()

    root = Path(args.attachments)
    thumb_dir = Path(args.thumb_dir)
    records = log_attachments(root, thumb_dir)

    with open(args.log, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["file", "thumbnail"])
        writer.writeheader()
        writer.writerows(records)

    print(f"Logged {len(records)} attachments to {args.log}")
