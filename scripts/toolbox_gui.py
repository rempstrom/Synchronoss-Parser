#!/usr/bin/env python3
"""Unified Tkinter GUI exposing multiple Synchronoss tools.

This script bundles the existing utilities into a single window with
tabbed navigation so non-technical users can run them more easily. Long
running operations are executed in background threads while an indeterminate
``ttk.Progressbar`` is shown to keep the interface responsive.

Tabs provided:

* **Collect Media** – wraps ``collect_media.collect_media`` and
  ``collect_media.write_excel``.
* **Contacts to Excel** – wraps ``contacts_to_excel.convert_contacts``.
* **Render Transcripts** – wraps ``render_transcripts.main`` and includes
  an entry for the target phone number.

The script can be packaged as a standalone executable with PyInstaller:

```
pyinstaller --onefile scripts/toolbox_gui.py
```
"""

from __future__ import annotations

import sys
import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, ttk

# Local modules
from collect_media import collect_media, write_excel
from contacts_to_excel import convert_contacts
import render_transcripts as rt


# ---------------------------------------------------------------------------
# Tab builders
# ---------------------------------------------------------------------------


def build_collect_media_tab(nb: ttk.Notebook) -> None:
    """Add the Collect Media UI to ``nb``."""

    frame = ttk.Frame(nb)
    nb.add(frame, text="Collect Media")

    in_var = tk.StringVar()
    out_var = tk.StringVar()
    status_var = tk.StringVar()
    progress = ttk.Progressbar(frame, mode="indeterminate")

    def browse_in() -> None:
        path = filedialog.askdirectory(initialdir=in_var.get() or ".")
        if path:
            in_var.set(path)

    def browse_out() -> None:
        path = filedialog.askdirectory(initialdir=out_var.get() or ".")
        if path:
            out_var.set(path)

    def run() -> None:
        progress.start()

        def task() -> None:
            root_path = Path(in_var.get()).expanduser()
            compiled_path = Path(out_var.get()).expanduser()

            if not root_path.exists():
                frame.after(
                    0,
                    lambda: [
                        status_var.set(f"Input folder '{root_path}' does not exist."),
                        progress.stop(),
                    ],
                )
                return

            try:
                compiled_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                frame.after(
                    0,
                    lambda: [
                        status_var.set(
                            f"Could not create output folder '{compiled_path}': {e}"
                        ),
                        progress.stop(),
                    ],
                )
                return

            logfile = compiled_path / "compiled_media_log" / "compiled_media_log.xlsx"
            try:
                records, exif_keys = collect_media(root_path, compiled_path)
                write_excel(records, exif_keys, logfile)
                msg = (
                    f"Copied {len(records)} files from '{root_path}' to '{compiled_path}' and "
                    f"logged to '{logfile}'."
                )
            except Exception as e:  # pragma: no cover - user feedback
                msg = f"Error: {e}"

            frame.after(0, lambda: [status_var.set(msg), progress.stop()])

        threading.Thread(target=task, daemon=True).start()

    ttk.Label(frame, text="Input folder:").grid(
        row=0, column=0, sticky="e", padx=5, pady=5
    )
    ttk.Entry(frame, textvariable=in_var, width=50).grid(
        row=0, column=1, padx=5, pady=5
    )
    ttk.Button(frame, text="Browse", command=browse_in).grid(
        row=0, column=2, padx=5, pady=5
    )

    ttk.Label(frame, text="Output folder:").grid(
        row=1, column=0, sticky="e", padx=5, pady=5
    )
    ttk.Entry(frame, textvariable=out_var, width=50).grid(
        row=1, column=1, padx=5, pady=5
    )
    ttk.Button(frame, text="Browse", command=browse_out).grid(
        row=1, column=2, padx=5, pady=5
    )

    ttk.Button(frame, text="Run", command=run).grid(row=2, column=1, pady=10)

    progress.grid(row=3, column=0, columnspan=3, sticky="ew", padx=5)

    ttk.Label(frame, textvariable=status_var, wraplength=400, justify="left").grid(
        row=4, column=0, columnspan=3, padx=5, pady=5
    )


def build_contacts_tab(nb: ttk.Notebook) -> None:
    """Add the Contacts to Excel UI to ``nb``."""

    frame = ttk.Frame(nb)
    nb.add(frame, text="Contacts to Excel")

    in_var = tk.StringVar()
    out_var = tk.StringVar()
    status_var = tk.StringVar()
    progress = ttk.Progressbar(frame, mode="indeterminate")

    def browse_in() -> None:
        path = filedialog.askopenfilename(
            title="Select contacts.txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if path:
            in_var.set(path)

    def browse_out() -> None:
        path = filedialog.asksaveasfilename(
            title="Save Excel file",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
        )
        if path:
            out_var.set(path)

    def convert() -> None:
        progress.start()
        status_var.set("Converting...")

        def task() -> None:
            try:
                rows = convert_contacts(in_var.get(), out_var.get())
                msg = f"Wrote {rows} rows to '{out_var.get()}'"
            except Exception as e:  # pragma: no cover - user feedback
                msg = f"Error: {e}"

            frame.after(0, lambda: [status_var.set(msg), progress.stop()])

        threading.Thread(target=task, daemon=True).start()

    ttk.Label(frame, text="Input file:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    ttk.Entry(frame, textvariable=in_var, width=50).grid(row=0, column=1, padx=5, pady=5)
    ttk.Button(frame, text="Browse", command=browse_in).grid(row=0, column=2, padx=5, pady=5)

    ttk.Label(frame, text="Output file:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    ttk.Entry(frame, textvariable=out_var, width=50).grid(row=1, column=1, padx=5, pady=5)
    ttk.Button(frame, text="Save As", command=browse_out).grid(row=1, column=2, padx=5, pady=5)

    ttk.Button(frame, text="Convert", command=convert).grid(row=2, column=1, pady=10)

    progress.grid(row=3, column=0, columnspan=3, sticky="ew", padx=5)

    ttk.Label(frame, textvariable=status_var, wraplength=400, justify="left").grid(
        row=4, column=0, columnspan=3, padx=5, pady=5
    )


def build_render_tab(nb: ttk.Notebook) -> None:
    """Add the Render Transcripts UI to ``nb``.

    Allows the user to specify the target phone number whose messages should
    be labeled in the transcript output.
    """

    frame = ttk.Frame(nb)
    nb.add(frame, text="Render Transcripts")

    in_var = tk.StringVar()
    out_var = tk.StringVar()
    contacts_var = tk.StringVar()
    target_var = tk.StringVar()
    status_var = tk.StringVar()
    progress = ttk.Progressbar(frame, mode="indeterminate")

    def browse_in() -> None:
        path = filedialog.askdirectory(initialdir=in_var.get() or ".")
        if path:
            in_var.set(path)

    def browse_out() -> None:
        path = filedialog.askdirectory(initialdir=out_var.get() or ".")
        if path:
            out_var.set(path)

    def browse_contacts() -> None:
        path = filedialog.askopenfilename(
            title="Select contacts Excel file",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
        )
        if path:
            contacts_var.set(path)

    def render() -> None:
        target = target_var.get().strip()
        if not (target and target.isdigit() and len(target) == 11):
            status_var.set("Target phone number must be an 11-digit number.")
            return

        contacts_path = Path(contacts_var.get()).expanduser()
        if not (contacts_var.get() and contacts_path.is_file()):
            status_var.set(f"Contacts file '{contacts_path}' does not exist.")
            return

        progress.start()
        status_var.set("Rendering...")

        def task() -> None:
            old_argv = sys.argv[:]
            try:
                sys.argv = [
                    "render_transcripts.py",
                    "--in",
                    in_var.get(),
                    "--out",
                    out_var.get(),
                    "--target-number",
                    target,
                    "--contacts-xlsx",
                    contacts_path.as_posix(),
                ]
                rt.main()
                msg = f"Rendered transcripts to '{out_var.get()}'"
            except Exception as e:  # pragma: no cover - user feedback
                msg = f"Error: {e}"
            finally:
                sys.argv = old_argv

            frame.after(0, lambda: [status_var.set(msg), progress.stop()])

        threading.Thread(target=task, daemon=True).start()

    ttk.Label(frame, text="Input folder:").grid(
        row=0, column=0, sticky="e", padx=5, pady=5
    )
    ttk.Entry(frame, textvariable=in_var, width=50).grid(
        row=0, column=1, padx=5, pady=5
    )
    ttk.Button(frame, text="Browse", command=browse_in).grid(
        row=0, column=2, padx=5, pady=5
    )

    ttk.Label(frame, text="Output folder:").grid(
        row=1, column=0, sticky="e", padx=5, pady=5
    )
    ttk.Entry(frame, textvariable=out_var, width=50).grid(
        row=1, column=1, padx=5, pady=5
    )
    ttk.Button(frame, text="Browse", command=browse_out).grid(
        row=1, column=2, padx=5, pady=5
    )

    ttk.Label(frame, text="Contacts file:").grid(
        row=2, column=0, sticky="e", padx=5, pady=5
    )
    ttk.Entry(frame, textvariable=contacts_var, width=50).grid(
        row=2, column=1, padx=5, pady=5
    )
    ttk.Button(frame, text="Browse", command=browse_contacts).grid(
        row=2, column=2, padx=5, pady=5
    )

    ttk.Label(frame, text="Target phone number (11 digits):").grid(
        row=3, column=0, sticky="e", padx=5, pady=5
    )
    ttk.Entry(frame, textvariable=target_var, width=20).grid(
        row=3, column=1, padx=5, pady=5, sticky="w"
    )

    ttk.Button(frame, text="Render", command=render).grid(row=4, column=1, pady=10)

    progress.grid(row=5, column=0, columnspan=3, sticky="ew", padx=5)

    ttk.Label(frame, textvariable=status_var, wraplength=400, justify="left").grid(
        row=6, column=0, columnspan=3, padx=5, pady=5
    )


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------


def main() -> None:  # pragma: no cover - GUI entry point
    root = tk.Tk()
    root.title("Synchronoss Toolbox")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    build_collect_media_tab(notebook)
    build_contacts_tab(notebook)
    build_render_tab(notebook)

    root.mainloop()


if __name__ == "__main__":  # pragma: no cover - GUI entry point
    main()

