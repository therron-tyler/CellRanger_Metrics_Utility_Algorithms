#!/usr/bin/env bash
# Usage: ./metrics_extractor_cellranger_vdj.sh [directory_list.csv] [output.csv]
# Defaults: directory_list.csv, cellranger_vdj_summary.csv

set -uo pipefail

DIRLIST="${1:-directory_list.csv}"
OUTCSV="${2:-cellranger_vdj_summary.csv}"

if [[ ! -f "$DIRLIST" ]]; then
  echo "ERROR: directory list '$DIRLIST' not found." >&2
  exit 1
fi

# Helper to CSV-quote a value (escape internal quotes)
csv_quote() {
  local s="$1"
  s="${s//\"/\"\"}"
  printf "\"%s\"" "$s"
}

# Write header from the FIRST metrics_summary.csv we find
header_written=false
> "$OUTCSV"

# Read each top-level directory name (one per line)
# (skips empty lines and a possible 'directory' header)
while IFS= read -r dir || [[ -n "$dir" ]]; do
  [[ -z "$dir" ]] && continue
  [[ "$dir" =~ ^[Dd]irectory(,.*)?$ ]] && continue

  base="${dir%/}"
  # Look for per-sample metrics files under: <dir>/outs/per_sample_outs/*/metrics_summary.csv
  shopt -s nullglob
  metrics_files=( "$base"/outs/per_sample_outs/*/metrics_summary.csv )
  shopt -u nullglob

  # If none found, you can optionally fall back to the legacy single-file path:
  # if [[ ${#metrics_files[@]} -eq 0 && -f "$base/outs/metrics_summary.csv" ]]; then
  #   metrics_files=( "$base/outs/metrics_summary.csv" )
  # fi

  for mf in "${metrics_files[@]}"; do
    [[ -f "$mf" ]] || continue
    sample="$(basename "$(dirname "$mf")")"  # the <sample> folder inside per_sample_outs

    # Write header once: prepend Directory,Sample to upstream header
    if ! $header_written; then
      upstream_header="$(head -n 1 "$mf")"
      printf "%s,%s,%s\n" "Directory" "Sample" "$upstream_header" > "$OUTCSV"
      header_written=true
    fi

    # Append rows: Directory,Sample,<upstream row...>
    # Properly quote Directory and Sample to keep CSV valid
    tail -n +2 "$mf" | awk -v d="$(csv_quote "$base")" -v s="$(csv_quote "$sample")" -F',' 'BEGIN{OFS=","} {print d, s, $0}' >> "$OUTCSV"

    echo "Appended $mf"
  done

done < "$DIRLIST"

if ! $header_written; then
  echo "No metrics_summary.csv files found under outs/per_sample_outs/*/ for any listed directory." >&2
  exit 2
fi

echo "Done -> $OUTCSV"