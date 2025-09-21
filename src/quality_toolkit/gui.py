from __future__ import annotations

from pathlib import Path
from tkinter import END, StringVar, Tk, filedialog, messagebox
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from typing import Iterable

import pandas as pd

from .analysis import DatasetQuality, evaluate_data_quality
from .data_loader import load_dataset
from .report import build_markdown_report


class QualityToolkitApp(Tk):
    """Tkinter application for exploring data-quality reports."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Quality Toolkit")
        self.minsize(960, 640)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        style = ttk.Style(self)
        # Use a modern theme when available
        if "clam" in style.theme_names():
            style.theme_use("clam")

        self._path_var = StringVar(value="No dataset loaded")
        self._status_var = StringVar(value="Load a CSV, Excel, or Parquet file to get started.")
        self._dataset: pd.DataFrame | None = None

        self._build_header()
        self._build_main_panes()
        self._update_status("Ready")

    # ------------------------------------------------------------------
    # UI construction helpers
    def _build_header(self) -> None:
        header = ttk.Frame(self, padding=(16, 16, 16, 8))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(1, weight=1)

        open_button = ttk.Button(header, text="Open Dataset?", command=self._handle_open)
        open_button.grid(row=0, column=0, padx=(0, 12))

        path_label = ttk.Label(header, textvariable=self._path_var, anchor="w")
        path_label.grid(row=0, column=1, sticky="ew")

        status_label = ttk.Label(header, textvariable=self._status_var, anchor="w", foreground="#555")
        status_label.grid(row=1, column=0, columnspan=2, pady=(8, 0), sticky="w")

    def _build_main_panes(self) -> None:
        container = ttk.Frame(self, padding=(16, 0, 16, 16))
        container.grid(row=1, column=0, sticky="nsew")
        container.columnconfigure(1, weight=1)
        container.rowconfigure(0, weight=1)

        # Column chooser panel
        chooser = ttk.Labelframe(container, text="Columns", padding=12)
        chooser.grid(row=0, column=0, sticky="nsw", padx=(0, 16))
        chooser.columnconfigure(0, weight=1)
        chooser.rowconfigure(1, weight=1)

        help_label = ttk.Label(
            chooser,
            text="Select the columns to include in the report. Leave empty to use all columns.",
            wraplength=220,
            justify="left",
        )
        help_label.grid(row=0, column=0, sticky="w")

        self._column_list = ttk.Treeview(chooser, show="tree", selectmode="extended")
        self._column_list.grid(row=1, column=0, sticky="nsew", pady=(8, 8))
        self._column_list.bind(
            "<<TreeviewSelect>>", lambda _: self._update_status("Columns selected.")
        )

        button_row = ttk.Frame(chooser)
        button_row.grid(row=2, column=0, sticky="ew")

        run_button = ttk.Button(button_row, text="Generate Report", command=self._handle_generate)
        run_button.pack(side="left")

        clear_button = ttk.Button(button_row, text="Clear Selection", command=self._clear_selection)
        clear_button.pack(side="left", padx=(8, 0))

        # Report panel
        report_panel = ttk.Notebook(container)
        report_panel.grid(row=0, column=1, sticky="nsew")

        overview_frame = ttk.Frame(report_panel, padding=12)
        overview_frame.columnconfigure(0, weight=1)
        overview_frame.rowconfigure(2, weight=1)
        report_panel.add(overview_frame, text="Overview")

        columns_frame = ttk.Frame(report_panel, padding=12)
        columns_frame.columnconfigure(0, weight=1)
        columns_frame.rowconfigure(0, weight=1)
        report_panel.add(columns_frame, text="Columns")

        markdown_frame = ttk.Frame(report_panel, padding=12)
        markdown_frame.columnconfigure(0, weight=1)
        markdown_frame.rowconfigure(0, weight=1)
        report_panel.add(markdown_frame, text="Markdown Report")

        self._metric_tree = ttk.Treeview(overview_frame, columns=("metric", "value"), show="headings")
        self._metric_tree.heading("metric", text="Metric")
        self._metric_tree.heading("value", text="Value")
        self._metric_tree.column("metric", width=180, anchor="w")
        self._metric_tree.column("value", anchor="w")
        self._metric_tree.grid(row=0, column=0, sticky="nsew")

        warning_label = ttk.Label(overview_frame, text="Warnings:")
        warning_label.grid(row=1, column=0, sticky="w", pady=(12, 0))

        self._warning_list = ttk.Treeview(overview_frame, show="tree")
        self._warning_list.grid(row=2, column=0, sticky="nsew", pady=(4, 0))

        self._column_tree = ttk.Treeview(
            columns_frame,
            columns=("dtype", "missing", "distinct", "samples"),
            show="headings",
        )
        for column_id, heading, width in (
            ("dtype", "Type", 140),
            ("missing", "Missing", 160),
            ("distinct", "Distinct", 120),
            ("samples", "Samples", 360),
        ):
            self._column_tree.heading(column_id, text=heading)
            self._column_tree.column(column_id, width=width, anchor="w", stretch=True)
        self._column_tree.grid(row=0, column=0, sticky="nsew")

        self._report_text = ScrolledText(markdown_frame, wrap="word")
        self._report_text.configure(state="disabled")
        self._report_text.grid(row=0, column=0, sticky="nsew")

    # ------------------------------------------------------------------
    # Event handlers
    def _handle_open(self) -> None:
        path = filedialog.askopenfilename(
            title="Select dataset",
            filetypes=[
                ("Supported files", "*.csv *.txt *.tsv *.parquet *.xls *.xlsx *.xlsm"),
                ("CSV", "*.csv"),
                ("Excel", "*.xls *.xlsx *.xlsm"),
                ("Parquet", "*.parquet"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return

        try:
            dataset = load_dataset(path)
        except ValueError as error:
            messagebox.showerror("Unsupported file", str(error))
            return
        except FileNotFoundError as error:
            messagebox.showerror("File not found", str(error))
            return
        except Exception as error:  # pragma: no cover - unexpected errors
            messagebox.showerror("Error loading file", str(error))
            return

        self._dataset = dataset
        self._path_var.set(str(Path(path)))
        self._populate_columns(dataset.columns)
        self._clear_report()
        self._update_status("Dataset loaded. Select columns and generate a report.")

    def _handle_generate(self) -> None:
        if self._dataset is None:
            messagebox.showinfo("No dataset", "Load a dataset before generating a report.")
            return

        selected_columns = self._get_selected_columns()
        if selected_columns:
            data = self._dataset[selected_columns]
        else:
            data = self._dataset

        try:
            quality = evaluate_data_quality(data)
        except ValueError as error:
            messagebox.showerror("Quality error", str(error))
            return

        self._render_quality(quality)
        self._update_status("Report generated")

    # ------------------------------------------------------------------
    # Rendering helpers
    def _populate_columns(self, column_names: Iterable[str]) -> None:
        self._column_list.delete(*self._column_list.get_children())
        for name in column_names:
            self._column_list.insert("", END, iid=name, text=name)

    def _get_selected_columns(self) -> list[str]:
        selection = self._column_list.selection()
        return list(selection)

    def _clear_selection(self) -> None:
        self._column_list.selection_remove(self._column_list.selection())
        self._update_status("Column selection cleared")

    def _render_quality(self, dataset_quality: DatasetQuality) -> None:
        self._metric_tree.delete(*self._metric_tree.get_children())
        self._metric_tree.insert("", END, values=("Rows", dataset_quality.row_count))
        self._metric_tree.insert("", END, values=("Duplicate rows", dataset_quality.duplicate_rows))

        self._warning_list.delete(*self._warning_list.get_children())
        if dataset_quality.warnings:
            for warning in dataset_quality.warnings:
                self._warning_list.insert("", END, text=warning)
        else:
            self._warning_list.insert("", END, text="No warnings")

        self._column_tree.delete(*self._column_tree.get_children())
        for column_name, column_quality in dataset_quality.columns.items():
            missing_display = f"{column_quality.missing_count} ({column_quality.missing_ratio:.1%})"
            sample_display = ", ".join(column_quality.sample_values[:5]) or "?"
            self._column_tree.insert(
                "",
                END,
                iid=column_name,
                values=(column_quality.dtype, missing_display, column_quality.distinct_count, sample_display),
                text=column_name,
            )

        report = build_markdown_report(dataset_quality)
        self._report_text.configure(state="normal")
        self._report_text.delete("1.0", END)
        self._report_text.insert("1.0", report)
        self._report_text.configure(state="disabled")

    def _clear_report(self) -> None:
        self._metric_tree.delete(*self._metric_tree.get_children())
        self._warning_list.delete(*self._warning_list.get_children())
        self._warning_list.insert("", END, text="No report generated")
        self._column_tree.delete(*self._column_tree.get_children())
        self._report_text.configure(state="normal")
        self._report_text.delete("1.0", END)
        self._report_text.configure(state="disabled")

    def _update_status(self, message: str) -> None:
        self._status_var.set(message)


def launch_gui() -> None:
    app = QualityToolkitApp()
    app.mainloop()


def main() -> None:
    launch_gui()


if __name__ == "__main__":
    main()
