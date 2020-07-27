import time
from dataclasses import dataclass

import pandas as pd
import requests
import vk
from tqdm import tqdm

def retry(retries=3):
    def decorator(f):
        def inner(*args, **kwargs):
            for i in range(1,retries+1):
                try:
                    return f(*args, **kwargs)
                except Exception as e:
                    print(e, 'sleep ', 5 * i, 'sec')
                    print("Retries Left", retries-i)
                    time.sleep(5 * i)
            raise Exception("Retried {} times".format(retries))
        return inner
    return decorator


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

    @retry(30)
    def __call__(self, **method_args):
        self._method_args = method_args
        res=self._api._session.make_request(self)
        if type(res)==dict:
            return DotDict(res)
        else:
            return res

vk.api.Request = Request_new


def download_photo(row_ind, url,group_id, album_id,pbar=None):
    content = requests.get(url, verify=False).content
    with open(f'./dir_to_send/{group_id}_{album_id}_file_{row_ind:05}.jpg', "wb") as file:
        file.write(content)

class CannotUploadPhotoException(Exception):
    pass




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
        df = pd.read_excel(file, index_col=0)
        big_df = big_df.append(df, ignore_index=True)
    big_df.to_excel('./_processed_FULL.xlsx', index=False)


if __name__ == '__main__':
    merge_excel()
