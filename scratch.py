from tqdm import tqdm,tqdm_gui
import time

for i in tqdm_gui(range(1000),gui=True,disable=False):
    time.sleep(0.1)