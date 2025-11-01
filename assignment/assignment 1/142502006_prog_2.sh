#!/bin/bash

traverse_dir() {
    local dir="$1"
    echo "Directory: $dir"
    ls -l "$dir"
    echo

    for subdir in "$dir"/*; do
        if [ -d "$subdir" ]; then
            traverse_dir "$subdir"
        fi
    done
}

traverse_dir "/"

