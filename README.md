# Synchronoss Parser

Utility scripts for working with Synchronoss data exports.

Phone numbers are normalized by removing punctuation and an optional
leading `1` country code. This allows contacts to be matched regardless of
whether numbers are provided as `+12223334444`, `111-222-3333`, `(111) 222-3333`,
`+1 111-222-3333`, or `1112223333`.

## Installation

Install dependencies with pip:

```bash
pip install -r requirements.txt
```

`pytest` is included for running the test suite.

## merge_contacts_logs.py

Merge a call log CSV (`Call Log/call_log.csv`) with a contacts Excel file to annotate phone numbers with
names.

```bash
python scripts/merge_contacts_logs.py --call-log 'Call Log/call_log.csv' --contacts-xlsx contacts.xlsx
```

The script writes `call_log_named.csv` alongside the original log and adds
`caller_name` and `recipient_name` columns derived from the contacts.

## attachment_log.py

Generate a log of every attachment referenced in the message CSVs.

```bash
python scripts/attachment_log.py --messages messages --out "Attachment Log"
```

This creates `attachment_log.xlsx` and `attachment_log.html` in the output
folder and saves thumbnails for image attachments under `thumbnails/`.
