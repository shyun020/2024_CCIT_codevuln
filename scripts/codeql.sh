#!/bin/bash

directory_name="$1"
clone_directory_name="$2"
language="$3"

echo -e "\033[32m[+] Create database\033[0m $@"
sleep 2
cd ~

codeql database create --language="$language" --source-root="/home/codevuln/target-repo/$directory_name/$clone_directory_name" "/home/codevuln/target-repo/$directory_name/codeql/codeql-db-$directory_name"

cwe_directories=$(find /home/codevuln/codeql/codeql-repo/$language/ql/src/Security/ -type d -name "CWE*")

for dir in $cwe_directories; do
    ql_files=$(find "$dir" -type f -name "*.ql")
    for ql_file in $ql_files; do
        echo "Analyzing $ql_file..."
        
        csv_output_file="/home/codevuln/target-repo/$directory_name/codeql/$(basename ${ql_file%.ql}).csv"
        
        codeql database analyze "/home/codevuln/target-repo/$directory_name/codeql/codeql-db-$directory_name" "$ql_file" --format=csv --output="$csv_output_file"
        echo "CSV output saved to $csv_output_file"
    done
done

python3 /home/codevuln/codeql/codeql_integrate_csv.py "$directory_name" "$clone_directory_name"
echo "Python script executed successfully."

echo "Scan completed for $directory_name" > "/home/codevuln/codeql_complete.txt"

exit 0