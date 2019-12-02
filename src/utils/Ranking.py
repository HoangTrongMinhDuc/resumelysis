from scipy.spatial.distance import cosine
from itertools import islice
import numpy as np
from sklearn import linear_model
from .DatabaseUtils import (Database)
from .Decision import (DecisionTree)
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split 
from sklearn import metrics

CRITERION_FIELDS = ['degrees', 'skills', 'schools', 'majors', 'occupations']
def addElementsToList(arr, ls):
        for d in arr:
            if d not in ls:
                ls.append(d)

def ranking(criterions, resumes):
    rating = ratePotentialRate()
    ranked = resumes
    allCriterions = []
    # add all criterions to allCriterions
    t_criterions = []
    for field in CRITERION_FIELDS:
        if field in criterions.keys():
            addElementsToList(criterions[field], allCriterions)
    addElementsToList(allCriterions, t_criterions)
    # add criterion from resumes
    for rm in resumes:
        ls = []
        for field in CRITERION_FIELDS:
            if field in rm.keys():
                addElementsToList(rm[field], ls)
        rm['criterions'] = ls
        addElementsToList(ls, allCriterions)
    # sort criterion list
    allCriterions.sort()
    p_criterion = [1]*len(allCriterions)
    for rm in resumes:
        isAnyMatch = False
        m_criterion = []
        for c in allCriterions:
            if c in t_criterions and c in rm['criterions']:
                m_criterion.append(1)
                isAnyMatch = True
            else:
                m_criterion.append(0)
        if not isAnyMatch:
            rm['point'] = 0.0
        else:
            rm['point'] = round((1 - cosine(m_criterion, p_criterion))*10, 5)
        po_criterion = []
        for c in rating[2]:
            if c in rm['criterions']:
                po_criterion.append(1)
            else:
                po_criterion.append(0)
        f = pd.DataFrame([po_criterion])
        gr = rating[0].predict(f)
        print(rating[1][int(gr[0])].predict(f))
        rm['potential'] = round(rating[1][int(gr[0])].predict(f)[0], 5)
        rm['selected'] = False
        rm['total'] = round(rm['potential'] + rm['point'], 5)
    def rk(v):
        return v['total']
    resumes.sort(reverse=True, key=rk)
    return resumes

def ratePotentialRate():
    db = Database()
    rates = db.getRegularRate().json()
    allCriterions = []
    for r in rates:
        addElementsToList(r['criterions'], allCriterions)
    allCriterions.append('point')
    rows = []
    #create row in matrix
    for r in rates:
        ro = []
        for c in allCriterions:
            if c in r['criterions']:
                ro.append(1)
            else:
                ro.append(0)
        ro.append(r['point'])
        rows.append(ro)
    #sort top
    def rk(v):
        return v[-1]
    rows.sort(reverse=True, key=rk)
    #split to 3 class
    classes = np.array_split(rows, 3)
    index = 0;
    # add label class to row
    n_classes = []
    for c in classes:
        for r in c:
            n_r = r.tolist()
            n_r.append(index)
            n_classes.append(n_r)
        index += 1
    df = pd.DataFrame(n_classes)
    # # #create tree from 3 class
    tree = DecisionTree(max_depth = 30, min_samples_split = 3)
    X = df.iloc[:, :-2]
    y = df.iloc[:, -1]
    tree.fit(X, y)
    print(accuracy_score(y, tree.predict(X)))

    # #create linear regression for each class
    reprList = []
    for c in classes:
        dff = pd.DataFrame(c);
        regr = linear_model.LinearRegression(fit_intercept=False)
        y_test = dff.iloc[:, -1]
        regr.fit(dff.iloc[:, :-1], dff.iloc[:, -1])
        y_pred = regr.predict(dff.iloc[:, :-1])
        print('Mean Absolute Error:', metrics.mean_absolute_error(y_test, y_pred))  
        print('Mean Squared Error:', metrics.mean_squared_error(y_test, y_pred))  
        print('Root Mean Squared Error:', np.sqrt(metrics.mean_squared_error(y_test, y_pred)))
        reprList.append(regr)

    return tree, reprList, allCriterions

