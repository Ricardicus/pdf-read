import fitz
import argparse
from markdownify import markdownify as md

def convert_pdf_to_txt(path):
    doc = fitz.open(path)
    full_text = ""
    for page_index in range(len(doc)):
        page = doc[page_index]
        text = page.get_text()
        images = page.get_image_info()
        #print(f"Page {page_index+1}, images: {len(images) if images else 0}: {text}")
        """for block in blocks:
            print(block)
            print(images)
            continue
            if block[6]: # If this is an image block
                for image in images:
                    if abs(image["width"] - block[2]) < 1.0 and abs(image["height"] - block[3]) < 1.0:
                        full_text += "<p>IMAGE HERE</p>\n"
            else: # If this is a text block
                full_text += block[4] + "\n"
        """
        if page_index == 12 or True:
            blocks = page.get_text("blocks")
            for i, block in enumerate(blocks):
                if block[6]:
                    print(block[4])
                    full_text += f"On page {page_index+1} of {path} there is an image. After the image, this text follows, it might be in reference to this image\n"
                else:
                    if block[4].count("\n") > 2:
                        print(block[4].split("\n"))
                        string = " - ".join(filter(None,block[4].split("\n"))) + "\n"
                    else:
                        string = block[4]
                    full_text += f"{string}"
                    
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

