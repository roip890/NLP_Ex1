import sys
import pickle

input_file_name =sys.argv[1]
model_name = sys.argv[2]
feature_map_file = sys.argv[3]
out_file_name = sys.argv[4]
loaded_model = pickle.load(open(model_name, 'rb'))
with open(input_file_name) as input_file:
    sentences = input_file.readlines()
    for sentence in sentences:
        sentence = sentence.strip()
        tokens = sentence.split(' ')
        for token in tokens:
