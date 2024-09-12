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
    print(len(keys), keys)
    f_string = re.sub(p_regex, r'"\1":', f_string)
    print(f_string)
    return f_string


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
            for i, t_str in enumerate(translation_string):
                # sheet_name = "Лист" + str(i + 1)
                sheet_name = "Лист1"
                formatted_string = format_string(t_str, pattern)
                translation_dict = eval(formatted_string)
                data = pd.DataFrame.from_dict(translation_dict, orient='index')
                if i == 0:
                    data.to_excel("Шторм.xlsx", sheet_name=sheet_name)
                else:
                    with pd.ExcelWriter('Шторм.xlsx', mode='a', if_sheet_exists='overlay') as writer:
                        data.to_excel(writer, sheet_name=sheet_name, startcol=(i + 1), index=False)
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