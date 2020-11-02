import logging
import zipfile
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List

from utils import date_XX_XX_XXXX, extract_correnct_art_and_name

logging.basicConfig(level=logging.DEBUG)
import pandas as pd

pd.options.display.max_colwidth =  40
pd.options.display.max_columns  =  400
pd.options.display.max_rows     = 1000
pd.options.display.width        =  222

def tryParse(value):
    try:
        return float(value) > 0
    except ValueError:
        return False

data_file = './PriceFresh/' + 'Клевер НАЛИЧИЕ 09_09.zip'
zip_ref   = zipfile.ZipFile(data_file, 'r')

class State(Enum):
    Init = 0
    Available_Sizes = 1
    Description = 2


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


def preprocess_data(df) -> pd.DataFrame:
    if len(df.columns) != 44:
        # Обработка без key:
        df = df[df.columns[:17]]
        df = df.iloc[5:]
        column_names = [
                'nm1', 'ps1', 'Unnamed: 2', 'key:', 'sz1', 'sz2', 'sz3', 'sz4', 'sz5', 'sz6', 'sz7', 'sz8', 'sz9', 'sz10', 'sc',
                'Unnamed: 42', 'sp'
                ]
        df.columns = column_names
        df['key:'] = df['ps1'].apply(lambda x: 'key' if tryParse(x) else None)
    else:
        df = df[df.columns[26:]]
        df = df.iloc[6:]

        if 'nm1' in df.columns:
            lst = list(df.columns)
            lst[lst.index('nm1') + 1] = 'ps1'
            df.columns = lst
    return df


def parse_data(df):
    item_list = []
    cur_item = None
    cur_state = State.Init
    for row in df.to_dict(orient='records'):

        if 'Описание' in row['nm1']:
            cur_state = State.Description

        if cur_state == State.Init and row['key:'] == 'key':
            name = row['nm1'].strip().strip('\n').replace('\n', '')
            cost = str(row['ps1']).replace(',', '.').replace(' ', '')

            if tryParse(cost):  # Начало

                cost = float(cost)
                cur_item = Item_row()

                cur_item.name = name
                cur_item.cost = cost
                for n in range(1, 11):
                    size = row[f'sz{n}']
                    if size is not None:
                        cur_item.sizes.append(size)
                cur_state = State.Available_Sizes

        elif cur_state == State.Available_Sizes:
            cur_item.color.append(row['nm1'])
            sizes_availables = []
            for n in range(1, 11):
                size = row[f'sz{n}']
                sizes_availables.append(not pd.isna(size))
            cur_item.availabels.append(sizes_availables)

        elif cur_state == State.Description:
            cur_item.description = row['nm1']
            item_list.append(cur_item)
            cur_state = State.Init
    return item_list



def format_data(filename, item_list):
    items = []
    for item in item_list:
        for color, available_size in zip(item.color, item.availabels):
            new_item = Item(
                    name=item.name  # Наименование
                         + " " + color,
                    cost=item.cost,  # Цена
                    description=item.name + '\n'
                                + item.description + '\n'
                                + color,
                    color=color,
                    availabel_sizes=', '.join(
                            [str(size) for ind1, size in enumerate(item.sizes) if available_size[ind1]])
                    )
            items.append(new_item)
    df = pd.DataFrame([asdict(x) for x in items])
    df["Вид номенклатуры"] = "CLEVER"
    df['Из файла'] = filename
    return df

def rename_collumns(df):
    df.columns = ['Наименование',
                  'Цена',
                  'Описание',
                  'Состав',
                  'Размер',
                  'Фото',
                  'Группа',
                  'Файл']
    df = df[['Наименование',
             'Описание',
             'Размер',
             'Цена',
             'Фото',
             'Группа',
             'Файл'
             ]]
    return df

def write_to_excel(df, filename):
    filename  = filename.replace('/','_')
    writer    = pd.ExcelWriter('./PriceFresh/' + filename, engine='xlsxwriter')
    df.to_excel(writer, index=False)
    workbook  = writer.book
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

def main():
    dataframe_list=[]
    for file in zip_ref.filelist:
        file: zipfile.ZipInfo
        file.filename = file.filename.encode('cp437').decode('cp866')
        if file.filename.endswith('.xlsx'):
            logging.info(f"process file: {file.filename}")
            df = pd.read_excel(zip_ref.open(file))
            df = preprocess_data(df)

            item_list = parse_data(df)

            df_out = format_data(file.filename, item_list)
            df_out = rename_collumns(df_out)

            dataframe_list.append(df_out)

            write_to_excel(df_out, "processed_" + file.filename)

            logging.info('processed items count: %i', len(item_list))
            logging.info("")
    df_full=pd.concat(dataframe_list)
    write_to_excel(df_full, 'CLEVER_FULL.xlsx')
    return df_full


def process_art(art):
    # art=art[art.index(' '):].strip()
    art = art.replace('CLE','').strip().lower().replace(' ','')
    # .replace('ТаТ','')
    return art

def extract_index(row):
    name=str(row['Наименование полное'])
    color=str(row['Состав'])
    if 'Цвет: ' in color:
        color=color[:color.index(' ',color.index('Цвет: ')+6)]
        ind=name+color
    else:
        ind=name
    ind=ind.strip().lower().replace(' ','')
    return ind

if __name__ == '__main__':
    # df=main()
    df=pd.read_excel('./File/17_09_2020/CLEVER_FULL.xlsx')

    df['ind']=df['Наименование'].apply(process_art)
    df = df.drop_duplicates('ind')
    df = df.set_index('ind')

    image_df = pd.read_excel('./File/' + date_XX_XX_XXXX +'/_VK_1C.xlsx')
    image_df = image_df.dropna(subset=['Картинка'])
    image_df['ind']=image_df[['Наименование полное','Состав']].apply(extract_index,axis=1)

    image_df = image_df.drop_duplicates('ind')
    image_df = image_df.set_index('ind')

    merged=df.join(image_df,rsuffix='___',how='inner')
write_to_excel(merged,'full_with_images.xlsx')


    print(df.head())
    print(image_df.head())
    print('*'*120)
    print('*'*120)
    print('*'*120)
    print(merged.head())
    print(len(merged),len(df),len(image_df))
    print(len(merged)/len(image_df))
