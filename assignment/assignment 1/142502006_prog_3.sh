#!/bin/bash

file="text.txt"

pr -n -t "$file" | sort -rn | cut -f2-

