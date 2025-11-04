#!/bin/bash

# Read the header from the first directory in the directory_list.csv
first_dir=$(head -n 1 directory_list.csv)
echo "Directory, $(head -n 1 "${first_dir}/outs/metrics_summary.csv")" > cellranger_summary.csv

# makes a filepath to the metrics_summary.csv using the first field in the directory_list.csv
# then prepends 'Directory' followed by comma, which becomes the first column of the output
# the output is produced using the 'echo' command but is redirected to cellranger_summary.csv using '>' operator

# Read directory names from directory_list.csv
cat directory_list.csv | while read -r dir; do
  # Construct the path to the 'outs' folder within each directory
  dir_path="${dir}/outs"

# cat reads directory_list.csv line-by-line, then puts the output into a 'while' loop
# the 'while' loop reads each line then assigns it to variable 'dir' 
# then the path to the output metrics is contructed through referencing the 'dir' variable in the 'dir_path' variable

  # Check if metrics_summary.csv exists in the 'outs' directory
  if [[ -f "${dir_path}/metrics_summary.csv" ]]; then
    # Skip the header and prepend the directory name to each line, then append to cellranger_summary.csv
    tail -n +2 "${dir_path}/metrics_summary.csv" | awk -v dir="$dir" -F',' '{print dir "," $0}' >> cellranger_summary.csv
    echo "Appended ${dir_path}/metrics_summary.csv to cellranger_summary.csv"
  fi
done

# -f checks the presence of a file\
# "${dir_path}/metrics_summary.csv" specifies the file to check
# ; is a command separator for bash scripts
# tail -n +2 skips the first line of metrics_summary.csv
# -v dir="$dir" assigns the 'dir' variable from earlier to an awk variable also named 'dir' 
# -F',' specifies that the input fields are separated by commas 
# '{print dir "," $0}' >> cellranger_summary.csv puts the directory name into the cellranger_summary.csv
# tells the user what samples were successfully appended to the CSV before finishing 

#@Tyler You should look at getopts, you can write input arguments including -h or —help

# notebook for bash commands

# error message

# purpose at top of line


