# -*- coding: utf-8 -*-
"""
Created on Mon Mar 19 09:58:00 2018

@author: sundar.p.jayaraman
"""
import configparser
import pandas as pd
import pickle
from preprocessing import *
import numpy as np

# =============================================================================
# Testing Time
# =============================================================================

from keras.models import load_model
from keras.preprocessing import sequence

import os
from flask import Flask, render_template, request, redirect, url_for

app= Flask(__name__)

@app.route('/', methods=['GET'])
def index():
	config = configparser.ConfigParser()
	config.read('Config.ini')
	sent_delim = config['Sentence']['Sentence_Delimiter']
	sent_delim_tag = config['Sentence']['Sentence_Delimiter_Tag']
	unknown_tag = config['General']['Unknown_Tag']
	string_tag = config['General']['String_Tag']
	delim_tag = config['General']['Delim_Tag']
	violns_s_lvl = config['Filenames']['StatementLevel_Violations']

	rnn_num_of_iterations = config['RNN_Model']['Num_of_Iterations']
	rnn_cells = config['RNN_Model']['RNN_Cells']
	learning_rate = config['RNN_Model']['learning_rate']

	#Reading Language Tokens
	vocab_data = open('LanguageTokens.txt', 'r').read()
	vocab_data = vocab_data.lower()
	vocab_words = sorted(set(vocab_data.split()))
	vocab_words.sort(key=len, reverse=True)
	vocab_words.append(string_tag)
	vocab_words.append(unknown_tag)
	vocab_words.append(delim_tag)
	vocab_chars = [i for i in vocab_words if len(i) == 1]

	model = load_model('rnn_model.h5')
	le = pickle.load(open("le.pkl","rb"))

	df_nova_violns_orig = pd.read_excel('NovaSuiteReport.xls',sheet_name='Best Practice Violations')

	df_nova_violns = df_nova_violns_orig.copy()

	model_rules_filter = ['Initialize Collections','Use Database Method','Declare Private','Hard Coding Fields','Use isBlank()','No System.debug statements','Avoid hardcoded Ids']

	df_nova_violns = df_nova_violns.loc[df_nova_violns['Rule'].isin(model_rules_filter)]


	df_nova_violns["preprocessed_content"] = df_nova_violns["Code Snippet"].apply(lambda x: data_preprocessing(x, vocab_chars))
	df_nova_violns["preprocessed_tags"] = df_nova_violns["preprocessed_content"].apply(lambda x: data_preprocessing_tags(x, vocab_words, unknown_tag, string_tag))
	df_nova_violns["preprocessed_labels"] = df_nova_violns["preprocessed_tags"].apply(lambda x: data_preprocessing_label(x, vocab_words))

	data_X = df_nova_violns['preprocessed_labels'].tolist()
	data_X_pad = sequence.pad_sequences(data_X, maxlen=500)
	data_X = df_nova_violns['preprocessed_labels'].tolist()


	data_y_test = model.predict(data_X_pad)
	max_test_prob = np.max(data_y_test, axis=1)
	max_test_rule_label = np.argmax(data_y_test, axis=1)

	df_nova_violns['AI_Predicted_Rule_Label'] = max_test_rule_label
	df_nova_violns['AI_Probability'] = max_test_prob
	df_nova_violns['AI_Predicted_Rule_Violation'] = le.inverse_transform(max_test_rule_label)

	result = pd.merge(df_nova_violns_orig, df_nova_violns,how='left')
	result = result.fillna('')
	writer = pd.ExcelWriter('NovaSuiteReport_AI.xls')

	result.to_excel(writer,'Best Practice Violations')
	writer.save()
	a="done"
	return a

if __name__ == '__main__':
    app.run(debug=True)
