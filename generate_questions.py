import argparse
import json
import os
import random
import time

import openai
import tiktoken

openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_BASE")
openai.api_version = "2023-03-15-preview"
openai.api_key = os.getenv("AZURE_OPENAI_KEY")

parser = argparse.ArgumentParser()
parser.add_argument("--questions", help="path to raw questions file to be condensed", required=False)
parser.add_argument("--document", help="path to document file", required=True)
parser.add_argument(
    "--pages-per-request",
    help="path to document file",
    type=int,
    required=False,
    default=3,
)

args = parser.parse_args()
pagesPerRequest = args.pages_per_request
questionsFile = args.questions

def prepareDocument():
    with open(args.document, "r") as f:
        content = f.read()
        document_list = content.split("======================\n")
    return document_list


def outputQuestions(questions, file):
    obj = json.dumps({"questions": questions})
    with open(file, "w") as f:
        f.write(obj)


def num_tokens_from_string(string: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model("gpt-4")
    num_tokens = len(encoding.encode(string))
    return num_tokens


def condenseQuestions(questions):
    request_msg = f"I am creating a series of questions based on the content of a document.\n\
The questions are generated without any context of previous generated questions. Perhaps there are\n\
many questions that are repeated. Can you help me condense this list of questions I have so that they don't \
contain too many repeated questions? Answer with a JSON string that has the field 'questions-condensed' and a list \
of questions that don't include repeats. Here are my questions:\n{questions}"

    a = num_tokens_from_string(request_msg)
    if a >= 4019 or len(questions) > 60:
        # Too large request
        # Divide up the load
        random.shuffle(questions)
        m = len(questions) // 2
        q1 = questions[:m]
        q2 = questions[m:]

        c1 = condenseQuestions(q1)
        c2 = condenseQuestions(q2)
        return c1 + c2
    
    response = openai.ChatCompletion.create(
        engine="gpt-4",  # engine = "deployment_name".
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant. You answer in valid JSON format.",
            },
            {"role": "user", "content": request_msg},
        ],
    )

    questions_condensed = []
    try:
        q_condensed = json.loads(response.choices[0].message.content)
        for q in q_condensed["questions-condensed"]:
            questions_condensed.append(q)
    except (json.JSONDecodeError, KeyError) as e:
        print(
            f"An error occurred trying to load {response.choices[0].message.content}: {e}"
        )
    return questions_condensed


if __name__ == "__main__":
    questions = []

    if questionsFile is None:
        document_pages = prepareDocument()
        # Parse two pages at the same time
        for i in range(len(document_pages) - pagesPerRequest + 1):
            pages = []
            for n in range(pagesPerRequest):
                pages.append(document_pages[i + n])

            request_msg = f"I am parsing a PDF document. I convert its content into \
text. Images are replaced with a text string where they appear. Help me create a dataset of questions based on the content from the document I provide you. Answer with a JSON \
string that has the field 'questions' and a list of questions. Here are {pagesPerRequest} pages from the document:\n\n\
{pages}\n\n"

            a = num_tokens_from_string(request_msg)
            if a >= 8193:
                # Too large request
                pages = []
                for n in range(pagesPerRequest - 1):
                    pages.append(document_pages[i + n])

                request_msg = f"I am parsing a PDF document. I convert its content into \
text. Images are replaced with a text string where they appear. Help me create a dataset of questions based on the content from the document I provide you. Answer with a JSON \
string that has the field 'questions' and a list of questions. Here are {pagesPerRequest} pages from the document:\n\n\
{pages}\n\n"

            response = openai.ChatCompletion.create(
                engine="gpt-4",  # engine = "deployment_name".
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant. You answer in valid JSON format.",
                    },
                    {"role": "user", "content": request_msg},
                ],
            )

            try:
                q = json.loads(response.choices[0].message.content)
                for question in q["questions"]:
                    questions.append(question)
            except (json.JSONDecodeError, KeyError) as e:
                print(
                    f"An error occurred trying to load {response.choices[0].message.content}: {e}"
                )
            time.sleep(1)

            outputQuestions(questions, "outputs/questions.json")
            print(
                f"Processed {i+1} of {len(document_pages)}... Generated {len(questions)} raw questions..."
            )
    else:
        # Load the json file questionsFile 
        with open(questionsFile, 'r') as file:
            questions = json.load(file)["questions"]
    questions_condensed = condenseQuestions(questions)
    outputQuestions(questions_condensed, "outputs/questions_condensed.json")

    print(f"Generated {len(questions_condensed)} condensed questions")

    random.shuffle(questions_condensed)
    questions_condensed = condenseQuestions(questions_condensed)
    outputQuestions(questions_condensed, "outputs/questions_condensed_again.json")

    print(f"Generated {len(questions_condensed)} condensed questions again")
        
