import argparse
import json
import os
import random
import sys
import time
import re

import openai
import tiktoken

openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_BASE")
openai.api_version = "2023-03-15-preview"
openai.api_key = os.getenv("AZURE_OPENAI_KEY")

parser = argparse.ArgumentParser()
parser.add_argument(
    "--questions", help="path to raw questions file to be condensed", required=True
)
parser.add_argument(
    "--pages-per-request",
    help="path to document file",
    type=int,
    required=False,
    default=1,
)
parser.add_argument("--document", help="path to document file", required=True)
args = parser.parse_args()
document = args.document
questionsFile = args.questions
pagesPerRequest = args.pages_per_request

def starts_with_number_dot(s):
    return bool(re.match(r'^\d+\. ', s))

def loadDocument():
    with open(document, "r") as f:
        content = f.read()
        document_list = content.split("======================\n")
    return document_list


def loadQuestions():
    # Load the json file questionsFile
    questions = []
    with open(questionsFile, "r") as file:
        questions = json.load(file)["questions"]
    return questions


def createIndexForQuestion(document, question):
    index = []
    for i in range(len(document) - pagesPerRequest + 1):
        pages = ""
        for n in range(pagesPerRequest):
            pages += document[i + n] + "\n"
        index_info = "" if len(index) > 0 else "...Empty..."
        print(pages)
        for ii, idx in enumerate(index):
            a = f"{ii+1}. {idx}\n"
            if starts_with_number_dot(idx):
                a = f"{idx}\n"
            index_info += a

        request_msg = (
            f"Answer the question: '{question}'\n"
            + f"Context information is below, it is provided in a numbered list "
            + f"(1 to {len(index)}, "
            + f"where each item in the list corresponds to a summary.\n"
            + f"--------------------------\n"
            + f"{index_info}\n"
            + f"--------------------------\n"
            + f"Given the context information, here is a new piece of information:\n"
            + f"--------------------------\n"
            + f"{pages}"
            + f"--------------------------\n"
            + f"If the new information is relevant to help answer the question '{question}' and it is already not in the numbered list, write a summary of the information \
to the list. Only add information that is not already in the list if an item in the list should be updated answer with the updated information."
            + 'Answer in the JSON form: {"add": ["summary 1", "summary 2"], "update":{"2":"updated info for the index 2"}}\n"add" can be empty if there is no new information.'
        )
        print(request_msg)
        a = num_tokens_from_string(request_msg)
        print(f"Request msg size: {a}")
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
        resp = None
        try:
            resp = json.loads(response.choices[0].message.content)
        except (json.JSONDecodeError, KeyError) as e:
            print(
                f"An error occurred trying to load {response.choices[0].message.content}: {e}"
            )
        if resp:
            if "add" in resp:
                for a in resp["add"]:
                    index.append(a)
            if "update" in resp:
                for a in resp["update"]:
                    s = int(a)
                    index[s - 1] = resp["update"][a]
        print(resp)
        print(index)
        time.sleep(1)
    return index


def outputQuestions(questions, file):
    obj = json.dumps({"questions": questions})
    with open(file, "w") as f:
        f.write(obj)


def num_tokens_from_string(string: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model("gpt-4")
    num_tokens = len(encoding.encode(string))
    return num_tokens


def outputIndexes(indexes, file):
    idxs = json.dumps(indexes)
    with open(file, "w") as f:
        f.write(idxs)


if __name__ == "__main__":
    doc = loadDocument()
    questions = loadQuestions()

    indexes = {}

    for question in questions:
        index = createIndexForQuestion(doc, question)
        indexes[question] = index
        print(index)
        outputIndexes(indexes, "outputs/indexes.json")
