from dataclasses import asdict
from pprint import pprint

import pandas as pd
import vk
import vk.api
from tqdm import tqdm

# session 
session = vk.Session('aef44be9f894721156bd392b40d79cd7c51fa6542d63980c04ee9a62a26c16b728819626b3d03c5f41cf4')

from utils import VK_Item, merge_excel, art_split_markers, split_marker


def process_photo_batch(photos):
    batch_items = []
    for photo in photos['items']:
        urls = list(sorted(photo['sizes'], key=lambda x: x['width'], reverse=True))

        batch_items.append(VK_Item(urls[0]['url'], photo['text'], f'https://vk.com/photo{photo.owner_id}_{photo.id}'))
    return batch_items


error_out = None
art_out = None


def get_sizes(art, rows):
    if ' р ' not in art:
        size = ''
        all_sizes = ''
    else:
        art, size = str(art).split(' р ')
        size = size.replace(' ', '')
        try:
            all_sizes = ', '.join([str(x).split(' р ')[1].replace(' ', '') for x in rows if x != ''])
        except Exception as e:
            error_out.write(str(rows[-4:]) + '\n')
            error_out.flush()
            all_sizes = "________ОШИБКА________"
    return all_sizes, art, size


def extract_art_and_data(raw_data):
    rows = []
    data_cols = []
    split = False
    for val in raw_data:
        val = val.strip()
        if val == '-' or val == '':
            split = True
            continue

        elif str(val).lower() in split_marker:
            split = True
        elif len(split_marker.intersection(set(str(val).lower().split(' ')))) != 0:
            split = True

        if not split:
            rows.append(val)
        elif not pd.isna(val):
            data_cols.append(val)
    if not split:
        error_out.write(str(raw_data[-4:]) + '\n')
        error_out.flush()
        rows = []
        data_cols = []
        for ind, val in enumerate(raw_data):
            if ind == 0:
                rows.append(str(val))
            elif not pd.isna(val):
                data_cols.append(val)
    return data_cols, rows


def extract_correnct_art_and_name(art: str):
    for word in art_split_markers:
        if word in art.lower():
            split_ind = art.lower().index(word)
            ret_art = art[:split_ind]
            ret_name = art[split_ind:]
            return ret_art, ret_name
    ### Если не нашли ни одного слова
    art_out.write(art + '\n')
    art_out.flush()
    return art, '________NOT_FOUND__________'


def process_to_1c(df, save_dir, name, name_album):
    df2 = pd.DataFrame(columns=[
            "Картинка",
            "Ссылка на товар",
            "Номенклатура",
            "Наименование полное",
            "Размер",
            'Состав',
            'Розничная',
            "Вид номенклатуры"
    ])
    global error_out, art_out
    error_out = open(f'./errors/{name}.txt', 'w', encoding='utf-8')
    art_out = open(f'./art/{name}.txt', 'w', encoding='utf-8')
    for ind, row in tqdm(df.iterrows(), total=len(df),desc=f'___{name_album}___'):

        raw_data = str(row['description']).split('\n')

        data_cols, rows = extract_art_and_data(raw_data)

        for ind1, art in enumerate(rows):
            all_sizes, art, size = get_sizes(art, rows)
            art_new, name_new = extract_correnct_art_and_name(art)

            if len(data_cols) == 0:
                continue
            try:
                data_cols[-1] = int(
                        str(data_cols[-1]).lower().replace('руб.', '').replace('руб', '').replace('цена:', '')
                            .replace(':', '').strip())
            except:
                data_cols[-1] = "_______НЕТ_ЦЕНЫ________"

            art = art.replace('?', '').strip()

            df2 = df2.append({
                    "Картинка"           : row['photo_url'] if ind1 == 0 else '',
                    "Ссылка на товар"    : row['link'] if ind1 == 0 else '',
                    "Номенклатура"       : art_new,
                    "Наименование полное": art,
                    "Размер"             : size,
                    'Состав'             : ((data_cols[-3] + " ") if len(data_cols) >= 3 else "") + (
                            data_cols[-2] if len(data_cols) >= 2 else ""),
                    'Розничная'          : data_cols[-1] if len(data_cols) >= 1 else "_______НЕТ_ЦЕНЫ???",
                    "Вид номенклатуры"   : name_album
            }, ignore_index=True)
    print('\n'*1)
    error_out.close()
    art_out.close()
    if len(df2) == 0:
        return
    else:
        df2.to_excel(f'{save_dir}/_processed_{name}.xlsx')
    return f'{save_dir}/_processed_{name}.xlsx'


def download_vk_album(group_id, album_id, save_dir):
    api = vk.API(session, v='5.92')

    group_id = int(group_id)
    if group_id > 0:
        print("[WARNING] Realy positive group id???")
        group_id = -group_id

    albums = api.photos.getAlbums(owner_id=group_id, album_ids=album_id)['items']

    result_files = []

    for album in tqdm(albums,desc="__ALBUMS__"):
        album_items = []
        offset = 0
        count  = 1000
        photos = api.photos.get(owner_id=group_id, album_id=album['id'], count=1000, photo_sizes=1, offset=offset)
        while (offset + count <= photos['count']):
            album_items.extend(process_photo_batch(photos))
            offset += count
            photos = api.photos.get(owner_id=group_id, album_id=album['id'], count=1000, photo_sizes=1,
                                    offset=offset)
        album_items.extend(process_photo_batch(photos))

        df = pd.DataFrame(list(map(asdict, album_items)))

        name_album = album["title"]
        name = album["title"].replace(" ", "_").replace("/", "-")
        df.to_excel(f'{save_dir}/{name}.xlsx')

        processed_file = process_to_1c(df, save_dir, name, name_album)

        result_files.append(f'{save_dir}/{name}.xlsx')
        result_files.append(processed_file)
    return result_files


if __name__ == '__main__':

    group_id = -198234557
    album_id = ''
    save_dir = './res'

    download_vk_album(group_id, album_id, save_dir)
    merge_excel(save_dir)
