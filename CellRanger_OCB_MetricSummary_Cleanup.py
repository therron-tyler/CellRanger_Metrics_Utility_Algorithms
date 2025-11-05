#!/usr/bin/env python3
"""
pivot_metrics_dir.py

Read multiple single-sample, transposed Cell Ranger-OCB metrics files from a directory
(each file has rows including: Category, Library Type, Grouped By, Group Name,
Metric Name, Metric Value), and append them into one tidy table:

    Metric Name    <metric1> ... <metricN>
    <SampleA>      <val1>   ... <valN>
    <SampleB>      <val1>   ... <valN>
    ...

- Input: directory containing *.csv and/or *.tsv (one sample per file)
- Output: TSV file (safer for commas/percents inside values)

Usage:
  python pivot_metrics_dir.py <input_dir> <output.tsv>
"""

import sys, os, csv, glob

ROW_METRIC_NAME  = "Metric Name"
ROW_METRIC_VALUE = "Metric Value"

def sniff_delimiter(first_line: str) -> str:
    # Prefer tab if present; else comma
    return '\t' if '\t' in first_line else ','

def read_table(path):
    with open(path, 'r', newline='') as fh:
        first = fh.readline()
        if not first:
            raise SystemExit(f"ERROR: empty file: {path}")
        delim = sniff_delimiter(first)
        fh.seek(0)
        rdr = csv.reader(fh, delimiter=delim)
        rows = [row for row in rdr]
    return rows

def to_map(rows):
    """
    Convert rows into {row_label: [col1, col2, ...]}.
    Assumes first column is the label text.
    """
    m = {}
    for r in rows:
        if not r:
            continue
        key = (r[0] or "").strip()
        vals = r[1:]
        if key:
            m[key] = vals
    return m

def stem(path):
    return os.path.splitext(os.path.basename(path))[0]

def main(indir, out_tsv):
    # Collect candidate files
    files = sorted(
        glob.glob(os.path.join(indir, "*.tsv")) +
        glob.glob(os.path.join(indir, "*.csv"))
    )
    if not files:
        print(f"ERROR: no *.csv or *.tsv files found in: {indir}", file=sys.stderr)
        sys.exit(1)

    header_metrics = None
    sample_rows = []  # list of [sample] + values

    for fp in files:
        rows = read_table(fp)
        m = to_map(rows)

        # Require Metric Name & Metric Value rows
        if ROW_METRIC_NAME not in m or ROW_METRIC_VALUE not in m:
            print(f"WARN: skipping (missing required rows) -> {fp}", file=sys.stderr)
            continue

        metric_names  = [x.strip() for x in m[ROW_METRIC_NAME]]
        metric_values = m[ROW_METRIC_VALUE]

        if len(metric_names) != len(metric_values):
            print(f"WARN: metric name/value length mismatch in {fp} "
                  f"({len(metric_names)} vs {len(metric_values)}). "
                  f"Proceeding with min length.", file=sys.stderr)
        n = min(len(metric_names), len(metric_values))
        metric_names  = metric_names[:n]
        metric_values = metric_values[:n]

        # Set canonical header from the first usable file
        if header_metrics is None:
            header_metrics = metric_names
        # If the file's order differs, map by metric name
        if metric_names != header_metrics:
            d = {mn: mv for mn, mv in zip(metric_names, metric_values)}
            ordered_vals = [d.get(h, "") for h in header_metrics]
        else:
            ordered_vals = metric_values

        sample_id = stem(fp)
        sample_rows.append([sample_id] + ordered_vals)

    if header_metrics is None:
        print("ERROR: no valid metrics found in input directory.", file=sys.stderr)
        sys.exit(2)

    # Write TSV
    with open(out_tsv, 'w', newline='') as fh:
        w = csv.writer(fh, delimiter='\t', lineterminator='\n')
        w.writerow(["Metric Name"] + header_metrics)
        for row in sample_rows:
            w.writerow(row)

    print(f"Done -> {out_tsv} (samples: {len(sample_rows)})")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python pivot_metrics_dir.py <input_dir> <output.tsv>", file=sys.stderr)
        sys.exit(2)
    main(sys.argv[1], sys.argv[2])
