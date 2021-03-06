
# Name: John Kelly
# ID: C00176932

import pickle

def create_dictionary():
    dictionary = []

    with open('words.txt', 'r') as fh:
        for line in fh:
            if len(line) > 3:
                dictionary.append(line[:-1].lower())

    with open('pickle/dictionary.pickle', 'wb') as ph:
        pickle.dump(dictionary, ph)

def create_selected_word_dictionary():
    source_words = []

    with open('words.txt', 'r') as fh:
        for line in fh:
            if len(line) >= 8:
                source_words.append(line[:-1].lower())

    with open('pickle/source_words.pickle', 'wb') as ph:
        pickle.dump(source_words, ph)
