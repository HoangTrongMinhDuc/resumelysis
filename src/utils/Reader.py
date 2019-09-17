from docx import Document
from tika import parser


def readFile(filename: str) -> str:
    if filename.endswith(".pdf"):
        fileContent = getPDFText(filename)
    else:
        fileContent = getDocxText(filename)
    return fileContent


def getDocxText(filename: str) -> str:
    docx = Document(filename)
    fileContent = []
    for para in docx.paragraphs:
        text = para.text
        fileContent.append(text)
    return "\n".join(fileContent)


def getPDFText(filename: str) -> str:
    raw = parser.from_file(filename)
    new_text = raw["content"]
    if "title" in raw["metadata"]:
        title = raw["metadata"]["title"]
        new_text = new_text.replace(title, "")
    return new_text
