#!/usr/bin/env python3
"""Simple Tkinter GUI wrapper around collect_media.py."""

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, ttk

from collect_media import collect_media, write_excel, ROOT, COMPILED, LOGFILE
import collect_media as cm


def main():
    window = tk.Tk()
    window.title("Collect Media")

    path_var = tk.StringVar(value=str(ROOT))
    status_var = tk.StringVar()

    def browse():
        path = filedialog.askdirectory(initialdir=path_var.get() or ".")
        if path:
            path_var.set(path)

    def run():
        root_path = Path(path_var.get()).expanduser()
        if not root_path.exists():
            status_var.set(f"Path '{root_path}' does not exist.")
            return

        cm.ROOT = root_path
        cm.COMPILED = root_path / "Compiled Media"
        cm.LOGFILE = root_path / "compiled_media_log.xlsx"

        progress.start()
        window.update_idletasks()
        try:
            records, exif_keys = collect_media()
            write_excel(records, exif_keys)
            status_var.set(
                f"Copied {len(records)} files to '{cm.COMPILED}' and logged to '{cm.LOGFILE}'."
            )
        except Exception as e:  # pragma: no cover - user feedback
            status_var.set(f"Error: {e}")
        finally:
            progress.stop()

    tk.Label(window, text="Root folder:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    tk.Entry(window, textvariable=path_var, width=50).grid(row=0, column=1, padx=5)
    tk.Button(window, text="Browse", command=browse).grid(row=0, column=2, padx=5)

    tk.Button(window, text="Run", command=run).grid(row=1, column=1, pady=10)

    progress = ttk.Progressbar(window, mode="indeterminate")
    progress.grid(row=2, column=0, columnspan=3, sticky="ew", padx=5)

    tk.Label(window, textvariable=status_var, wraplength=400, justify="left").grid(
        row=3, column=0, columnspan=3, padx=5, pady=5
    )

    window.mainloop()


if __name__ == "__main__":  # pragma: no cover - GUI entry point
    main()
