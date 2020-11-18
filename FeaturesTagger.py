import sys
import pickle
import regex as re
START_TOKEN = '$START$'
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

    return true_count/(false_count+ true_count)




features_dict ={}
input_file_name =sys.argv[1]
model_name = sys.argv[2]
feature_map_file = sys.argv[3]
out_file_name = sys.argv[4]
with open(feature_map_file,"r") as input_file:
    features = input_file.readline()
    features = features.split(" ")
    for index in range(len(features)):
        (feature, value) = features[index].split("=",1)
        features_dict[(feature,value)] = index
output=""
output_sentences =[]
loaded_model = pickle.load(open(model_name, 'rb'))
with open(input_file_name) as input_file:
    sentences = input_file.readlines()
    for sentence in sentences:
        output_sentence =[]
        sentence = sentence.strip()
        tokens = sentence.split(' ')
        prev_tag = START_TOKEN
        for token in tokens:
            features_list = [0] * len(features)
            pre = get_prefix(token)
            suf = get_suffix(token)
            reg = get_type(token)
            form = token
            features_list[features_dict[("pt", prev_tag)]] = 1
            if ("pref",pre) in features_dict.keys():
                features_list[features_dict[("pref",pre)]] = 1
            if ("suff",suf) in features_dict.keys():
                features_list[features_dict[("suff",suf)]] = 1
            if ("form",form) in features_dict.keys():
                features_list[features_dict[("form",form)]] = 1
            if ("type",reg) in features_dict.keys():
                features_list[features_dict[("type",reg)]] = 1
            prev_tag = loaded_model.predict(features_list)
            output_sentence.append(token+ "/"+prev_tag)
        output_sentences.append(" ".join(output_sentence))
output = "\n".join(output_sentences)
with open("data/ass1-tagger-dev","r") as f:
    check_text(output,f.read())
