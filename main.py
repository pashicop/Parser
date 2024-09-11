from pprint import pprint

import pandas as pd
import openpyxl


def main():
    data = pd.read_excel('data/olta.xlsx')
    # pprint(data["Телефон"])
    chars_to_remove = [' ', '-', '‑', '(', ')', '+']
    tel_series = pd.Series
    tel_list = list()
    for i, tel in enumerate(data["Телефон"]):
        tel_formatted = (str(tel).strip() + '.')[:-1]
        for char in chars_to_remove:
            tel_formatted = tel_formatted.replace(char, "")
        if len(tel_formatted) == 10:
            tel_formatted = '8' + tel_formatted
        if len(tel_formatted) == 11 and tel_formatted[1] == '9':
            tel_list.append(tel_formatted)
        else:
            tel_list.append('')
        print(i, tel, tel_formatted, type(tel_formatted))
    tel_series = tel_list
    data["tel"] = tel_series
    print(data['tel'].head())
    data.to_excel("olta_formatted.xlsx", sheet_name="Лист1")
    # print(f'\nКоличество номеров: {data["Телефон"].size}')



if __name__ == "__main__":
    main()