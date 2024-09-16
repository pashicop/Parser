from copy import deepcopy
from pprint import pprint
from collections import defaultdict
import pandas as pd
import openpyxl
import re
import ast
import os


def format_string(string, p):
    f_string = string[len(p):]
    if p == 'msg:' or p == 'set:':
        # print(f_string)
        del_part = r'\w+?(: )'
        del_regex = re.compile(del_part)
        f_string = re.sub(del_regex, r'- ', f_string)
        # print(f_string)
    key_pattern = r'(\w+):'
    p_regex = re.compile(key_pattern)
    keys = re.findall(p_regex, f_string)
    # print(len(keys), keys)
    f_string = re.sub(p_regex, r'"\1":', f_string)
    # print(f_string)
    return f_string


def has_cyrillic(text):
    return bool(re.search('[а-яА-Я]', text))


# def has_latin(text):
#     result = False
#     for char in text:
#         if char.lower() in ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',' ','!','?']:
#             result = True
#         else:
#             return False
#     return result


def parse(text: str):
    patterns = {'map': ["nameCannotNull",'Please enter the complete name'],
                'window': ["savedSuccessfully", "Saved successfully"],
                'msg': ["ring_one", "ring one"],
                'set': ["setWifiConfigFailed", "Failed to set Wi-Fi configuration"],
                'record': ["startRelay", "Action Module"],
                'playback': ["playback", "Data Playback"],
                'analyze': ["timeSelect", "Time selection"],
                'spectrum': ["spectrumInit", "Device initializing"]}
    i = True
    depth = 0
    for patt, value in patterns.items():
        pattern = patt + ':'
        reg_exp = re.escape(pattern) + r'{.*?}'
        pattern_re = re.compile(reg_exp)
        translation_string = pattern_re.findall(text)
        if not translation_string:
            print(f'Не найдено')
        else:
            # print(f'Найдено({len(translation_string)}): {translation_string}')
            for t_str in translation_string:
                formatted_string = format_string(t_str, pattern)
                translation_dict = ast.literal_eval(formatted_string)
                if translation_dict[value[0]] == value[1]:
                    dict_en = deepcopy(translation_dict)
                    print(f'Найден блок {pattern} - en')
                elif has_cyrillic(translation_dict[value[0]]):
                    dict_ru = deepcopy(translation_dict)
                    print(f'Найден блок {pattern} - ru')
            if dict_ru:
                if dict_en:
                    dd = defaultdict(list)
                    dd[pattern] = ['', '']
                    # list_dict_en_keys = list(dict_en.keys())
                    list_dict_ru_keys = list(dict_ru.keys())
                    for key in list(dict_en.keys()):
                        dd[key].append(dict_en[key])
                        if key in list_dict_ru_keys:
                            dd[key].append(dict_ru[key])
                    for key in list(dict_ru.keys()):
                        if key not in list(dd.keys()):
                            dd[key] = ['', dict_ru[key]]
                    # print(dd)
                sheet_name = "Лист1"
                if i:
                    data = pd.DataFrame.from_dict(dict(dd), orient='index', columns=['EN', 'RU'])
                    data.to_excel("Шторм.xlsx", sheet_name=sheet_name)
                    i = False
                else:
                    data = pd.DataFrame.from_dict(dict(dd), orient='index', columns=['', ''])
                    with pd.ExcelWriter('Шторм.xlsx', mode='a', if_sheet_exists='overlay') as writer:
                        data.to_excel(writer, sheet_name=sheet_name, startrow=(depth))
                depth += len(dd) + 2
            # print(type(translation_dict), len(translation_dict), translation_dict)


def read_from_file(file=os.path.join('data', 'app.fc4d0722.js')):
    with open(file, encoding='utf-8') as f:
        # print(f.read())
        return f.read()


def main():
    # term_size = os.get_terminal_size()
    while True:
        print('Что вы хотите сделать?\n1. Считать файл js и записать в Шторм.xlsx?\n'
              '2. Записать данные из Шторм.xslx в файл js?\n'
              '3. Выйти')
        task = input('Введите число: ')
        if task == '1':
            try:
                src_text = read_from_file()
                if src_text:
                    parse(src_text)
                    print('=' * 80)
                    print('Считано и записано в файл xlsx успешно')
                    print('=' * 80 + '\n')
            except Exception as e:
                print(f'{e}')
        elif task == '2':
            try:
                print('=' * 80)
                print('Записано в файл js успешно')
                print('=' * 80 + '\n')
            except Exception as e:
                print(f'{e}')
        elif task == '3':
            print('=' * 80)
            print('Выход из программы')
            print('=' * 80 + '\n')
            break


if __name__ == "__main__":
    main()