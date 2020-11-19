import sys
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction import DictVectorizer
from sklearn.model_selection import train_test_split
import pickle

def get_data(features_file_path):
    features = []
    labels = []
    with open(features_file_path) as features_file:
        features_lines = features_file.readlines()
        for features_line in features_lines:
            features_line = features_line.strip()
            (label, label_features_rest) = features_line.split(' ', 1)
            label_features_tokens = label_features_rest.split(' ')
            label_features = {}
            for token in label_features_tokens:
                feature_tag, feature_value = token.split('=', 1)
                label_features[feature_tag] = feature_value
            features.append(label_features)
            labels.append(label)
    return np.array(labels), np.array(features)


def train_model(features, labels):
    dv = DictVectorizer(sparse=False)
    features_list = dv.fit_transform(features)
    x_train, x_test, y_train, y_test = train_test_split(features_list, labels, test_size=0.2, random_state=30)
    lr = LogisticRegression(max_iter=100, verbose=1, n_jobs=-1)
    lr.fit(x_train, y_train)
    pickle.dump(lr, open('linear_regression', 'wb'))
    with open('feature_map_file.txt', 'w+') as f:
        f.write(' '.join(dv.get_feature_names()))

    # get score
    result = lr.score(x_test, y_test)
    print(result)

    # manual
    y_predict = lr.predict(x_test)
    predict_rate = check_prediction(y_predict, y_test)
    print(str(predict_rate))


def check_prediction(y_predict, y_values):
    f = 0
    t = 0
    for i in range(len(y_predict)):
        if y_predict[i] == y_values[i]:
            t += 1
        else:
            f += 1
    return t / (f + t)


if len(sys.argv) >= 1:
    features_file_path = sys.argv[1]
    labels, features = get_data(features_file_path)
    train_model(features, labels)
