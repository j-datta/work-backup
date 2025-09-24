import json
import random

def create_subset(file_path, subset_file_path, num_samples):
    with open(file_path, 'r', encoding='utf-8') as file, \
         open(subset_file_path, 'w', encoding='utf-8') as output_file:
        lines = file.readlines()
        chosen_lines = random.sample(lines, min(num_samples, len(lines)))
        for line in chosen_lines:
            output_file.write(line)

if __name__ == "__main__":
    original_dataset_path = '/home/IAIS/jdatta/kenlm_training/oscar_dataset.jsonl'
    subset_dataset_path = '/home/IAIS/jdatta/kenlm_training/oscar_dataset_subset.jsonl'
    num_samples = 20000 

    create_subset(original_dataset_path, subset_dataset_path, num_samples)