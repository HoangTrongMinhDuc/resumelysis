import re
import spacy
from spacy.matcher import Matcher
import phonenumbers
from .Reader import (readFile)
import os
import pandas as pd
from .HeadWord import (getHeadWord)
from collections import defaultdict


DEGREE_DIC = {
    'a': 'Associate',
    'b': 'Bachelor',
    'e': 'Engineer',
    'm': 'Master',
    'p': 'Ph.D'
}


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
        self.nlpNer = spacy.load(os.path.join(os.getcwd(), 'models/ner'))
        self.nlpNerNew = spacy.load(os.path.join(os.getcwd(), 'models/New'))
        print('loaded model')
        self.matcher = Matcher(self.nlp.vocab)

    def extractInformationFromFile(self, file):
        print('begin extract ', file)
        # ocrText = readFile(file, True, True)
        rawText = readFile(file, False, True)
        doco = self.nlp(rawText)
        docr = self.nlp(rawText)
        nerdoc = self.nlpNer(rawText)
        nernewdoc = self.nlpNerNew(rawText)
        name = self.extractName(doco)
        email = self.extractEmail(doco)
        phones = self.extractPhone(rawText)
        educations = self.extractEducation(docr, nernewdoc)
        degrees = self.extractDegree(nernewdoc, rawText)
        majors = self.extractMajor(nernewdoc)
        occupations = self.extractOccupation(nernewdoc)
        works = self.extractWork(nerdoc)
        skills = self.extractSkills(doco, nernewdoc)
        hyperlinks = self.extractHyperLink(docr)
        return {
            "rawText": rawText,
            "label": name[1]+phones[1]+educations[1]+occupations[1]+skills[1],
            "name": name[0],
            "email": email,
            "phones": phones[0],
            "schools": educations[0],
            "degrees": degrees,
            "majors": majors,
            "occupations": occupations[0],
            "work": works,
            "skills": skills[0],
            "links": hyperlinks
        }

    def extractName(self, doc):
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
            span = doc[label[0]:label[1]]
            name = span.text.strip()
            if(self.isPersonName(name)):
                return name.title(), [{'start': span.start_char, 'end': span.end_char, 'label': 'PERSON', 'text': name.title()}]
        return 'Unknown'

    def extractPhone(self, text):
        phone = set()
        # for sent in self.nlp(text).sents:
        #     numbers = re.findall(r"\(?\+?\d+\)?\d+(?:[- \)]+\d+)*", sent.text)
        #     if numbers:
        #         for number in numbers:
        #             if len(number) >= 8 and not re.findall(r"^[0-9]{2,4} *-+ *[0-9]{2,4}$", number) and not re.findall(r"\(?[0-9]{4} ?- ?[0-9]{4}\)?", number):
        #                 phone.add(number.strip())
        for ent in self.nlpNerNew(text).ents:
            if(ent.label_ == 'PHONE' and not bool(re.match(r"\(?[0-9]{4} ?-? ?[0-9]{4}\)?", ent.label_))):
                phone.add(ent.text.strip())
                return list(phone), [{'start': ent.start_char, 'end': ent.end_char, 'label': 'PHONE', 'text': ent.text.strip()}]
        return list(phone), []

    def extractEmail(self, doc):
        for token in doc:
            if re.findall("([^@|\s]+@[^@]+\.[^@|\s]+)", token.text):
                return token.text
            if re.findall("mailto", token.text):
                return token.text
        return 'Unknown'

    def extractSkills(self, doc, docner):
        skillset = set()
        label = list()
        for ent in docner.ents:
            if(ent.label_ == 'SKILL'):
                skillset.add(ent.text.strip().capitalize())
                label.append({'start': ent.start_char,
                              'end': ent.end_char, 'label': 'SKILL', 'text': ent.text.strip()})
        return list(skillset), label
        # tokens = [token.text for token in doc if not token.is_stop]
        # skillset = []
        # for token in tokens:
        #     if token.lower() in self.skills:
        #         skillset.append(token)
        # for token in doc.noun_chunks:
        #     token = token.text.lower().strip()
        #     if token in self.skills:
        #         skillset.append(token)
        # return [i.capitalize() for i in set([i.lower() for i in skillset])]

    def extractEducation(self, doc, sdoc):
        schools = set()
        label = list()
        for ent in doc.ents:
            if ent.label_ == 'ORG' and self.isContainSchoolWord(ent.text.strip()):
                schools.add(ent.text.strip())
                label.append({'start': ent.start_char,
                              'end': ent.end_char, 'label': 'SCHOOL', 'text': ent.text.strip()})
        for ent in sdoc.ents:
            if ent.label_ == 'SCHOOL':
                schools.add(ent.text.strip())
                label.append({'start': ent.start_char,
                              'end': ent.end_char, 'label': 'SCHOOL', 'text': ent.text.strip()})
        return list(schools), label

    def isContainSchoolWord(self, text):
        return bool(re.match(r"\s?(university|school|college)\s?", text))

    def extractDegree(self, doc, text):
        degrees = set()
        raw_degrees = []
        for ent in doc.ents:
            if(ent.label_ == 'DEGREE'):
                raw_degrees.append(ent.text.strip())
        if text.find('Ph.D') != -1:
            raw_degrees.append('Ph')
        if text.lower().find('bs') != -1 or text.lower().find('bachelor') != -1:
            raw_degrees.append('Bs')
        for degree in raw_degrees:
            if(degree.lower()[0] in DEGREE_DIC):
                degrees.add(DEGREE_DIC[degree.lower()[0]])
        return list(degrees)

    def extractOccupation(self, doc):
        occupations = set()
        label = list()
        for ent in doc.ents:
            if(ent.label_ == 'TITLE'):
                occupations.add(ent.text.lower().strip())
                label.append({'start': ent.start_char,
                              'end': ent.end_char, 'label': 'TITLE'})
        return [i.title() for i in occupations], label

    def extractMajor(seft, doc):
        majors = set()
        for ent in doc.ents:
            if(ent.label_ == 'MAJOR'):
                majors.add(ent.text.lower().strip())
        return [i.title() for i in majors]

    def extractWork(self, doc):
        works = set()
        for ent in doc.ents:
            if(ent.label_ == 'COMPANY'):
                works.add(ent.text)
        return list(works)

    def isPersonName(self, text):
        doc = self.nlp(text)
        return len(doc.ents) == 1 and doc.ents[0].label_ == "PERSON"

    def extractHyperLink(self, doc):
        hyperlinks = []
        for i, token in enumerate(doc):
            if(token.like_url):
                hyperlinks.append(token.text)
        return hyperlinks

    def extractCategories(self, text):
        data = defaultdict(list)
        page_count = 0
        prev_count = 0
        prev_line = None
        prev_k = None
        for line in text.split("\n"):
            line = re.sub(r"\s+?", " ", line).strip()
            for (k, wl) in getHeadWord().items():
                for w in wl:
                    if self.countWords(line) < 10:
                        match = re.findall(w, line)
                        if match:
                            size = page_count - prev_count
                            if prev_k is not None:
                                data[prev_k].append(
                                    (size, prev_count, prev_line))
                            prev_count = page_count
                            prev_k = k
                            prev_line = line
            page_count += 1
        if prev_k is not None:
            size = page_count - prev_count - 1
            data[prev_k].append((size, prev_count, prev_line))
        for k in data:
            if len(data[k]) >= 2:
                data[k] = [max(data[k], key=lambda x: x[0])]
        return data

    def countWords(self, line):
        count = 0
        is_space = False
        for c in line:
            is_not_char = not c.isspace()
            if is_space and is_not_char:
                count += 1
            is_space = not is_not_char
        return count


# ie = InformationExtraction()
# print(ie.extractInformationFromFile(os.path.join(
#     'src/data/resumes', 'Online-Resume-April-17-Adam-Smallhorn.pdf')))
# print(ie.extractInformationFromFile(os.path.join(
#     'src/data/resumes', '2017-10-04_Jeyakumaran.pdf')))
# print(ie.extractInformationFromFile(os.path.join(
#     'src/data/resumes', 'Computer Game Development Resume Samples.pdf')))

# print(readFile('/home/hoangtrongminhduc/Documents/resumelysis/src/data/resumes/DanGrassi_Resume.pdf', False, True))
