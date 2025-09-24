import sys
import nltk

nltk_data_dir = '/app/data'
nltk.data.path.append(nltk_data_dir)

nltk.download('punkt', download_dir=nltk_data_dir)

for line in sys.stdin:
    for sentence in nltk.sent_tokenize(line, language='german'):
        print(' '.join(nltk.word_tokenize(sentence, language='german')).lower())
