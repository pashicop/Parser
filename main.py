import shutil
from copy import deepcopy
from pprint import pprint
from collections import defaultdict
import pandas as pd
import openpyxl
import re
import ast
import os
import PySimpleGUI as sg
import subprocess


VERSION = 1.0


def m_window():
    col1 = sg.Column([[sg.Frame('Чтение файла перевода',
                                [[sg.T('* По умолчанию поиск идёт в папке data')],
                                 [sg.T('Выберите файл'),
                                  sg.Input(disabled=True,
                                           enable_events=True,
                                           key='-IN-',
                                           disabled_readonly_background_color='gray'),
                                  sg.FileBrowse('Открыть',
                                                initial_folder=os.path.join('.', 'data'),
                                                enable_events=True,
                                                file_types=(('Файл перевода Шторм', '.js'),),
                                                key='-IN-FB-', ),
                                  ]],
                                p=(5, (5, 20)))],
                      [sg.Frame('Изменение файла перевода',
                                [[sg.T('* Открывает сгенерированный файл Шторм.xslx в стандартном редакторе')],
                                 [sg.Button('Открыть файл',
                                            key='-Open-',
                                            disabled=True,
                                            enable_events=True,
                                            disabled_button_color='dark gray'), ]],
                                expand_x=True,
                                p=(5, (5, 20))), ],
                      [sg.Frame('Запись файла перевода',
                                [[sg.T('Выберите файл'),
                                  sg.Input(disabled=True,
                                           enable_events=True,
                                           key='-WR-IN-',
                                           disabled_readonly_background_color='gray'),
                                  sg.FileBrowse('Открыть',
                                                initial_folder=os.getcwd(),
                                                enable_events=True,
                                                key='-WR-FB-', ),
                                  ]],
                                p=(5, (5, 20)))]],
                     vertical_alignment='top')
    col2 = sg.Column([[sg.Multiline(key='-OUT-',
                                    size=(81, 20),
                                    autoscroll=True,
                                    disabled=True,
                                    reroute_stdout=True, )],])
    layout = [[col1, sg.VSep(), col2]]
    window = sg.Window('Перевод Шторм вер.' + str(VERSION), layout)
    return window


def format_string(string, p):
    f_string = string[len(p):]
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
    found_blocks_en = []
    found_blocks_ru = []
    for patt, value in patterns.items():
        pattern = patt + ':'
        reg_exp = re.escape(pattern) + r'{.*?}'
        pattern_re = re.compile(reg_exp)
        translation_string = pattern_re.findall(text)
        if not translation_string:
            print(f'Не найдено')
        else:
            # print(f'Найдено({len(translation_string)}): {translation_string}')
            dict_en, dict_ru = dict(), dict()
            for t_str in translation_string:
                formatted_string = format_string(t_str, pattern)
                translation_dict = ast.literal_eval(formatted_string)
                if translation_dict[value[0]] == value[1]:
                    dict_en = deepcopy(translation_dict)
                    print(f'Найден блок {pattern} - en')
                    found_blocks_en.append(pattern)
                elif has_cyrillic(translation_dict[value[0]]):
                    dict_ru = deepcopy(translation_dict)
                    print(f'Найден блок {pattern} - ru')
                    found_blocks_ru.append(pattern)
            if dict_ru:
                if dict_en:
                    dd = defaultdict(list)
                    dd[pattern] = ['', '', '']
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
                    data = pd.DataFrame.from_dict(dict(dd), orient='index', columns=['EN', 'RU', 'Исправленный перевод писать в этом столбце'])
                    data.to_excel(os.path.join('original', "Шторм_original.xlsx"), sheet_name=sheet_name)
                    data.to_excel("Шторм.xlsx", sheet_name=sheet_name)
                    i = False
                else:
                    data = pd.DataFrame.from_dict(dict(dd), orient='index', columns=['', '', ''])
                    with pd.ExcelWriter(os.path.join('original', "Шторм_original.xlsx"),
                                        mode='a',
                                        if_sheet_exists='overlay') as writer:
                        data.to_excel(writer, sheet_name=sheet_name, startrow=depth)
                    with pd.ExcelWriter('Шторм.xlsx', mode='a', if_sheet_exists='overlay') as writer:
                        data.to_excel(writer, sheet_name=sheet_name, startrow=depth)
                depth += len(dd) + 2
    return found_blocks_en, found_blocks_ru


def read_from_file(file=os.path.join('data', 'app.fc4d0722.js')):
    with open(file, encoding='utf-8') as f:
        # print(f.read())
        shutil.copy(file, os.path.join('out', 'app.fc4d0722.js'))
        return f.read()


def write_js(f_read=os.path.join('Шторм.xlsx'), f_write=os.path.join('out', 'app.fc4d0722.js')):
    df = pd.read_excel(f_read)
    # print(df)
    df = df.replace({float('nan'): None})
    data = df.to_dict('records')
    with open(f_write, mode='r', encoding='utf-8') as f:
        file_js = f.read()
        is_changed = False
        for record in data:
            if record['Исправленный перевод писать в этом столбце']:
                is_changed = True
                file_js = file_js.replace(record['RU'], record['Исправленный перевод писать в этом столбце'])
                print(f"Изменена переменная '{record['Unnamed: 0']}' с '{record['RU']}' на '{record['Исправленный перевод писать в этом столбце']}'")
    with open(f_write, mode='w', encoding='utf-8') as f:
        print('=' * 80)
        if is_changed:
            f.write(file_js)
            print('Записано в файл js успешно')
        else:
            print('Не найдено изменений!')
        print('=' * 80 + '\n')


    # print(data)


def main():
    # term_size = os.get_terminal_size()
    main_window = m_window()
    while True:
        event, values = main_window.Read()
        if event in (None, 'Exit'):
            break
        elif event == '-IN-':
            try:
                main_window['-Open-'].Update(disabled=False)
                src_text = read_from_file(values['-IN-'])
                if src_text:
                    en_blocks, ru_blocks = parse(src_text)
                    print('=' * 80)
                    print(f'Найдено {len(en_blocks)} модулей -', *en_blocks, f' на англ. языке', sep=' '  )
                    print(f'Найдено {len(ru_blocks)} модулей -', *ru_blocks, f' на русском языке', sep=' '  )
                    print('Записано в файл Шторм.xlsx успешно')
                    print('=' * 80 + '\n')
            except Exception as e:
                print(f'{e}')
        elif event == '-Open-':
            # os.open(os.path.join(os.getcwd(), 'Шторм.xlsx'), os.O_RDWR)
            command = 'open'
            path =  os.path.join(os.getcwd(), 'Шторм.xlsx')
            subprocess.Popen([command, path])
        elif event == '-WR-IN-':
            try:
                write_js(values['-WR-IN-'])
            except Exception as e:
                print(f'{e}')
        else:
            print(event, values)
    # while True:
    #     print('Что вы хотите сделать?\n1. Считать файл js и записать в Шторм.xlsx?\n'
    #           '2. Записать данные из Шторм.xslx в файл js?\n'
    #           '3. Выйти')
    #     task = input('Введите число: ')
    #     if task == '1':
    #         try:
    #             src_text = read_from_file()
    #             if src_text:
    #                 parse(src_text)
    #                 print('=' * 80)
    #                 print('Считано и записано в файл xlsx успешно')
    #                 print('=' * 80 + '\n')
    #         except Exception as e:
    #             print(f'{e}')
    #     elif task == '2':
    #         try:
    #             print('=' * 80)
    #             print('Записано в файл js успешно')
    #             print('=' * 80 + '\n')
    #         except Exception as e:
    #             print(f'{e}')
    #     elif task == '3':
    #         print('=' * 80)
    #         print('Выход из программы')
    #         print('=' * 80 + '\n')
    #         break


if __name__ == "__main__":
    main()