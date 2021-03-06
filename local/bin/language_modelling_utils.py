#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

import os
import errno
import codecs
import shlex
import shutil
import subprocess
import tokenization
import requests

def execute_shell(cmd):
    print('$ %s' % cmd)
    o = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in o.stdout:
        print (line.rstrip())
    print ('')


def save_alphabet(alphabet, destination_file_path):
    with codecs.open(destination_file_path, "w", encoding='utf-8') as alphabet_file_out:
        for c in sorted(alphabet):
            alphabet_file_out.write('%s\n' % c) 


def get_alphabet(transcript):
    return set(transcript)


def save_corpus(corpus, corpus_file_path):
    with codecs.open(corpus_file_path, 'w', encoding='utf-8') as corpus_file:
        for l in corpus:
            corpus_file.write(l + '\n')


def fetch_corpus(corpus_url, corpus_file_path):
    tokenizer = tokenization.Tokenization()
    r = requests.get("https://api.techiaith.org/assistant/get_all_sentences")
    data = r.json()

    if data["success"]:
        with codecs.open(corpus_file_path, 'w', encoding='utf-8') as corpus_file:
            for r in data["result"]:
                line = process_transcript(r[0])
                line = tokenizer.tokenize(line) 
                line = ' '.join(line)
                corpus_file.write(line + '\n')


def process_transcript(orig_transcript):
    transcript = orig_transcript.replace("_"," ")
    transcript = transcript.replace("-"," ")
    transcript = transcript.lower()
    return transcript 


def create_binary_language_model(lm_binary_file_path, corpus_file_path):

    # create arpa language model 
    arpa_file_path = corpus_file_path.replace(".txt", ".arpa")
    lm_cmd = '/django-deepspeech-server/native_client/kenlm/build/bin/lmplz --text %s --arpa %s --o 6 --discount_fallback' % (corpus_file_path, arpa_file_path)
    execute_shell(lm_cmd)

    # create binary language model
    #lm_binary_file_path = os.path.join(os.path.abspath(os.path.join(corpus_file_path,'..')), 'lm.binary')
    lm_bin_cmd = '/django-deepspeech-server/native_client/kenlm/build/bin/build_binary -a 22 -q 8 trie  %s %s' % (arpa_file_path, lm_binary_file_path)
    execute_shell(lm_bin_cmd)

    return lm_binary_file_path


def create_trie(trie_file_path, alphabet_file_path, lm_binary_file_path):
    # create trie
    trie_cmd = '/django-deepspeech-server/native_client/generate_trie %s %s %s' % (alphabet_file_path, lm_binary_file_path, trie_file_path)
    execute_shell(trie_cmd)

    return trie_file_path

