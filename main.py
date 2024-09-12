from copy import deepcopy
from pprint import pprint
from collections import defaultdict
import pandas as pd
import openpyxl
import re
import ast


def format_string(string, p):
    f_string = string.replace(p, '')
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


def parse(text: str, lang:'en'):
    # translation_string = text[text.find('={map:{'):text.rfind('}')]
    if lang == 'en':
        pattern = '{map:'
        reg_exp = r'{map:{.*?}'
        pattern_re = re.compile(reg_exp)
        translation_string = pattern_re.findall(text)
        if not translation_string:
            print(f'Не найдено')
        else:
            print(f'Найдено({len(translation_string)}): {translation_string}')
            for t_str in translation_string:
                formatted_string = format_string(t_str, pattern)
                translation_dict = eval(formatted_string)
                if translation_dict['nameCannotNull'] == 'Please enter the complete name':
                    dict_en = deepcopy(translation_dict)
                    # dict_en = {"a": 12, "b": "bbb", "c": "ccc", "d": "ddd",}
                elif has_cyrillic(translation_dict['nameCannotNull']):
                    dict_ru = deepcopy(translation_dict)
                    # dict_ru = {"a": 13, "b": "ЫВАВАЫВВ", "d": "ываыва", "e": "ЫВАВЫАААА"}
            if dict_ru:
                if dict_en:
                    dd = defaultdict(list)
                    list_dict_en_keys = list(dict_en.keys())
                    list_dict_ru_keys = list(dict_ru.keys())
                    for key in list(dict_en.keys()):
                        dd[key].append(dict_en[key])
                        if key in list_dict_ru_keys:
                            dd[key].append(dict_ru[key])
                    for key in list(dict_ru.keys()):
                        if key not in list(dd.keys()):
                            dd[key] = ['', dict_ru[key]]
                    # for key in set(list(dict_ru.keys()) + list(dict_en.keys())):
                    #     if key in dict_en:
                    #         dd[key].append(dict_en[key])
                    #     if key in dict_ru:
                    #         dd[key].append(dict_ru[key])
                    print(dd)
                    # data_en = pd.DataFrame.from_dict(dict_en, orient='index')
                    # data_ru = pd.DataFrame.from_dict(dict_ru, orient='index')
                sheet_name = "Лист1"
                data = pd.DataFrame.from_dict(dict(dd), orient='index', columns=['EN', 'RU'])
                data.to_excel("Шторм.xlsx", sheet_name=sheet_name)
                # else:
                #     with pd.ExcelWriter('Шторм.xlsx', mode='a', if_sheet_exists='overlay') as writer:
                #         data.to_excel(writer, sheet_name=sheet_name, startcol=(i + 1), index=False)
            print(type(translation_dict), len(translation_dict), translation_dict)
            return translation_dict
    elif lang == 'ru':
        pattern = '{map:'
        # reg_exp = r'{map:{.*:"[А-я]*?}'
        reg_exp = r'{map:{.*?:"[А-я]+?".*?}'
        pattern_re = re.compile(reg_exp)
        translation_string = pattern_re.search(text)
        if not translation_string:
            print(f'Не найдено')
        else:
            print(f'Найдено({len(translation_string.group())}): {translation_string.group()}')
            formatted_string = format_string(translation_string.group(), pattern)
            translation_dict = eval(formatted_string)
            print(type(translation_dict), len(translation_dict), translation_dict)
            return translation_dict

def read_from_file(file="data/app.fc4d0722.js"):
    with open(file) as f:
        # print(f.read())
        return f.read()


def main():
    src_text = read_from_file()
    if src_text:
        # dict_from_str = parse(src_text, 'ru')
        dict_from_str = parse(src_text, 'en')

        # data = pd.DataFrame.from_dict(dict_from_str, orient='index')
        # data.to_excel("Шторм.xlsx", sheet_name="Лист1")


if __name__ == "__main__":
    main()