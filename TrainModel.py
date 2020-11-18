import sys
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_extraction import DictVectorizer
from sklearn.model_selection import train_test_split

FEATURES_INDEX = {
    'form': 0,
    'suff': 1,
    'pref': 2,
    'type': 3,
    'pt': 4
}


def get_data(features_file_path):
    # features = [[] for index in FEATURES_INDEX]
    features = []
    labels = []
    with open(features_file_path) as features_file:
        features_lines = features_file.readlines()
        for features_line in features_lines:
            features_line = features_line.strip()
            (label, label_features_rest) = features_line.split(' ', 1)
            label_features_tokens = label_features_rest.split(' ')
            #label_features = ['' for index in FEATURES_INDEX]
            label_features = {}
            for token in label_features_tokens:
                feature_tag, feature_value = token.split('=', 1)
                label_features[feature_tag] = feature_value
                #label_features[FEATURES_INDEX[feature_tag]] = (feature_value)
            # for index in range(len(label_features)):
            #     features[index].append(label_features[index])
            features.append(label_features)
            labels.append(label)
    return np.array(labels), np.array(features)


def train_model(features, labels):
    #ohe = OneHotEncoder()
    v = DictVectorizer(sparse=False)
    #features = np.delete(features, 0, 1)
    #one_hot_features = ohe.fit_transform(features).toarray()
    dict_feature = v.fit_transform(features)
    x_train, x_test, y_train, y_test = train_test_split(dict_feature, labels, test_size=0.2, random_state=30)
    lr = LogisticRegression(max_iter=100, verbose=1,n_jobs = -1)
    lr.fit(x_train, y_train)

    y_predict = lr.predict(x_test)
    f = 0
    t = 0
    for i in range(len(y_predict)):
        if y_predict[i] == y_test[i]:
            t += 1
        else:
            f += 1

    print(t / (f + t))

if len(sys.argv) >= 1:
    features_file_path = sys.argv[1]

    labels, features = get_data(features_file_path)
    train_model(features, labels)
