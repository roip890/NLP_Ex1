import regex as re
import sys

START_TOKEN = '$START$'
END_TOKEN = '$END$'

def push_to_dict(dict, value):
    if value in dict.keys():
        dict[value] = dict[value] + 1
    else:
        dict[value] = 1


def getE(input_file):
    e_dict = {}
    with open(input_file) as content_file:
        content = content_file.read()
        tokens = content.split()
        for token in tokens:
            (word, tag) = token.rsplit('/', 1)
            push_to_dict(e_dict, (word, tag))
            if str(word).endswith('tial'):
                push_to_dict(e_dict, ('^*tial', tag))
            if str(word).endswith('tion'):
                push_to_dict(e_dict, ('^*tion', tag))
            if str(word).endswith('sion'):
                push_to_dict(e_dict, ('^*sion', tag))
            if str(word).endswith('sious'):
                push_to_dict(e_dict, ('^*ious', tag))
            if str(word).endswith('age'):
                push_to_dict(e_dict, ('^*age', tag))
            if str(word).endswith('al'):
                push_to_dict(e_dict, ('^*al', tag))
            if str(word).endswith('wise'):
                push_to_dict(e_dict, ('^*wise', tag))
            if str(word).endswith('ity'):
                push_to_dict(e_dict, ('^*ity', tag))
            if str(word).endswith('ty'):
                push_to_dict(e_dict, ('^*ty', tag))
            if str(word).endswith('ment'):
                push_to_dict(e_dict, ('^*ment', tag))
            if str(word).endswith('ness'):
                push_to_dict(e_dict, ('^*ness', tag))
            if str(word).endswith('ship'):
                push_to_dict(e_dict, ('^*ship', tag))
            if str(word).endswith('ing'):
                push_to_dict(e_dict, ('^*ing', tag))
            if re.match('^[A-Z][a-z]*', word):
                push_to_dict(e_dict, ('^Aa', tag))
            if re.match('^[0-9]*.[0-9]*$', word):
                push_to_dict(e_dict, ('^number', tag))
            if re.match('^(?:(?:31(\/|-|\.)(?:0?[13578]|1[02]))\1|(?:(?:29|30)(\/|-|\.)(?:0?[13-9]|1[0-2])\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(\/|-|\.)0?2\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(\/|-|\.)(?:(?:0?[1-9])|(?:1[0-2]))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})$', word):
                push_to_dict(e_dict, ('^date', tag))
    return e_dict


def getQ(input_file):
    q_dict = {}
    with open(input_file) as content_file:
        sentences = content_file.readlines()
        for sentence in sentences:
            sentence = ' '.join([
                '/'.join([START_TOKEN, START_TOKEN]),
                '/'.join([START_TOKEN, START_TOKEN]),
                sentence.strip(),
                '/'.join([END_TOKEN, END_TOKEN])
            ])
            tokens = sentence.split()
            for index in range(2, len(tokens)):
                (w1, t1) = tokens[index-2].rsplit('/', 1)
                (w2, t2) = tokens[index-1].rsplit('/', 1)
                (w3, t3) = tokens[index].rsplit('/', 1)
                # single
                push_to_dict(q_dict, tuple([t1]))
                # tuple
                push_to_dict(q_dict, (t1, t2))
                # triple
                push_to_dict(q_dict, (t1, t2, t3))

            # last values
            # (w_before_last, t_before_last) = tokens[len(tokens)-1].rsplit('/', 1)
            # (w_last, t_last) = tokens[len(tokens)-2].rsplit('/', 1)
            # push_to_dict(q_dict, tuple([t_before_last]))
            # push_to_dict(q_dict, tuple([t_last]))
            # push_to_dict(q_dict, (t_before_last, t_last))

    return q_dict


if len(sys.argv) >= 4:
    input_file_path = sys.argv[1]
    q_mle_path = sys.argv[2]
    e_mle_path = sys.argv[3]

    # generate q.mle file
    with open(q_mle_path, 'w+') as q_mle_file:
        q_dict = getQ(input_file_path)
        q_mle_content = ''
        for key in q_dict:
            q_mle_content += ' '.join(key) + '\t' + str(q_dict[key]) + '\n'
        q_mle_file.write(q_mle_content)

    # generate e.mle file
    with open(e_mle_path, 'w+') as e_mle_file:
        e_dict = getE(input_file_path)
        e_mle_content = ''
        for key in e_dict:
            e_mle_content += ' '.join(key) + '\t' + str(e_dict[key]) + '\n'
        e_mle_file.write(e_mle_content)