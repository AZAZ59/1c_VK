from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List

import pandas as pd
import urllib3
from bs4 import BeautifulSoup


def tryParse(value):
    try:
        float(value)
        return True
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



def parse_file(filename)->List[Item_row] :
    soup = BeautifulSoup(open(filename, encoding='1251'), 'html.parser')
    item_list = []
    cur_item = None
    cur_state = State.Init
    for ind, row in enumerate(soup.select('tr')):
        if 'Описание' in row.select('td')[0].text:
            cur_state = State.Description

        if cur_state == State.Init and len(row.select('td')) > 1:
            name = row.select('td')[0].text.strip().strip('\n').replace('\n','')
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
    filename='./sheet001.htm'

    item_list = parse_file(filename)

    items=[]
    for item in item_list:
        for ind,color in enumerate(item.color):
            new_item=Item(
                name            = item.name + ' ' + item.color[ind],
                cost            = item.cost,
                description     = item.description,
                color           = item.color[ind],
                availabel_sizes = ', '.join ([size for ind1,size in enumerate(item.sizes) if item.availabels[ind][ind1]]),
                imgs_str        = ', '.join (item.imgs)
            )
            items.append(new_item)

    df = pd.DataFrame([asdict(x) for x in items])
    print(df.columns)
    df.columns=['Номенклатура', 'Розничная', 'Описание', 'Состав', 'Размер', 'Картинка', "Вид номенклатуры"]
    df.to_excel('./result.xlsx')


if __name__ == '__main__':
    main()