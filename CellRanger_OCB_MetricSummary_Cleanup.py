#!/usr/bin/env python3
"""
pivot_transposed_metrics.py
Convert a transposed Cell Ranger-OCB metrics sheet into:
    Metric Name,<metric1>,<metric2>,...,<metricN>
    <SampleA>,<val1>,<val2>,...,<valN>
    <SampleB>,<val1>,<val2>,...,<valN>
Usage:
  python pivot_transposed_metrics.py input.tsv output.tsv
Notes:
  - Input is the "wide" transposed table where each column is one metric entry.
  - First column contains row labels:
      Sample / Category / Library Type / Grouped By / Group Name / Metric Name / Metric Value
  - Output is TSV by default to avoid quoting commas in values.
"""
import sys, csv, itertools, os

ROW_SAMPLE       = "Sample"
ROW_METRIC_NAME  = "Metric Name"
ROW_METRIC_VALUE = "Metric Value"

def sniff_delimiter(first_line: str) -> str:
    # Simple, reliable: prefer tab if present; else comma.
    return '\t' if '\t' in first_line else ','

def read_table(path):
    with open(path, 'r', newline='') as fh:
        first = fh.readline()
        if not first:
            raise SystemExit("ERROR: empty input file")
        delim = sniff_delimiter(first)
        fh.seek(0)
        rdr = csv.reader(fh, delimiter=delim)
        rows = [row for row in rdr]
    return rows, delim

def to_map(rows):
    """
    Convert rows into a dict: {row_label: [col1, col2, ...]}
    Assumes first column of each row is the label.
    """
    m = {}
    for r in rows:
        if not r: 
            continue
        key = r[0].strip()
        vals = r[1:]
        # keep the last occurrence if duplicates; typical sheets won’t duplicate keys
        m[key] = vals
    return m

def contiguous_segments(labels):
    """
    Given a list of sample labels (one per column), return segments of contiguous identical labels:
    [(name, start_idx, end_idx_exclusive), ...] in the order they appear.
    """
    segs = []
    if not labels:
        return segs
    start = 0
    curr = labels[0]
    for i, s in enumerate(labels[1:], 1):
        if s != curr:
            segs.append((curr, start, i))
            curr = s
            start = i
    segs.append((curr, start, len(labels)))
    return segs

def main(in_path, out_path):
    rows, _ = read_table(in_path)
    m = to_map(rows)

    for required in (ROW_SAMPLE, ROW_METRIC_NAME, ROW_METRIC_VALUE):
        if required not in m:
            raise SystemExit(f"ERROR: required row '{required}' not found in first column.")

    samples_per_col = m[ROW_SAMPLE]
    metric_names    = m[ROW_METRIC_NAME]
    metric_values   = m[ROW_METRIC_VALUE]

    if not (len(samples_per_col) == len(metric_names) == len(metric_values)):
        raise SystemExit("ERROR: lengths of Sample / Metric Name / Metric Value rows do not match.")

    # Identify contiguous sample blocks (the first block provides the canonical metric order)
    segs = contiguous_segments(samples_per_col)
    if not segs:
        raise SystemExit("ERROR: no sample columns found.")

    # Canonical header metrics from the first sample's contiguous block
    first_name, s0, e0 = segs[0]
    header_metrics = metric_names[s0:e0]

    # Build rows per sample (preserving appearance order)
    out_rows = []
    for name, s, e in segs:
        # Block for this sample
        names_block  = metric_names[s:e]
        values_block = metric_values[s:e]

        # If metric names line up exactly with header_metrics, fast path
        if names_block == header_metrics:
            ordered_vals = values_block
        else:
            # Fallback: map by metric name; fill missing with empty string
            d = {mn: mv for mn, mv in zip(names_block, values_block)}
            ordered_vals = [d.get(h, "") for h in header_metrics]

        out_rows.append([name] + ordered_vals)

    # Write TSV (safer for embedded commas/percents)
    with open(out_path, 'w', newline='') as fh:
        w = csv.writer(fh, delimiter='\t', lineterminator='\n')
        w.writerow(["Metric Name"] + header_metrics)
        w.writerows(out_rows)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python pivot_transposed_metrics.py input.tsv output.tsv", file=sys.stderr)
        sys.exit(2)
    main(sys.argv[1], sys.argv[2])
