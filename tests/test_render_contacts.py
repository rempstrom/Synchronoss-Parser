import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))
from scripts.render_transcripts import Message, build_contact_lookup, render_thread_html


def test_contact_lookup_replaces_number_with_name(tmp_path):
    df = pd.DataFrame(
        [{"firstname": "Alice", "lastname": "Smith", "phone_numbers": "(123) 456-7890"}]
    )
    xlsx_path = tmp_path / "contacts.xlsx"
    df.to_excel(xlsx_path, index=False)

    lookup = build_contact_lookup(str(xlsx_path))

    msg = Message(
        date_raw="",
        date_dt=None,
        msg_type="sms",
        direction="in",
        attachments=[],
        body="Hello",
        sender="1234567890",
        recipients="",
        message_id="id1",
        attachment_day=None,
    )

    out_file = tmp_path / "out.html"
    render_thread_html(tmp_path, out_file, [msg], ["1234567890"], "1234567890", lookup)

    html = out_file.read_text()
    assert '<div class="sender">Alice Smith</div>' in html
    assert "Participants: Alice Smith" in html
