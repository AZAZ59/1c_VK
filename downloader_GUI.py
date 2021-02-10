from dataclasses import asdict
from pprint import pprint

import pandas as pd
import vk
import vk.api
from tqdm import tqdm

# session Ксении
session = vk.Session('c297dec325e43588e5472b7331c343760072c052abe7a0c90725f86e7bce440a9a2175629003e34c83916')

#        stambul     - 'aef44be9f894721156bd392b40d79cd7c51fa6542d63980c04ee9a62a26c16b728819626b3d03c5f41cf4'
session = vk.Session('aef44be9f894721156bd392b40d79cd7c51fa6542d63980c04ee9a62a26c16b728819626b3d03c5f41cf4')


from utils import VK_Item, merge_excel, art_split_markers, split_marker, date_XX_XX_XXXX,safelist

def process_photo_batch(photos):
    batch_items = []
    for photo in photos['items']:
        urls = list(sorted(photo['sizes'], key=lambda x: x['width'], reverse=True))

        batch_items.append(VK_Item(urls[0]['url'], photo['text'], f'https://vk.com/photo{photo.owner_id}_{photo.id}'))
    return batch_items

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
            ret_art   = art[:split_ind]
            ret_name  = art[split_ind:]
            return ret_art, ret_name
    ### Если не нашли ни одного слова

    error_out.write(' Не найден тип товара - ' + art + '\n')
#   art_out.flush()
    return art, '________NOT_FOUND__________'


def process_to_1c(df, save_dir, name, name_album):
    df2 = pd.DataFrame(columns=[
            "Картинка",
            "Ссылка на товар",
            "Номенклатура",
            "Наименование полное",
            'Состав',
            "Вид номенклатуры",
            'Группа',
            'Наименование',
            'Описание',
            'Размер',
            'Фото',
            'Цена'
    ])

    global error_out
    error_out = open(f'./File/' + date_XX_XX_XXXX + '/errors/' + name + '.txt', 'w', encoding='utf-8')
  
    for ind, row in tqdm(df.iterrows(), total=len(df),desc=f'___{name_album}___'):

        raw_data = str(row['description']).split('\n')
        raw_data=safelist(raw_data)
        data_cols, rows = extract_art_and_data(raw_data)

        # из первой строки Описания формиуем Наименование полное - текст до "размера" 
        if len(rows)==0:
            continue
        art = rows[0]

        if ' р ' in art:
            art, size = str(art).split(' р ')
        art = art.replace('?', '').strip()

        # Артикул - это текст Наименование полное до "джемпер"
        art_new, name_new = extract_correnct_art_and_name(art)

        # может вынести формирование состава 
#        print(len(raw_data))
        df2 = df2.append({
            "Картинка"           : row['photo_url'],
            "Ссылка на товар"    : row['link'],
            "Номенклатура"       : art_new,
            "Наименование полное": art,
            'Состав'             : ((data_cols[-3] + " ") if len(data_cols) >= 3 else "") + (
                    data_cols[-2] if len(data_cols) >= 2 else ""),
            "Вид номенклатуры"   : name_album,
            'Группа'             : '02_дек ' + name_album,
            'Наименование'       : art,
            'Описание'           : ( 'Артикул: '  + art         + '\n' 
                                   + 'Описание: ' + raw_data[2] + '\n' 
                                   + raw_data.get(3,"")                + '\n' 
				   + raw_data.get(4,"")
                                   ),
            'Размер'             : raw_data.get(5,"Нет размера"),
            'Фото'               : row['photo_url'],
            'Цена'               : raw_data.get(6,0)
        }, ignore_index=True)

    # вывести дубли 
    duplicated=df2[df2.duplicated(subset='Номенклатура')]
    dupli_out.write(duplicated.to_csv(None,sep=';'))
 
    # убрать дубли по art_new  -- аритикул --
    df2 = df2.drop_duplicates(subset='Номенклатура')
    
    print('\n'*1)

    error_out.close()
#   art_out.close()

    if len(df2) == 0:
        return
    else:
        df2.to_excel(f'{save_dir}/_processed_{name}.xlsx')
    return           f'{save_dir}/_processed_{name}.xlsx'


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

    group_id = -182912257
#               198234557 ФРЕШ (фото клевер)
#               202009856 1С клевер
    group_id = -202009856

    album_id = ''

    save_dir = './File/' + date_XX_XX_XXXX + '/res'

    error_out = None
    dupli_out = open(f'./File/' + date_XX_XX_XXXX + '/errors/Дубли_в_Альбомах.txt', 'w', encoding='utf-8')

    download_vk_album(group_id, album_id, save_dir)
    merge_excel(save_dir)
