#!/bin/bash

for i in * .* ; do
    echo -n $i": " ;
    (find "$i" -type f | wc -l);
done
