import sys
from transformers import XLMRobertaTokenizer

model_cache_dir = '/app/data'
tokenizer = XLMRobertaTokenizer.from_pretrained("xlm-roberta-base", cache_dir=model_cache_dir)
special_tokens = ['<s>', '</s>', '<unk>']

for line in sys.stdin:
    tokens = tokenizer.tokenize(line)
    tokens = [token for token in tokens if token not in special_tokens]  # Remove special tokens
    tokenized_text = ' '.join(tokens).lower()
    print(tokenized_text)
