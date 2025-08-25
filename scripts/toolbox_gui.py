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
import collect_media as cm
from contacts_to_excel import convert_contacts
import render_transcripts as rt


# ---------------------------------------------------------------------------
# Tab builders
# ---------------------------------------------------------------------------


def build_collect_media_tab(nb: ttk.Notebook) -> None:
    """Add the Collect Media UI to ``nb``."""

    frame = ttk.Frame(nb)
    nb.add(frame, text="Collect Media")

    path_var = tk.StringVar(value=str(cm.ROOT))
    status_var = tk.StringVar()
    progress = ttk.Progressbar(frame, mode="indeterminate")

    def browse() -> None:
        path = filedialog.askdirectory(initialdir=path_var.get() or ".")
        if path:
            path_var.set(path)

    def run() -> None:
        progress.start()

        def task() -> None:
            root_path = Path(path_var.get()).expanduser()
            if not root_path.exists():
                frame.after(
                    0,
                    lambda: [
                        status_var.set(f"Path '{root_path}' does not exist."),
                        progress.stop(),
                    ],
                )
                return

            cm.ROOT = root_path
            cm.COMPILED = root_path / "Compiled Media"
            cm.LOGFILE = root_path / "compiled_media_log.xlsx"
            try:
                records, exif_keys = collect_media()
                write_excel(records, exif_keys)
                msg = (
                    f"Copied {len(records)} files to '{cm.COMPILED}' and "
                    f"logged to '{cm.LOGFILE}'."
                )
            except Exception as e:  # pragma: no cover - user feedback
                msg = f"Error: {e}"

            frame.after(0, lambda: [status_var.set(msg), progress.stop()])

        threading.Thread(target=task, daemon=True).start()

    ttk.Label(frame, text="Root folder:").grid(
        row=0, column=0, sticky="e", padx=5, pady=5
    )
    ttk.Entry(frame, textvariable=path_var, width=50).grid(
        row=0, column=1, padx=5, pady=5
    )
    ttk.Button(frame, text="Browse", command=browse).grid(
        row=0, column=2, padx=5, pady=5
    )

    ttk.Button(frame, text="Run", command=run).grid(row=1, column=1, pady=10)

    progress.grid(row=2, column=0, columnspan=3, sticky="ew", padx=5)

    ttk.Label(frame, textvariable=status_var, wraplength=400, justify="left").grid(
        row=3, column=0, columnspan=3, padx=5, pady=5
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

    def render() -> None:
        target = target_var.get().strip()
        if not (target and target.isdigit() and len(target) == 11):
            status_var.set("Target phone number must be an 11-digit number.")
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

    ttk.Label(frame, text="Target phone number (11 digits):").grid(
        row=2, column=0, sticky="e", padx=5, pady=5
    )
    ttk.Entry(frame, textvariable=target_var, width=20).grid(
        row=2, column=1, padx=5, pady=5, sticky="w"
    )

    ttk.Button(frame, text="Render", command=render).grid(row=3, column=1, pady=10)

    progress.grid(row=4, column=0, columnspan=3, sticky="ew", padx=5)

    ttk.Label(frame, textvariable=status_var, wraplength=400, justify="left").grid(
        row=5, column=0, columnspan=3, padx=5, pady=5
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

