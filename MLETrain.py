path = 'data/ass1-tagger-train'

with open(path) as content_file:
    content = content_file.read()
    tokens = content.split(' ')
    for token in tokens:
        if '/' in token and len(token.split('/')) == 2:
            [word, tag] = token.split('/')
            print(word, ':', tag)
