import collections
import json
import logging
import time
from functools import partial
from multiprocessing.dummy import Pool
from pprint import pprint
from typing import List

from jinja2 import Template

import pandas as pd
import requests
import urllib3
from pandas import DataFrame

logging.basicConfig(level=logging.INFO)
from tqdm import tqdm
from config import сonfig

group_id = 192858688
owner_id = -group_id

from utils import CannotUploadPhotoException, download_photo, date_XX_XX_XXXX, get_id, get_request

pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', 1000)
pd.set_option('display.max_colwidth', 1000)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

api = сonfig.get_session()

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


def main(in_group_names:List=None):
    if in_group_names is None:
        in_group_names=[]
    if not isinstance(in_group_names,list):
        in_group_names=[in_group_names]
    df2 = pd.read_excel('./File/' + "13_04_2023" + '/Альбомы для ВК.xlsx',index_col=0)
    df2:DataFrame
    category_list=[]
    offer_list=[]
    for group_ind,(group_name, df) in enumerate(df2.groupby('Группа')):
        if in_group_names and group_name not in in_group_names:
            continue
        # df=df.head(5)
        # if group_ind>3:
        #     break
        df:DataFrame
        print(f'Process group {group_name}')

        category_list.append({'id':group_ind,'name':group_name})
        df['Размер']=df['Размер'].map(lambda x: str(x).split(','))
        df=df.explode('Размер',ignore_index=True)
        df['Размер']=df['Размер'].str.strip()
        df['id'] = df.index.map(lambda x: f'{group_name}_{group_ind}_{x}')

        df.rename(columns={
                "Наименование":"art",
                "Описание":"description",
                "Размер":"size",
                "Фото":"photo_url",
                "Цена":"price"
                },inplace=True)
        df['category_id']=group_ind
        df.drop(columns=['Группа','Состав'],inplace=True)
        df=df.dropna()
        offer_list.extend(
                df.to_dict(orient='records')
                )
    sizes=collections.Counter()
    for el in offer_list:
        sizes[el['size']]+=1
    pprint(sizes)
    print(len(offer_list))
    print(len(sizes))
    with open('./yml_template.jinja','r',encoding='utf-8') as f:
        template=Template(f.read())
    render_res=template.render(category_list=category_list,offer_list=offer_list,group_id=group_id)
    with open('out_file.xml', 'w',encoding='utf-8') as f:
        f.write(render_res)



if __name__ == '__main__':

#    remove_all_items(owner_id)
#    remove_all_albums(owner_id)


    main()
