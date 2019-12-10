import json
import random
import logging
from sklearn.metrics import classification_report
from sklearn.metrics import precision_recall_fscore_support
from spacy.gold import GoldParse
from spacy.scorer import Scorer
from sklearn.metrics import accuracy_score
import spacy

def convertData(jsonfile):
    training_data = []
    lines=[]
    with open(jsonfile, 'r') as f:
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
                entities.append((point['start'], point['end'] + 1 ,label))
        training_data.append((text, {"entities" : entities}))
    return training_data

def train_spacy():
    TRAIN_DATA = convertData("/home/hoangtrongminhduc/Documents/resumelysis/src/data/testdata.json")
    nlp = spacy.load('/home/hoangtrongminhduc/Documents/resumelysis/src/models/New')#spacy.blank('en')  
    # if 'ner' not in nlp.pipe_names:
    #     ner = nlp.create_pipe('ner')
    #     nlp.add_pipe(ner, last=True)
    # for _, annotations in TRAIN_DATA:
    #      for ent in annotations.get('entities'):
    #         ner.add_label(ent[2])
    # other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
    # with nlp.disable_pipes(*other_pipes):
    #     optimizer = nlp.begin_training()
    #     for itn in range(300):
    #         print("Statring iteration " + str(itn))
    #         random.shuffle(TRAIN_DATA)
    #         losses = {}
    #         for text, annotations in TRAIN_DATA:
    #             nlp.update(
    #                 [text], 
    #                 [annotations],
    #                 drop=0.2, 
    #                 sgd=optimizer,
    #                 losses=losses)
    #         print(losses)
    examples = convertData("/home/hoangtrongminhduc/Documents/resumelysis/src/data/testdata.json")
    tp=0
    tr=0
    tf=0

    ta=0
    c=0        
    for text,annot in examples:

       
        testdoc = nlp(text)
        d={}
        for ent in testdoc.ents:
            d[ent.label_]=[]
        for ent in testdoc.ents:
            d[ent.label_].append(ent.text)
        d={}
        for ent in testdoc.ents:
            d[ent.label_]=[0,0,0,0,0,0]
        for ent in testdoc.ents:
            doc_gold_text= nlp.make_doc(text)
            gold = GoldParse(doc_gold_text, entities=annot.get("entities"))
            y_true = [ent.label_ if ent.label_ in x else 'Not '+ent.label_ for x in gold.ner]
            y_pred = [x.ent_type_ if x.ent_type_ ==ent.label_ else 'Not '+ent.label_ for x in testdoc]  
            if(d[ent.label_][0]==0):
                (p,r,f,s)= precision_recall_fscore_support(y_true,y_pred,average='weighted')
                a=accuracy_score(y_true,y_pred)
                d[ent.label_][0]=1
                d[ent.label_][1]+=p
                d[ent.label_][2]+=r
                d[ent.label_][3]+=f
                d[ent.label_][4]+=a
                d[ent.label_][5]+=1
        c+=1
    for i in d:
        print("\n For Entity "+i+"\n")
        print("Accuracy : "+str((d[i][4]/d[i][5])*100)+"%")
        print("Precision : "+str(d[i][1]/d[i][5]))
        print("Recall : "+str(d[i][2]/d[i][5]))
        print("F-score : "+str(d[i][3]/d[i][5]))
train_spacy()
