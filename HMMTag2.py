import sys
import operator
import regex as re
import math
import itertools

EPSILON = sys.float_info.min
LOG_EPSILON = math.log(EPSILON, 10)
ONE_WORD_TOKEN = '$ONE_WORD$'
START_TOKEN = '$START$'
END_TOKEN = '$END$'
tags = []
tags_tuple = []
tags_transition_probs = {}
q_dict = {
    ONE_WORD_TOKEN: {}
}
e_dict = {}


def ensure_value_in_dict(dict, value):
    if value not in dict.keys():
        dict[value] = {}


def parse_training_data(q_mle_path, e_mle_path):
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


def normalize_data():
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


def prepare_tags_probs():
    tags.extend(list(q_dict[ONE_WORD_TOKEN].keys()))

    for t1 in tags:
        for t2 in tags:
            tags_tuple.append((t1, t2))
            for t3 in tags:
                q_dict_one_word_key = q_dict.get(ONE_WORD_TOKEN, {}).get(t1, EPSILON)
                q_dict_tag1_key = q_dict.get(t2, {}).get(t1, EPSILON)
                q_dict_tag1_tag2_key = q_dict.get((t3, t2), {}).get(t1, EPSILON)
                q_value = (0.05 * q_dict_one_word_key) + (0.2 * q_dict_tag1_key) + (0.75 * q_dict_tag1_tag2_key)
                tags_transition_probs[(t3, t2, t1)] = q_value

    # for q in q_dict:
    #     if isinstance(q, tuple) and len(q) == 2:
    #         tags_tuple.append(q)


def test_input_file(input_file_path):
    acc_true_count = 0
    acc_false_count = 0
    acc_true_words = []
    acc_false_words = []
    output_text = ''
    with open(input_file_path) as input_file, open('data/ass1-tagger-dev') as result_file:
        result_sentences = result_file.readlines()
        sentences = input_file.readlines()
        for sentence_index in range(0, len(sentences)):
            output_words = []
            result_sentence = result_sentences[sentence_index].strip()
            sentence = ' '.join([
                START_TOKEN,
                sentences[sentence_index].strip()
            ])
            tokens = sentence.split(' ')

            # init start
            pie_start = {(u, v): (START_TOKEN, LOG_EPSILON) for u, v in tags_tuple if u != START_TOKEN and v != START_TOKEN}
            pie = [(START_TOKEN, pie_start)]

            # fill pie matrix
            for k in range(1, len(tokens)):
                pie_k_prev = pie[k-1]
                if tokens[k] in e_dict.keys():
                    e_values = e_dict[tokens[k]]
                else:
                    e_values = {} if get_word_key(tokens[k]) not in e_dict.keys() else e_dict[get_word_key(tokens[k])]

                pie_k = {}
                for u, v in tags_tuple:
                    max_dict = {w: get_prob_of_word(u, v, w, e_values, pie_k_prev[1]) for w in tags}
                    max_arg = max(max_dict.items(), key=lambda x: x[1])[0]
                    max_value = max_dict[max_arg]
                    pie_k[(u, v)] = (max_arg, max_value)
                pie.append((tokens[k], pie_k))

            pie_end = {(u, v): get_prob_of_end(u, v, pie[len(pie) - 1][1]) for u, v in tags_tuple}
            y2, y3 = max(pie_end.items(), key=lambda x: x[1])[0]

            output_words.append('/'.join([pie[len(pie) - 1][0], y3]))
            output_words.append('/'.join([pie[len(pie) - 2][0], y2]))

            # back propagation
            for index in range(len(pie) - 3, 0, -1):
                word = pie[index+2][0]
                y1 = pie[index+2][1][(y2, y3)][0]
                y3 = y2
                y2 = y1
                if word != START_TOKEN and word != END_TOKEN:
                    output_words.append('/'.join([word, y1]))
            output_sentence = ' '.join(reversed(output_words))

            # check
            true_count, false_count, true_words, false_words = check_text(output_sentence, result_sentence)
            acc_true_count += true_count
            acc_false_count += false_count
            acc_true_words.extend(true_words)
            acc_false_words.extend(false_words)
            print(str(sentence_index) + ': ' + str(true_count / (true_count + false_count))
                  + ', acc: ' + str(acc_true_count / (acc_true_count + acc_false_count)))


def get_prob_of_word(u, v, w, e_values, pie_k):
    q_value = tags_transition_probs.get((w, u, v), EPSILON)
    e_value = e_values.get(v, EPSILON)
    pie_k_key = pie_k.get((w, u), ('_', LOG_EPSILON))[1]
    return math.log(e_value, 10) + math.log(q_value, 10) + pie_k_key


def get_prob_of_end(u, v, pie_k):
    q_value = tags_transition_probs.get((u, v, END_TOKEN), EPSILON)
    pie_k_key = pie_k.get((u, v), ('_', LOG_EPSILON))[1]
    return math.log(q_value, 10) + pie_k_key


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

    return true_count, false_count, true_words, false_words

if len(sys.argv) >= 6:
    input_file_path = sys.argv[1]
    q_mle_path = sys.argv[2]
    e_mle_path = sys.argv[3]
    result_file_path = sys.argv[4]
    extra_file_path = sys.argv[5]

    parse_training_data(q_mle_path, e_mle_path)
    normalize_data()
    prepare_tags_probs()
    test_input_file(input_file_path)
