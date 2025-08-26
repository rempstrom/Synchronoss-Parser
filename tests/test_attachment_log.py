import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from scripts.attachment_log import create_thumbnail, log_attachments


def test_create_thumbnail_and_logging(tmp_path):
    Image = pytest.importorskip("PIL.Image")

    src = tmp_path / "image.png"
    Image.new("RGB", (300, 200), color="red").save(src)

    thumb = tmp_path / "thumb.png"
    assert create_thumbnail(src, thumb) is not None
    assert thumb.exists()

    # Non-image file should be skipped
    (tmp_path / "text.txt").write_text("hello")

    records = log_attachments(tmp_path, tmp_path / "thumbs")
    assert len(records) == 1
    thumb_record = records[0]
    assert Path(thumb_record["thumbnail"]).exists()
    im = Image.open(thumb_record["thumbnail"])
    assert max(im.size) <= 150
