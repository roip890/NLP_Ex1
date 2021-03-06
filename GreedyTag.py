import sys
import operator
import regex as re

ONE_WORD_TOKEN = '$ONE_WORD$'
START_TOKEN = '$START$'
END_TOKEN = '$END$'
q_dict = {}
e_dict = {}

def ensure_value_in_dict(dict, value):
    if value not in dict.keys():
        dict[value] = {}


def parse_training_data(q_mle_path, e_mle_path):
    q_dict = {
        ONE_WORD_TOKEN: {}
    }
    e_dict = {}
    with open(q_mle_path) as q_mle_file, open(e_mle_path) as e_mle_file:

        # q dict
        q_mle_lines = q_mle_file.readlines()
        for q_mle_line in q_mle_lines:
            q_mle_line = q_mle_line.split('\n')[0]
            key, value = q_mle_line.split('\t')
            tags = str(key).split()

            # single word
            if len(tags) == 1:
                q_dict[ONE_WORD_TOKEN][tags[0]] = int(value)

            if len(tags) == 2:
                ensure_value_in_dict(q_dict, tags[0])
                q_dict[tags[0]][tags[1]] = int(value)

            if len(tags) == 3:
                ensure_value_in_dict(q_dict, (tags[0], tags[1]))
                q_dict[(tags[0], tags[1])][tags[2]] = int(value)

        # e dict
        e_mle_lines = e_mle_file.readlines()
        for e_mle_line in e_mle_lines:
            e_mle_line = e_mle_line.split('\n')[0]
            key, value = e_mle_line.split('\t')
            word, tag = str(key).rsplit()
            if word not in e_dict.keys():
                e_dict[word] = {}
            e_dict[word][tag] = int(value)

    # normalize dicts
    for word in e_dict:
        word_e_value = e_dict[word]
        e_values_sum = sum(word_e_value.values())
        if not 0.9 < e_values_sum <= 1:
            for key in word_e_value.keys():
                word_e_value[key] = word_e_value[key] / e_values_sum

    for tag in q_dict:
        q_dict_tag_sum = sum(q_dict.get(tag, {1: 1}).values())
        if not 0.9 < q_dict_tag_sum <= 1:
            for key in q_dict[tag].keys():
                q_dict[tag][key] = q_dict[tag][key] / q_dict_tag_sum

    return q_dict, e_dict


def test_input_file(input_file_path):
    output_text = ''
    with open(input_file_path) as input_file, open('data/ass1-tagger-dev') as result_file:
        result_sentences = result_file.readlines()
        sentences = input_file.readlines()
        f = 0
        t = 0
        for sentence_index in range(0, len(sentences)):
            # -----DELETE - START------
            result_sentence = ' '.join([
                '/'.join([START_TOKEN, START_TOKEN]),
                '/'.join([START_TOKEN, START_TOKEN]),
                result_sentences[sentence_index].strip(),
                '/'.join([END_TOKEN, END_TOKEN])
            ])
            result_tokens = result_sentence.split(' ')
            # -----DELETE - END------
            sentence = ' '.join([
                START_TOKEN,
                START_TOKEN,
                sentences[sentence_index].strip(),
                END_TOKEN
            ])
            tokens = sentence.split(' ')
            tag1 = tokens[0]
            tag2 = tokens[1]
            for index in range(2, len(tokens)-1):
                tag3 = tag_word(tag1, tag2, tokens[index])
                tag1 = tag2
                tag2 = tag3
                output_text += tokens[index] + '/' + str(tag3) + ' '
                # -----DELETE - START------
                (result_word, result_tag) = result_tokens[index].rsplit('/', 1)
                if result_tag == tag3:
                    t += 1
                else:
                    # print('word: ' + tokens[index] + ', ' + 'tag: ' + tag3 + '. result_word: ' + result_word + ', result_tag: ' + result_tag)
                    f += 1
                # -----DELETE - END------
            output_text += '\n'
            # -----DELETE - START------
            if t + f != 0:
                print(str(sentence_index) + ": " + str(t / (t + f)))
            # -----DELETE - END------
        print(t / (t + f))


def tag_word(tag1, tag2, word):
    if word in e_dict.keys():
        e_values = e_dict[word]
    else:
        e_values = {} if get_word_key(word) not in e_dict.keys() else e_dict[get_word_key(word)]

    result_dict = {key: get_prob_of_word(tag1, tag2, key, e_values, q_dict)
                   for key in merge_dicts(tag1, tag2, e_values, q_dict)}

    return max(result_dict.items(), key=operator.itemgetter(1))[0]


def get_prob_of_word(tag1, tag2, key, e_values, q_dict):
    # q_dict_one_word = q_dict.get(ONE_WORD_TOKEN, {})
    # q_dict_tag1 = q_dict.get(tag1, {})
    # q_dict_tag1_tag2 = q_dict.get((tag1, tag2), {})
    e_value = e_values.get(key, 0)
    q_dict_one_word_key = q_dict.get(ONE_WORD_TOKEN, {}).get(key, 0)
    q_dict_tag2_key = q_dict.get(tag2, {}).get(key, 0)
    q_dict_tag1_tag2_key = q_dict.get((tag1, tag2), {}).get(key, 0)
    q_value = (0.1 * q_dict_one_word_key) + (0.2 * q_dict_tag2_key) + (0.7 * q_dict_tag1_tag2_key)
    return (0.5 * e_value) + (0.5 * q_value)


def merge_dicts(tag1, tag2, e_values, q_dict):
    q_dict_one_word_keys = q_dict.get(ONE_WORD_TOKEN, {}).keys()
    q_dict_tag1_keys = q_dict.get(tag1, {}).keys()
    q_dict_tag1_tag2_keys = q_dict.get((tag1, tag2), {}).keys()
    merged_keys = list(e_values) + list(q_dict_one_word_keys) + list(q_dict_tag1_keys) + list(q_dict_tag1_tag2_keys)
    return set(merged_keys)


def get_word_key(word):
    if str(word).endswith('ing'):
        return '^*ing'
    if str(word).endswith('tial'):
        return '^*tial'
    if re.match('^[A-Z][a-z]*', word):
        return '^Aa'
    if re.match('^[0-9]*.[0-9]*$', word):
        return '^number'
    if re.match(
            '^(?:(?:31(\/|-|\.)(?:0?[13578]|1[02]))\1|(?:(?:29|30)(\/|-|\.)(?:0?[13-9]|1[0-2])\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(\/|-|\.)0?2\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(\/|-|\.)(?:(?:0?[1-9])|(?:1[0-2]))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})$',
            word):
        return '^date'
    return word


if len(sys.argv) >= 6:
    input_file_path = sys.argv[1]
    q_mle_path = sys.argv[2]
    e_mle_path = sys.argv[3]
    result_file_path = sys.argv[4]
    extra_file_path = sys.argv[5]

    q_dict, e_dict = parse_training_data(q_mle_path, e_mle_path)
    test_input_file(input_file_path)
