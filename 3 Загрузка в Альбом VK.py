import math
import os
import time
from multiprocessing.pool import ThreadPool as Pool

import pandas as pd
import requests
import urllib3
from tqdm import tqdm

from config import сonfig
from utils import CannotUploadPhotoException, download_photo, date_XX_XX_XXXX, album_comment, retry

pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 1000)
pd.set_option('display.max_colwidth', 1000)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main():
    # api = vk.API(session, v='5.92')
    out_group_id = сonfig.out_group_id
    api = сonfig.get_session()
    print(os.getcwd())
    df2 = pd.read_excel('./File/' + date_XX_XX_XXXX + '/Альбомы для ВК.xlsx')

    for group_name, df in df2.groupby('Группа'):
        print(f'Process group {group_name}')
        if len(df)<=1:
            print('='*120,f'Пустой альбом -- не грузим (group_name)','='*120)
            continue

        if group_name == 'НОВЫЕ_ТОВАРЫ':
            print(f'НОВЫЕ_ТОВАРЫ -- не грузим ({len(df)} штук)')
            continue
        # create album
        # privacy_view настройки приватности просмотра альбома
        # privacy_comment настройки приватности комментирования альбома в
        # upload_by_admins_only - 1 только
        # СДЕЛАТЬ - альбом создаем пользователем

        album = retry(5)(api.photos.createAlbum)(title=group_name, group_id=out_group_id, description=album_comment,
                                                 privacy_view='all',
                                                 privacy_comment='all', upload_by_admins_only=1, comments_disabled=1)
        album_id = album.id

        # СДЕЛАТЬ - фото грузим правами группы

        # 18 09 2022 ВРЕМЕННО !
        download_all_photo(df)
        print('all photo downloads')

        upload_url = api.photos.getUploadServer(album_id=album_id, group_id=out_group_id)['upload_url']
        print(upload_url)

        for ind, row in tqdm(df.iterrows(), total=len(df)):
            # 19082020 - в выгрузку добавляем размер и цену .. в Описание в выгрузку они не входят .. Объеденям здесь
            # 19082020 - для того чтобы в Товарах была информация о цене и размерах
            description = row['Описание']
            size = row['Размер']
            cost = row['Цена']
            if not math.isnan(cost):
                if float.is_integer(float(cost)):
                    cost = str(int(cost))
                else:
                    cost = f'{float(cost):.2f}'

                description = description + '\nРазмер: ' + str(size) + f'\nЦена: {cost} руб.'

            filename = ''.join([q if str.isalnum(q) else ' ' for q in row['Наименование']])
            filename = f'./dir_to_send/{filename}.jpg'

            if pd.isna(filename[0]):
                print(f'Ошибка! В строке {ind + 2} нет изображения')
                continue

            photo_id = retry(retries=10)(upload_phhoto)(api, out_group_id, album_id, description, filename)

            # Запиши фото в Обложка альбома
            if "Обложка альбома" in description:
                photo_resp = retry(100)(api.photos.makeCover)(
                        owner_id=-out_group_id,
                        photo_id=photo_id,
                        album_id=album_id
                        )


def upload_phhoto(api, group_id, album_id, description, filename):
    resp_json = upload_photo_file(api, group_id, album_id, filename)
    photo_resp = api.photos.save(album_id=album_id,
                                 group_id=group_id,
                                 server=resp_json['server'],
                                 photos_list=resp_json['photos_list'],
                                 hash=resp_json['hash'],
                                 caption=description
                                 )
    photo_id = photo_resp[0]['id']
    return photo_id


def upload_photo_file(api, group_id, album_id, filename):
    photo_list = '[]'
    resp_json = {}
    upload_url = api.photos.getUploadServer(album_id=album_id, group_id=group_id)['upload_url']

    for k in range(10):
        try:
            for i in range(15):
                resp = requests.post(upload_url, files={
                        'file1': open(filename, 'rb')
                        }, verify=False)
                resp_json = resp.json()
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
            api._api.set_next_token()
            upload_url = api.photos.getUploadServer(album_id=album_id, group_id=group_id)['upload_url']
            print(e, 'sleep ', k * 3, 'sec')
            time.sleep(k * 3)
    return resp_json


def download_all_photo(df):
    photo = df['Фото']
    filename = df['Наименование'].apply(lambda x: ''.join([q if str.isalnum(q) else ' ' for q in x]))
    url_name = list(zip(photo, filename))

    print('start download photo', 'count = ', len(url_name))
    with Pool(10) as pool:
        with tqdm(total=len(url_name)) as pbar:
            pool.map(lambda x: download_photo(*x, pbar), url_name)

    # for url, name in tqdm(url_name):
    #     download_photo(url, name)
    print('photos downloaded')


if __name__ == '__main__':
    main()
