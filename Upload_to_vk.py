import time
from multiprocessing import Pool

import pandas as pd
import requests
import urllib3
from tqdm import tqdm

from config import *
from utils  import CannotUploadPhotoException, download_photo, date_XX_XX_XXXX, album_comment

pd.set_option('display.max_rows',     1000)
pd.set_option('display.max_columns',  1000)
pd.set_option('display.max_colwidth', 1000)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():

# создать excel_1 файл 

    api = vk.API(session, v='5.92')
    df2 = pd.read_excel('./File/' + date_XX_XX_XXXX + '/Альбомы для ВК.xlsx')
    send_data=[]

    for group_name, df in df2.groupby('Группа'):

        print(f'Process group {group_name}')
# create album
# privacy_view настройки приватности просмотра альбома 
# privacy_commentнастройки приватности комментирования альбома в
# upload_by_admins_only - 1 только
# СДЕЛАТЬ - альбом создаем пользователем 

        album    = api.photos.createAlbum(title=group_name, group_id=group_id, description=album_comment, privacy_view=all, privacy_comment=all, upload_by_admins_only=1, comments_disabled=1 )
        album_id = album.id
# СДЕЛАТЬ - фото грузим правами группы 

#       download_all_photo(df)

        upload_url = api.photos.getUploadServer(album_id=album_id, group_id=group_id)['upload_url']

        for ind, row in tqdm(df.iterrows(), total=len(df)):

# 19082020 - в выгрузку добавляем размер и цену .. в Описание в выгрузку они не входят .. Объеденям здесь
# 19082020 - для того чтобы в Товарах была информация о цене и размерах 

            description = row['Описание']
            size        = row['Размер']
            cost        = row['Цена']  
            description = description + '\nРазмер: ' + str(size)+ f'\nЦена: {float(cost):.2f} руб.'
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


# Название	Цена	Цвета	Страна	Состав	Размеры	О товаре	Коллекция	Артикул	Изображение
# В доках говорится, что надо использовать метод photos.getById:
# https://vk.com/dev/photos.getById?params[photos]=213737404_316668269&params[extended]=1&params[photo_sizes]=0&params[v]=5.52
            
            send_data.append({
                 "Название"   :row['Наименование'],
                 "Цена"       :row['Цена'],
                 "Цвета"      :'',
                 "Страна"     :'',
                 "Состав"     :row['Состав'],
                 "Размеры"    :row['Размер'],
                 "О товаре"   :row['Описание'],
                 "Коллекция"  :group_name,
                 "Артикул"    :'',
                 "Изображение":filename
            })            


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




    df_send=pd.DataFrame(send_data)
    df_send.to_excel('./qwe.xlsx')

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
