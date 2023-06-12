import fitz
import argparse
from markdownify import markdownify as md

def convert_pdf_to_txt(path):
    doc = fitz.open(path)
    full_text = ""
    for page in doc:
        blocks = page.get_text("blocks")
        images = page.get_image_info()
        for block in blocks:
            if block[6]: # If this is an image block
                for image in images:
                    if abs(image["width"] - block[2]) < 1.0 and abs(image["height"] - block[3]) < 1.0:
                        full_text += "<p>IMAGE HERE</p>\n"
            else: # If this is a text block
                full_text += block[4] + "\n"
    return full_text

def convert_html_to_md(html_content):
    markdown_text = md(html_content)
    return markdown_text

# create parser
parser = argparse.ArgumentParser()
parser.add_argument('--path', type=str, help='Path to the PDF file.')

# parse arguments
args = parser.parse_args()

# validate arguments
if not args.path:
    print("Please provide a path to a PDF file (--path).")
    exit(1)

# path to the pdf file
pdf_path = args.path

# extract text from pdf
pdf_text = convert_pdf_to_txt(pdf_path)

# convert to markdown
markdown_text = convert_html_to_md(pdf_text)
print(markdown_text)

