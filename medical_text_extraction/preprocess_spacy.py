import sys
import spacy
import logging

nlp = spacy.load("de_core_news_sm", disable=["tagger", "ner", "attribute_ruler", "lemmatizer"])

for line in sys.stdin:
    doc = nlp(line)
    for sent in doc.sents:
        print(' '.join(token.text.lower() for token in sent))

   

