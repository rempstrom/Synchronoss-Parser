# Synchronoss Parser

Utility scripts for working with Synchronoss data exports.

## merge_contacts_logs.py

Merge a call log CSV with a contacts Excel file to annotate phone numbers with
names.

```bash
python scripts/merge_contacts_logs.py --call-log call_log.csv --contacts-xlsx contacts.xlsx
```

The script writes `call_log_named.csv` alongside the original log and adds
`caller_name` and `recipient_name` columns derived from the contacts.
