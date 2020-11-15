import sys
import operator
import regex as re

# w1 = 0.33
# w2 = 0.33
# w3 = 0.34
ONE_WORD_TOKEN = '$ONE_WORD$'


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

    tags = list(q_dict[ONE_WORD_TOKEN].keys())

    tags_tuple = []
    for t1 in tags:
        for t2 in tags:
            tags_tuple.append((t1, t2))

    return q_dict, e_dict, tags, tags_tuple


def test_input_file(input_file_path, q_dict, e_dict, tags, tags_tuple):
    output_text = ''
    with open(input_file_path) as input_file, open('data/ass1-tagger-dev') as result_file:
        result_sentences = result_file.readlines()
        sentences = input_file.readlines()
        f = 0
        t = 0
        for sentence_index in range(0, len(sentences)):
            if t + f != 0:
                print(str(sentence_index) + ": " + str(t / (t + f)))
            sentence = '$START$ $START$ ' + sentences[sentence_index].strip()
            result_sentence = '$START$/$START$ $START$/$START$ ' + result_sentences[sentence_index].strip()
            tokens = sentence.split(' ')
            result_tokens = result_sentence.split(' ')
            v_list = [
                {key: max(q_dict[key].items(), key=operator.itemgetter(1)) for key in q_dict if isinstance(key, tuple)},
                {key: max(q_dict[key].items(), key=operator.itemgetter(1)) for key in q_dict if isinstance(key, tuple)}
            ]
            for index in range(2, len(tokens)):
                tag = tag_word(tokens[index], e_dict, q_dict, v_list[index-1], v_list, tags, tags_tuple)
                output_text += tokens[index] + '/' + str(tag) + ' '
                (result_word, result_tag) = result_tokens[index].rsplit('/', 1)
                if result_tag == tag or tag == '$START$':
                    t += 1
                else:
                    # print('word: ' + tokens[index] + ', ' + 'tag: ' + tag + '. result_word: ' + result_word + ', result_tag: ' + result_tag)
                    f += 1
            output_text += '\n'
        print(t / (t + f))


def tag_word(word, e_dict, q_dict, v_1, v_list, tags, tags_tuple):
    if word in e_dict.keys():
        e_values = e_dict[word]
    else:
        e_values = {} if get_word_key(word) not in e_dict.keys() else e_dict[get_word_key(word)]

    v_i = {}
    for t1, t2 in tags_tuple:
        v_i_t_dict = {t: get_prob_of_word(t1, t2, t, e_values, q_dict, v_1) for t in tags}
        v_i_t = max(v_i_t_dict.items(), key=operator.itemgetter(1))[0]
        v_i[(t1, t2)] = (v_i_t, v_i_t_dict[v_i_t])
    # v_i = {key: get_prob_of_word(tag1, tag2, key, e_values, q_dict, v_1, v_2) for key in tags_tuple}

    v_list.append(v_i)
    res = sorted(v_i.items(), key=lambda x: x[1][1], reverse=True)[0][1][0]

    return res

def get_prob_of_word(tag1, tag2, t, e_values, q_dict, v_1):

    e_value = e_values.get(t, 0)

    q_dict_one_word_key = q_dict.get(ONE_WORD_TOKEN, {}).get(t, 0)
    q_dict_tag1_key = q_dict.get(tag2, {}).get(t, 0)
    q_dict_tag1_tag2_key = q_dict.get((tag1, tag2), {}).get(t, 0)

    v_1_key = v_1.get((tag2, t), 0)
    if isinstance(v_1_key, tuple):
        v_1_key = v_1_key[1]

    q_value = (0.1 * q_dict_one_word_key) + (0.2 * q_dict_tag1_key) + (0.7 * q_dict_tag1_tag2_key)
    return e_value * q_value * v_1_key



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

    q_dict, e_dict, tags, tags_tuple = parse_training_data(q_mle_path, e_mle_path)
    test_input_file(input_file_path, q_dict, e_dict, tags, tags_tuple)
