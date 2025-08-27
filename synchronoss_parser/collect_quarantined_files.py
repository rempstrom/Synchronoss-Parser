#!/usr/bin/env python3
"""Extract quarantined zip files fixing missing or wrong extensions."""
from __future__ import annotations

from pathlib import Path
import zipfile
import imghdr
from typing import Iterable, List, Tuple

from .collect_media import ensure_unique_name


def _guess_extension(data: bytes, original_suffix: str = "") -> str:
    """Guess file extension based on file signature.

    Falls back to ``original_suffix`` if type cannot be determined.
    """
    kind = imghdr.what(None, data)
    if kind:
        if kind == "jpeg":
            return ".jpg"
        return f".{kind}"
    if data.startswith(b"%PDF"):
        return ".pdf"
    try:
        data.decode("utf-8")
        return ".txt"
    except Exception:
        pass
    return original_suffix


def collect_quarantined_files(
    archives: Iterable[Path], compiled_path: Path
) -> Tuple[List[Path], List[str]]:
    """Extract files from ``archives`` into ``compiled_path``.

    Files inside archives with missing or wrong extensions will be written
    using the extension guessed from their contents. Duplicate file names are
    resolved using :func:`ensure_unique_name`.

    Parameters
    ----------
    archives: Iterable[Path]
        Paths to ``.zip`` files (possibly with non-standard extensions).
    compiled_path: Path
        Destination directory for extracted files.

    Returns
    -------
    Tuple[List[Path], List[str]]
        A tuple of ``(outputs, errors)`` where ``outputs`` is the list of
        extracted file paths and ``errors`` contains error messages for any
        archives that could not be processed.
    """
    compiled_path.mkdir(exist_ok=True)
    outputs: List[Path] = []
    errors: List[str] = []

    for archive in archives:
        try:
            if not zipfile.is_zipfile(archive):
                errors.append(f"{archive} is not a zip file")
                continue
            with zipfile.ZipFile(archive) as zf:
                for info in zf.infolist():
                    if info.is_dir():
                        continue
                    data = zf.read(info)
                    orig_suffix = Path(info.filename).suffix
                    ext = _guess_extension(data, orig_suffix)
                    name = Path(info.filename).stem + ext
                    dest = ensure_unique_name(compiled_path, name)
                    dest.write_bytes(data)
                    outputs.append(dest)
        except Exception as exc:
            errors.append(f"{archive}: {exc}")
    return outputs, errors


__all__ = ["collect_quarantined_files"]
