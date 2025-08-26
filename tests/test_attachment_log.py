import os
import sys
from pathlib import Path

from PIL import Image

sys.path.append(str(Path(__file__).resolve().parents[1]))
from scripts.attachment_log import generate_log


def test_attachment_log_html_contains_rows(tmp_path):
    messages_dir = tmp_path / "messages"
    messages_dir.mkdir()
    attachments_dir = messages_dir / "attachments" / "mms" / "in" / "2024-01-01"
    attachments_dir.mkdir(parents=True)

    img = Image.new("RGB", (10, 10), color="red")
    img_path = attachments_dir / "sample.png"
    img.save(img_path)

    csv_content = (
        "Date,Type,Direction,Attachments,Body,Sender,Recipients,\"Message ID\"\n"
        "2024-01-01T00:00:00Z,mms,in,sample.png,Hi,Alice,Bob,id1\n"
    )
    (messages_dir / "20240101.csv").write_text(csv_content)

    out_dir = tmp_path / "Attachment Log"
    generate_log(messages_dir, out_dir)

    html_file = out_dir / "attachment_log.html"
    assert html_file.exists()
    html = html_file.read_text()

    rel_link = os.path.relpath(img_path, start=out_dir).replace(os.sep, "/")
    assert f'<a href="{rel_link}">sample.png</a>' in html
    assert "<td>Alice</td>" in html
    assert "<td>Bob</td>" in html
    assert '<img src="thumbnails/sample.png"' in html
