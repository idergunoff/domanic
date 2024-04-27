import random
import os

from PyQt5.QtWidgets import QTableWidgetItem, QFileDialog, QCheckBox, QColorDialog, QListWidgetItem, QLabel, QMessageBox
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtCore import Qt

from sqlalchemy import text, desc, literal_column
from pandas import read_excel
import pyqtgraph as pg
from scipy.stats import describe, gmean, gaussian_kde, pearsonr
from numpy import median, float64
from collections import Counter
from statistics import mean
import pandas as pd
import lasio as ls
import math
import json
import datetime
import pickle
from tqdm import tqdm

import traceback
import matplotlib.pyplot as plt
from matplotlib.backends import backend_ps
from matplotlib.gridspec import GridSpec
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import seaborn as sns

from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.decomposition import PCA
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import ElasticNet, Lasso, LinearRegression
from sklearn.manifold import TSNE
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.neighbors import KNeighborsRegressor, LocalOutlierFactor, NearestNeighbors
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.pipeline import Pipeline


from platypus import NSGAII, NSGAIII, OMOPSO, GDE3, Problem, Real

from qt.add_area_dialog import *
from qt.add_region_dialog import *
from qt.add_well_dialog import *
from qt.add_class_limit import *
from qt.add_class_lda import *
from qt.edit_user_interval import *
from qt.compare_table_dialog import *
from qt.regression_form import *
from qt.lof_form import *
from qt.comment_form import *
from qt.choose_calculated_data import *

from objects import *

import numpy as np
from sqlalchemy.exc import IntegrityError

# Сброс ограничений на количество выводимых рядов
# pd.set_option('display.max_rows', None)

# Сброс ограничений на число столбцов
# pd.set_option('display.max_columns', None)

# Сброс ограничений на количество символов в записи
# pd.set_option('display.max_colwidth', None)


def clear_table(table):
    row_count = table.rowCount()            # очистка таблицы
    for i in range(row_count + 1):          # удаление циклом
        table.removeRow(row_count - i)      # всех строк


def update_spinbox(start, stop):
    """Обновляет макс-мин зависимых спинбоксов"""
    start.setMaximum(stop.value())
    stop.setMinimum(start.value())


def update_interval():
    update_spinbox(ui.doubleSpinBox_start, ui.doubleSpinBox_stop)
    calc_stat()


def check_start_stop():
    start = ui.doubleSpinBox_start.value()
    stop = ui.doubleSpinBox_stop.value()
    return start, stop


# def read_las_info(file_name):
#     """Считывает информацию из las-файла"""
#     with open(file_name) as f:
#         n = 0
#         while n < 1000:
#             n += 1
#             line = f.readline()
#             if line.strip().startswith('VERS.'):
#                 version = line.split(':')[0].split()[1]
#             if line.strip().startswith('STRT.M'):
#                 start_depth = float(line.split(':')[0].split()[1])
#             if line.strip().startswith('STOP.M'):
#                 stop_depth = float(line.split(':')[0].split()[1])
#             if line.strip().startswith('NULL.'):
#                 null_value = line.split(':')[0].split()[1]
#             if line.strip().startswith('~A'):
#                 param = line.split()
#                 data_row = n
#                 break
#         if version == '2.0':
#             with open(file_name) as f:
#                 n = 0
#                 while n < 1000:
#                     n += 1
#                     line = f.readline()
#                     if line.strip().startswith('#CURVE'):
#                         param = line.split(':')[0].split()[1]
#         if type(param) is list:
#             if '~A' in param:
#                 # todo убрать костыль, не везде есть Log
#                 try:
#                     param.remove('~A')
#                     param.remove('Log')
#                 except:
#                     pass
#         return version, start_depth, stop_depth, null_value, param, data_row


def get_well_id():
    """ Получаем id выбранной в комбобоксах (выпадающий список) скважины"""
    if ui.comboBox_region.currentText() and ui.comboBox_area.currentText() and ui.comboBox_well.currentText():
        return session.query(Well.id).join(Area).join(Region).filter(Region.title == ui.comboBox_region.currentText(),
                                                                 Area.title == ui.comboBox_area.currentText(),
                                                                 Well.title == ui.comboBox_well.currentText())[0][0]


def add_slots(start, stop):
    """Добавить ряды в таблицу DataLas"""
    w_id = get_well_id()
    ui.progressBar.setMaximum(int((stop - start)*10))
    ui.label_info.setText('Обновление базы данных. Это может занять некоторое время...')
    ui.label_info.setStyleSheet('color: blue')
    add_rows = 0
    #   получаем глубины по выбранной скважине
    #   -> список кортежей преобразуем в список списков "map"
    #   -> складываем в один список "sum"
    well_depths = sum(list(map(list, session.query(DataLas.depth).filter(DataLas.well_id == w_id).all())), [])
    for n, i in enumerate(range(int(start * 10), int((stop + 0.1) * 10))):
        if not i / 10 in well_depths:
            new_depth = DataLas(depth=i / 10, well_id=w_id)
            session.add(new_depth)
            add_rows += 1
        ui.progressBar.setValue(n)
    session.commit()
    ui.label_info.setText(f'Добавлно {add_rows} ячеек.')
    ui.label_info.setStyleSheet('color: green')


def load_param_from_las(param, null, file_name, row, index_list, well_id):
    """
    Загрузка параметра из las-файла
    :param param: название параметра из БД
    :param null: нулевые значения в LAS (9999.9)
    :param file_name: имя las-файла
    :param row: номер строки начала данных
    :param index_list: индекс параметра в списке параметров
    :param well_id: id скважины
    :return: True - если входит в список параметров БД, False - если не входит
    """
    list_columns = DataLas.__table__.columns.keys()

    if param in list_columns:
        print(f'Загрузка параметра "{param}".')
        ui.label_info.setText(f'Загрузка параметра "{param}".')
        ui.label_info.setStyleSheet('color: blue')
        with open(file_name) as f:
            ui.progressBar.setMaximum(len(f.readlines()))
        with open(file_name) as f:
            n = 0
            while True:
                line = f.readline()
                if not line:
                    break
                if n > row:
                    try:
                        if line.split()[index_list+1] != null:
                            session.query(DataLas).filter(DataLas.well_id == well_id, DataLas.depth == line.split()[0]).update(
                            {param: line.split()[index_list+1]}, synchronize_session="fetch")
                    except IndexError:
                        ui.label_info.setText(f'Внимание! Ошибка загрузки данных. Проверьте LAS-файл.')
                        ui.label_info.setStyleSheet('color: red')
                        return False
                n += 1
                ui.progressBar.setValue(n)
        return True
    else:
        return False


# Функция для удаления всех пробелов из строки и преобразования во float
def remove_spaces_and_convert_to_float(x):
    if isinstance(x, str):  # Проверяем, является ли x строкой
        x = x.replace(" ", "")  # Удаляем все пробелы из строки
        try:
            return float(x)  # Преобразуем во float
        except ValueError:
            return x  # Если не удалось преобразовать, оставляем как есть
    else:
        return x  # Возвращаем x без изменений, если не является строкой


def load_param_pir_chrom(file_name, table, rename_column):
    """
    Загрузка параметров пиролиза и хроматографии
    :param file_name: имя файла с данными
    :param table: Таблица в которую загружаются данные
    :param rename_column: Bool При загрузке хроматографии столбца переименовываются, при загрузке пиролиза - нет
    :return:
    """
    w_id = get_well_id()
    data_tab = read_excel(file_name, header=0)
    data_tab.dropna(how='all', inplace=True)
    data_tab = data_tab.applymap(remove_spaces_and_convert_to_float)
    if rename_column:
        dict_col = {}
        for i in data_tab.columns:
            dict_col[i] = rename_columns(i)
        data_tab = data_tab.rename(columns=dict_col)
    for i in data_tab['n_obr']:
        if session.query(table.name).filter(table.well_id == w_id,
                                                   table.name == replace_letter_of_name(str(i))).count() == 0:
            new_sample = table(name=replace_letter_of_name(str(i)), well_id=w_id)
            session.add(new_sample)
    list_columns = table.__table__.columns.keys()  # список параметров таблицы
    [list_columns.remove(i) for i in ['id', 'well_id', 'name']]  # удаляем не нужные колонки
    ui.progressBar.setMaximum(len(data_tab.columns))
    val_str = False # флаг строчных значений в таблице
    for n, i in enumerate(data_tab.columns):
        if i in list_columns:
            ui.label_info.setText(f'Загрузка параметра "{i}"...')
            ui.label_info.setStyleSheet('color: blue')
            for j in data_tab.index:
                if type(data_tab[i][j]) is not str:
                    session.query(table).filter(table.name == replace_letter_of_name(str(data_tab['n_obr'][j])),
                                                   table.well_id == w_id).update({i: round(data_tab[i][j], 5)},
                                                                                        synchronize_session="fetch")
                else:
                    val_str = True
        ui.progressBar.setValue(n+1)
    session.commit()
    if val_str:
        ui.label_info.setText('Готово. Внимание! В таблице содержались строчные значения. Такие данные не закгружены.')
        ui.label_info.setStyleSheet('color: orange')
    else:
        ui.label_info.setText('Готово. Загруженные параметры отображаются в "списке загруженных параметров".')
        ui.label_info.setStyleSheet('color: green')


def load_depth_name_param(file_name, w_id, table):
    """    Привязка глубины к образцам      """
    data_tab = read_excel(file_name, header=0)
    for i in data_tab.index:
        session.query(table).filter(table.well_id == w_id, table.name == replace_letter_of_name(str(data_tab['n_obr'][i]))).\
            update({'depth': round(data_tab['depth'][i], 2)}, synchronize_session="fetch")
    session.commit()


def check_list_param():
    """Проверка загруженных параметров по id выбранной скважинвы и внесение их в список"""
    ui.listWidget_pir_kern.clear()
    ui.listWidget_pir_extr.clear()
    ui.listWidget_chrom_extr.clear()
    ui.listWidget_chrom_kern.clear()
    ui.listWidget_las.clear()
    ui.listWidget_lit.clear()
    w_id = get_well_id()
    check_null_param(ui.listWidget_pir_kern, DataPirolizKern, True, w_id)
    check_null_param(ui.listWidget_pir_extr, DataPirolizExtr, True, w_id)
    check_null_param(ui.listWidget_chrom_extr, DataChromExtr, True, w_id)
    check_null_param(ui.listWidget_chrom_kern, DataChromKern, True, w_id)
    check_null_param(ui.listWidget_lit, DataLit, True, w_id)
    check_null_param(ui.listWidget_las, DataLas, False, w_id)


def check_null_param(listwidget, data_tab, name, w_id):
    """    Выбор загруженных параметров и отображение в соответствующем виджете списка """
    list_columns = data_tab.__table__.columns.keys()  # список параметров таблицы
    [list_columns.remove(i) for i in ['id', 'depth', 'well_id']]  # удаляем не нужные колонки
    if name:
        list_columns.remove('name')
    for i in list_columns:
        if session.query(data_tab.depth).filter(text(f"well_id=:w_id and {i} NOT NULL")).params(w_id=w_id).count() > 0:
            listwidget.addItem(i)


def select_start_stop_depth(w_id, table):
    """ Выбор минимального и максимального значений глубины в таблице """
    stop_depth = session.query(table.depth).filter(table.well_id == w_id).order_by(desc(table.depth)).first()
    start_depth = session.query(table.depth).filter(table.well_id == w_id).order_by(table.depth).first()
    return start_depth, stop_depth


def select_start_stop_depth_param(w_id, table_text, param):
    """ Выбор минимального и максимального значений глубины в таблице по параметру """
    if table_text == 'ML':
        calc_data = session.query(CalculatedData).filter_by(id=w_id).first()
        list_depth = [float(i) for i in json.loads(calc_data.data).keys()]
        start_depth, stop_depth = min(list_depth), max(list_depth)
    else:
        table = get_table(table_text)
        stop_depth = session.query(table.depth).filter(table.well_id == w_id, literal_column(f'{table_text}.{param}') != None).order_by(desc(table.depth)).first()[0]
        start_depth = session.query(table.depth).filter(table.well_id == w_id, literal_column(f'{table_text}.{param}') != None).order_by(table.depth).first()[0]
    return start_depth, stop_depth


def get_min_max_tablet_graph():
    """ Получаем минимум/максимум параметров планшета """
    params_graph_tablet = session.query(DrawGraphTablet).all()
    count_graph = len(params_graph_tablet)
    list_min, list_max = [], []
    for i in range(count_graph):
        p = params_graph_tablet[i]
        if p.param:
            min_depth, max_depth = select_start_stop_depth_param(p.well_id, p.table, p.param)
            list_min.append(min_depth)
            list_max.append(max_depth)
    return min(list_min), max(list_max)


def replace_letter_of_name(name):
    """ Замена кириллицы на английские буквы. Для названий образцов """
    list_old = ['е', 'у', 'о', 'р', 'х', 'а', 'с', 'б', ' ']
    list_new = ['e', 'y', 'o', 'p', 'x', 'a', 'c', 'b', '']
    name_new = name
    for n, i in enumerate(list_old):
        name_new = name_new.replace(i, list_new[n])
    return name_new


def rename_columns(name):
    """ Замены названий столбцов загружаемых таблиц для хроматографии """
    list_old = [' (', ')', '/', '-', '№ образца', 'ОЕР', ' при ', 'CPI ', 'С', ' ']
    list_new = ['_', '', '__', '_', 'n_obr', 'OEP', '_', 'CPI_', 'C', '']
    name_new = name
    for n, i in enumerate(list_old):
        name_new = name_new.replace(i, list_new[n])
    return name_new


def draw_param_table(widget_list, table, table_text):
    """
    Отображение таблицы одного выбранного параметра
    :param widget_list: виджет списка в котором выбран параметр
    :param table: таблица в БД с нужным параметром
    :param table_text: текстовое название таблицы для literal_column
    """
    w_id = get_well_id()
    param = widget_list.currentItem().text()   # выбор выделенного параметра
    clear_table(ui.tableWidget)
    if table == DataLas:        # для las файлов отображается только столбец глубины и значения параметра
        data_table = session.query(table.depth, literal_column(f'{table_text}.{param}')).filter(table.well_id == w_id,
                                  literal_column(f'{table_text}.{param}') != None).order_by(table.depth).all()
        ui.tableWidget.setColumnCount(3)
        ui.tableWidget.setHorizontalHeaderLabels(['depth', param, 'age'])
    else:   # для остальных данных отображается глубина, название образца
        data_table = session.query(table.depth, table.name, literal_column(f'{table_text}.{param}')).\
            filter(table.well_id == w_id, literal_column(f'{table_text}.{param}') != None). \
            order_by(table.depth).all()
        ui.tableWidget.setColumnCount(4)
        ui.tableWidget.setHorizontalHeaderLabels(['depth', 'name', param, 'age'])
    for n, i in enumerate(data_table):
        ui.tableWidget.insertRow(n)
        for k, j in enumerate(i):
            if k == 0:
                j = round(j, 1)
                age = session.query(DataAge.age).filter(DataAge.well_id == w_id, DataAge.depth >= j, DataAge.depth < j + 0.1).first()
                age = '' if age is None else str(age[0])
            if k == 2:
                j = round(j, 5)
            ui.tableWidget.setItem(n, k, QTableWidgetItem(str(j)))
        ui.tableWidget.setItem(n, k + 1, QTableWidgetItem(age))
    ui.tableWidget.verticalHeader().hide()
    ui.tableWidget.resizeColumnsToContents()
    ui.label_table_name.setText(f'{param} скв. {ui.comboBox_well.currentText()}')


def draw_param_graph(widget_list, table, table_text):
    """
    Отображение графика одного выбранного параметра
    :param widget_list: виджет списка в котором выбран параметр
    :param table: таблица в БД с нужным параметром
    :param table_text: текстовое название таблицы для literal_column
    """
    # выключаем пользовательские интервалы
    # for i in range(ui.listWidget_user_int.count()):
    #     item = ui.listWidget_user_int.item(i)
    #     if isinstance(item, QListWidgetItem):
    #         checkbox = ui.listWidget_user_int.itemWidget(item)
    #         if isinstance(checkbox, QCheckBox):
    #             checkbox.setChecked(False)
    # ui.checkBox_choose_all_user_int.setChecked(False)

    w_id = get_well_id()
    try:
        param = widget_list.currentItem().text()
    except AttributeError:
        return
    X = sum(list(map(list, session.query(literal_column(f'{table_text}.{param}')).filter(table.well_id == w_id,
                                  literal_column(f'{table_text}.{param}') != None).order_by(table.depth).all())), [])
    Y = sum(list(map(list, session.query(table.depth).filter(table.well_id == w_id,
                                  literal_column(f'{table_text}.{param}') != None).order_by(table.depth).all())), [])
    ui.graphicsView.clear()
    color = choice_color()
    dash = choice_dash()
    width = choice_width()
    if table == DataLas:    # las файлы отображаются графиком
        try:
            curve = pg.PlotCurveItem(x=X, y=Y, pen=pg.mkPen(color=color, width=width, dash=dash))
        except ValueError:
            ui.label_info.setText(f'По данной скважине нет соответствующих данных.')
            ui.label_info.setStyleSheet('color: red')
            return
    else:   # остальные данные отображаются в виде гистограммы
        try:
            curve = pg.BarGraphItem(x0=0, y=Y, height=0.1, width=X, brush=color, pen=pg.mkPen(color=color, width=0.4))
        except ValueError:
            ui.label_info.setText(f'По данной скважине нет соответствующих данных.')
            ui.label_info.setStyleSheet('color: red')
            return
    try:
        ui.graphicsView.addItem(curve)
        curve.getViewBox().invertY(True)
    except TypeError:
        ui.label_info.setText(f'Внимание! Ошибка. Образцы не привязаны к глубине.')
        ui.label_info.setStyleSheet('color: red')


def check_tabWidjet():
    """ Определение активного виджета и соответствующей ему таблице в БД """
    if ui.tabWidget.currentIndex() == 0:
        if ui.toolBox_pir.currentIndex() == 0:
            Data_table = DataPirolizKern
            Data_table_text = 'data_piroliz_kern'
            widget = ui.listWidget_pir_kern
        elif ui.toolBox_pir.currentIndex() == 1:
            Data_table = DataPirolizExtr
            Data_table_text = 'data_piroliz_extr'
            widget = ui.listWidget_pir_extr
    elif ui.tabWidget.currentIndex() == 1:
        if ui.toolBox_chrom.currentIndex() == 0:
            Data_table = DataChromKern
            Data_table_text = 'data_chrom_kern'
            widget = ui.listWidget_chrom_kern
        elif ui.toolBox_chrom.currentIndex() == 1:
            Data_table = DataChromExtr
            Data_table_text = 'data_chrom_extr'
            widget = ui.listWidget_chrom_extr
    elif ui.tabWidget.currentIndex() == 2:
        Data_table = DataLit
        Data_table_text = 'data_lit'
        widget = ui.listWidget_lit
    elif ui.tabWidget.currentIndex() == 3:
        Data_table = DataLas
        Data_table_text = 'data_las'
        widget = ui.listWidget_las
    return Data_table, Data_table_text, widget


def choice_color_rel():
    """ Выбор цвета """
    return ui.pushButton_rel_color.palette().color(ui.pushButton_rel_color.backgroundRole()).name()


def choice_color():
    return ui.pushButton_color.palette().color(ui.pushButton_color.backgroundRole()).name()


def choice_dash():
    """ Выбор штриха """
    dash = ui.comboBox_dash.currentText()
    if dash == '__________':
        get_dash = [9]
    elif dash == '.................':
        get_dash = [1, 4]
    elif dash == '- - - - - - - - - ':
        get_dash = [6, 6]
    elif dash == '-.-.-.-.-.-.-.-.':
        get_dash = [9, 4, 2, 4]
    else:
        get_dash = [9]
    return get_dash


def get_line_dash(dash):
    """ Получение штриха из строки """
    if dash == '9':
        get_dash = '__________'
    elif dash == '1 4':
        get_dash = '.................'
    elif dash == '6 6':
        get_dash = '- - - - - - - - - '
    elif dash == '9 4 2 4':
        get_dash = '-.-.-.-.-.-.-.-.'
    else:
        get_dash = '__________'
    return get_dash


def get_dash(dash_str: str):
    if dash_str == '9':
        dash = '-'
    elif dash_str == '1 4':
        dash = '--'
    elif dash_str == '6 6':
        dash = ':'
    elif dash_str == '9 4 2 4':
        dash = '-.'
    else:
        dash = '-'
    return dash


def get_marker(dash_str: str):
    if dash_str == '9':
        marker = 'o'
    elif dash_str == '1 4':
        marker = '.'
    elif dash_str == '6 6':
        marker = '<'
    elif dash_str == '9 4 2 4':
        marker = 's'
    else:
        marker = 'o'
    return marker


# def get_hatch(dash_str: str):
#     if dash_str == '9':
#         hatch = ''
#     elif dash_str == '1 4':
#         hatch = '|'
#     elif dash_str == '6 6':
#         hatch = '.'
#     elif dash_str == '9 4 2 4':
#         hatch = 'x'
#     else:
#         hatch = ''
#     return hatch


def choice_width():
    """ Выбор толщины """
    return float(ui.comboBox_width.currentText())


def choice_color_tablet():
    """ Выбор цвета """
    return ui.pushButton_color_tablet.palette().color(ui.pushButton_rel_color.backgroundRole()).name()


def choice_dash_tablet():
    """ Выбор штриха """
    dash = ui.comboBox_dash_tablet.currentText()
    if dash == '__________':
        get_dash = [9]
    elif dash == '.................':
        get_dash = [1, 4]
    elif dash == '- - - - - - - - - ':
        get_dash = [6, 6]
    elif dash == '-.-.-.-.-.-.-.-.':
        get_dash = [9, 4, 2, 4]
    else:
        get_dash = [9]
    return get_dash


def choice_width_tablet():
    """ Выбор толщины """
    return float(ui.comboBox_width_tablet.currentText())



def get_table(table_text):
    """ Получить таблицу БД по ее текстовому названию """
    if table_text == 'data_las':
        tab = DataLas
    elif table_text == 'data_lit':
        tab = DataLit
    elif table_text == 'data_piroliz_kern':
        tab = DataPirolizKern
    elif table_text == 'data_piroliz_extr':
        tab = DataPirolizExtr
    elif table_text == 'data_chrom_kern':
        tab = DataChromKern
    else:
        tab = DataChromExtr
    return tab


def calc_stat():
    try:
        w_id = get_well_id()
        start, stop = check_start_stop()
        table, table_text, widget = check_tabWidjet()
        param = widget.currentItem().text()
        values = sum(list(map(list, session.query(literal_column(f'{table_text}.{param}')).filter(table.well_id == w_id,
                  table.depth >= start, table.depth <= stop, literal_column(f'{table_text}.{param}') != None).all())), [])
        desc_values = describe(values)
        nskew = abs(desc_values.skewness / (6 / desc_values.nobs) ** 0.5)
        nkurt = abs(desc_values.kurtosis / (24 / desc_values.nobs) ** 0.5)
        ui.lineEdit_n.clear()
        ui.lineEdit_n.setText(str(desc_values.nobs))
        ui.lineEdit_min.clear()
        ui.lineEdit_min.setText(str(round(desc_values.minmax[0], 5)))
        ui.lineEdit_max.clear()
        ui.lineEdit_max.setText(str(round(desc_values.minmax[1], 5)))
        ui.lineEdit_amean.clear()
        ui.lineEdit_amean.setText(str(round(desc_values.mean, 5)))
        ui.lineEdit_skew.clear()
        ui.lineEdit_skew.setText(str(round(desc_values.skewness, 5)))
        ui.lineEdit_kurt.clear()
        ui.lineEdit_kurt.setText(str(round(desc_values.kurtosis, 5)))
        ui.lineEdit_gmean.clear()
        ui.lineEdit_gmean.setText(str(round(gmean(values), 5)))
        ui.lineEdit_med.clear()
        ui.lineEdit_med.setText(str(round(median(values), 5)))
        ui.lineEdit_nskew.clear()
        ui.lineEdit_nskew.setText(str(round(nskew, 5)))
        ui.lineEdit_nkurt.clear()
        ui.lineEdit_nkurt.setText(str(round(nkurt, 5)))
    except ValueError:
        pass
    except AttributeError:
        pass


def comboBox_class_lim_update():
    """Обновление выпадающего списка классификаций по пределам"""
    ui.comboBox_class_lim.clear()
    for i in session.query(ClassByLimits).order_by(ClassByLimits.id).all():
        ui.comboBox_class_lim.addItem(f'{i.id}. {i.title}')
    ui.comboBox_class_lim.setCurrentIndex(0)


def check_value_in_limits(val, lim):
    """
    Функция определяет в какой интервал попадает значение
    :param val: искомое значение
    :param lim: список интервалов
    :return: индекс интервала
    """
    n = 0
    for i in lim:
        if val >= i:
            n += 1
        else:
            break
    try:
        n10 = (val - lim[n - 1]) / (lim[n] - lim[n - 1]) if ui.checkBox_pdf_class.isChecked() else 0
    except IndexError:
        n10 = (val - lim[n - 1]) / (lim[n - 1] - lim[n - 2]) if ui.checkBox_pdf_class.isChecked() else 0
        n10 = 0.99 if n10 >= 1 else n10
    return (n - 1) + n10


def arithmetic_round(x):
    """ арифметическое округление """
    a = int(x)
    b = x - a
    if b < 0.5:
        return round(x)
    else:
        return round(x + 0.01)


def choice_category(list_cat, count_param):
    """ Выбор результирующей категории """
    if ui.checkBox_pdf_class.isChecked():
        try:
            interval = np.linspace(0, count_param + 1, 1000)
            pdf = gaussian_kde(list_cat)
            res_cat = int(interval[pdf.evaluate(interval).argmax()])
        except np.linalg.LinAlgError:
            print('LinalgError')
            res_cat = int(list_cat[0])
        except ValueError:
            res_cat = int(list_cat[0])
        return res_cat
    else:
        a = Counter(list_cat).most_common(2)    # максимальное количество вхождений значений в список (первые два)
        try:
            if a[0][1] != a[1][1]:  # если количество первых двух макс. вхождений не совпадает
                res_cat = a[0][0]   # берём первый
            else:   # если количество первых двух макс. вхождений совпадает
                res_cat = arithmetic_round(mean(list_cat))  # берём среднее арифметическое
            return res_cat
        except IndexError:    # если в списке одно значение
            return a[0][0]


def comboBox_class_lda_update():
    """Обновление выпадающего списка классификаций по пределам"""
    ui.comboBox_class_lda.clear()
    for i in session.query(ClassByLda).order_by(ClassByLda.id).all():
        ui.comboBox_class_lda.addItem(f'{i.id}. {i.title} скв.{i.well.title}')
    ui.comboBox_class_lda.setCurrentIndex(0)


def comboBox_class_lda_cat_update():
    """Обновление списка дискриминантного анализа LDA категорий"""
    ui.comboBox_class_lda_cat.clear()
    try:
        c_id = int(ui.comboBox_class_lda.currentText().split('.')[0])
        for i in session.query(ClassByLda.category).filter(ClassByLda.id == c_id).first()[0].split(';'):
            ui.comboBox_class_lda_cat.addItem(i)
        ui.comboBox_class_lda_cat.setCurrentIndex(0)
        update_table_lda_cat()
        update_graph_lda_cat()
        # reset_fake_lda()
    except ValueError:
        pass


def update_table_lda_cat():
    """ отображение в таблице разметки LDA """
    clear_table(ui.tableWidget)
    ui.label_table_name.setText(f'Обучающая выборка LDA скв.{ui.comboBox_class_lda.currentText().split(".")[2]}')
    c_id = int(ui.comboBox_class_lda.currentText().split('.')[0])
    list_mark = session.query(ClassByLdaMark).filter(ClassByLdaMark.class_id == c_id, ClassByLdaMark.fake == 0).all()
    ui.tableWidget.setColumnCount(2)
    ui.tableWidget.setHorizontalHeaderLabels(['depth', 'mark'])
    list_cat = []
    for i in range(ui.comboBox_class_lda_cat.count()):
        list_cat.append(ui.comboBox_class_lda_cat.itemText(i))
    for n, i in enumerate(list_mark):
        ui.tableWidget.insertRow(n)
        ui.tableWidget.setItem(n, 0, QTableWidgetItem(str(i.depth)))
        ui.tableWidget.setItem(n, 1, QTableWidgetItem(i.mark))
        ui.tableWidget.item(n, 1).setBackground(QtGui.QColor(color_list[list_cat.index(i.mark)]))
    ui.tableWidget.resizeColumnsToContents()
    # ui.tableWidget.verticalHeader().hide()
    # reset_fake_lda()


def update_graph_lda_cat():
    """ отображение баров разметки LDA """
    ui.graphicsView.clear()
    c_id = int(ui.comboBox_class_lda.currentText().split('.')[0])
    list_cat = []
    for i in range(ui.comboBox_class_lda_cat.count()):
        list_cat.append(ui.comboBox_class_lda_cat.itemText(i))
    for n, i in enumerate(list_cat):
        Y = sum(list(map(list, session.query(ClassByLdaMark.depth).
                         filter(ClassByLdaMark.class_id == c_id, ClassByLdaMark.mark == i,
                                ClassByLdaMark.fake == 0).all())), [])
        color = color_list[n]
        curve = pg.BarGraphItem(x0=0, y=Y, height=0.1, width=n+1, brush=color, pen=pg.mkPen(color=color))
        ui.graphicsView.addItem(curve)
        curve.getViewBox().invertY(True)


def build_table_train_lda():
    """ Собирает DataFrame для обучающей выборки по выбранным параметрам """
    # Получаем id класса из выпадающего списка в UI
    c_id = int(ui.comboBox_class_lda.currentText().split('.')[0])
    # Получаем список параметров и таблиц для запросов из списка параметров в UI
    list_param = []
    list_tab = []
    for i in range(ui.listWidget_class_lda_param.count()):
        item_i = ui.listWidget_class_lda_param.item(i).text().split(' ')
        list_param.append(item_i[0])
        list_tab.append(item_i[1])
    # Создаем пустой DataFrame с нужными колонками
    data_train = pd.DataFrame(columns=['depth', 'mark'] + list_param)
    # Итерируемся по всем объектам класса, удовлетворяющим условию
    for i in session.query(ClassByLdaMark).filter(ClassByLdaMark.class_id == c_id, ClassByLdaMark.fake == 0).all():
        # Для каждого объекта создаем словарь со значениями параметров, соответствующими его глубине
        dict_value = {}
        for j in range(len(list_param)):
            tab = get_table(list_tab[j])
            val = session.query(literal_column(f'{list_tab[j]}.{list_param[j]}')).filter(
                tab.well_id == i.class_lda.well_id, tab.depth >= i.depth, tab.depth < i.depth + 0.1).first()
            if val:
                if val[0]:
                    dict_value[list_param[j]] = val[0]
        # Если для всех параметров есть значения, то добавляем строку в DataFrame
        if len(dict_value) == len(list_param):
            dict_value['mark'] = i.mark
            dict_value['depth'] = i.depth
            data_train = pd.concat([data_train, pd.DataFrame(pd.Series(dict_value)).T], ignore_index=True)

    # Возвращаем DataFrame и списки параметров и таблиц
    return data_train, list_param, list_tab


def reset_fake_lda():
    session.query(ClassByLdaMark).filter(ClassByLdaMark.fake == 1).update({'fake': 0}, synchronize_session="fetch")
    session.commit()


def build_tableWidget_from_pd(df, widget, list_cat):
    """ Перенос таблицы из DataFrame в tableWidget """
    clear_table(widget)
    widget.setColumnCount(len(df.columns))
    widget.setHorizontalHeaderLabels(list(df.columns))
    for n, i in enumerate(df.index):
        widget.insertRow(n)
        for k, j in enumerate(df.columns):
            if type(df[j][i]) is float64:
                val = round(df[j][i], 5)
            else:
                val = df[j][i]
            widget.setItem(n, k, QTableWidgetItem(str(val)))
        if list_cat:
            widget.item(n, 2).setBackground(QtGui.QColor(color_list[list_cat.index(df['mark'][i])]))
    widget.resizeColumnsToContents()


def category_to_resource(list_cat):
    del_category_to_resource()
    for n, i in enumerate(list_cat):
        ui.checkBox = QtWidgets.QCheckBox()
        font = QtGui.QFont()
        font.setPointSize(9)
        ui.checkBox.setFont(font)
        ui.checkBox.setText(i)
        ui.gridLayout_resourse.addWidget(ui.checkBox)
        ui.checkBox.setStyleSheet(f'background-color:{color_list[n]}')
        ui.checkBox.clicked.connect(interval_to_db)


def interval_to_db():
    try:
        session.query(IntervalFromCat).delete()
        d, n = get_n_cat_column()
        list_cat_for_calc = []
        text_int = 'Выбраны интервалы: '
        for i in ui.cat_resource.findChildren(QtWidgets.QCheckBox):
            if i.isChecked():
                list_cat_for_calc.append(i.text())
                text_int += f'{i.text()}, '
        ui.label_int.setText(text_int)
        list_int = []
        text_int_res = 'Расчёт русурсов в интервалах: '
        for i in range(ui.tableWidget.rowCount()):
            if ui.tableWidget.item(i, n).text() in list_cat_for_calc:
                if len(list_int) == 0 and i != 0:
                    value = (float(ui.tableWidget.item(i, d).text()) + float(ui.tableWidget.item(i - 1, d).text())) / 2
                    list_int.append(round(value, 2))
                else:
                    list_int.append(float(ui.tableWidget.item(i, d).text()))
            else:
                if len(list_int) > 0:
                    value = (float(ui.tableWidget.item(i, d).text()) + float(ui.tableWidget.item(i - 1, d).text())) / 2
                    list_int.append(round(value, 2))
                    new_int = IntervalFromCat(int_from=list_int[0], int_to=list_int[-1])
                    session.add(new_int)
                    text_int_res += f'\n{str(list_int[0])} - {str(list_int[-1])} м.'
                    list_int = []
        if len(list_int) > 0:
            new_int = IntervalFromCat(int_from=list_int[0], int_to=list_int[-1])
            text_int_res += f'\n{str(list_int[0])} - {str(list_int[-1])} м.'
            session.add(new_int)
        session.commit()
        ui.label_int_resource.setText(text_int_res)
    except UnboundLocalError:
        ui.label_info.setText(f'Внимание! Для выбора категорий необходима таблица результатов классификации. Выполните расчёт классификации заново.')
        ui.label_info.setStyleSheet('color: red')


def del_category_to_resource():
    for i in ui.cat_resource.findChildren(QtWidgets.QCheckBox):
        i.deleteLater()
    ui.textEdit_resourse.clear()


def get_n_cat_column():
    for i in range(ui.tableWidget.columnCount()):
        if ui.tableWidget.horizontalHeaderItem(i).text() == 'depth':
            n_depth = i
            break
    for i in range(ui.tableWidget.columnCount()):
        if ui.tableWidget.horizontalHeaderItem(i).text() in ['category', 'mark']:
            n_cat = i
            break
    return n_depth, n_cat



def del_none_from_list(values):
    return [value for value in values if value]


def remove_nan(lst):
    return list(filter(lambda x: not math.isnan(x), lst))


def set_info(text, color):
    ui.textEdit_resourse.append(f'<span style =\"color:{color};\" >{text}</span>')


def set_label_info(text, color):
    ui.label_info.setText(text)
    ui.label_info.setStyleSheet(f'color: {color}')


def show_list_tablet():
    """ Очищает виджет списка `listWidget_param_tablet` и заполняет его элементами на основе записей в таблице `DrawGraphTablet`. """
    ui.listWidget_param_tablet.clear()
    for i in session.query(DrawGraphTablet).all():
        if i.param:
            color = i.color
            color = 'grey' if color == 'black' else color
            ui.listWidget_param_tablet.addItem(f'{i.id} {i.param} {i.table} {i.type_graph} {get_line_dash(i.dash)} {i.width}')
            ui.listWidget_param_tablet.item(ui.listWidget_param_tablet.count() - 1).setBackground(QtGui.QColor(color))
        else:
            ui.listWidget_param_tablet.addItem(f'{i.id} Новый график')


def get_random_color():
    red = random.randint(0, 255)
    green = random.randint(0, 255)
    blue = random.randint(0, 255)
    color = f'#{red:02x}{green:02x}{blue:02x}'
    return color


def set_random_color(button):
    color = get_random_color()
    button.setStyleSheet(f"background-color: {color};")
    button.setText(color)


def change_color():
    button_color = ui.pushButton_color.palette().color(ui.pushButton_color.backgroundRole())
    color = QColorDialog.getColor(button_color)
    ui.pushButton_color.setStyleSheet(f"background-color: {color.name()};")
    ui.pushButton_color.setText(color.name())
    table, table_text, widget = check_tabWidjet()
    draw_param_graph(widget, table, table_text)


def set_row_background_color(table_widget, row_index, color):
    """ Устанавливаем цвет фона для строки таблицы с индексом row_index """
    for j in range(table_widget.columnCount()):
        item = table_widget.item(row_index, j)
        item.setBackground(QColor(color))


def alignment_table(table):
    for i in range(table.columnCount()):
        table.resizeColumnToContents(i)


def get_listwidget_by_table(table):
    if table == 'data_las':
        return ui.listWidget_las
    if table == 'data_chrom_extr':
        return ui.listWidget_chrom_extr
    if table == 'data_chrom_kern':
        return ui.listWidget_chrom_kern
    if table == 'data_piroliz_extr':
        return ui.listWidget_pir_extr
    if table == 'data_piroliz_kern':
        return ui.listWidget_pir_kern
    if table == 'data_lit':
        return ui.listWidget_lit


def clear_horizontalLayout(h_l_widget):
    while h_l_widget.count():
        item = h_l_widget.takeAt(0)
        widget = item.widget()
        if widget:
            widget.deleteLater()


def get_calc_data():
    return session.query(CalculatedData).filter_by(id=ui.listWidget_calc_data.currentItem().text().split(' id')[-1]).first()


def median_in_interval(dict_depth_param, depth_value, int_depth):
    # Определите границы интервала
    lower_bound = depth_value - int_depth
    upper_bound = depth_value + int_depth

    # Отфильтруйте элементы словаря, которые находятся в указанном интервале
    filtered_values = [value for depth, value in dict_depth_param.items() if lower_bound <= float(depth) <= upper_bound]

    # Если отфильтрованный список пуст, верните None или 0 (в зависимости от ваших требований)
    if not filtered_values:
        return None

    # Верните среднее значение отфильтрованных значений
    return median(filtered_values)


def math_round(number, n_digits=0):
    """
    Округляет число по математическим правилам до заданного количества десятичных знаков.

    Параметры:
    number (float): Число, которое необходимо округлить.
    ndigits (int): Количество знаков после запятой для округления.

    Возвращает:
    float: Округлённое значение числа.
    """
    # Множитель для сдвига десятичной точки
    multiplier = 10 ** n_digits

    # Умножаем, чтобы сдвинуть десятичную точку на нужное количество знаков
    result = number * multiplier

    # Извлечение дробной части числа
    fractional_part = result % 1

    # Определение, нужно ли округлять вверх или вниз
    if fractional_part < 0.5:
        result = int(result)  # Округление вниз
    else:
        result = int(result) + 1  # Округление вверх

    # Возвращаем значение, сдвинув десятичную точку обратно
    return result / multiplier


def get_linking_id():
    """ Возвращает id привязки """
    return ui.comboBox_linking.currentText().split(' id')[-1]

def get_trying_id():
    """ Возвращает trying_id """
    return ui.listWidget_trying.currentItem().text().split(' id')[-1]

def get_sample_id():
    """ Возвращает id образца """
    return ui.listWidget_sample.currentItem().text().split(' id')[-1]


def update_combobox_linking():
    """ Обновление списка привязок """
    ui.comboBox_linking.clear()
    n = 1
    for i in session.query(Linking).filter_by(well_id=get_well_id()).all():
        ui.comboBox_linking.addItem(f'{n}. {i.table_curve}({i.param_curve}) - {i.table_sample}({i.param_sample}) id{i.id}')
        n += 1
    ui.comboBox_linking.setCurrentIndex(0)
    update_listwidget_samples()


def update_listwidget_samples():
    """ Обновление списка образцов """
    ui.listWidget_sample.clear()
    n = 1
    for i in session.query(Sample).filter_by(linking_id=get_linking_id()).all():
        ui.listWidget_sample.addItem(f'{n}. {i.depth} - {i.value}')
        n += 1


def update_listwidget_samples_for_trying():
    """ Обновление списка образцов """
    ui.listWidget_sample.clear()
    id_trying = get_trying_id()
    n = 1
    for i in session.query(Sample).filter_by(linking_id=get_linking_id()).all():
        shift = session.query(Shift).filter_by(trying_id=id_trying, sample_id=i.id).first()
        shift_dist = shift.distance if shift else 0
        ui.listWidget_sample.addItem(f'{n}. {i.depth} - {i.value} shift: {shift_dist} м id{i.id}')
        n += 1


def update_listwidget_trying():
    ui.listWidget_trying.clear()
    n = 1
    for i in session.query(Trying).filter_by(linking_id=get_linking_id()).all():
        item = QtWidgets.QListWidgetItem(f'{n}. {i.algorithm} {i.old_corr}/{i.corr} {i.method_shift}:{i.shift_value} id{i.id}')
        text_tooltip = (f'depth: {i.up_depth}-{i.down_depth}\n'
                        f'algorithm: {i.algorithm}\n'
                        f'n_iter: {i.n_iter}\n'
                        f'limit:{i.limit}\n'
                        f'bin:{i.bin}\n'
                        f'{i.method_shift}: {i.shift_value}\n'
                        f'old_corr/corr: {i.old_corr}/{i.corr}\n')
        item.setToolTip(text_tooltip)
        ui.listWidget_trying.addItem(item)
        n += 1
