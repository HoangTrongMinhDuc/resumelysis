import re
import os
from pdf2image import convert_from_path
import sys
import pytesseract
from PIL import Image
from docx import Document
import textract


def readFile(filename, orc=False, cleanup=False):
    if filename.endswith(".pdf"):
        if orc:
            fileContent = readPdfByOcr(filename)
        else:
            fileContent = getPDFText(filename)
    else:
        fileContent = getDocxText(filename)
    # fileContent = textract.process(filename)
    if cleanup:
        return cleanupText(fileContent)
    return fileContent


def getDocxText(filename):
    docx = Document(filename)
    fileContent = []
    for para in docx.paragraphs:
        text = para.text
        fileContent.append(text)
    return "\n".join(fileContent)


def getPDFText(filename):
    fileContent = textract.process(filename, method='pdfminer')
    return str(fileContent, 'utf-8')


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


def turnImageToBlackWhite(images):
    for img in images:
        image_file = Image.open(img)
        image_file = image_file.convert('1')
        image_file.save(img)


def readImageToText(images):
    text = ''
    for i in images:
        text += (str(((pytesseract.image_to_string(Image.open(i))))))
    return text.replace('-\n', '')


def cleanupImage(files):
    for f in files:
        os.remove(f)


def cleanupText(text):
    text = re.sub(
        '[^\d\w\s\+\-\(\)\.\,\\\/\@\#\%\^\&\*\-\=\{\}\:\;\"\'\<\>\?\~]', ' ', text)
    text = repr(text).replace('\\t', ' ').replace('\\n', '\n').replace('\\x0c', ' ').replace('\\xa0', ' ').replace('\\r', ' ').replace('\\u', ' ')
    text = re.sub('[–—]', '-', text)
    text = re.sub(' +', ' ', text)
    return text[1:len(text)-1].strip()


def readPdfByOcr(pdfFile):
    images = convertPdftoImage(pdfFile)
    turnImageToBlackWhite(images)
    text = readImageToText(images)
    cleanupImage(images)
    return text
