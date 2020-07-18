import glob
import numpy as np

from utils import clear_file

for file in glob.glob('./art/*.txt'):
    clear_file(file)
for file in glob.glob('./errors/*.txt'):
    clear_file(file)