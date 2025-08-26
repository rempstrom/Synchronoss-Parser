# Synchronoss Parser

Utility scripts for working with Synchronoss data exports.

This toolbox converts Verizon/Synchronoss backups into more useful formats. It can compile media
files, convert contact lists, merge call logs with contacts, render HTML message transcripts and
produce attachment inventories. A Tkinter GUI exposes these features for non‑technical users.

Phone numbers are normalized by removing punctuation and an optional leading `1` country code so
contacts match regardless of formatting.

## Sample data layout

Scripts expect exports arranged like:

```
Call Log/
  call_log.csv
messages/
  <date>.csv
  attachments/
    mms/in/<YYYY-MM-DD>/<files>
    mms/out/<YYYY-MM-DD>/<files>
```

## Installation

Install dependencies with pip:

```bash
pip install -r requirements.txt
```

`requirements.txt` lists Pillow, openpyxl, pandas and pytest (Tkinter may require OS packages).

## Scripts

### collect_media.py
Copy media from a Verizon Mobile backup into a single folder and log EXIF metadata to Excel.

```bash
python scripts/collect_media.py
```

### collect_attachments.py
Collect message attachments from a Synchronoss export into a single folder and log metadata to
Excel.

The script scans the `messages/attachments/` directory:

```
messages/
  attachments/
    mms/in/<YYYY-MM-DD>/<files>
    mms/out/<YYYY-MM-DD>/<files>
```

All files are copied to `Compiled Attachments/` and their details recorded in
`Compiled Attachments/compiled_attachment_log/compiled_attachment_log.xlsx`.

```bash
python scripts/collect_attachments.py
```

### contacts_to_excel.py
Convert a `contacts.txt` export to an Excel spreadsheet.

```bash
python scripts/contacts_to_excel.py --input contacts.txt --output contacts.xlsx
```

### merge_contacts_logs.py
Annotate a call log CSV with caller and recipient names using a contacts Excel file.

```bash
python scripts/merge_contacts_logs.py --call-log "Call Log/call_log.csv" --contacts-xlsx contacts.xlsx
```

### render_transcripts.py
Render chat-bubble style HTML transcripts from message CSVs and link attachments. Optionally supply
a contacts Excel file for name lookups.

```bash
python scripts/render_transcripts.py --in messages --out transcripts --contacts-xlsx contacts.xlsx
```

### toolbox_gui.py
Tkinter GUI that wraps Collect Media, Collect Attachments, Contacts to Excel and Render Transcripts workflows.

```bash
python scripts/toolbox_gui.py
```

### collect_media_gui.py
Simple GUI wrapper for `collect_media.py`.

```bash
python scripts/collect_media_gui.py
```

Both GUI scripts can be packaged as standalone executables with PyInstaller, e.g.

```bash
pyinstaller --onefile scripts/toolbox_gui.py
```

## Testing

Run the test suite with:

```bash
pytest
```

