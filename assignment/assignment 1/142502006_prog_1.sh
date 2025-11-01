#!/bin/bash

echo "Enter coefficients a, b, c: "
read a b c

d=$(echo "$b * $b - 4 * $a * $c" | bc)

if [ "$d" -gt 0 ]; then
    sqrt_d=$(echo "scale=5; sqrt($d)" | bc -l)
    root1=$(echo "scale=5; (-1 * $b + $sqrt_d) / (2 * $a)" | bc -l)
    root2=$(echo "scale=5; (-1 * $b - $sqrt_d) / (2 * $a)" | bc -l)
    echo "Root 1 = $root1"
    echo "Root 2 = $root2"

elif [ "$d" -eq 0 ]; then
    root=$(echo "scale=5; (-1 * $b) / (2 * $a)" | bc -l)
    echo "Root = $root"

else
    d_abs=$(echo "scale=5; sqrt(-1 * $d)" | bc -l)
    real=$(echo "scale=5; (-1 * $b) / (2 * $a)" | bc -l)
    imag=$(echo "scale=5; $d_abs / (2 * $a)" | bc -l)
    echo "Root 1 = $real + ${imag}i"
    echo "Root 2 = $real - ${imag}i"
fi

