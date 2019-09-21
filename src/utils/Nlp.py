import re
import spacy
from spacy.matcher import Matcher
import phonenumbers
from .Reader import (readFile)
import os
import pandas as pd


class InformationExtraction:
    def __init__(self):
        def segment_on_newline(doc):
            for token in doc[:-1]:
                if token.text.endswith("\n"):
                    doc[token.i + 1].is_sent_start = True
            return doc
        print('loading model...')
        self.nlp = spacy.load('en_core_web_lg')
        self.nlp.add_pipe(segment_on_newline, before="parser")
        self.nlpNer = spacy.load(os.path.join('./src/models/ner'))
        print('loaded model')
        self.matcher = Matcher(self.nlp.vocab)
        # print('loading skill set')
        # self.skills = list(pd.read_csv(os.path.join(
        #     'src/data', 'skills.csv')).columns.values)
        # print('loaded skill set')

    def extractInformationFromFile(self, file):
        print('begin extract ', file)
        rawText = readFile(file)
        doc = self.nlp(rawText)
        nerdoc = self.nlpNer(rawText)
        name = self.extractName(doc)
        email = self.extractEmail(doc)
        phone = self.extractPhone(doc)
        # education = self.extractEducation(nerdoc)
        # works = self.extractWork(nerdoc)
        skills = []  # self.extractSkills(doc)
        # "education": education, "work": works, "skills": skills}
        return {"name": name, "email": email, "phone": phone}

    def extractName(self, doc):
        fullname = 'Unknown'
        # for ent in doc.ents:
        #     if ent.label_ == "PERSON":
        #         return ent.text.strip()
        patternName = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]
        self.matcher.add('NAME', None, patternName)
        matches = self.matcher(doc)
        if(len(matches) <= 0):
            return 'Unknown'
        finalMatches = [[matches[0][1], matches[0][2]]]
        merged = [[matches[0][1], matches[0][2]]]
        for i in range(len(matches)):
            if(i != 0):
                lastIndex = len(merged) - 1
                if(merged[lastIndex][1] >= matches[i][1]):
                    merged[lastIndex][1] = matches[i][2]
                else:
                    merged.append([matches[i][1], matches[i][2]])
        for label in merged:
            name = doc[label[0]:label[1]].text.strip()
            if(self.isPersonName(name)):
                return name
        return 'Unknown'

    def extractPhone(self, doc):
        for sent in doc.sents:
            numbers = re.findall(r"\(?\+?\d+\)?\d+(?:[- \)]+\d+)*", sent.text)
            if numbers:
                for number in numbers:
                    if len(number) >= 8 and any([
                        not re.findall(
                            r"^[0-9]{2,4} *-+ *[0-9]{2,4}$", number),  # number is not birthday
                            not re.findall(r"\d{4} *- *\d{4}", number)
                    ]
                    ):
                        return number
        return 'Unknown'

    def extractEmail(self, doc):
        for token in doc:
            if re.findall("([^@|\s]+@[^@]+\.[^@|\s]+)", token.text):
                return token.text
        return 'Unknown'

    def extractSkills(self, doc):
        tokens = [token.text for token in doc if not token.is_stop]
        skillset = []
        for token in tokens:
            if token.lower() in self.skills:
                skillset.append(token)
        for token in doc.noun_chunks:
            token = token.text.lower().strip()
            if token in self.skills:
                skillset.append(token)
        return [i.capitalize() for i in set([i.lower() for i in skillset])]

    def extractEducation(self, doc):
        schools = []
        for ent in doc.ents:
            if ent.label_ == 'College Name' and any(['university' in ent.text.lower(), 'college' in ent.text.strip()]):
                schools.append(ent.text.strip())
        return schools

    def extractWork(self, doc):
        works = set()
        for ent in doc.ents:
            if(ent.label_ == 'Companies worked at'):
                works.add(ent.text)
        return works

    def isPersonName(self, text):
        doc = self.nlp(text)
        return len(doc.ents) == 1 and doc.ents[0].label_ == "PERSON"


# ie = InformationExtraction()
# print(ie.extractInformationFromFile(os.path.join(
#     'src/data/resumes', 'Dushyant Bhatt.pdf')))
# print(ie.extractInformationFromFile(os.path.join(
#     'src/data/resumes', '2017-10-04_Jeyakumaran.pdf')))
# print(ie.extractInformationFromFile(os.path.join(
#     'src/data/resumes', 'Lowell2018.docx')))
# print(ie.extractInformationFromFile(os.path.join(
#     'src/data/resumes', 'Computer Game Development Resume Samples.pdf')))
