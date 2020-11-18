import regex as re
import sys
START_TOKEN = '$START$'
END_TOKEN = '$END$'
Word_count = {}
def push_to_dict(dict, value):
    if value in dict.keys():
        dict[value] = dict[value] + 1
    else:
        dict[value] = 1


def extract_features(input_file_path, output_file_path):
    output_file_content = ''
    with open(input_file_path) as input_file, open(output_file_path, 'w+') as output_file:
        sentences = input_file.readlines()
        for sentence in sentences:
            sentence = sentence.strip()
            tokens = sentence.split(' ')
            for token in tokens:
                (word, tag) = token.rsplit('/', 1)
                form = word
                word_suffix = get_suffix(word)
                word_prefix = get_prefix(word)
                if word_prefix is not None:
                    form = form[len(word_prefix):]
                if word_suffix is not None and len(form) > len(word_suffix):
                    form = form[:len(form) - len(word_suffix)]
                if form in Word_count.keys():
                    Word_count[form] += 1
                else:
                    Word_count[form] = 1
        for sentence in sentences:
            sentence =  sentence = ' '.join([
                '/'.join([START_TOKEN, START_TOKEN]),
                '/'.join([START_TOKEN, START_TOKEN]),
                sentence.strip(),
                '/'.join([END_TOKEN, END_TOKEN])
            ])
            tokens = sentence.split(' ')
            prev_tag = START_TOKEN
            for index in range(2, len(tokens)):
                (word, tag) = tokens[index].rsplit('/', 1)
                features = get_word_features(word, prev_tag)
                output_file_content += tag + ' ' + ' '.join(['='.join(feature) for feature in features]) + '\n'
                prev_tag = tag
        output_file.write(output_file_content)

def get_word_features(word, prev_tag):
    features = []
    word_suffix = get_suffix(word)
    word_prefix = get_prefix(word)
    word_type = get_type(word)
    # prev tag
    features.append(('pt', prev_tag))
    # suffix
    if word_suffix is not None:
        features.append(('suff', word_suffix))
    # prefix
    if word_prefix is not None:
        features.append(('pref', word_prefix))
    # type
    if word_type is not None:
        features.append(('type', word_type))
    form = word
    if word_prefix is not None:
        form = form[len(word_prefix):]
    if word_suffix is not None and len(form) > len(word_suffix):
        form = form[:len(form) - len(word_suffix)]
    if Word_count[form] > 100:
    # form
        features.append(('form', form))

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
    if re.match('^[A-Z][a-z]*', word):
        return 'name'
    if re.match('^[0-9]*.[0-9]*$', word):
        return 'number'
    if re.match('^(?:(?:31(\/|-|\.)(?:0?[13578]|1[02]))\1|(?:(?:29|30)(\/|-|\.)(?:0?[13-9]|1[0-2])\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(\/|-|\.)0?2\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(\/|-|\.)(?:(?:0?[1-9])|(?:1[0-2]))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})$', word):
        return 'date'
    return None

if len(sys.argv) >= 2:
    corpus_input_file_path = sys.argv[1]
    corpus_output_file_path = sys.argv[2]
    # generate file
    extract_features(corpus_input_file_path, corpus_output_file_path)
