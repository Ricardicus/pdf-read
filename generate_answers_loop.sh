#!/bin/bash

# Check if $1 is defined
if [ -z "$1" ]; then
    echo "usage: $0 document"
    exit 1
fi

counter=0
while [ $counter -lt 100 ];
do
    python generate_answers.py --document $1 --questions outputs/questions_condensed_again.json --index outputs/indexes.json
    counter=$((counter+1))
    sleep 1
done
