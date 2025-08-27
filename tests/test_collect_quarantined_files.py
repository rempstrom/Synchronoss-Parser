import importlib
import io
import sys
import zipfile
from pathlib import Path

import pytest
from PIL import Image


def load_module():
    project_root = Path(__file__).resolve().parents[1]
    sys.path.append(str(project_root))
    return importlib.import_module("synchronoss_parser.collect_quarantined_files")


def _png_bytes(color: str) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (1, 1), color=color).save(buf, format="PNG")
    return buf.getvalue()


def test_collect_quarantined_files_handles_missing_and_wrong_extensions(tmp_path):
    module = load_module()

    # Create sample archives with files lacking or having wrong extensions
    archive1 = tmp_path / "sample.zip_file_1"
    with zipfile.ZipFile(archive1, "w") as zf:
        zf.writestr("image", _png_bytes("red"))
        zf.writestr("image_wrong.txt", _png_bytes("blue"))

    archive2 = tmp_path / "sample2.zip_file_1"
    with zipfile.ZipFile(archive2, "w") as zf:
        zf.writestr("image", _png_bytes("green"))

    not_zip = tmp_path / "notzip.zip_file_1"
    not_zip.write_text("not a zip archive")

    output_dir = tmp_path / "compiled"
    outputs, errors = module.collect_quarantined_files([archive1, archive2, not_zip], output_dir)

    names = sorted(p.name for p in outputs)
    assert names == ["image.png", "image_1.png", "image_wrong.png"]
    assert sorted(f.name for f in output_dir.iterdir()) == names

    for p in outputs:
        assert p.suffix == ".png"

    assert any("notzip.zip_file_1" in e for e in errors)
