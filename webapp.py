from flask import Flask, render_template, request, session
from operator import itemgetter
from collections import Counter
import pickle
import random
import time
import os.path
import parse_words

app = Flask(__name__)


@app.route('/')
def start_app():
    if os.path.isfile('pickle/source_words.pickle'):
        with open('pickle/source_words.pickle', 'rb') as ph:
            source_words = pickle.load(ph)
    else:
        parse_words.create_selected_word_dictionary()
    session.setdefault('selected_word', '')
    session.setdefault('current_user', {})
    session['selected_word'] = random.choice(source_words)
    session['current_user']['start_time'] = time.time() * 1000
    return render_template('entries.html',
                                    title=session['selected_word'] + ' | Word Game',
                                    sourceWord=session['selected_word'])


@app.route('/checkscore', methods=['POST'])
def process_the_data():
    session['current_user']['end_time'] = time.time() * 1000
    session.setdefault('user_input', {})
    session['user_input'] = request.form.to_dict()
    valid_word = validate_input_duplicates(session['user_input'])

    if valid_word:
        valid_word, session['user_input'] = validate_input(session['user_input'], session['selected_word'])

    if valid_word is False:
        return render_template('wrong_results.html',
                                        sourceWord=session['selected_word'],
                                        words=session['user_input'])

    session['current_user']['total_time'] = session['current_user']['end_time'] -session['current_user']['start_time']
    return render_template('right_answer.html',
                                    selected_word=session['selected_word'])


@app.route('/topscorerslist', methods=['POST'])
def join_the_scoreboard():
    user_input = request.form.to_dict()
    if os.path.isfile('pickle/top_scorers_list.pickle'):
        with open('pickle/top_scorers_list.pickle', 'rb') as ph:
            top_scorers_list = pickle.load(ph)
    else:
        top_scorers_list = []
    session['current_user']['name'] = user_input['name']
    session['current_user']['display_time'] = calculate_display_time(session['current_user']['total_time'])
    top_scorers_list.append(session['current_user'])
    with open('pickle/top_scorers_list.pickle', 'wb') as ph:
        pickle.dump(top_scorers_list, ph)
    sorted_list = sorted(top_scorers_list, key=itemgetter('total_time', 'start_time'), reverse=False)

    return render_template('top_ten.html',
                                    words=session['user_input'],
                                    selected_word=session['selected_word'],
                                    top_ten_scorers=sorted_list[:10],
                                    position=sorted_list.index(session['current_user']) + 1)



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
    if os.path.isfile('pickle/dictionary.pickle'):
        with open('pickle/dictionary.pickle', 'rb') as ph:
            dictionary = pickle.load(ph)
    else:
        parse_words.create_dictionary()
    return word in dictionary

def calculate_display_time(milliseconds):
    seconds = int((session['current_user']['total_time'] / 1000) % 60)
    minutes = int(((session['current_user']['total_time'] / (1000*60)) % 60))
    hours   = int(((session['current_user']['total_time'] / (1000*60*60)) % 24))
    return str(hours) + ':' + str(minutes) + ':' + str(seconds)

if __name__ == '__main__':
    app.config['SECRET_KEY'] = 'THISISMYSECRETKEY'
    app.run(debug=True)
