from PyQt5.QtWidgets import QTableWidgetItem, QFileDialog, QCheckBox
from sqlalchemy import text, desc, literal_column
from pandas import read_excel
import pyqtgraph as pg
from scipy.stats import describe, gmean
from numpy import median, float64
from collections import Counter
from statistics import mean
import pandas as pd

import traceback
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

from qt.add_area_dialog import *
from qt.add_region_dialog import *
from qt.add_well_dialog import *
from qt.add_class_limit import *
from qt.add_class_lda import *

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


def read_las_info(file_name):
    """Считывает информацию из las-файла"""
    with open(file_name) as f:
        n = 0
        while n < 100:
            n += 1
            line = f.readline()
            if line.strip().startswith('VERS.'):
                version = line.split(':')[0].split()[1]
            if line.strip().startswith('STRT.M'):
                start_depth = float(line.split(':')[0].split()[1])
            if line.strip().startswith('STOP.M'):
                stop_depth = float(line.split(':')[0].split()[1])
            if line.strip().startswith('NULL.'):
                null_value = line.split(':')[0].split()[1]
            if line.strip().startswith('~A'):
                param = line.split()
                data_row = n
                break
        if version == '2.0':
            with open(file_name) as f:
                n = 0
                while n < 100:
                    n += 1
                    line = f.readline()
                    if line.strip().startswith('#CURVE'):
                        param = line.split(':')[0].split()[1]
        if type(param) is list:
            if '~A' in param:
                param.remove('~A')
                param.remove('Log')
        return version, start_depth, stop_depth, null_value, param, data_row


def get_well_id():
    """ Получаем id выбранной в комбобоксах (выпадающий список) скважины"""
    if ui.comboBox_region.currentText() and ui.comboBox_area.currentText() and ui.comboBox_well.currentText():
        return session.query(Well.id).join(Area).join(Region).filter(Region.title == ui.comboBox_region.currentText(),
                                                                 Area.title == ui.comboBox_area.currentText(),
                                                                 Well.title == ui.comboBox_well.currentText())[0][0]


def add_slots(start, stop):
    """Добавить ряды в таблицу DataLas"""
    w_id = get_well_id()
    ui.progressBar.setMaximum(10 * (stop - start))
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
    for n, i in enumerate(data_tab.columns):
        if i in list_columns:
            ui.label_info.setText(f'Загрузка параметра "{i}"...')
            ui.label_info.setStyleSheet('color: blue')
            for j in data_tab.index:
                session.query(table).filter(table.name == replace_letter_of_name(str(data_tab['n_obr'][j])),
                                                   table.well_id == w_id).update({i: round(data_tab[i][j], 5)},
                                                                                        synchronize_session="fetch")
        ui.progressBar.setValue(n+1)
    session.commit()
    ui.label_info.setText('Готово. Загруженные параметры отобразаются в "списке загруженных параметров".')
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
        ui.tableWidget.setColumnCount(2)
        ui.tableWidget.setHorizontalHeaderLabels(['depth', param])
    else:   # для остальных данных отображается глубина, название образца
        data_table = session.query(table.depth, table.name, literal_column(f'{table_text}.{param}')).\
            filter(table.well_id == w_id, literal_column(f'{table_text}.{param}') != None). \
            order_by(table.depth).all()
        ui.tableWidget.setColumnCount(3)
        ui.tableWidget.setHorizontalHeaderLabels(['depth', 'name', param])
    for n, i in enumerate(data_table):
        ui.tableWidget.insertRow(n)
        for k, j in enumerate(i):
            if k == 0:
                j = round(j, 1)
            if k == 2:
                j = round(j, 5)
            ui.tableWidget.setItem(n, k, QTableWidgetItem(str(j)))
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
        curve = pg.PlotCurveItem(x=X, y=Y, pen=pg.mkPen(color=color, width=width, dash=dash))
    else:   # остальные данные отображаются в виде гистограммы
        curve = pg.BarGraphItem(x0=0, y=Y, height=0.1, width=X, brush=color, pen=pg.mkPen(color=color, width=0.4))
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


def choice_color():
    """ Выбор цвета """
    return ui.comboBox_color.currentText()


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


def choice_width():
    """ Выбор толщины """
    return float(ui.comboBox_width.currentText())


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
    return n - 1


def arithmetic_round(x):
    """ арифметическое округление """
    a = int(x)
    b = x - a
    if b < 0.5:
        return round(x)
    else:
        return round(x + 0.01)


def choice_category(list_cat):
    """ Выбор результирующей категории """
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
    c_id = int(ui.comboBox_class_lda.currentText().split('.')[0])
    list_param = []
    list_tab = []
    for i in range(ui.listWidget_class_lda_param.count()):
        item_i = ui.listWidget_class_lda_param.item(i).text().split(' ')
        list_param.append(item_i[0])
        list_tab.append(item_i[1])
    data_train = pd.DataFrame(columns=['depth', 'mark'] + list_param)
    for i in session.query(ClassByLdaMark).filter(ClassByLdaMark.class_id == c_id, ClassByLdaMark.fake == 0).all():
        dict_value = {}
        for j in range(len(list_param)):
            tab = get_table(list_tab[j])
            val = session.query(literal_column(f'{list_tab[j]}.{list_param[j]}')).filter(
                tab.well_id == i.class_lda.well_id, tab.depth >= i.depth, tab.depth < i.depth + 0.1).first()
            if val:
                if val[0]:
                    dict_value[list_param[j]] = val[0]
        if len(dict_value) == len(list_param):
            dict_value['mark'] = i.mark
            dict_value['depth'] = i.depth
            data_train = data_train.append(dict_value, ignore_index=True)
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


def set_info(text, color):
    ui.textEdit_resourse.append(f'<span style =\"color:{color};\" >{text}</span>')