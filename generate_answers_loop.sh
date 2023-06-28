

counter=0
while [ $counter -lt 100 ];
do
    python generate_answers.py --document outputs/TIS0004144-output.txt --questions outputs/questions_condensed_again.json --index outputs/indexes.json
    counter=$((counter+1))
    sleep 1
done
