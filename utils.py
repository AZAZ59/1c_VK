from dataclasses import dataclass

import pandas as pd
from tqdm import tqdm


class DotDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, dct):
        for key, value in dct.items():
            if hasattr(value, 'keys'):
                value = DotDict(value)
            elif type(value) == list:
                value = [DotDict(x) for x in value]
            self[key] = value


class Request_new(object):
    __slots__ = ('_api', '_method_name', '_method_args')

    def __init__(self, api, method_name):
        self._api = api
        self._method_name = method_name

    def __getattr__(self, method_name):
        return Request_new(self._api, self._method_name + '.' + method_name)

    def __call__(self, **method_args):
        self._method_args = method_args
        return DotDict(self._api._session.make_request(self))


@dataclass
class VK_Item():
    photo_url: str
    description: str
    link: str

def clear_file(file):
    if '_cleaned' in file:
        return
    f = open(file, encoding='utf-8', mode='r')
    data = f.readlines()
    f.close()
    f = open(file[:-4] + '_cleaned.txt', encoding='utf-8', mode='w')
    f.writelines(sorted(list(set(data))))
    f.close()

def merge_excel():
    import glob
    big_df = pd.DataFrame()
    for file in tqdm(glob.glob('./res/_processed_*')):
        df = pd.read_excel(file,index_col=0)
        big_df = big_df.append(df,ignore_index=True)
    big_df.to_excel('./_processed_FULL.xlsx',index=False)

if __name__ == '__main__':
    merge_excel()