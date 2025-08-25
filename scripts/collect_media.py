#!/usr/bin/env python3
"""
Collect media from a Verizon Mobile backup and log metadata to Excel.

Folder structure expected:
VZMOBILE/
 └─ YYYY-MM-DD/
     └─ My Device Name/
         └─ media files

Outputs:
1. Compiled Media/   — all copied media
2. compiled_media_log.xlsx — metadata spreadsheet
"""

from pathlib import Path
import hashlib
import shutil
from PIL import Image, ExifTags
from openpyxl import Workbook

# -------------------------------------------------------------
# Configuration
# -------------------------------------------------------------
ROOT = Path("VZMOBILE")            # root folder containing date/device hierarchy
COMPILED = ROOT / "Compiled Media" # output folder
LOGFILE = ROOT / "compiled_media_log.xlsx"

# Media file extensions to search
MEDIA_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".mp4", ".mov"}

# -------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------
def md5sum(path: Path) -> str:
    """Return MD5 hash of a file."""
    h = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def extract_exif(path: Path) -> dict:
    """
    Extract EXIF data from an image (if any).
    Returns dict with human-readable keys; empty dict if none or file not image.
    """
    try:
        with Image.open(path) as img:
            exif = img._getexif() or {}
    except Exception:
        return {}

    # Convert tag IDs to names
    tag_map = {ExifTags.TAGS.get(k, k): v for k, v in exif.items()}
    return tag_map

def ensure_unique_name(target_dir: Path, filename: str) -> Path:
    """Ensure unique filename inside target_dir to avoid overwrites."""
    base = Path(filename).stem
    ext = Path(filename).suffix
    counter = 0
    candidate = target_dir / filename
    while candidate.exists():
        counter += 1
        candidate = target_dir / f"{base}_{counter}{ext}"
    return candidate

# -------------------------------------------------------------
# Main processing
# -------------------------------------------------------------
def collect_media():
    COMPILED.mkdir(exist_ok=True)

    records = []
    exif_keys = set()

    for date_dir in sorted(ROOT.glob("20??-??-??")):           # match YYYY-MM-DD
        if not date_dir.is_dir():
            continue
        date_str = date_dir.name

        for device_dir in date_dir.iterdir():
            if not device_dir.is_dir():
                continue
            device_name = device_dir.name

            for media_file in device_dir.rglob("*"):
                if media_file.suffix.lower() not in MEDIA_EXTS:
                    continue

                # Copy to compiled folder
                dest = ensure_unique_name(COMPILED, media_file.name)
                shutil.copy2(media_file, dest)

                # Metadata
                exif = extract_exif(media_file)
                exif_keys.update(exif.keys())
                record = {
                    "File Name": dest.name,
                    "Date": date_str,
                    "Device": device_name,
                    "MD5": md5sum(media_file)
                }
                record.update(exif)
                records.append(record)

    return records, sorted(exif_keys)

# -------------------------------------------------------------
# Excel logging
# -------------------------------------------------------------
def write_excel(records, exif_keys):
    wb = Workbook()
    ws = wb.active
    ws.title = "Media Metadata"

    headers = ["File Name", "Date", "Device", "MD5"] + list(exif_keys)
    ws.append(headers)

    for rec in records:
        row = [rec.get(h, "") for h in headers]
        ws.append(row)

    wb.save(LOGFILE)

# -------------------------------------------------------------
if __name__ == "__main__":
    if not ROOT.exists():
        raise SystemExit(f"Root folder '{ROOT}' not found.")

    records, exif_keys = collect_media()
    write_excel(records, exif_keys)
    print(f"Copied {len(records)} files to '{COMPILED}' and logged metadata to '{LOGFILE}'.")
