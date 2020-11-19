import sys
import pickle
import regex as re
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression

START_TOKEN = '$START$'
features_list = []
model = LogisticRegression()
dict_vectorizer = DictVectorizer(sparse=False)


def check_text(text, result_text):
    true_count = 0
    false_count = 0
    true_words = []
    false_words = []
    sentences = str(text).split('\n')
    result_sentences = str(result_text).split('\n')
    for sentence_index in range(0, min(len(sentences), len(result_sentences))):
        result_sentence = result_sentences[sentence_index].strip()
        sentence = sentences[sentence_index].strip()
        result_tokens = result_sentence.split(' ')
        tokens = sentence.split(' ')
        for index in range(0, min(len(tokens), len(result_tokens))):
            (result_word, result_tag) = result_tokens[index].rsplit('/', 1)
            (word, tag) = tokens[index].rsplit('/', 1)
            if result_tag == tag:
                true_count += 1
                true_words.append('/'.join([word, tag, result_tag]))
            else:
                # print('word: ' + tokens[index] + ', ' + 'tag: ' + tag + '. result_word: ' + result_word + ', result_tag: ' + result_tag)
                false_words.append('/'.join([word, tag, result_tag]))
                false_count += 1

    return true_count / (false_count + true_count)


def get_features(features_map_file):
    global dict_vectorizer
    global features_list
    with open(features_map_file, 'r') as input_file:
        features_lines = input_file.readline()
        features_tokens = features_lines.split(' ')
        for index in range(len(features_tokens)):
            # (feature, value) = features_tokens[index].split('=', 1)
            # features_dict[(feature, value)] = index
            features_dict = {features_tokens[index]: 1}
            features_list.append(features_dict)
    dict_vectorizer.fit(features_list)
    return features_dict


def get_model(model_name):
    return pickle.load(open(model_name, 'rb'))


def predict_file(input_file_name):
    output_sentences = []
    with open(input_file_name) as input_file:
        sentences = input_file.readlines()
        for sentence in sentences:
            output_sentence = []
            sentence = ' '.join([
                START_TOKEN,
                START_TOKEN,
                sentence.strip()
            ])
            sentence = sentence.strip()
            tokens = sentence.split(' ')
            prev_prev_tag = START_TOKEN
            prev_tag = START_TOKEN
            for index in range(2, len(tokens)):
                word_features_dict = get_word_features(tokens[index], prev_tag, prev_prev_tag, index-2)
                word_features = dict_vectorizer.transform([word_features_dict])[0]
                tag = model.predict(word_features)
                output_sentence.append('/'.join([tokens[index], tag]))
                prev_prev_tag = prev_tag
                prev_tag = tag
            output_sentences.append(' '.join(output_sentence))
    output = '\n'.join(output_sentences)
    return output


def get_word_features(word, prev_tag, prev_prev_tag, index):
    word_features = {}

    # prev tag
    word_features['='.join(['pt', str(prev_tag)])] = 1

    # prev prev tag
    word_features['='.join(['ppt', str(prev_prev_tag)])] = 1

    # position
    word_features['='.join(['pos', str(index)])] = 1

    # word form
    word_features['='.join(['form', str(word)])] = 1

    # suffix and prefix
    if word.isalpha():

        # suffix
        word_suffix = get_suffix(word)
        if word_suffix is not None:
            word_features['='.join(['suff', str(word_suffix)])] = 1

        # prefix
        word_prefix = get_prefix(word)
        if word_prefix is not None:
            word_features['='.join(['pref', str(word_prefix)])] = 1

    # type
    word_types = get_type(word)
    for word_type in word_types:
        if word_type is not None:
            word_features['='.join(['type', str(word_type)])] = 1

    # hyphen
    if '-' in word:
        word_features['='.join(['hyphen', 'true'])] = 1

    # underscore
    if '_' in word:
        word_features['='.join(['underscore', 'true'])] = 1

    return word_features


def get_prefix(word):
    if str(word).startswith('post'):
        return '^post*'
    if str(word).startswith('pre'):
        return '^pre*'
    if str(word).startswith('pro'):
        return '^pro*'
    if str(word).startswith('sub'):
        return '^sub*'
    if str(word).startswith('syn'):
        return '^syn*'
    if str(word).startswith('sym'):
        return '^sym*'
    if str(word).startswith('tele'):
        return '^tele*'
    if str(word).startswith('trans'):
        return '^trans*'
    if str(word).startswith('tri'):
        return '^tri*'
    if str(word).startswith('un'):
        return '^un*'
    if str(word).startswith('dis'):
        return '^dis*'
    if str(word).startswith('uni'):
        return '^uni*'
    if str(word).startswith('omni'):
        return '^omni*'
    if str(word).startswith('up'):
        return '^up*'
    return None


def get_suffix(word):
    if str(word).endswith('tion'):
        return '^*tion'
    if str(word).endswith('sion'):
        return '^*sion'
    if str(word).endswith('sious'):
        return '^*ious'
    if str(word).endswith('age'):
        return '^*age'
    if str(word).endswith('al'):
        return '^*al'
    if str(word).endswith('wise'):
        return '^*wise'
    if str(word).endswith('ity'):
        return '^*ity'
    if str(word).endswith('ty'):
        return '^*ty'
    if str(word).endswith('ment'):
        return '^*ment'
    if str(word).endswith('ness'):
        return '^*ness'
    if str(word).endswith('ship'):
        return '^*ship'
    if str(word).endswith('ing'):
        return '^*ing'
    if str(word).endswith('tial'):
        return '^*tial'
    return None


def get_type(word):
    types = []
    if re.match('^[A-Z][a-z]*', word):
        types.append('name')
    if re.match('^[0-9]*.[0-9]*$', word):
        types.append('number')
    if re.match('^(?:(?:31(\/|-|\.)(?:0?[13578]|1[02]))\1|(?:(?:29|30)(\/|-|\.)(?:0?[13-9]|1[0-2])\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(\/|-|\.)0?2\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(\/|-|\.)(?:(?:0?[1-9])|(?:1[0-2]))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})$', word):
        types.append('date')
    if word.isupper():
        types.append('upper')
    if word[1:].upper() != word[1:]:
        types.append('containUpper')
    if word.islower():
        types.append('lower')
    if word[1:].lower() != word[1:]:
        types.append('containLower')
    if word.isalpha():
        types.append('alpa')
    return types


if len(sys.argv) >= 4:
    input_file_name = sys.argv[1]
    model_name = sys.argv[2]
    feature_map_file = sys.argv[3]
    out_file_name = sys.argv[4]

    features = get_features(feature_map_file)
    model = get_model(model_name)
    output_file_content = predict_file(input_file_name)
    with open('data/ass1-tagger-dev', 'r') as f:
        result = check_text(output_file_content, f.read())
        print(str(result))
