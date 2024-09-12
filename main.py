from pprint import pprint

import pandas as pd
import openpyxl
import re
import ast


def format_string(string, p):
    f_string = string.replace(p, '')
    key_pattern = r'(\w+):'
    p_regex = re.compile(key_pattern)
    keys = re.findall(p_regex, f_string)
    print(keys)
    f_string = re.sub(p_regex, r'"\1":', f_string)
    print(f_string)
    return f_string


def parse(text: str, lang:'en'):
    # translation_string = text[text.find('={map:{'):text.rfind('}')]
    if lang == 'en':
        pattern = '{map:'
        reg_exp = r'{map:{.*?}'
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

        data = pd.DataFrame.from_dict(dict_from_str, orient='index')
        data.to_excel("Шторм.xlsx", sheet_name="Лист1")


if __name__ == "__main__":
    main()