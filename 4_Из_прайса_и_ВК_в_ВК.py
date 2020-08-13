import pandas as pd
from tqdm import tqdm

from utils import extract_correnct_art_and_name, extract_art, extract_size

pd.options.display.max_colwidth = 40
pd.options.display.max_columns = 40
pd.options.display.max_rows = 100
pd.options.display.width = 222


def main(from_file, to_file):
    # download_vk_album("-182912257", "", "./res")
    # result_file=merge_excel()

    #  result_file = './_processed_FULL.xlsx'
    result_file = './File/_VK_1C.xlsx'

    df = pd.read_excel(from_file)
    df = df[~df['Номенклатура'].isna()]

    df['art']    = df['Номенклатура'].apply(extract_art)
    df['art_o3'] = df['art'].apply(extract_correnct_art_and_name)
    df['size']   = df['Номенклатура'].apply(extract_size)

    df_price     = df.fillna(value='')

    df_vk = pd.read_excel(result_file)
    df_vk = df_vk.set_index('Номенклатура')
    df_vk = df_vk.dropna(subset=['Картинка'])

    df_res                     = df_price.join(df_vk, on='art_o3', how='left', rsuffix='VK_')

    df_res['Вид номенклатуры'] = df_res['Вид номенклатуры'].fillna(value='НОВЫЕ_ТОВАРЫ')
    df_res['Картинка']         = df_res['Картинка'].fillna(value='https://sun9-69.userapi.com/c858032/v858032503/22eaad/z0j4XJ9gbEk.jpg')
    df_res                     = df_res.fillna(value='')

    df_out=df_res[[
        'art_o3',
        'art',
        'size',
        'Цена',
        'Состав',
        'Вид номенклатуры',
        'Картинка'
    ]]

    df_out.columns=[
        "Артикул",
        "Наименование",
        "Характеристика",
        "Розничная",
        "Состав",
        "НГруппа",
        "Фото",
    ]

    df_out.to_excel('./File/Выгрузка в ВК.xlsx')


if __name__ == '__main__':
    main('./InputPrice/Прайс_для_VK_06_08.xlsx', 'w')
