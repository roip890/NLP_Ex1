import regex as re
import sys
START_TOKEN = '$START$'
END_TOKEN = '$END$'
word_count = {}
def push_to_dict(dict, value):
    if value in dict.keys():
        dict[value] = dict[value] + 1
    else:
        dict[value] = 1


def extract_features(input_file_path, output_file_path):
    output_file_content = ''
    with open(input_file_path) as input_file, open(output_file_path, 'w+') as output_file:
        sentences = input_file.readlines()
        for sentence_index in range(len(sentences)):
            sentence = sentences[sentence_index].strip()
            tokens = sentence.split(' ')
            for token in tokens:
                (word, tag) = token.rsplit('/', 1)
                form = word
                if form in word_count.keys():
                    word_count[form] += 1
                else:
                    word_count[form] = 1
        for sentence_index in range(len(sentences)):
            sentence = ' '.join([
                '/'.join([START_TOKEN, START_TOKEN]),
                '/'.join([START_TOKEN, START_TOKEN]),
                sentences[sentence_index].strip()
            ])
            tokens = sentence.split(' ')
            for index in range(2, len(tokens)):
                (word, tag) = tokens[index].rsplit('/', 1)
                (prev_word, prev_tag) = tokens[index-1].rsplit('/', 1)
                (prev_prev_word, prev_prev_tag) = tokens[index-2].rsplit('/', 1)
                features = get_word_features(word, prev_tag, prev_prev_tag, index-2, len(tokens)-index-3)
                output_file_content += tag + ' ' + ' '.join(['='.join(feature) for feature in features]) + '\n'
            if sentence_index % 500 == 0:
                output_file.write(output_file_content)
                output_file_content = ''
            output_file.write(output_file_content)
            output_file_content = ''

def get_word_features(word, prev_tag, prev_prev_tag, index, last_index):
    features = []
    word_suffix = get_suffix(word)
    word_prefix = get_prefix(word)

    # prev tag
    features.append(('pt', prev_tag))

    # prev prev tag
    features.append(('ppt', prev_prev_tag))

    # position
    features.append(('pos', str(index)))

    # word form
    if word_count[word] > 100:
        features.append(('form', word))

    # suffix and prefix
    if word.isalpha():
        # suffix
        if word_suffix is not None:
            features.append(('suff', word_suffix))

        # prefix
        if word_prefix is not None:
            features.append(('pref', word_prefix))

    # type
    word_types = get_type(word)
    for word_type in word_types:
        if word_type is not None:
            features.append(('type', word_type))

    # hyphen
    if '-' in word:
        features.append(('hyphen', 'true'))

    # underscore
    if '_' in word:
        features.append(('underscore', 'true'))

    return features


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


if len(sys.argv) >= 2:
    corpus_input_file_path = sys.argv[1]
    corpus_output_file_path = sys.argv[2]
    # generate file
    extract_features(corpus_input_file_path, corpus_output_file_path)
