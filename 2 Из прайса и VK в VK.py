import pandas as pd
from tqdm import tqdm

from utils import extract_correnct_art_and_name, extract_art, extract_size

pd.options.display.max_colwidth =  40
pd.options.display.max_columns  =  40
pd.options.display.max_rows     = 100
pd.options.display.width        = 222

def main( ):
 
    from_file   = './InputPrice/Прайс_для_VK.xlsx'
    result_file = './File/_VK_1C.xlsx'
    to_file     = 'w' 

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

    df_out=df_res  [[
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

    group_data=[
        ('ЯЯЯ001','Обложка альбома Тrikozza'        ,'Тrikozza и Very Neat (для взрослых)','https://sun9-6.userapi.com/xj77BosQ320oM6oy_F_j82ZeWDsEaD0mXxmvMw/UO5mw0BlwX4.jpg' ),
        ('ЯЯЯ002','Обложка альбома CUBBY_-_трикотаж','CUBBY - трикотаж'                   ,'https://sun9-21.userapi.com/uQAe-cx3gUisnONlFHDOlzCsfjbnOcKo4oqXxw/JkDDPBeB174.jpg'),
        ('ЯЯЯ003','Обложка альбома ФЛИС'            ,'ФЛИС'                               ,'https://sun9-20.userapi.com/Bannzg4pFLhnQd7Hv9-pgTVKsp7gnwC04D87sA/x-D4DUpjHXs.jpg'),
        ('ЯЯЯ004','Обложка альбома КОЛГОТКИ - НОСКИ','КОЛГОТКИ - НОСКИ'                   ,'https://sun9-57.userapi.com/pF9mcrxdCDEHNlH5BUB5k5q1OHCXtv0LoCvSIg/zYRmGgFNC4Y.jpg'),
        ('ЯЯЯ005','Обложка альбома ДЖИНСА'          ,'ДЖИНСА'                             ,'https://sun9-26.userapi.com/VmjooL4FowU3N-_2a9vHHsGX_HCGEP0LyYo8jQ/wn686Vx_ubE.jpg'),
        ('ЯЯЯ006','Обложка альбома КУПАЛЬНИКИ'      ,'КУПАЛЬНИКИ'                         ,'https://sun9-75.userapi.com/zSre8RzvfKpKL3T1_mUYhe-Ojm5PWOvrenYS5g/p6U_1bameag.jpg'),
        ('ЯЯЯ007','Обложка альбома ШКОЛА-сад'       ,'ШКОЛА-сад'                          ,'https://sun9-41.userapi.com/4rwOjTtJ5Nmsxj-TNgz8uP313bIDgxil0UEB-Q/lBf0n4vYUVU.jpg'),
        ('ЯЯЯ008','Обложка альбома БЕЛЬЕ'           ,'БЕЛЬЕ'                              ,'https://sun9-24.userapi.com/4rY8g5ICrao0erTDc25oYFWbK2Tt2Wa-c1J96A/OuNYL4YBV_0.jpg'),
        ('ЯЯЯ009','Обложка альбома КЕПКИ + шапки хб','КЕПКИ + шапки хб'                   ,'https://sun9-36.userapi.com/TLO-l5EUyo45NczyCRWy5u5NrdRxJCHZqRSF4w/840WPxuITLg.jpg'),
        ('ЯЯЯ010','Обложка альбома ПИЖАМЫ - ХАЛАТЫ' ,'ПИЖАМЫ - ХАЛАТЫ'                    ,'https://sun9-21.userapi.com/uQAe-cx3gUisnONlFHDOlzCsfjbnOcKo4oqXxw/JkDDPBeB174.jpg'),
        ('ЯЯЯ011','Обложка альбома КР'              ,'КР'                                 ,'https://sun9-68.userapi.com/G5Vg622R2hatQ5IrOQ7KuCjC5CZ8h0wgmczuIQ/YVemFnbPiWE.jpg'),
        ('ЯЯЯ012','Обложка альбома ДЕВОЧКИ'         ,'ДЕВОЧКИ'                            ,'https://sun9-60.userapi.com/zhHxzJP5YFdlVIDC-UDm4qFdQfkWJZe7sOa1Ww/NA-KRhSfK4w.jpg'),
        ('ЯЯЯ013','Обложка альбома МАЛЬЧИКИ'        ,'МАЛЬЧИКИ'                           ,'https://sun9-69.userapi.com/trXTVMgarPUFBq8_CVzru8x-8Y8mLn_PCdUY4A/chpmJtx4DWM.jpg'),
        ('ЯЯЯ014','Обложка альбома МАЛЫШИ'          ,'МАЛЫШИ'                             ,'https://sun9-36.userapi.com/6D8GQpRVmDgpnqf8JS0WHc9cGk20F2Q0DNoKfA/UsCEu6P8r60.jpg'),
        ('ЯЯЯ015','Обложка альбома РЮКЗАКИ'         ,'РЮКЗАКИ'                            ,'https://sun9-5.userapi.com/7KyQTwFsEE3ORCeKHNd3B4yBNmNLLUBkLhAijg/AMt0yaA3yvs.jpg' ),
        ('ЯЯЯ016','Обложка альбома ВЯЗКА'           ,'ВЯЗКА'                              ,'https://sun9-44.userapi.com/M0dRuGUeEvgARbDOre3i1vMVsYTlqqa6cvKwwQ/v2aZqP2YVwM.jpg'),
        ('ЯЯЯ017','Обложка альбома ОСЕНЬ/ВЕСНА'     ,'ОСЕНЬ/ВЕСНА (верхняя одежда)'       ,'https://sun9-66.userapi.com/Idn6FBB-i0QQhTdyDDwES6CHstuqgUcNRvCsZg/y8xWlIJf-vw.jpg'),
    ]                                                                                

# CUBBY пижамы/халаты/белье
# ЗИМА (верхняя одежда)
                                                                                     
    df_out=df_out.append([                                                           
        {                                                                            
        "Артикул":x[0],                                                              
        "Наименование":x[1],                                                         
        "НГруппа":x[2],                                                              
        "Фото":x[3],                                                                 
        } for x in group_data                                                        
        ],ignore_index=True)                                                         
                                                                                     
    df_out.to_excel    ('./File/Товары для загрузки в ВК.xlsx')
    df  = df_out
    df2 = pd.DataFrame()

    for name, group in tqdm(df.groupby('Артикул')):
        sizes = ', '.join([str(x) for x in list(group['Характеристика'])])
        description = ''
        description += f'Артикул: {group["Наименование"].iloc[0]}\n'
        if len(sizes) != 0 and sizes != 'nan':
            description += f'Размеры: {sizes}\n'
        if str(group["Состав"].iloc[0]) != 'nan':
            description += f'Состав: {group["Состав"].iloc[0]}\n'

        if str(group["Розничная"].iloc[0]) != 'nan':
            description += f'Цена: {int(group["Розничная"].iloc[0])} руб.\n'

        if 'http' in str(group['Фото'].iloc[0]):
            df2 = df2.append({
                'Наименование': str(group['Наименование'].iloc[0]),
                'Описание'    : description,
                'Фото'        : str(group['Фото'].iloc[0]),
                'Группа'      : str(group['НГруппа'].iloc[0]),
            }, ignore_index=True)
        else:
            print(str(group['Фото'].iloc[0]))

    df2.to_excel('./File/Альбомы для ВК.xlsx')

if __name__ == '__main__':
    main( )

