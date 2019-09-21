import spacy
import json
import random
import logging
import re
from sklearn.metrics import classification_report
from sklearn.metrics import precision_recall_fscore_support
from spacy.gold import GoldParse
from spacy.scorer import Scorer
from sklearn.metrics import accuracy_score
from spacy.util import minibatch, compounding
import os


def convert_dataturks_to_spacy(dataturks_JSON_FilePath):
    try:
        training_data = []
        lines = []
        with open(dataturks_JSON_FilePath, 'r') as f:
            lines = f.readlines()

        for line in lines:
            data = json.loads(line)
            text = data['content']
            entities = []
            for annotation in data['annotation']:
                point = annotation['points'][0]
                labels = annotation['label']
                if not isinstance(labels, list):
                    labels = [labels]

                for label in labels:
                    entities.append((point['start'], point['end'] + 1, label))

            training_data.append((text, {"entities": entities}))

        return training_data
    except Exception as e:
        logging.exception("Unable to process " +
                          dataturks_JSON_FilePath + "\n" + "error = " + str(e))
        return None


################### Train ###########


def trim_entity_spans(data: list) -> list:
    invalid_span_tokens = re.compile(r'\s')

    cleaned_data = []
    for text, annotations in data:
        entities = annotations['entities']
        valid_entities = []
        for start, end, label in entities:
            valid_start = start
            valid_end = end
            while valid_start < len(text) and invalid_span_tokens.match(
                    text[valid_start]):
                valid_start += 1
            while valid_end > 1 and invalid_span_tokens.match(
                    text[valid_end - 1]):
                valid_end -= 1
            valid_entities.append([valid_start, valid_end, label])
        cleaned_data.append([text, {'entities': valid_entities}])

    return cleaned_data


def train_spacy():

    TRAIN_DATA = convert_dataturks_to_spacy(
        os.path.join('./src/data/dataset.json'))
    TRAIN_DATA = trim_entity_spans(TRAIN_DATA)
    nlp = spacy.blank('en')
    if 'ner' not in nlp.pipe_names:
        ner = nlp.create_pipe('ner')
        nlp.add_pipe(ner, last=True)

    for _, annotations in TRAIN_DATA:  # get each resume, _ is full text, annotations is entities
        for ent in annotations.get('entities'):  # read each entity in resume
            ner.add_label(ent[2])                   # add label of token

    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
    with nlp.disable_pipes(*other_pipes):
        optimizer = nlp.begin_training()
        for itn in range(10):
            print("Statring iteration " + str(itn))
            random.shuffle(TRAIN_DATA)
            losses = {}
            batches = minibatch(TRAIN_DATA, size=compounding(4.0, 32.0, 1.001))
            for batch in batches:
                text, annotations = zip(*batch)
                nlp.update(
                    [text],
                    [annotations],
                    drop=0.2,  # dropout
                    sgd=optimizer,
                    losses=losses)
            print(losses)

    examples = convert_dataturks_to_spacy("./src/data/testdata.json")
    tp = 0
    tr = 0
    tf = 0

    ta = 0
    c = 0
    for text, annot in examples:
        doc_to_test = nlp(text)
        d = {}
        for ent in doc_to_test.ents:
            d[ent.label_] = []
        for ent in doc_to_test.ents:
            d[ent.label_].append(ent.text)

        d = {}
        for ent in doc_to_test.ents:
            d[ent.label_] = [0, 0, 0, 0, 0, 0]
        for ent in doc_to_test.ents:
            doc_gold_text = nlp.make_doc(text)
            gold = GoldParse(doc_gold_text, entities=annot.get("entities"))
            y_true = [ent.label_ if ent.label_ in x else 'Not ' +
                      ent.label_ for x in gold.ner]
            y_pred = [x.ent_type_ if x.ent_type_ ==
                      ent.label_ else 'Not '+ent.label_ for x in doc_to_test]
            if(d[ent.label_][0] == 0):
                (p, r, f, s) = precision_recall_fscore_support(
                    y_true, y_pred, average='weighted')
                a = accuracy_score(y_true, y_pred)
                d[ent.label_][0] = 1
                d[ent.label_][1] += p
                d[ent.label_][2] += r
                d[ent.label_][3] += f
                d[ent.label_][4] += a
                d[ent.label_][5] += 1
        c += 1

    nlp.to_disk(os.path.join('./src/models/ner'))
    for i in d:
        print("\n For Entity "+i+"\n")
        print("Accuracy : "+str((d[i][4]/d[i][5])*100)+"%")
        print("Precision : "+str(d[i][1]/d[i][5]))
        print("Recall : "+str(d[i][2]/d[i][5]))
        print("F-score : "+str(d[i][3]/d[i][5]))


train_spacy()
