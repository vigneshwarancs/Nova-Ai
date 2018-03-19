# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 15:15:24 2018

@author: sundar.p.jayaraman
"""

import regex as re

def data_preprocessing(content, vocab_chars):
    content = content.lower()
    for i in vocab_chars:
        content = content.replace(i, " " + i + " ") 
    
    return content

def data_preprocessing_tags(content, vocab_words, unknown_tag, string_tag):
    vocab_set = set(vocab_words)
    result = ""
    single_quoted_string_value_pattern = re.compile(r"'([^'\\]*(?:\\.[^'\\]*)*)'")
    content = single_quoted_string_value_pattern.sub(string_tag, content)

    for word in content.split():
        if word in vocab_set:
            result += " " + word
        else:
            result += " " + unknown_tag
    
    return result    


def data_preprocessing_label(content, vocab_words):
    labels=[]
    vocab_set = set(vocab_words)
    for word in content.split():
        if word in vocab_set:
            labels.append(vocab_words.index(word))
    
    return labels

def data_preprocessing_method(content):
    pattern = re.compile(r'\. \w+ \(')
    methods = pattern.findall(content)
    methods = [w.replace('.', '') for w in methods]
    methods = [w.replace('(', '') for w in methods]
    methods = [w.replace(' ', '') for w in methods]
    
    return methods
