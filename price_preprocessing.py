import pandas as pd
from pprint import pprint
import hashlib
from tkinter import *
from tkinter import filedialog

from tqdm import tqdm

art_split_markers = set(" "+(x.lower().strip()) for x in open('./art_markers.txt', encoding='utf-8').readlines())


def extract_art(x):
    x=str(x)  
    if ' р ' in x:
        x=x[:x.index(' р ')]
    return x

def extract_correnct_art_and_name(art: str):
    for word in art_split_markers:
        if word in art.lower():
            split_ind = art.lower().index(word)
            ret_art = art[:split_ind]
            ret_name = art[split_ind:]
            return ret_art
    ### Если не нашли ни одного слова
    print(f'Error in art: {art}')
    return art

def extract_size(x):
    x=str(x)  
    try:
        return x[x.index(' р ')+3:]
    except Exception as e:
        return ""
def main(from_file,to_file):    
    df = pd.read_excel(from_file)
    df=df[~df['Номенклатура'].isna()]
    
    df['art']=df['Номенклатура'].apply(extract_art)
    df['art_o3']=df['art'].apply(extract_correnct_art_and_name)
    df['size']=df['Номенклатура'].apply(extract_size)

    df=df.fillna(value='')
    df2=pd.DataFrame()

    for art,group in tqdm(df.groupby('art_o3')):
       
        all_sizes=', '.join([str(x) for x in group['size']])      
        art_wo3=' '.join(art.split(' ')[:-3]).strip()    
        

        ind=0    
        for ind_1, item in group.iterrows():

#description=f'''Артикул: {item['art']}
#Размеры: {all_sizes}'''.strip()

            df2=df2.append({
                        "Номенклатура":item['art_o3'],
     #                  "Наименование полное":item['Номенклатура'],
                        'Наименование полное':item['art'],
                        "Код":item['Код'],
                        "Штрихкод":item['Штрихкод'],
                        "Остаток":item['Остаток'],
                        "Размер":item['size'],
                        'Розничная':item['Цена'],
     #                  'Описание':description,
                        "Вид номенклатуры": "Новые товары поставщика"
                    },ignore_index=True)

    df2=df2[["Номенклатура","Наименование полное","Код","Штрихкод","Остаток","Размер",'Розничная',"Вид номенклатуры"]]
    df2.to_excel(to_file)
    df2.head()



class MyFirstGUI:
    def __init__(self, master):
        self.master = master

        self.create_wigets()
        self.pack()

    def pack(self):
        self.file_frame.pack()
        self.input_file_btn.pack(side='left')
        self.selected_input_file.pack(side='right')

        self.process_button.pack()
        self.process_status.pack()

    def create_wigets(self):
        self.master.title("Обработка прайса")

        self.file_frame = Frame(self.master)
        self.input_file_btn = Button(self.file_frame, text="Выбрать прайс", command=self.select_save_file)
        self.selected_input_file = Label(self.file_frame, text="")

        self.process_button = Button(self.master, text="Начать обработку", command=self.process)

        self.process_status = Label(self.master, text="...")

    def select_save_file(self):
        self.input_file = filedialog.askopenfilename()
        self.selected_input_file['text'] = 'Обрабатываемый прайс:\n ' + self.input_file

    def process(self):
        save_file=filedialog.asksaveasfilename( defaultextension='.xlsx')
        print("process_file")
        self.process_status['text'] = 'В обработке'
        main(self.input_file,save_file)
        self.process_status['text'] = 'Обработка завершена'
        # process_files(self.price_file,self.blank_file,self.out_file,self.log)


root = Tk()
root.geometry("640x480")
my_gui = MyFirstGUI(root)
root.mainloop()
