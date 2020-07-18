import glob
import numpy as np


def clear_file(file):
    f = open(file, encoding='utf-8', mode='r')
    data = f.readlines()
    f.close()
    f = open(file[:-4]+'_cleaned.txt', encoding='utf-8', mode='w')
    f.writelines(sorted(list(set(data))))
    f.close()


for file in glob.glob('./art/*.txt'):
    clear_file(file)
for file in glob.glob('./errors/*.txt'):
    clear_file(file)