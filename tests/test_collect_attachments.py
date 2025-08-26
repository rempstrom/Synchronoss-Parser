import importlib
import hashlib
import sys
from pathlib import Path

from PIL import Image
from openpyxl import load_workbook


def load_module():
    project_root = Path(__file__).resolve().parents[1]
    sys.path.append(str(project_root))
    return importlib.import_module("scripts.collect_attachments")


def test_collect_attachments_excel_contains_rows(tmp_path):
    collect_attachments = load_module()

    messages_dir = tmp_path / "messages"
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

    compiled = tmp_path / "Compiled Attachments"
    records, exif_keys = collect_attachments.collect_attachments(messages_dir / "attachments", compiled)
    logfile = compiled / "log.xlsx"
    collect_attachments.write_excel(records, exif_keys, logfile)

    dest_files = list(compiled.glob("*.png"))
    assert len(dest_files) == 1

    md5 = hashlib.md5(img_path.read_bytes()).hexdigest()

    wb = load_workbook(logfile)
    ws = wb.active
    assert ws.cell(row=2, column=1).value == dest_files[0].name
    assert ws.cell(row=2, column=2).value == "2024-01-01T00:00:00Z"
    assert ws.cell(row=2, column=3).value == "Alice"
    assert ws.cell(row=2, column=4).value == "Bob"
    assert ws.cell(row=2, column=5).value == md5


def test_duplicate_filenames_different_contexts(tmp_path):
    collect_attachments = load_module()

    messages_dir = tmp_path / "messages"
    messages_dir.mkdir()

    # First attachment
    dir1 = messages_dir / "attachments" / "mms" / "in" / "2024-01-01"
    dir1.mkdir(parents=True)
    img1 = Image.new("RGB", (10, 10), color="red")
    img1_path = dir1 / "sample.png"
    img1.save(img1_path)

    # Second attachment with same filename in different folder
    dir2 = messages_dir / "attachments" / "sms" / "out" / "2024-01-02"
    dir2.mkdir(parents=True)
    img2 = Image.new("RGB", (10, 10), color="blue")
    img2_path = dir2 / "sample.png"
    img2.save(img2_path)

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

    compiled = tmp_path / "Compiled Attachments"
    records, _ = collect_attachments.collect_attachments(messages_dir / "attachments", compiled)

    names = {r["File Name"] for r in records}
    assert names == {"sample.png", "sample_1.png"}

    senders = {r["Sender"] for r in records}
    assert senders == {"Alice", "Bob"}

    assert len(list(compiled.glob("*.png"))) == 2
