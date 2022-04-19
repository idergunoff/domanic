from functions import *


def click_table():
    """ При клике по таблице выделение этого места на графике """
    row = ui.tableWidget.currentRow()
    depth_table = float(ui.tableWidget.item(row, 0).text())
    depth_line = pg.InfiniteLine(angle=0, pen=pg.mkPen(color='b', width=0.7, dash=[2, 2]))
    ui.graphicsView.addItem(depth_line)
    depth_line.setPos(depth_table)


def set_style_combobox():
    """ Установка выбранного цвета фоном комбобокса (выпадающего списка) """
    color = choice_color()
    color = 'grey' if color == 'black' else color
    ui.comboBox_color.setStyleSheet(f"background-color: {color};")
    table, table_text, widget = check_tabWidjet()
    draw_param_graph(widget, table, table_text)


def choice_param():
    """ Добавление параметра в список для отображения нескольких параметров """
    table, table_text, widget = check_tabWidjet()
    try:
        param = widget.currentItem().text()
        color = choice_color()
        new_graph = DrawSeveralGraph(well_id=get_well_id(), table=table_text, param=param, color=color,
                                     dash=' '.join(list(map(str, choice_dash()))), width=choice_width())
        session.add(new_graph)  # параметр добавляется в отдельную таблицу + параметры графика
        session.commit()
        color = 'grey' if color == 'black' else color
        ui.listWidget_param.addItem(param)
        ui.listWidget_param.item(ui.listWidget_param.count() - 1).setBackground(QtGui.QColor(color))
    except AttributeError:
        ui.label_info.setText(f'Внимание! Не выбран параметр.')
        ui.label_info.setStyleSheet('color: red')


def clear_param():
    """ Очистка списка выбранных параметров """
    ui.listWidget_param.clear()
    session.query(DrawSeveralGraph).delete()
    session.commit()


def draw_sev_param():
    """ Отрисовка графиков нескольких параметров в выбранном интервале """
    start, stop = check_start_stop()
    sev_param = session.query(DrawSeveralGraph).all()
    ui.graphicsView.clear()
    for i in sev_param:
        tab = get_table(i.table)
        X = sum(list(map(list, session.query(literal_column(f'{i.table}.{i.param}')).filter(tab.depth > start,
                        tab.depth < stop, tab.well_id == i.well_id, literal_column(f'{i.table}.{i.param}') != None).
                         order_by(tab.depth).all())), [])
        Y = sum(list(map(list, session.query(tab.depth).filter(tab.depth > start, tab.depth < stop,
            tab.well_id == i.well_id, literal_column(f'{i.table}.{i.param}') != None).order_by(tab.depth).all())), [])
        if i.table == 'data_las':
            curve = pg.PlotCurveItem(x=X, y=Y, pen=pg.mkPen(color=i.color, width=float(i.width),
                                                            dash=list(map(int, (i.dash).split(' ')))))
        else:
            curve = pg.BarGraphItem(x0=0, y=Y, height=0.1, width=X, brush=i.color,
                                    pen=pg.mkPen(color=i.color, width=0.4))
        try:
            ui.graphicsView.addItem(curve)
            curve.getViewBox().invertY(True)
        except TypeError:
            ui.label_info.setText(f'Внимание! Ошибка. Образцы не привязаны к глубине.')
            ui.label_info.setStyleSheet('color: red')


def draw_norm_sev_param():
    """ Отрисовка графиков нескольких нормированных параметров в выбранном интервале """
    start, stop = check_start_stop()
    sev_param = session.query(DrawSeveralGraph).all()
    ui.graphicsView.clear()
    for i in sev_param:
        tab = get_table(i.table)
        X = sum(list(map(list, session.query(literal_column(f'{i.table}.{i.param}')).filter(tab.depth > start,
                tab.depth < stop, tab.well_id == i.well_id, literal_column(f'{i.table}.{i.param}') != None).
                                                                                order_by(tab.depth).all())), [])
        X = [(j - min(X)) / (max(X) - min(X)) for j in X]
        Y = sum(list(map(list, session.query(tab.depth).filter(tab.depth > start, tab.depth < stop,
                        tab.well_id == i.well_id, literal_column(f'{i.table}.{i.param}') != None).order_by(
                        tab.depth).all())), [])
        if i.table == 'data_las':
            curve = pg.PlotCurveItem(x=X, y=Y, pen=pg.mkPen(color=i.color, width=float(i.width),
                                                            dash=list(map(int, (i.dash).split(' ')))))
        else:
            curve = pg.BarGraphItem(x0=0, y=Y, height=0.1, width=X, brush=i.color,
                                    pen=pg.mkPen(color=i.color, width=0.4))
        try:
            ui.graphicsView.addItem(curve)
            curve.getViewBox().invertY(True)
        except TypeError:
            ui.label_info.setText(f'Внимание! Ошибка. Образцы не привязаны к глубине.')
            ui.label_info.setStyleSheet('color: red')


def build_table_sev_param():
    """ Построение сводной таблицы по нескольким параметрам и отображение ее в виджете"""
    clear_table(ui.tableWidget)
    w_id = get_well_id()
    start, stop = check_start_stop()
    sev_param = session.query(DrawSeveralGraph).all()
    if sev_param:
        list_param = ['depth', 'n_obr']
        [list_param.append(i.param) for i in sev_param]
        wlist_param = []
        [wlist_param.append([i.table, i.param]) for i in sev_param]
        pd_tab = pd.DataFrame(columns=list_param)
        ui.tableWidget.setColumnCount(len(list_param))
        ui.tableWidget.setHorizontalHeaderLabels(list_param)
        d, n = start, 0
        ui.progressBar.setMaximum(int((stop - start) / 0.1))
        ui.label_info.setText(f'Формирование сводной таблицы по выбранным параметрам...')
        ui.label_info.setStyleSheet('color: blue')
        while d <= stop:
            d = round(d, 2)
            empty_row = {}
            [empty_row.update({i: None}) for i in list_param]
            pd_tab = pd_tab.append(empty_row, ignore_index=True)
            pd_tab['depth'][n] = d
            ui.tableWidget.insertRow(n)
            ui.tableWidget.setItem(n, 0, QTableWidgetItem(str(round(d, 1))))
            for col, l in enumerate(wlist_param):
                tab = get_table(l[0])
                if l[0] == 'data_las':
                    value = session.query(literal_column(f'{l[0]}.{l[1]}')).filter(tab.depth >= d, tab.depth < d + 0.1,
                                                                                   tab.well_id == w_id).first()
                    if value:
                        pd_tab[l[1]][n] = value[0]
                        ui.tableWidget.setItem(n, col + 2, QTableWidgetItem(str(value[0])))
                else:
                    value = session.query(literal_column(f'{l[0]}.{l[1]}')).filter(tab.depth >= d, tab.depth < d + 0.1,
                                                                                   tab.well_id == w_id).first()
                    if value:
                        pd_tab[l[1]][n] = value[0]
                        if value[0]:
                            ui.tableWidget.setItem(n, col + 2, QTableWidgetItem(str(round(value[0], 5))))
                        else:
                            ui.tableWidget.setItem(n, col + 2, QTableWidgetItem(str(value[0])))
                        value = session.query(tab.name).filter(tab.depth >= d, tab.depth < d + 0.1,
                                                                        tab.well_id == w_id).first()
                        pd_tab['n_obr'][n] = value.name
                        ui.tableWidget.setItem(n, 1, QTableWidgetItem(value.name))
            d += 0.1
            n += 1
            ui.progressBar.setValue(n)
        ui.tableWidget.verticalHeader().hide()
        ui.tableWidget.resizeColumnsToContents()
        ui.label_info.setText(f'Готово!')
        ui.label_info.setStyleSheet('color: green')


def save_table_sev_param():
    """ Сохранение сводной таблицы из виджета в Excel """
    list_col = []
    [list_col.append(ui.tableWidget.horizontalHeaderItem(i).text()) for i in range(ui.tableWidget.columnCount())]
    pd_tab = pd.DataFrame()
    for n, i in enumerate(list_col):
        data = []
        for row in range(ui.tableWidget.rowCount()):
            if ui.tableWidget.item(row, n) is not None:
                if ui.tableWidget.item(row, n).text() != 'None':
                    if i in ['n_obr', 'name']:
                        data.append(ui.tableWidget.item(row, n).text())
                    else:
                        data.append(float(ui.tableWidget.item(row, n).text()))
                else:
                    data.append(None)
            else:
                data.append(None)
        pd_tab[i] = data
    list_col.remove('depth')
    if 'n_obr' in list_col:
        list_col.remove('n_obr')
    if 'name' in list_col:
        list_col.remove('name')
    for i in pd_tab.index:
        l = []
        for j in list_col:
            if pd.isna(pd_tab[j][i]):
                l.append(1)
        if len(l) == len(list_col):
            pd_tab = pd_tab.drop(index=i)
    try:
        file_name = f'{ui.comboBox_area.currentText()}_скв.{ui.comboBox_well.currentText()}_{"_".join(list_col)}.xlsx'
        fn = QFileDialog.getSaveFileName(caption="Сохранить сводную таблицу", directory=file_name,
                                         filter="Excel Files (*.xlsx)")
        pd_tab.to_excel(fn[0])
        ui.label_info.setText(f'Таблица сохранена в файл: {fn[0]}')
        ui.label_info.setStyleSheet('color: green')
    except ValueError:
        pass


def add_param_for_relation():
    """ Добавление параметра для построение зависимости """
    table, table_text, widget = check_tabWidjet()
    try:
        param = widget.currentItem().text()
        if ui.listWidget_relation.findItems(f'{param} {table_text}', QtCore.Qt.MatchExactly):
            ui.label_info.setText(f'Внимание! Параметр "{param}" уже добавлен.')
            ui.label_info.setStyleSheet('color: red')
        else:
            if ui.listWidget_relation.count() == 4:
                ui.listWidget_relation.clear()
            ui.listWidget_relation.addItem(f'{param} {table_text}')
    except AttributeError:
        ui.label_info.setText(f'Внимание! Не выбран параметр.')
        ui.label_info.setStyleSheet('color: red')


def draw_relation():
    """ Построение зависимости """
    w_id = get_well_id()
    try:
        param_1 = ui.listWidget_relation.item(0).text().split(' ')[0]
        table_name_1 = ui.listWidget_relation.item(0).text().split(' ')[1]
        table_1 = get_table(table_name_1)
        param_2 = ui.listWidget_relation.item(1).text().split(' ')[0]
        table_name_2 = ui.listWidget_relation.item(1).text().split(' ')[1]
        table_2 = get_table(table_name_2)
        data = pd.DataFrame(columns=[f'{param_1}_{table_name_1}', f'{param_2}_{table_name_2}'])
        if ui.listWidget_relation.count() > 2:
            param_3 = ui.listWidget_relation.item(2).text().split(' ')[0]
            table_name_3 = ui.listWidget_relation.item(2).text().split(' ')[1]
            table_3 = get_table(table_name_3)
            data[f'{param_3}_{table_name_3}'] = 0
        if ui.listWidget_relation.count() > 3:
            param_4 = ui.listWidget_relation.item(3).text().split(' ')[0]
            table_name_4 = ui.listWidget_relation.item(3).text().split(' ')[1]
            table_4 = get_table(table_name_4)
            data[f'{param_4}_{table_name_4}'] = 0
        if table_name_1 != 'data_las':
            data['name'] = 0
        start, stop = check_start_stop()
        ui.progressBar.setMaximum(int((stop - start) / 0.1))
        d, n = start, 0
        while d <= stop:
            d = round(d, 2)
            dict_values = {}
            value_1 = session.query(literal_column(f'{table_name_1}.{param_1}')).filter(table_1.depth >= d,
                                                        table_1.depth < d + 0.1, table_1.well_id == w_id).first()
            value_2 = session.query(literal_column(f'{table_name_2}.{param_2}')).filter(table_2.depth >= d,
                                                        table_2.depth < d + 0.1, table_2.well_id == w_id).first()
            if value_1 and value_2:
                if value_1[0] and value_2[0]:
                    dict_values[f'{param_1}_{table_name_1}'] = value_1[0]
                    dict_values[f'{param_2}_{table_name_2}'] = value_2[0]
                    if table_name_1 != 'data_las':
                        name = session.query(table_1.name).filter(table_1.depth >= d, table_1.depth < d + 0.1,
                                                                  table_1.well_id == w_id).first()
                        dict_values['name'] = name[0]
                    if ui.listWidget_relation.count() > 2:
                        value_3 = session.query(literal_column(f'{table_name_3}.{param_3}')).filter(table_3.depth >= d,
                                                        table_3.depth < d + 0.1, table_3.well_id == w_id).first()
                        if value_3:
                            if value_3[0]:
                                dict_values[f'{param_3}_{table_name_3}'] = value_3[0]
                                if ui.listWidget_relation.count() > 3:
                                    value_4 = session.query(literal_column(f'{table_name_4}.{param_4}')).filter(table_4.depth >= d,
                                                                        table_4.depth < d + 0.1, table_4.well_id == w_id).first()
                                    if value_4:
                                        if value_4[0]:
                                            dict_values[f'{param_4}_{table_name_4}'] = value_4[0]
            if table_name_1 != 'data_las':
                if len(dict_values) == ui.listWidget_relation.count() + 1:
                    data = data.append(dict_values, ignore_index=True)
            else:
                if len(dict_values) == ui.listWidget_relation.count():
                    data = data.append(dict_values, ignore_index=True)
            d += 0.1
            n += 1
            ui.progressBar.setValue(n)
    except AttributeError:
        ui.label_info.setText(f'Внимание! Параметры не выбраны или выбран только один параметр.')
        ui.label_info.setStyleSheet('color: red')
    pal = ui.comboBox_rel.currentText()
    fig = plt.figure(figsize=(10, 10), dpi=80)
    ax = plt.subplot()
    if ui.checkBox_xlg.isChecked():
        ax.set(xscale="log")
    if ui.checkBox_ylg.isChecked():
        ax.set(yscale="log")
    if ui.listWidget_relation.count() == 2:
        sns.scatterplot(data=data, x=f'{param_1}_{table_name_1}', y=f'{param_2}_{table_name_2}')
        # sns.lmplot(data=data, x=f'{param_1}_{table_name_1}', y=f'{param_2}_{table_name_2}')
    elif ui.listWidget_relation.count() == 3:
        sns.scatterplot(data=data, x=f'{param_1}_{table_name_1}', y=f'{param_2}_{table_name_2}',
                        hue=f'{param_3}_{table_name_3}', size=f'{param_3}_{table_name_3}', sizes=(5, 250), palette=pal)
    else:
        sns.scatterplot(data=data, x=f'{param_1}_{table_name_1}', y=f'{param_2}_{table_name_2}',
                        hue=f'{param_3}_{table_name_3}', size=f'{param_4}_{table_name_4}', sizes=(5, 250), palette=pal)
    if ui.checkBox_trend.isChecked():
        a, b = np.polyfit(data[f'{param_1}_{table_name_1}'], data[f'{param_2}_{table_name_2}'], deg=1)  # расчитываем коэф уравнения для линии тренда
        x = data[f'{param_1}_{table_name_1}']
        y_trend = a * x + b
        ax.plot(x, y_trend, '-')
    ax.grid()
    ax.xaxis.grid(True, "minor", linewidth=.25)
    ax.yaxis.grid(True, "minor", linewidth=.25)
    title_graph = f'{ui.comboBox_area.currentText()} площадь, скв.{ui.comboBox_well.currentText()}\nИнтервал: ' \
                  f'{str(start)} - {str(stop)} м. \nЗависимость ' f'{param_1} - {param_2}'
    if ui.listWidget_relation.count() > 2:
        title_graph += f' - {param_3}'
    if ui.listWidget_relation.count() > 3:
        title_graph += f' - {param_4}'
    title_graph += f'\nКоличество образцов: {str(len(data.index))}'
    if ui.checkBox_trend.isChecked():
        title_graph += f'\ny = {round(a, 5)} * x + {round(b, 5)}'
    plt.title(title_graph, fontsize=16)
    fig.tight_layout()
    fig.show()


def save_relation():
    """ Сохранение сводной таблицы из списка параметров для построения зависимости """
    w_id = get_well_id()
    try:
        param_1 = ui.listWidget_relation.item(0).text().split(' ')[0]
        table_name_1 = ui.listWidget_relation.item(0).text().split(' ')[1]
        table_1 = get_table(table_name_1)
        param_2 = ui.listWidget_relation.item(1).text().split(' ')[0]
        table_name_2 = ui.listWidget_relation.item(1).text().split(' ')[1]
        table_2 = get_table(table_name_2)
        data = pd.DataFrame(columns=[f'{param_1}_{table_name_1}', f'{param_2}_{table_name_2}'])
        if ui.listWidget_relation.count() > 2:
            param_3 = ui.listWidget_relation.item(2).text().split(' ')[0]
            table_name_3 = ui.listWidget_relation.item(2).text().split(' ')[1]
            table_3 = get_table(table_name_3)
            data[f'{param_3}_{table_name_3}'] = 0
        if ui.listWidget_relation.count() > 3:
            param_4 = ui.listWidget_relation.item(3).text().split(' ')[0]
            table_name_4 = ui.listWidget_relation.item(3).text().split(' ')[1]
            table_4 = get_table(table_name_4)
            data[f'{param_4}_{table_name_4}'] = 0
        if table_name_1 != 'data_las':
            data['name'] = 0
        start, stop = check_start_stop()
        ui.progressBar.setMaximum(int((stop - start) / 0.1))
        d, n = start, 0
        while d <= stop:
            d = round(d, 2)
            dict_values = {}
            value_1 = session.query(literal_column(f'{table_name_1}.{param_1}')).filter(table_1.depth >= d,
                                                                                        table_1.depth < d + 0.1,
                                                                                        table_1.well_id == w_id).first()
            value_2 = session.query(literal_column(f'{table_name_2}.{param_2}')).filter(table_2.depth >= d,
                                                                                        table_2.depth < d + 0.1,
                                                                                        table_2.well_id == w_id).first()
            if value_1 and value_2:
                if value_1[0] and value_2[0]:
                    dict_values[f'{param_1}_{table_name_1}'] = value_1[0]
                    dict_values[f'{param_2}_{table_name_2}'] = value_2[0]
                    if table_name_1 != 'data_las':
                        name = session.query(table_1.name).filter(table_1.depth >= d, table_1.depth < d + 0.1,
                                                                  table_1.well_id == w_id).first()
                        dict_values['name'] = name[0]
                    if ui.listWidget_relation.count() > 2:
                        value_3 = session.query(literal_column(f'{table_name_3}.{param_3}')).filter(table_3.depth >= d,
                                                                                                    table_3.depth < d + 0.1,
                                                                                                    table_3.well_id == w_id).first()
                        if value_3:
                            if value_3[0]:
                                dict_values[f'{param_3}_{table_name_3}'] = value_3[0]
                                if ui.listWidget_relation.count() > 3:
                                    value_4 = session.query(literal_column(f'{table_name_4}.{param_4}')).filter(
                                        table_4.depth >= d,
                                        table_4.depth < d + 0.1, table_4.well_id == w_id).first()
                                    if value_4:
                                        if value_4[0]:
                                            dict_values[f'{param_4}_{table_name_4}'] = value_4[0]
            if table_name_1 != 'data_las':
                if len(dict_values) == ui.listWidget_relation.count() + 1:
                    data = data.append(dict_values, ignore_index=True)
            else:
                if len(dict_values) == ui.listWidget_relation.count():
                    data = data.append(dict_values, ignore_index=True)
            d += 0.1
            n += 1
            ui.progressBar.setValue(n)
    except AttributeError:
        ui.label_info.setText(f'Внимание! Параметры не выбраны или выбран только один параметр.')
        ui.label_info.setStyleSheet('color: red')
    try:
        file_name = f'{ui.comboBox_area.currentText()}_скв.{ui.comboBox_well.currentText()}_{param_1}_{param_2}.xlsx'
        fn = QFileDialog.getSaveFileName(caption="Сохранить параметры в таблицу", directory=file_name,
                                         filter="Excel Files (*.xlsx)")
        data.to_excel(fn[0])
        ui.label_info.setText(f'Таблица сохранена в файл: {fn[0]}')
        ui.label_info.setStyleSheet('color: green')
    except ValueError:
        pass


def clear_param_relation():
    """ Очистка списка выбранных параметров """
    ui.listWidget_relation.clear()


def del_param_rel():
    """ Удалить выбранный параметр """
    ui.listWidget_relation.takeItem(ui.listWidget_relation.currentRow())


def del_param_srav():
    """ Удалить выбранный параметр """
    try:
        param = ui.listWidget_param.currentItem().text()
        session.query(DrawSeveralGraph).filter(DrawSeveralGraph.param == param).delete()
        session.commit()
        ui.listWidget_param.takeItem(ui.listWidget_param.currentRow())
    except AttributeError:
        ui.label_info.setText(f'Параметр не выбран.')
        ui.label_info.setStyleSheet('color: red')


def add_param_corr():
    """ Добавление параметра для расчёта корреляций """
    table, table_text, widget = check_tabWidjet()
    try:
        param = widget.currentItem().text()
        if ui.listWidget_correlation.findItems(f'{param} {table_text}', QtCore.Qt.MatchExactly):
            ui.label_info.setText(f'Внимание! Параметр "{param}" уже добавлен.')
            ui.label_info.setStyleSheet('color: red')
        else:
            ui.listWidget_correlation.addItem(f'{param} {table_text}')
            ui.label_info.setText(f'Параметр {param} добавлен.')
            ui.label_info.setStyleSheet('color: green')
    except AttributeError:
        ui.label_info.setText(f'Внимание! Не выбран параметр.')
        ui.label_info.setStyleSheet('color: red')


def add_all_param_corr():
    """ Добавление всех параметров выбранной таблицы для расчёта корреляций """
    table, table_text, widget = check_tabWidjet()
    no_add = ''
    for i in range(widget.count()):
        param = widget.item(i).text()
        if ui.listWidget_correlation.findItems(f'{param} {table_text}', QtCore.Qt.MatchExactly):
            no_add += f'{param}, '
            ui.label_info.setText(f'Внимание! Параметры {no_add} уже добавлены.')
            ui.label_info.setStyleSheet('color: red')
        else:
            ui.listWidget_correlation.addItem(f'{param} {table_text}')


def clear_param_corr():
    """ Очистка списка выбранных параметров """
    ui.listWidget_correlation.clear()


def del_param_corr():
    """ Удалить выбранный параметр """
    ui.listWidget_correlation.takeItem(ui.listWidget_correlation.currentRow())


def calc_corr():
    """ Рассчитать корреляцию """
    w_id = get_well_id()
    list_column, list_param, list_tab = [], [], []
    for i in range(ui.listWidget_correlation.count()):
        item = ui.listWidget_correlation.item(i).text().split(' ')
        list_param.append(item[0])
        list_tab.append(item[1])
        list_column.append(ui.listWidget_correlation.item(i).text())
    data_corr = pd.DataFrame(columns=list_column)
    start, stop = check_start_stop()
    ui.progressBar.setMaximum(int((stop - start) / 0.1))
    d, n = start, 0
    while d <= stop:
        d = round(d, 2)
        dict_values = {}
        for i in range(len(list_param)):
            table = get_table(list_tab[i])
            value = session.query(literal_column(f'{list_tab[i]}.{list_param[i]}')).filter(
                table.depth >= d, table.depth < d + 0.1, table.well_id == w_id).first()
            if value:
                if value[0]:
                    dict_values[f'{list_param[i]} {list_tab[i]}'] = value[0]
            if len(dict_values) == len(list_param):
                data_corr = data_corr.append(dict_values, ignore_index=True)
        d += 0.1
        n += 1
        ui.progressBar.setValue(n)
    fig = plt.figure(figsize=(14, 12), dpi=70)
    ax = plt.subplot()
    sns.heatmap(data_corr.corr(), xticklabels=list_param, yticklabels=list_param, cmap='seismic', annot=True, linewidths=0.25, center=0)
    plt.title(f'Корреляция параметров по {len(data_corr.index)} измерениям', fontsize=22)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    fig.tight_layout()
    fig.show()
    if ui.checkBox_save_data_corr.isChecked():  # сохранение результирующей таблицы в файл XLS
        try:
            file_name = f'{"_".join(list_param)}_{ui.comboBox_area.currentText()}_скв.' \
                        f'{ui.comboBox_well.currentText()}.xlsx'
            fn = QFileDialog.getSaveFileName(caption="Сохранить параметры для корреляции в таблицу",
                                             directory=file_name,
                                             filter="Excel Files (*.xlsx)")
            data_corr.to_excel(fn[0])
            ui.label_info.setText(f'Таблица сохранена в файл: {fn[0]}')
            ui.label_info.setStyleSheet('color: green')
        except ValueError:
            pass
