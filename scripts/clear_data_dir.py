from genericpath import isfile
import os

DATA_DIR = "../data/extracted"
MAX_DEPTH = 5


def clear_dir(directory, depth=0):
    if depth >= MAX_DEPTH:
        return
    for file in os.listdir(directory):
        fp = os.path.join(directory,file)
        if os.path.isfile(fp):
            os.remove(fp)
        else:
            clear_dir(fp, depth+1)

clear_dir(DATA_DIR)