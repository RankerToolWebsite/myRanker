import numpy as np
import pandas as pd
import json
from sklearn.linear_model import SGDClassifier
import pyximport
pyximport.install()
from math import log10, floor


def normalize(df):
    return(df - df.mean()) / df.std()


def scale(df):
    return(df - df.min()) / (df.max() - df.min())

# p_test -> pairs labeled 1 from training data
# y_test -> labels
# clf -> classifier trained on pairs
# size = number of points in dataset (not pairs)
# this function computes a version of the kendall tau to measure the quality of the learned ranking.
# it assumes any unlabeled pairs are predicted discordant
def get_tau(p_test,p_y,clf,size):

    p_pred = clf.predict(p_test)
#     get number of concordant training pairs
    conc = np.count_nonzero(p_y==p_pred)
    m = len(p_test)

#     assume half of unlabeled pairs are discordant, compute kendall tau
    tau =((2*conc)-m)/max(size,m)
#     score for the expected value of a random ordering
#     scale tau to between 0 and 100
    return 99*tau

def clean_dataset(dataset, primary_key):
    #   temp make primary key index so it doesn't get converted
    dataset.set_index(primary_key, inplace=True)
    #convert categorical variables
    cleaned_dataset = pd.get_dummies(dataset)
    # normalize the data
    cleaned_dataset = normalize(cleaned_dataset)
    cleaned_dataset.reset_index(inplace=True)
    return cleaned_dataset


def get_training(dataset,pairs):
    X = []
    y = []
    for i in range(len(pairs["high"])):

        X.append(np.array(dataset.iloc[pairs["high"][i]]-dataset.iloc[pairs["low"][i]]))
        y.append(1)
        X.append(np.array(dataset.iloc[pairs["low"][i]]-dataset.iloc[pairs["high"][i]]))
        y.append(-1)
    return X,y

def get_confidence(data, clf):
    all_pairs = []
    for i in range(len(data)):
        for j in range(len(data)):
            if i != j:
                pair=[i,j]
                d = data[i] - data[j]
                all_pairs.append(np.append(d,pair))
    df = pd.DataFrame()
    df['conf'] = abs(clf.decision_function(np.array(all_pairs)[:,:-2]))
    df['first'] = np.array(all_pairs)[:,-2]
    df['second'] = np.array(all_pairs)[:,-1]
    df.sort_values('conf', inplace=True)
    arr = np.array(df)
    conf_scores = np.zeros(len(data))
    for i in range(len(arr)):
        conf_scores[int(arr[i][1])] += arr[i][0]
        conf_scores[int(arr[i][2])] += arr[i][0]
    return conf_scores


def build(dataset, pairs, primary_key = 'Title', rank = 'Rank', score = 'Score', confd = 'Confidence') :

#     make normalized copy of dataset
    dataset_copy = dataset.copy(deep = True)
    dataset_copy = clean_dataset(dataset_copy, primary_key)
    dataset_copy.drop(primary_key, axis=1, inplace=True)

#     get training pairs
    X,y = get_training(dataset_copy,pairs)
    data = np.array(dataset_copy)

#     train linear SVM classifier
    clf = SGDClassifier(penalty='L2',loss='hinge',fit_intercept=True,
                        max_iter=5000,random_state=9)
    clf.fit(X,y)

#     in future maybe train in online fashion
#     for more accuratae feedback- right now outcome depends on radom state,
#     not just previous input
#     clf.partial_fit(X,y,np.unique(y))
    conf_scores = get_confidence(data, clf)
    conf_scores = scale(conf_scores)
    conf_scores = [round(x, 2) for x in conf_scores]

    weights = clf.coef_[0]
    y_pred=[]
    y_pred=np.dot(weights,data.T)

#     scale outputs for display
    y_pred=scale(y_pred)
    weights = scale(abs(weights))
#     overall confidence score for model
    tau = get_tau(X, y, clf, len(data))

#     format output
    weights_list = []


    for i,w in enumerate(weights) :
        #if w != 0.:
        d={}
        d['attribute']=dataset_copy.columns.values[i]
        d['weight']=round(w, 2)
        weights_list.append(d)

    weights_json = json.dumps(weights_list)
#     predicted score for each item
    dataset[score] = y_pred
#     ordinal ranking for each item
    dataset[rank] = dataset[score].rank(ascending=False)
#     confidence in prediction for each item
    dataset[confd] = conf_scores

    return dataset, weights_json, tau
