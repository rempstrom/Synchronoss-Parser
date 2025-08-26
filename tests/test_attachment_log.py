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
    assert '<img src="thumbnails/mms/in/2024-01-01/sample.png"' in html


def test_duplicate_filenames_different_contexts(tmp_path):
    messages_dir = tmp_path / "messages"
    messages_dir.mkdir()

    attachments_dir1 = messages_dir / "attachments" / "mms" / "in" / "2024-01-01"
    attachments_dir1.mkdir(parents=True)
    img1 = Image.new("RGB", (10, 10), color="red")
    img_path1 = attachments_dir1 / "sample.png"
    img1.save(img_path1)

    attachments_dir2 = messages_dir / "attachments" / "sms" / "out" / "2024-01-02"
    attachments_dir2.mkdir(parents=True)
    img2 = Image.new("RGB", (10, 10), color="blue")
    img_path2 = attachments_dir2 / "sample.png"
    img2.save(img_path2)

    csv1 = (
        "Date,Type,Direction,Attachments,Body,Sender,Recipients,\"Message ID\"\n"
        "2024-01-01T00:00:00Z,mms,in,sample.png,Hi,Alice,Bob,id1\n"
    )
    csv2 = (
        "Date,Type,Direction,Attachments,Body,Sender,Recipients,\"Message ID\"\n"
        "2024-01-02T00:00:00Z,sms,out,sample.png,Bye,Bob,Alice,id2\n"
    )
    (messages_dir / "20240101.csv").write_text(csv1)
    (messages_dir / "20240102.csv").write_text(csv2)

    out_dir = tmp_path / "Attachment Log"
    generate_log(messages_dir, out_dir)

    html_file = out_dir / "attachment_log.html"
    html = html_file.read_text()

    rel1 = os.path.relpath(img_path1, start=out_dir).replace(os.sep, "/")
    rel2 = os.path.relpath(img_path2, start=out_dir).replace(os.sep, "/")
    assert f'<a href="{rel1}">sample.png</a>' in html
    assert f'<a href="{rel2}">sample.png</a>' in html
    assert html.count('thumbnails/mms/in/2024-01-01/sample.png') == 1
    assert html.count('thumbnails/sms/out/2024-01-02/sample.png') == 1
