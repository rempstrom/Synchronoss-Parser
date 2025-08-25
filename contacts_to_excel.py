#!/usr/bin/env python3
# contacts_to_excel.py — no-arg, hardcoded paths version

# ==== EDIT THESE TWO LINES ====
INPUT_FILE  = r"C:\Users\Frosty\Desktop\CASE FOLDER\OPEN\LD07QR25LD00XX - CT #182193209 - Synchronoss -\Analyzed Synchronoss Data\Contacts Python Process\contacts_20250716.txt"
OUTPUT_FILE = r"C:\Users\Frosty\Desktop\CASE FOLDER\OPEN\LD07QR25LD00XX - CT #182193209 - Synchronoss -\Analyzed Synchronoss Data\Contacts Python Process\contacts.xlsx"
# ==============================

import sys, re, json
from pathlib import Path

# Try imports and give friendly guidance if packages aren't installed
try:
    import pandas as pd
except ImportError:
    print("Missing dependency: pandas. Install with:\n  pip install --user pandas openpyxl")
    input("\nPress Enter to close...")
    sys.exit(1)

# ----- helpers to clean/parse “almost JSON” -----
def quick_clean(txt: str) -> str:
    txt = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', txt)  # remove control chars
    txt = re.sub(r',\s*([}\]])', r'\1', txt)                # trailing commas
    return txt.strip()

def coerce_to_json(txt: str) -> str:
    s = txt.strip()
    if s.startswith('{"contacts"') and not s.endswith('}'):
        s = s.rstrip() + "}}"
    if s.startswith('[') and not s.endswith(']'):
        s = s.rstrip().rstrip(',') + ']'
    return s

def parse_contacts(raw_text: str):
    txt = coerce_to_json(quick_clean(raw_text))
    try:
        data = json.loads(txt)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON parse error at char {e.pos}: {e.msg}")
    if isinstance(data, dict):
        contacts = (data.get("contacts") or {}).get("contact") or data.get("contact")
    else:
        contacts = data
    if not isinstance(contacts, list):
        raise ValueError("Couldn’t find a contact list in the file.")
    return contacts

def normalize_lists_to_strings(df):
    def list_to_str(v):
        if isinstance(v, list):
            if v and all(isinstance(x, dict) for x in v):
                def one(d): return ", ".join(f"{k}={d.get(k,'')}" for k in d.keys())
                return "; ".join(one(x) for x in v)
            return "; ".join(map(str, v))
        return v
    for col in df.columns:
        df[col] = df[col].apply(list_to_str)
    return df

def extract_phone_columns(df):
    if 'tel' in df.columns:
        numbers, types, prefs = [], [], []
        for val in df['tel'].fillna(""):
            num_list, type_list, pref_list = [], [], []
            for part in str(val).split(';'):
                for kv in part.split(','):
                    k, _, v = kv.partition('=')
                    k, v = k.strip(), v.strip()
                    if k == 'number' and v: num_list.append(v)
                    elif k == 'type' and v: type_list.append(v)
                    elif k == 'preference' and v: pref_list.append(v)
            numbers.append("; ".join(num_list) or None)
            types.append("; ".join(type_list) or None)
            prefs.append("; ".join(pref_list) or None)
        df['phone_numbers'] = numbers
        df['phone_types'] = types
        df['phone_preferences'] = prefs
    return df

def build_dataframe(contacts):
    import pandas as pd
    df = pd.json_normalize(contacts, sep='.')
    df = normalize_lists_to_strings(df)
    df = extract_phone_columns(df)
    preferred = [
        'firstname','lastname','phone_numbers','phone_types','phone_preferences',
        'source','created','deleted','itemguid','incaseofemergency','favorite'
    ]
    cols = [c for c in preferred if c in df.columns] + [c for c in df.columns if c not in preferred]
    return df[cols]

def main():
    in_path = Path(INPUT_FILE)
    if not in_path.exists():
        print(f"File not found: {in_path}")
        input("\nPress Enter to close...")
        sys.exit(1)

    raw = in_path.read_text(encoding="utf-8", errors="ignore")
    try:
        contacts = parse_contacts(raw)
    except ValueError as e:
        print(f"Error: {e}")
        input("\nPress Enter to close...")
        sys.exit(1)

    try:
        df = build_dataframe(contacts)
        # openpyxl is auto-used by pandas for .xlsx if installed
        df.to_excel(OUTPUT_FILE, index=False)
        print(f"Wrote {len(df)} rows to {OUTPUT_FILE}")
    except Exception as e:
        print(f"Failed to write Excel: {e}")
        input("\nPress Enter to close...")
        sys.exit(1)

    input("\nDone. Press Enter to close...")

if __name__ == "__main__":
    main()
