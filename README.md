# Generate a question and answers database

Provide a PDF document and generate a database with questions and answers with the help of GPT-4.

## Install

This is a python project that comes with a requirements.txt file. You need Python 3.
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Parse PDF

Convert a PDF to text, with images replaced as they appear in the document, with a reference text.

```bash
python parse.py --path path/to/pdf > path/to/output
```

## Generate questions

Depending on how much text there is on every page, you may want to edit the --pages-per-request document.
We try to fit into the context window. 

```
python generate_questions.py --document path/to/text/document --pages-per-request 3
```

this will output to "outputs/questions_condensed.json" and "outputs/questions_condensed_again.json".
The files are GPT-4s attempt to condense a set of randomized questions.

## Generate answers
```bash
python generate_answers.py --document path/to/text/document --questions outputs/questions_condensed.json --index outputs/indexes.json --answers outputs/answers.json
```
