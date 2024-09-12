from copy import deepcopy
from pprint import pprint
from collections import defaultdict
import pandas as pd
import openpyxl
import re
import ast


def format_string(string, p):
    f_string = string.replace(p, '')
    if p == 'msg:':
        print(f_string)
        f_string = f_string.replace('unit: meter', "unit - meter")
        f_string = f_string.replace('单位:', "单位-")
        f_string = f_string.replace('единица измерения: метр', "единица измерения - метр")
        f_string = f_string.replace('الوحدة:', "الوحدة-")
        f_string = f_string.replace('unité:', "unité-")
        f_string = f_string.replace('unidad:', "unidad-")
        print(f_string)
    key_pattern = r'(\w+):'
    p_regex = re.compile(key_pattern)
    keys = re.findall(p_regex, f_string)
    print(len(keys), keys)
    f_string = re.sub(p_regex, r'"\1":', f_string)
    print(f_string)
    return f_string


def has_cyrillic(text):
    return bool(re.search('[а-яА-Я]', text))


def has_latin(text):
    result = False
    for char in text:
        if char.lower() in ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',' ','!','?']:
            result = True
        else:
            return False
    return result


def parse(text: str):
    # translation_string = text[text.find('={map:{'):text.rfind('}')]
    # pattern = 'window:'
    # reg_exp = r'window:{.*?}'
    patterns = {'map': ["nameCannotNull",'Please enter the complete name'],
                'window': ["savedSuccessfully", "Saved successfully"],
                'msg': ["ring_one", "ring one"],
                'set': ["ssid", "matching rule"]}
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
            print(f'Найдено({len(translation_string)}): {translation_string}')
            for t_str in translation_string:
                formatted_string = format_string(t_str, pattern)
                # translation_dict = eval(formatted_string)
                translation_dict = ast.literal_eval(formatted_string)
                if translation_dict[value[0]] == value[1]:
                    dict_en = deepcopy(translation_dict)
                    # dict_en = {"a": 12, "b": "bbb", "c": "ccc", "d": "ddd",}
                elif has_cyrillic(translation_dict[value[0]]):
                    dict_ru = deepcopy(translation_dict)
                    # dict_ru = {"a": 13, "b": "ЫВАВАЫВВ", "d": "ываыва", "e": "ЫВАВЫАААА"}
            if dict_ru:
                if dict_en:
                    dd = defaultdict(list)
                    dd[pattern] = ['', '']
                    list_dict_en_keys = list(dict_en.keys())
                    list_dict_ru_keys = list(dict_ru.keys())
                    for key in list(dict_en.keys()):
                        dd[key].append(dict_en[key])
                        if key in list_dict_ru_keys:
                            dd[key].append(dict_ru[key])
                    for key in list(dict_ru.keys()):
                        if key not in list(dd.keys()):
                            dd[key] = ['', dict_ru[key]]
                    print(dd)
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


def read_from_file(file="data/app.fc4d0722.js"):
    with open(file) as f:
        # print(f.read())
        return f.read()


def main():
    src_text = read_from_file()
    if src_text:
        # dict_from_str = parse(src_text, 'ru')
        parse(src_text)

        # data = pd.DataFrame.from_dict(dict_from_str, orient='index')
        # data.to_excel("Шторм.xlsx", sheet_name="Лист1")


if __name__ == "__main__":
    main()