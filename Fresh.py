from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List

import pandas as pd
from bs4 import BeautifulSoup

from utils import date_XX_XX_XXXX, album_comment


def tryParse(value):
    try:
        return float(value) > 0
    except ValueError:
        return False


@dataclass
class Item_row:
    name: str = ""
    cost: str = 0
    description: str = ""
    color: List[str] = field(default_factory=list)
    sizes: List[str] = field(default_factory=list)
    availabels: List[List[bool]] = field(default_factory=list)
    imgs: List[str] = field(default_factory=list)


@dataclass
class Item:
    name: str = ""
    cost: str = 0
    description: str = ""
    color: str = ""
    availabel_sizes: str = ""
    imgs_str: str = ""


class State(Enum):
    Init = 0
    Available_Sizes = 1
    Description = 2


def parse_file(filename) -> List[Item_row]:
    soup = BeautifulSoup(open(filename, encoding='1251'), 'html.parser')
    item_list = []
    cur_item = None
    cur_state = State.Init
    for ind, row in enumerate(soup.select('tr')):
        if 'Описание' in row.select('td')[0].text:
            cur_state = State.Description

        if cur_state == State.Init and len(row.select('td')) > 1:
            name = row.select('td')[0].text.strip().strip('\n').replace('\n', '')
            cost = row.select('td')[1].text.replace(',', '.').replace(' ', '')

            if tryParse(cost):  # Начало

                cost = float(cost)
                cur_item = Item_row()

                cur_item.name = name
                cur_item.cost = cost
                for td in row.select('td')[4:14]:
                    cur_item.sizes.append(td.text)
                cur_state = State.Available_Sizes

        elif cur_state == State.Available_Sizes:
            cur_item.color.append(row.select('td')[0].text)
            sizes_availables = []
            for td in row.select('td')[4:14]:
                sizes_availables.append(td.text != "")
            cur_item.availabels.append(sizes_availables)

        elif cur_state == State.Description:
            cur_item.description = row.select('td')[0].text
            imgs = row.select('a')
            cur_item.imgs = [img.attrs['href'] for img in imgs]

            item_list.append(cur_item)
            cur_state = State.Init
    return item_list


def main():
    filename = './PriceFresh/1.files/sheet001.htm'

    item_list = parse_file(filename)

    items = []
    for item in item_list:

        if len(item.color) == len(item.imgs):
            for ind, color in enumerate(item.color):
                new_item = Item(
                        name=item.name  # Наименование
                             + " " + item.color[ind],
                        cost=item.cost,  # Цена
                        description=item.name
                                    + '\n' + item.description
                                    + '\n' + item.color[ind],
#                                    + '\nРазмер: ' + ', '.join(
#                                [size for ind1, size in enumerate(item.sizes) if item.availabels[ind][ind1]]),
                        color=item.color[ind],  # Состав
                        availabel_sizes=', '.join(
                                [size for ind1, size in enumerate(item.sizes) if item.availabels[ind][ind1]]),
                        imgs_str=item.imgs[ind]
                )
                items.append(new_item)
        else:
            for ind, color in enumerate(item.color):
                new_item = Item(
                        name=item.name  # Наименование
                             + " " + item.color[ind],
                        cost=item.cost,  # Цена
                        description=item.name
                                    + '\n' + item.description
                                    + '\n' + item.color[ind],
                        color=item.color[ind],
                        availabel_sizes=', '.join(
                                [size for ind1, size in enumerate(item.sizes) if item.availabels[ind][ind1]]),
                        imgs_str=item.imgs[0]
                )
                items.append(new_item)

    df = pd.DataFrame([asdict(x) for x in items])

    print(df.columns)

    df["Вид номенклатуры"] = "CLEVER"

    df.columns = ['Наименование',
                  'Цена',
                  'Описание',
                  'Состав',
                  'Размер',
                  'Фото',
                  'Группа']

    df = df[[
            'Наименование',
            'Описание',
            #                 'Состав',
            'Размер',
            'Цена',
            'Фото',
            'Группа'
             ]]

    writer = pd.ExcelWriter("./File/" + date_XX_XX_XXXX + "/Альбомы для ВК.xlsx", engine='xlsxwriter')
    df.to_excel(writer, index=False)

    workbook = writer.book
    worksheet = writer.sheets['Sheet1']

    worksheet.set_column('A:A', 55)
    worksheet.set_column('B:B', 8)
    worksheet.set_column('C:C', 25)
    worksheet.set_column('D:D', 25)
    worksheet.set_column('E:E', 25)
    worksheet.set_column('F:F', 25)
    worksheet.set_column('G:G', 25)

    writer.save()
    writer.close()


if __name__ == '__main__':
    main()
