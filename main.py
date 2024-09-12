from pprint import pprint

import pandas as pd
import openpyxl
import re


def parse(text: str):
    # translation_string = text[text.find('={map:{'):text.rfind('}')]
    p = re.compile(r'{map:{.*?}')
    translation_string = p.search(text)
    if translation_string:
        print(f'Найдено({len(translation_string.group())}): {translation_string.group()}')
    else:
        print(f'Не найдено')
    dict_string = translation_string.group().replace('{map:{', '')
    print(len(dict_string), dict_string)


def read_from_file(file="data/app.fc4d0722.js"):
    with open(file) as f:
        # print(f.read())
        return f.read()


def main():
    # data = pd.read_excel('data/olta.xlsx')
    # # pprint(data["Телефон"])
    # chars_to_remove = [' ', '-', '‑', '(', ')', '+']
    # tel_series = pd.Series
    # tel_list = list()
    # for i, tel in enumerate(data["Телефон"]):
    #     tel_formatted = (str(tel).strip() + '.')[:-1]
    #     for char in chars_to_remove:
    #         tel_formatted = tel_formatted.replace(char, "")
    #     if len(tel_formatted) == 10:
    #         tel_formatted = '8' + tel_formatted
    #     if len(tel_formatted) == 11 and tel_formatted[1] == '9':
    #         tel_list.append(tel_formatted)
    #     else:
    #         tel_list.append('')
    #     print(i, tel, tel_formatted, type(tel_formatted))
    # tel_series = tel_list
    # data["tel"] = tel_series
    # print(data['tel'].head())
    # data.to_excel("olta_formatted.xlsx", sheet_name="Лист1")
    # # print(f'\nКоличество номеров: {data["Телефон"].size}')
    src_text = read_from_file()
    if src_text:
        parse(src_text)



if __name__ == "__main__":
    main()