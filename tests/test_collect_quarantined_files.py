import importlib
import sys
from pathlib import Path
import zipfile


def load_module():
    project_root = Path(__file__).resolve().parents[1]
    sys.path.append(str(project_root))
    return importlib.import_module("synchronoss_parser.collect_quarantined_files")


def test_collect_quarantined_files(tmp_path):
    module = load_module()
    root = tmp_path / "VZMOBILE"
    root.mkdir()
    compiled = root / "Compiled Quarantine Files"

    data = b"\x89PNG\r\n\x1a\nrest"
    zip_path = root / "sample.zip_file_1"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("image", data)

    copied = module.collect_quarantined_files(root, compiled)

    assert len(copied) == 1
    dest = compiled / "image.png"
    assert dest.exists()
    assert dest.suffix == ".png"
    assert copied[0] == dest
