from datasets import load_dataset
import os

def download_dataset(directory):
    dataset = load_dataset("oscar", "unshuffled_deduplicated_de", split='train')
    dataset.save_to_disk(directory)

if __name__ == "__main__":
    directory = '/home/IAIS/jdatta/kenlm_training/oscar_dataset' 
    download_dataset(directory)
