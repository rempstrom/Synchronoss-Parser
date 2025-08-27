#!/usr/bin/env python3
"""Extract and collect quarantined files from a Verizon backup."""

from __future__ import annotations

from pathlib import Path
import shutil
import tempfile
import zipfile

from .collect_media import ensure_unique_name

# -------------------------------------------------------------
# Default paths used when running as a script
# -------------------------------------------------------------
DEFAULT_ROOT = Path("VZMOBILE")
DEFAULT_COMPILED = DEFAULT_ROOT / "Compiled Quarantine Files"

# -------------------------------------------------------------
# File type detection
# -------------------------------------------------------------

def detect_extension(path: Path) -> str | None:
    """Return file extension based on signature bytes."""
    with path.open("rb") as f:
        header = f.read(16)

    signatures = {
        b"\xFF\xD8\xFF": ".jpg",
        b"\x89PNG\r\n\x1a\n": ".png",
        b"GIF87a": ".gif",
        b"GIF89a": ".gif",
        b"BM": ".bmp",
        b"%PDF": ".pdf",
    }
    for sig, ext in signatures.items():
        if header.startswith(sig):
            return ext
    if len(header) >= 12 and header[4:8] == b"ftyp":
        return ".mp4"
    return None


def rename_with_extension(path: Path) -> Path:
    """Rename file to have correct extension if detectable."""
    ext = detect_extension(path)
    if ext and path.suffix.lower() != ext:
        new_path = ensure_unique_name(path.parent, path.stem + ext)
        path.rename(new_path)
        return new_path
    return path

# -------------------------------------------------------------
# Main processing
# -------------------------------------------------------------

def collect_quarantined_files(root: Path, compiled_path: Path) -> list[Path]:
    """Extract quarantined zip files and copy contents to ``compiled_path``."""
    compiled_path.mkdir(parents=True, exist_ok=True)
    copied: list[Path] = []

    for zip_path in root.rglob("*.zip_file_*"):
        if not zip_path.is_file():
            continue
        with zipfile.ZipFile(zip_path) as zf, tempfile.TemporaryDirectory() as tmpdir:
            zf.extractall(tmpdir)
            for extracted in Path(tmpdir).rglob("*"):
                if extracted.is_dir():
                    continue
                fixed = rename_with_extension(extracted)
                dest = ensure_unique_name(compiled_path, fixed.name)
                shutil.copy2(fixed, dest)
                copied.append(dest)
    return copied

# -------------------------------------------------------------
# CLI
# -------------------------------------------------------------

def main(root_path: Path = DEFAULT_ROOT, compiled_path: Path = DEFAULT_COMPILED) -> None:
    """CLI entry point using default paths."""
    if not root_path.exists():
        raise SystemExit(f"Root folder '{root_path}' not found.")

    files = collect_quarantined_files(root_path, compiled_path)
    print(
        f"Copied {len(files)} files from '{root_path}' to '{compiled_path}'.",
    )


if __name__ == "__main__":
    main()
