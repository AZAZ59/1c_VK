import hashlib
from dataclasses import asdict
from pprint import pprint
from tkinter import *
from tkinter import filedialog

import pandas as pd
import vk
import vk.api
from tqdm import tqdm

# dct = DotDict(dct)
from config import session
from utils import Request_new, VK_Item

vk.api.Request = Request_new

split_marker = set(x.lower().strip() for x in open('./split_markers.txt', encoding='utf-8').readlines())
art_split_markers = set(x.lower().strip() for x in open('./art_markers.txt', encoding='utf-8').readlines())

pprint(split_marker)
pprint(art_split_markers)


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


def extract_correnct_art_and_name(art:str):
    for word in art_split_markers:
        if word in art.lower():
            split_ind=art.lower().index(word)
            ret_art=art[:split_ind]
            ret_name=art[split_ind:]
            return ret_art,ret_name
    ### Если не нашли ни одного слова
    art_out.write(art+'\n')
    art_out.flush()
    return art,'________NOT_FOUND__________'

def process_to_1c(df, save_dir, name):
    df2 = pd.DataFrame(columns=[
        "Большое фото",
        "Ссылка на товар",
        "Артикул",
        "Наименование",
        "Размеры",
        "Ткань",
        'Состав',
        'Цена',
        'Описание',
        "new_name"
    ])
    global error_out,art_out
    error_out = open(f'./errors/{name}.txt', 'w', encoding='utf-8')
    art_out = open(f'./art/{name}.txt', 'w', encoding='utf-8')
    for ind, row in tqdm(df.iterrows(), total=len(df)):

        raw_data = str(row['description']).split('\n')

        data_cols, rows = extract_art_and_data(raw_data)

        for ind1, art in enumerate(rows):
            all_sizes, art, size = get_sizes(art, rows)
            art_new,name_new = extract_correnct_art_and_name(art)

            if len(data_cols) < 1:
                continue
            try:
                data_cols[-1] = int(
                    str(data_cols[-1]).lower().replace('руб.', '').replace('руб', '').replace('цена:', '')
                    .replace(':','').strip())
            except:
                data_cols[-1] = "_______НЕТ_ЦЕНЫ________"

            art = art.replace('?', '').strip()

            description = f'Артикул: {art}\n' + f'Размеры: {all_sizes}\n'
            if len(data_cols) >= 3:
                description += f'{data_cols[-3]}\n'
            if len(data_cols) >= 2:
                description += f'{data_cols[-2]}\n'
            description = description.strip()

            df2 = df2.append({
                "Большое фото"      : row['photo_url'] if ind1 == 0 else '',
                "Ссылка на товар"   : row['link'] if ind1 == 0 else '',
                "Артикул"           : art_new,
                "Наименование"      : art,
                "Размеры"           : size,
                "Ткань"             : data_cols[-3] if len(data_cols) >= 3 else "",
                'Состав'            : data_cols[-2] if len(data_cols) >= 2 else "",
                'Цена'              : data_cols[-1] if len(data_cols) >= 1 else "_______НЕТ_ЦЕНЫ???",
                'Описание'          : description,
                "new_name"          :name_new
            }, ignore_index=True)

    error_out.close()
    art_out.close()
    if len(df2) == 0:
        return
    else:
        df2.to_excel(f'{save_dir}/_processed_{name}.xlsx')


def download_vk_album(group_id, album_id, save_dir):

    api = vk.API(session, v='5.92')

    group_id = int(group_id)
    if group_id > 0:
        print("[WARNING] Realy positive group id???")
        group_id = -group_id

    albums = api.photos.getAlbums(owner_id=group_id, album_ids=album_id)['items']

    for album in tqdm(albums, desc='___ALBUMS___'):
        album_items = []
        offset = 0
        count = 1000
        photos = api.photos.get(owner_id=group_id, album_id=album['id'], count=1000, photo_sizes=1, offset=offset)
        while (offset + count <= photos['count']):
            album_items.extend(process_photo_batch(photos))

            offset += count
            photos = api.photos.get(owner_id=group_id, album_id=album['id'], count=1000, photo_sizes=1,
                                    offset=offset)
        album_items.extend(process_photo_batch(photos))

        df = pd.DataFrame(list(map(asdict, album_items)))

        name = album["title"].replace(" ", "_").replace("/", "-")
        df.to_excel(f'{save_dir}/{name}.xlsx')

        process_to_1c(df, save_dir, name)
    pass


class MyFirstGUI:
    def __init__(self, master):
        self.master = master

        self.create_wigets()
        self.pack()

    def pack(self):
        self.group_id_frame.pack()
        self.group_id_label.pack(side='left')
        self.group_id.pack(side='right')

        self.album_id_frame.pack()
        self.album_id_label.pack(side='left')
        self.album_id.pack(side='right')

        self.file_frame.pack()
        self.output_file.pack(side='left')
        self.selected_save_file.pack(side='right')
        self.process_button.pack()
        self.process_status.pack()

    def create_wigets(self):
        self.master.title("Загрузка альбома")

        self.group_id_frame = Frame(self.master)
        self.group_id_label = Label(self.group_id_frame, text="id группы: ")
        self.group_id = Entry(self.group_id_frame)
        self.group_id.insert(END, '-182912257')

        self.album_id_frame = Frame(self.master)
        self.album_id_label = Label(self.album_id_frame,
                                    text="id альбомов через ',' ( оставить пустым для скачивания всех альбомов): ")
        self.album_id = Entry(self.album_id_frame)
        self.album_id.insert(END, '272262579')

        self.file_frame = Frame(self.master)
        self.output_file = Button(self.file_frame, text="Каталог для сохранения", command=self.select_save_file)
        self.selected_save_file = Label(self.file_frame, text="")

        self.process_button = Button(self.master, text="Начать обработку", command=self.process)

        self.process_status = Label(self.master, text="...")

        self.save_dir='./res'

    def select_save_file(self):
        self.save_dir = filedialog.askdirectory()
        self.selected_save_file['text'] = 'Каталог для сохранения:\n ' + self.save_dir

    def process(self):
        split_marker = set(x.lower().strip() for x in open('./split_markers.txt', encoding='utf-8').readlines())
        art_split_markers = set(x.lower().strip() for x in open('./art_markers.txt', encoding='utf-8').readlines())

        pprint(split_marker)
        pprint(art_split_markers)

        print("process_file")
        self.process_status['text'] = 'В обработке'
        download_vk_album(self.group_id.get(), self.album_id.get(), self.save_dir)
        self.process_status['text'] = 'Обработка завершена'
        # process_files(self.price_file,self.blank_file,self.out_file,self.log)


root = Tk()
my_gui = MyFirstGUI(root)
root.mainloop()

#download_vk_album(-182912257, 272262579, './res')