import json
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
from tqdm import tqdm

from config import *

from utils import CannotUploadPhotoException, download_photo, date_XX_XX_XXXX, album_comment, get_id, get_request

pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 1000)
pd.set_option('display.max_colwidth', 1000)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

api = vk.API(session, v='5.120')
group_id = 192858688
owner_id = -group_id

req = requests.get(
        url='https://vk.com/public192858688?act=market_group_items',
        cookies={
                "remixsid": remixsid
        }
)
for line in req.text.splitlines():
    if line.startswith('window.initReactApplication'):
        json_line = line[line.index('{'):line.rindex('}') + 1]
        market_data = json.loads(json_line)
        csrf_hash = market_data['options']['csrf_hash']
        break
print(csrf_hash)

def remove_all_items(owner_id):
    count = api.market.get(owner_id=owner_id, count=0, offset=0).count
    step = 200
    while count > 0:
        res = api.market.get(owner_id=owner_id, count=step, offset=0)
        count = res['count']
        items = res['items']
        print(count)
        for item in tqdm(items):
            item_id = item.id
            q = api.market.delete(owner_id=owner_id, item_id=item_id)
            time.sleep(0.3)


def remove_all_albums(owner_id):
    count = api.market.getAlbums(owner_id=owner_id, count=0, offset=0).count
    step = 100
    while count > 0:
        res = api.market.getAlbums(owner_id=owner_id, count=step, offset=0)
        count = res['count']
        items = res['items']
        print(count)
        for album in tqdm(items):
            album_id = album.id
            q = api.market.deleteAlbum(owner_id=owner_id, album_id=album_id)
            time.sleep(0.3)


def main( group_name7 ):

    df2 = pd.read_excel('./File/' + date_XX_XX_XXXX + '/Альбомы для ВК.xlsx')

    for group_name, df in df2.groupby('Группа'):
        if group_name != group_name7 :
            continue
        print(f'Process group {group_name}')

        # create album

        album = api.market.addAlbum(title=group_name, owner_id=owner_id)
        time.sleep(0.3)
        album_id = album.market_album_id

        property_response = get_request(f'[{{"action":"addProperty","title":"Размер","type":"text"}}]', hash=csrf_hash,
                                        group_id=group_id)
        prop_id = get_id(property_response)

        sizes = df['Размер'].map(lambda x: str(x).split(','))
        sizes = {str(x_i).strip() for x in sizes for x_i in x}
        sizes -= {''}
        sizes_dict = dict()
        for size in sizes:

            action = f'[{{"action": "addVariant", "property_id": {str(int(prop_id))}, "title": "{size}"}}]'
            resp_json = get_request(action, hash=csrf_hash, group_id=group_id)
            item_id = get_id(resp_json)
            sizes_dict[size] = item_id
            if item_id == 0:
                print(f"ERROR in album {group_name} -- too much sizes")
                break


        download_all_photo(df)

        upload_market_items(album_id, df,sizes_dict)


def upload_market_items(album_id, df,sizes_dict):
    for ind, row in tqdm(df.iterrows(), total=len(df)):
        # 19082020 - в выгрузку добавляем размер и цену .. в Описание в выгрузку они не входят .. Объеденям здесь
        # 19082020 - для того чтобы в Товарах была информация о цене и размерах
        description = row['Описание']

        filename = ''.join([q if str.isalnum(q) else ' ' for q in row['Наименование']])
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
        time.sleep(0.3)

        add_resp = api.market.add(
                owner_id=owner_id,
                name=row['Наименование'],
                description=description,
                category_id=1,  # TODO get from list
                price=row['Цена'],
                main_photo_id=save_resp['id']
        )
        time.sleep(0.3)

        item_id = add_resp['market_item_id']

        api.market.addToAlbum(
                owner_id=owner_id,
                item_id=item_id,
                album_ids=[album_id],

        )
        time.sleep(0.3)

        sizes = [x.strip() for x in  str(row['Размер']).split(',')]
        action_list=[]
        clone_ids = [item_id]
        if len(sizes)>1:
            for size in sizes:
                action_list.append({
                        "action" : "cloneItem",
                        "item_id": item_id
                })
            action = json.dumps(action_list[:-1])
            clone_resp = get_request(action, hash=csrf_hash)
            clone_ids += [x[0] for x in clone_resp['payload'][1][0]['data']]

        action_list = []
        for size, clone_id in zip(sizes, clone_ids):
            action_list.append({
                    "action"     : "setItemVariants",
                    "item_id"    : clone_id,
                    "variant1_id": sizes_dict[size],
                    "variant2_id": 0
            })
        action_list.append({
                "action"      : "groupItems",
                "item_ids"    : clone_ids,
                "main_item_id": item_id})
        get_request(json.dumps(action_list), hash=csrf_hash)

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
    filename = df['Наименование'].apply(lambda x: ''.join([q if str.isalnum(q) else ' ' for q in x]))

    url_name = list(zip(photo, filename))

    print('start download photo', 'count = ', len(url_name))
    part_download_photo = partial(download_photo)
    download_pool = Pool(16)
    download_pool.starmap(download_photo, url_name)
    download_pool.close()
    print('photos downloaded')


if __name__ == '__main__':
#   remove_all_items(owner_id)
#   remove_all_albums(owner_id)

#    main('CUBBY пижамы/халаты/белье')
#    main('CUBBY - трикотаж')
#    main('БЕЛЬЕ')
#    main('РЮКЗАКИ')
#    main('ЗИМА (верхняя одежда)')
#    main('ОСЕНЬ/ВЕСНА (верхняя одежда)')

# main('ВЯЗКА') -- много размеров

#  main('Тrikozza и Very Neat (для взрослых)')
#  main('ПИЖАМЫ - ХАЛАТЫ')
#  main('ШКОЛА-сад')
 
# main('МАЛЫШИ')  -- ошибка  247 строка 

#  main('ДЕВОЧКИ') -- ошибка
   main('МАЛЬЧИКИ')
   main('КЕПКИ + шапки хб')
   main('КОЛГОТКИ - НОСКИ')

# main('КР')
# main('КУПАЛЬНИКИ')
# main('ДЖИНСА')
# main('ФЛИС')
                 