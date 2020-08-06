#################
import logging
import time
from functools import partial
from multiprocessing import Pool
from pprint import pprint

import pandas as pd
import requests
import urllib3

logging.basicConfig(level=logging.INFO)
# logging.basicConfig(level=logging.DEBUG)
import vk
from tqdm import tqdm

from config import *

from utils import CannotUploadPhotoException, download_photo

pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 1000)
pd.set_option('display.max_colwidth', 1000)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

api = vk.API(session, v='5.120')
group_id = 192858688
owner_id = -group_id


def remove_all_items(owner_id):
    count=api.market.get(owner_id=owner_id,count=0,offset=0).count
    step=200
    while count>0:
        res=api.market.get(owner_id=owner_id,count=step,offset=0)
        count=res['count']
        items=res['items']
        print(count)
        for item in tqdm(items):
            item_id=item.id
            q=api.market.delete(owner_id=owner_id,item_id=item_id)
            time.sleep(0.2)


def remove_all_albums(owner_id):
    count=api.market.getAlbums(owner_id=owner_id,count=0,offset=0).count
    step=100
    while count>0:
        res=api.market.getAlbums(owner_id=owner_id,count=step,offset=0)
        count=res['count']
        items=res['items']
        print(count)
        for album in tqdm(items):
            album_id=album.id
            q=api.market.deleteAlbum(owner_id=owner_id,album_id=album_id)
            time.sleep(0.2)

def main():

    preprocessed = preprocess()
    # album_id = 12
    for group_name, df in preprocessed.groupby('Группа'):
        print(f'Process group {group_name}')
        # create album

        album = api.market.addAlbum(title=group_name, owner_id=owner_id)
        album_id = album.market_album_id

        download_all_photo(df)

        for ind, row in tqdm(df.iterrows(), total=len(df)):
            description = row['Описание']
            filename=''.join([q if str.isalnum(q) else ' ' for q in row['Наименование'] ])
            filename = f'./dir_to_send/{filename}.jpg'

            if pd.isna(filename[0]):
                print(f'Ошибка! В строке {ind + 2} нет изображения')
                continue

            resp_json = upload_photo(api, group_id, filename)
            if 'error' in resp_json or 'photo' not in resp_json:
                print(f'Ошибка! В строке {ind + 2}')
                pprint(resp_json)
                print(filename)
                continue

            save_resp = api.photos.saveMarketPhoto(
                group_id=group_id,
                photo=resp_json['photo'],
                server=resp_json['server'],
                hash=resp_json['hash'],
                crop_data=resp_json['crop_data'],
                crop_hash=resp_json['crop_hash'],
            )[0]

            add_resp = api.market.add(
                owner_id=owner_id,
                name=row['Наименование'],
                description=description,
                category_id=1,  # TODO get from list
                price=row['Цена'],
                main_photo_id=save_resp['id']
            )

            api.market.addToAlbum(
                owner_id=owner_id,
                item_id=add_resp['market_item_id'],
                album_ids=[album_id],

            )
            time.sleep(1.0)


def upload_photo(api, group_id, filename):
    photo_list = '[]'
    resp_json = {}
    upload_url = api.photos.getMarketUploadServer(group_id=group_id, main_photo=1)['upload_url']


    for k in range(10):
        try:
            for i in range(15):
                resp = requests.post(upload_url, files={
                    'file': open(filename, 'rb')
                }, verify=False)
                resp_json = resp.json()
                if len(resp_json) == 0:
                    print(filename, resp_json, resp.raw, resp, 'sleep', i)
                    time.sleep(i)
                    continue
                else:
                    break
            if len(resp_json) == 0:
                raise CannotUploadPhotoException()
            break
        except Exception as e:
            upload_url = api.photos.getMarketUploadServer(group_id=group_id, main_photo=1)['upload_url']
            print(e, 'sleep ', k * 3, 'sec')
            time.sleep(k * 3)
    return resp_json


def download_all_photo(df):
    photo = df['Фото']
    filename = df['Наименование'].apply(lambda x:''.join([q if str.isalnum(q) else ' ' for q in x ]))

    url_name=list(zip(photo,filename))

    print('start download photo','count = ',len(url_name))
    part_download_photo = partial(download_photo)
    download_pool = Pool(16)
    download_pool.starmap(download_photo, url_name)
    download_pool.close()
    print('photos downloaded')


def preprocess():
    df = pd.read_excel('./File/Выгрузка в ВК.xlsx',header=3).iloc[3:]
    # df = df[df['НГруппа'] == 'ЗИМА_(верхняя_одежда)']
    sizes_set=set()
    df2 = pd.DataFrame()
    for name, group in tqdm(df.groupby('Наименование')):
        sizes_set.update(set([str(x) for x in list(group['Характеристика'])]))
        sizes = ', '.join([str(x) for x in list(group['Характеристика'])])
        description = ''
        if len(sizes) != 0 and sizes != 'nan':
            description += f'Размеры: {sizes}\n'
        if str(group["Состав"].iloc[0]) != 'nan':
            description += f'Состав: {str(group["Состав"].iloc[0])}\n'


        if 'https' in str(group['Фото'].iloc[0]):
            df2 = df2.append({
                'Наименование': str(name),
                'Описание'    : description,
                'Фото'        : str(group['Фото'].iloc[0]),
                'Группа'      : str(group['НГруппа'].iloc[0]),
                'Цена'        : float(group["Розничная"].iloc[0])
            }, ignore_index=True)
        else:
            print(str(group['Фото'].iloc[0]))
    print(df2.head())
    print(sizes_set)
    print(len(sizes_set))
    return df2


if __name__ == '__main__':
    remove_all_items(owner_id)
    remove_all_albums(owner_id)
    main()
