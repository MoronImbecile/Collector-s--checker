import json
import re
from scrapy.utils.project import get_project_settings


def validate_args(spider_name, args, args_spec_path):
    sel = 'args'    # выбор валидации аргументов из args_spec_path по умолчанию
    # проверка на то, является ли проходящий валидацию объект настройками, то есть файлом 'settings.py'
    if args == get_project_settings():
        sel = 'settings'    # выбор валидации настроек из args_spec_path
    newargset = json.load(open(args_spec_path))    # открытие и преобразование в dict type файл 'args_and_settings.json'
    newargset = newargset[spider_name][sel]
    data = []    # массив для записи пар имя-значение
    for key in range(len(newargset)):
        name = newargset[key]['name']    # имя объекта
        typ = newargset[key]['type']    # тип
        default = newargset[key]['default']    # значение по умолчанию
        required = newargset[key]['required']    # необходимость
        noerror = True    # переменная для определения наличия ошибок
        value = args[name]    # полученное значение объекта
        # проверки типа и формата
        if typ == 'int':    # тип значения — int
            try:
                value = int(value)    # проверка на допустимость через try
            except Exception:
                # в случае любых прерываний программ, ошибок (кроме KeyboardInterrupt и SystemExit) переменая наличия ошибки меняется на False, и впоследствии определяет возможность записи значения
                noerror = False
                print('ValueError')
        elif typ == 'float':    # тип значения — float
            try:
                value = float(value)    # проверка на допустимость
            except Exception:
                noerror = False
                print('ValueError')
        elif typ == 'string':
            try:
                value = str(value)    # проверка на допустимость
            except Exception:
                noerror = False
                print('ValueError')
        elif typ == 'boolean':    # тип значения — boolean
            try:
                value = bool(value)    # проверка на допустимость
            except Exception:
                noerror = False
                print('ValueError')
        # тип значения — date, также здесь находится проверка на допустимость значения через re.fullmatch
        elif typ == 'date' and re.fullmatch('(19[89]\d|20\d\d)-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]) (0\d|1\d|2[0-3]):([0-5]\d):([0-5]\d)', value) == None:
            noerror = False
            print('ValueError')
        elif typ == 'array':    # тип значения — array
            try:
                value = json.loads(value)    # проверка на принадлежность к JSON
                print(value)
                if str(type(value)) != "<class 'list'>":    # проверка на принадлежность к JSON-array
                    noerror = False
                    print('ValueError')
            except Exception:
                # в случае, если это не JSON-array, происходит образование обычного строчного массива
                sep = ','
                # определение разделителя: '\n' (правда, вроде бы, в использованном мной input() нельзя реализовать переход на другую строку) или ','
                if value.find('\n') != -1:
                    sep = '\n'
                value = value.split(sep)    # преобразование строки в массив через разделители
        elif typ == 'object':    # тип значения — JSON-object
            try:
                value = json.loads(value)    # проверка на допустимость
            except Exception:
                noerror = False
                print('ValueError')
        # проверка на присутствие ошибок или недопустимости значений, а также необязательности значений
        if noerror or not required:
            # проверка на необходимость значения, на недопустимость введенного и наличия значения по умолчанию,
            # сделанная для определения надобности использования значения по умолчанию
            if not noerror and default != None:
                value = default    # присваивание значения по умолчанию
                noerror = True    # обновления значения наличия ошибки
            # вспомогательный массив для создания матрицы, где элементы представляют собой пару имя-значение
            auxdata = []
            auxdata.append(name)    # запись введенного имени объекта в новый массив
            if noerror:    # дополнительная проверка допустимости value в случае отсутствия default
                auxdata.append(value)    # запись значения
            else:
                print("The value isn't allowed or missed")
                raise ValueError    # выбрасывание ошибки при отсутствии default
            data.append(auxdata)    # запись в основную матрицу
        else:    # проверка на необходимость в случае, если value не определено и не записано
            print("The required value has been missed")
            raise ValueError    # выбрасывание ошибки в данной ситуации
    return dict(data)    # окончательное возвращение словаря с введенными парами имя-значение


def validate_settings(spider_name, sets_spec_path):
    return validate_args(spider_name, get_project_settings(), sets_spec_path)    # взятие за args файл setting.py
