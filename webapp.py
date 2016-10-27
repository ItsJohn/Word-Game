from flask import Flask, render_template, request
import pickle
import random
import time
import os.path
from operator import itemgetter
from collections import Counter

app = Flask(__name__)

with open('pickle/source_words.pickle', 'rb') as ph:
    source_words = pickle.load(ph)

with open('pickle/dictionary.pickle', 'rb') as ph:
    dictionary = pickle.load(ph)

current_user = {
    'name': None,
    'start_time': None,
    'end_time': None,
    'total_time': None
}


@app.route('/')
def start_app():
    current_user['start_time'] = time.time() * 1000
    return render_template('entries.html',
                                    title='Word Game',
                                    sourceWord=random.choice(source_words))


@app.route('/checkscore', methods=['POST'])
def process_the_data():
    current_user['end_time'] = time.time() * 1000
    user_input = request.form.to_dict()
    selected_word = user_input['source_word']
    del user_input['source_word']

    valid_word = validate_input_duplicates(user_input)
    if valid_word:
        valid_word, user_input = validate_input(user_input, selected_word)

    if valid_word is False:
        return render_template('wrong_results.html',
                                        sourceWord=selected_word,
                                        words=user_input)
    current_user['total_time'] = current_user['end_time'] -current_user['start_time']
    return render_template('right_answer.html',
                                    selected_word=selected_word,
                                    words=user_input)


@app.route('/topscorerslist', methods=['POST'])
def join_the_scoreboard():
    user_input = request.form.to_dict()
    if os.path.isfile('pickle/top_scorers_list.pickle'):
        with open('pickle/top_scorers_list.pickle', 'rb') as ph:
            top_scorers_list = pickle.load(ph)
    else:
        top_scorers_list = []
    current_user['name'] = user_input['name']
    current_user['display_time'] = calculate_display_time(current_user['total_time'])
    top_scorers_list.append(current_user)
    with open('pickle/top_scorers_list.pickle', 'wb') as ph:
        pickle.dump(top_scorers_list, ph)
    sorted_list = sorted(top_scorers_list, key=itemgetter('total_time', 'start_time'), reverse=False)

    return render_template('top_ten.html',
                                    words=user_input['words'],
                                    selected_word=user_input['selected_word'],
                                    top_ten_scorers=sorted_list[:10],
                                    position=sorted_list.index(current_user) + 1)



def validate_input(user_input, selected_word):
    valid_word = True
    for user_input_key, user_input_value in user_input.items():
        if validate_input_length(user_input_value) and validate_input_characters(user_input_value.lower(), selected_word) and validate_input_in_dictionary(user_input_value) and user_input_value != selected_word:
            user_input[user_input_key] = {
                'word': user_input_value,
                'color': 'green'
            }
        else:
            user_input[user_input_key] = {
                'word': user_input_value,
                'color': 'red'
            }
            valid_word = False
    return valid_word, user_input

def validate_input_length(word):
    return len(word) > 2

def validate_input_characters(word, selected_word):
    valid_word = True

    for letter in word:
        if letter not in selected_word:
            valid_word = False
    return valid_word

def validate_input_duplicates(all_values):
    return len(set(all_values)) == 7

def validate_input_in_dictionary(word):
    return word in dictionary

def calculate_display_time(milliseconds):
    seconds = int((current_user['total_time'] / 1000) % 60)
    minutes = int(((current_user['total_time'] / (1000*60)) % 60))
    hours   = int(((current_user['total_time'] / (1000*60*60)) % 24))
    return str(hours) + ':' + str(minutes) + ':' + str(seconds)

if __name__ == '__main__':
    app.run(debug=True)
