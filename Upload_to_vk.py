import time
from multiprocessing import Pool

import pandas as pd
import requests
import urllib3
from tqdm import tqdm

from config import *
from utils import CannotUploadPhotoException, download_photo

# logging.basicConfig(level=logging.DEBUG)

pd.set_option('display.max_rows',     1000)
pd.set_option('display.max_columns',  1000)
pd.set_option('display.max_colwidth', 1000)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():

    api = vk.API(session, v='5.92')

    df2 = pd.read_excel('./File/Альбомы для ВК.xlsx')

    for group_name, df in df2.groupby('Группа'):

        print(f'Process group {group_name}')
        # create album
        album    = api.photos.createAlbum(title=group_name, group_id=group_id, description="Добавлено 16 августа")
        album_id = album.id

        download_all_photo(df)

        upload_url = api.photos.getUploadServer(album_id=album_id, group_id=group_id)['upload_url']

        for ind, row in tqdm(df.iterrows(), total=len(df)):
            description = row['Описание']
            filename    = ''.join([q if str.isalnum(q) else ' ' for q in row['Наименование']])
            filename    = f'./dir_to_send/{filename}.jpg'

            if pd.isna(filename[0]):
                print(f'Ошибка! В строке {ind + 2} нет изображения')
                continue

            resp_json = upload_photo(api, group_id, album_id, filename, upload_url)

            for i in range(100):
                try:
                    photo_resp=api.photos.save(album_id    = album_id, 
                                    group_id    = group_id,
                                    server      = resp_json['server'], 
                                    photos_list = resp_json['photos_list'],
                                    hash        = resp_json['hash'], 
                                    caption     = description
                                    )
                    break
                except Exception as e:
                    print(e, 'sleep ', 3 * i, 'sec')
                    time.sleep(3 * i)

# Запиши фото в Обложка альбома

            if "Обложка альбома" in description:
                photo_id=photo_resp[0]['id']
                for i in range(100):
                    try:
                        photo_resp=api.photos.makeCover(
                                        owner_id    = -group_id, 
                                        photo_id    = photo_id,
                                        album_id    = album_id
                                        )
                        break
                    except Exception as e:
                        print(e, 'sleep ', 3 * i, 'sec')
                        time.sleep(3 * i)


def upload_photo(api, group_id, album_id, filename, upload_url):
    photo_list = '[]'
    resp_json = {}
    for k in range(10):
        try:
            for i in range(15):
                resp = requests.post(upload_url, files={
                    'file1': open(filename, 'rb')
                }, verify=False)
                resp_json  = resp.json()
                photo_list = resp_json['photos_list']
                if photo_list == "[]":
                    print(filename, resp_json, resp.raw, resp, 'sleep', i)
                    time.sleep(i)
                    continue
                else:
                    break
            if photo_list == "[]":
                raise CannotUploadPhotoException()
            break
        except Exception as e:
            upload_url = api.photos.getUploadServer(album_id=album_id, group_id=group_id)['upload_url']
            print(e, 'sleep ', k * 3, 'sec')
            time.sleep(k * 3)
    return resp_json


def download_all_photo(df):
    photo    = df['Фото']
    filename = df['Наименование'].apply(lambda x: ''.join([q if str.isalnum(q) else ' ' for q in x]))
    url_name = list(zip(photo, filename))

    print('start download photo', 'count = ', len(url_name))
    download_pool = Pool(16)
    download_pool.starmap(download_photo, url_name)
    download_pool.close()
    print('photos downloaded')

if __name__ == '__main__':
    main()
