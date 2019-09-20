from docx import Document
from tika import parser
from PIL import Image
import pytesseract
import sys
from pdf2image import convert_from_path
import os
import re


def readFile(filename):
    if filename.endswith(".pdf"):
        fileContent = readPdfByOcr(filename)
    else:
        fileContent = getDocxText(filename)
    fileContent = repr(fileContent).replace('\\n', '.').replace('\\t', '.')
    fileContent = re.sub('\.+', '.', fileContent)
    fileContent = re.sub(' +', ' ', fileContent)
    return fileContent


def getDocxText(filename):
    docx = Document(filename)
    fileContent = []
    for para in docx.paragraphs:
        text = para.text
        fileContent.append(text)
    return "\n".join(fileContent)


def getPDFText(filename):
    raw = parser.from_file(filename)
    fileContent = raw["content"]
    if "title" in raw["metadata"]:
        title = raw["metadata"]["title"]
        if(isinstance(title, str)):
            fileContent = fileContent.replace(title, "")
    return fileContent


def convertPdftoImage(pdfFile):
    pages = convert_from_path(pdfFile, 500)
    images = []
    image_counter = 0
    for page in pages:
        image_counter += 1
        filename = "temp_page_"+str(image_counter)+".jpg"
        page.save(filename, 'JPEG')
        images.append(filename)
    return images


def readImageToText(images):
    text = ''
    for i in images:
        text += (str(((pytesseract.image_to_string(Image.open(i))))))
    return text.replace('-\n', '')


def cleanupImage(files):
    for f in files:
        os.remove(f)


def readPdfByOcr(pdfFile):
    images = convertPdftoImage(pdfFile)
    text = readImageToText(images)
    cleanupImage(images)
    return text
