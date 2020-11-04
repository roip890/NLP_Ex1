import sys

w1 = 0.33
w2 = 0.33
w3 = 0.34
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

    return q_dict, e_dict


def test_input_file(input_file_path, q_dict, e_dict):
    with open(input_file_path) as input_file:
        sentences = input_file.readlines()
        for sentence in sentences:
            tokens = sentence.split(' ')

            # first word
            first_word_e_value = {} if e_dict[tokens[0]] is None else e_dict[tokens[0]]
            first_word_q_value = {} if q_dict[ONE_WORD_TOKEN][tokens[0]] is None else q_dict[ONE_WORD_TOKEN][tokens[0]]

            # second word
            second_word_e_value = 0 if e_dict[tokens[1]] is None else e_dict[tokens[1]]
            second_q_value = 0 if q_dict[ONE_WORD_TOKEN][tokens[0]] is None else q_dict[ONE_WORD_TOKEN][tokens[0]]




if len(sys.argv) >= 6:
    input_file_path = sys.argv[1]
    q_mle_path = sys.argv[2]
    e_mle_path = sys.argv[3]
    result_file_path = sys.argv[4]
    extra_file_path = sys.argv[5]

    q_dict, e_dict = parse_training_data(q_mle_path, e_mle_path)

