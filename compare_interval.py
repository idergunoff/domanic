import pandas as pd

from functions import *


def add_compare_interval():
    """ Добавление интервала сравнения """
    list_int_text = []
    for i in range(ui.listWidget_user_int.count()):
        item = ui.listWidget_user_int.item(i)
        if isinstance(item, QListWidgetItem):
            checkbox = ui.listWidget_user_int.itemWidget(item)
            if isinstance(checkbox, QCheckBox) and checkbox.isChecked():
                user_int = session.query(UserInterval).filter_by(id=checkbox.property('interval_id')).first()
                list_int_text.append(user_int.title)
                new_compare_int = CompareInterval(
                    well_id=user_int.well_id,
                    int_from=user_int.int_from,
                    int_to=user_int.int_to,
                    title=user_int.title,
                    color=user_int.color
                )
                session.add(new_compare_int)
    if len(list_int_text) > 0:
        session.commit()
        update_list_compare_interval()
        ui.label_info.setText(f'Интервалы сравнения успешно добавлены: {", ".join(list_int_text)}')
        ui.label_info.setStyleSheet('color: green')


def update_list_compare_interval():
    """ Обновление списка интервалов сравнения """
    ui.listWidget_compare_int.clear()
    intervals = session.query(CompareInterval).all()
    for interval in intervals:
        well = session.query(Well).filter_by(id=interval.well_id).first()
        label_widget = QLabel(f'скв.{well.title} - {interval.title}')
        label_widget.setToolTip(f'{interval.int_from} - {interval.int_to} м')
        label_widget.setStyleSheet(f'background-color:{interval.color}')
        label_widget.setProperty('interval_id', interval.id)
        # check_box_widget.clicked.connect(choose_current_user_interval)
        # check_box_widget.clicked.connect(check_draw_user_intervals)
        list_item = QListWidgetItem()
        # list_item.setSizeHint(check_box_widget.sizeHint())  # установить размер элемента
        ui.listWidget_compare_int.addItem(list_item)
        ui.listWidget_compare_int.setItemWidget(list_item, label_widget)


def delete_compare_interval():
    """ Удаление интервала сравнения """
    curr_item = ui.listWidget_compare_int.currentItem()
    if curr_item is not None:
        int_id = ui.listWidget_compare_int.itemWidget(curr_item).property('interval_id')
        interval = session.query(CompareInterval).filter_by(id=int_id).first()
        title = interval.title
        well = session.query(Well).filter_by(id=interval.well_id).first()
        message = f'Удалить интервал {interval.title} (скв.{well.title}) из списка сравнения интервалов?'
        result = QtWidgets.QMessageBox.question(
            ui.listWidget_compare_int,
            'Удаление интервала',
            message,
            QtWidgets.QMessageBox.Yes,
            QtWidgets.QMessageBox.No
        )
        if result == QtWidgets.QMessageBox.Yes:
            session.delete(interval)
            session.commit()
            ui.label_info.setText(f'Интервал "{title}" удалён из списка сравнения интервалов')
            ui.label_info.setStyleSheet('color: green')
            update_list_compare_interval()
        elif result == QtWidgets.QMessageBox.No:
            pass

def clear_compare_interval():
    """ Очистка списка интервалов сравнения """
    result = QtWidgets.QMessageBox.question(
        ui.listWidget_compare_int,
        'Очистка списка интервалов',
        'Очистить список интервалов сравнения?',
        QtWidgets.QMessageBox.Yes,
        QtWidgets.QMessageBox.No
    )
    if result == QtWidgets.QMessageBox.Yes:
        session.query(CompareInterval).delete()
        session.commit()
        ui.label_info.setText('Список интервалов очищен.')
        ui.label_info.setStyleSheet('color: green')
        update_list_compare_interval()
    elif result == QtWidgets.QMessageBox.No:
        pass


def add_compare_parameter():
    """ Добавление параметра сравнения """
    table, table_text, widget = check_tabWidjet()
    try:
        param = widget.currentItem().text()
        if ui.listWidget_compare_param.findItems(f'{param} {table_text}', QtCore.Qt.MatchExactly):
            ui.label_info.setText(f'Внимание! Параметр "{param}" уже добавлен.')
            ui.label_info.setStyleSheet('color: red')
        else:
            ui.listWidget_compare_param.addItem(f'{table_text} {param}')
    except AttributeError:
        ui.label_info.setText(f'Внимание! Не выбран параметр.')
        ui.label_info.setStyleSheet('color: red')


def delete_compare_parameter():
    """ Удаление параметра сравнения """
    curr_item = ui.listWidget_compare_param.currentItem()
    if curr_item is not None:
        item = ui.listWidget_compare_param.takeItem(ui.listWidget_compare_param.row(curr_item))
        ui.label_info.setText(f'Параметр "{item.text()}" удален.')
        ui.label_info.setStyleSheet('color: green')


def clear_compare_parameter():
    """ Очистка списка параметров сравнения """
    ui.listWidget_compare_param.clear()
    ui.label_info.setText('Список параметров очищен.')
    ui.label_info.setStyleSheet('color: green')


def table_compare_interval():
    """ Отображение таблицы сравнения интервалов """
    Compare_Table = QtWidgets.QDialog()
    ui_cit = Ui_CompareTableInt()
    ui_cit.setupUi(Compare_Table)
    Compare_Table.show()
    Compare_Table.setAttribute(QtCore.Qt.WA_DeleteOnClose)  # атрибут удаления виджета после закрытия
    ui_cit.tableWidget.setColumnCount(12)
    header_list = ['Парам.', 'Инт-л', 'Кол-во', 'Мин', 'Макс', 'Ср.арифм.', 'Ср.геом', 'Медиана', 'Ассим.', 'Эксцесс', 'Норм.ассим', 'Норм.эксцесс']
    ui_cit.tableWidget.setHorizontalHeaderLabels(header_list)
    pd_compare, list_int_id, list_param = get_table_compare_interval()
    pd_stat = pd.DataFrame(columns=header_list)
    n_row = 0
    for param in list_param:
        for int_id in list_int_id:
            stat_dict = {}
            ui_cit.tableWidget.insertRow(n_row)
            interval = session.query(CompareInterval).filter(CompareInterval.id == int_id).first()
            values = pd_compare[param].loc[pd_compare['int_id'] == int_id]
            values = remove_nan(values.tolist())
            ui_cit.tableWidget.setVerticalHeaderItem(n_row, QtWidgets.QTableWidgetItem(f'{interval.title} {param.split(" ")[1]}'))
            ui_cit.tableWidget.setItem(n_row, 0, QtWidgets.QTableWidgetItem(param))
            stat_dict['Парам.'] = param
            ui_cit.tableWidget.setItem(n_row, 1, QtWidgets.QTableWidgetItem(interval.title))
            stat_dict['Инт-л'] = interval.id
            if len(values) == 0:
                ui_cit.tableWidget.setItem(n_row, 2, QtWidgets.QTableWidgetItem('0'))
                for col in range(3, 12):
                    ui_cit.tableWidget.setItem(n_row, col, QtWidgets.QTableWidgetItem('empty'))
                for p in header_list[2:]:
                    stat_dict[p] = 0
                set_row_background_color(ui_cit.tableWidget, n_row, interval.color)
                pd_stat = pd.concat([pd_stat, pd.DataFrame([stat_dict])], ignore_index=True)
                n_row += 1
                continue
            stats = describe(values)
            nskew = abs(stats.skewness / (6 / stats.nobs) ** 0.5)
            nkurt = abs(stats.kurtosis / (24 / stats.nobs) ** 0.5)
            ui_cit.tableWidget.setItem(n_row, 2, QtWidgets.QTableWidgetItem(str(stats.nobs)))
            stat_dict['Кол-во'] = stats.nobs
            ui_cit.tableWidget.setItem(n_row, 3, QtWidgets.QTableWidgetItem(str(stats.minmax[0])))
            stat_dict['Мин'] = stats.minmax[0]
            ui_cit.tableWidget.setItem(n_row, 4, QtWidgets.QTableWidgetItem(str(stats.minmax[1])))
            stat_dict['Макс'] = stats.minmax[1]
            ui_cit.tableWidget.setItem(n_row, 5, QtWidgets.QTableWidgetItem(str(round(stats.mean, 5))))
            stat_dict['Ср.арифм.'] = round(stats.mean, 5)
            ui_cit.tableWidget.setItem(n_row, 6, QtWidgets.QTableWidgetItem(str(round(gmean(values), 5))))
            stat_dict['Ср.геом'] = round(gmean(values), 5)
            ui_cit.tableWidget.setItem(n_row, 7, QtWidgets.QTableWidgetItem(str(round(median(values), 5))))
            stat_dict['Медиана'] = round(median(values), 5)
            ui_cit.tableWidget.setItem(n_row, 8, QtWidgets.QTableWidgetItem(str(round(stats.skewness, 5))))
            stat_dict['Ассим.'] = round(stats.skewness, 5)
            ui_cit.tableWidget.setItem(n_row, 9, QtWidgets.QTableWidgetItem(str(round(stats.kurtosis, 5))))
            stat_dict['Эксцесс'] = round(stats.kurtosis, 5)
            ui_cit.tableWidget.setItem(n_row, 10, QtWidgets.QTableWidgetItem(str(round(nskew, 5))))
            stat_dict['Норм.ассим'] = round(nskew, 5)
            ui_cit.tableWidget.setItem(n_row, 11, QtWidgets.QTableWidgetItem(str(round(nkurt, 5))))
            stat_dict['Норм.эксцесс'] = round(nkurt, 5)
            set_row_background_color(ui_cit.tableWidget, n_row, interval.color)
            pd_stat = pd.concat([pd_stat, pd.DataFrame([stat_dict])], ignore_index=True)
            n_row += 1
    alignment_table(ui_cit.tableWidget)
    ui.label_info.setText('Таблица сравнения интервалов построена.')
    ui.label_info.setStyleSheet('color: green')

    def click_compare_table():
        """ При клике по таблице выделение построение столбчатой диаграммы """
        cell = ui_cit.tableWidget.currentItem()
        table_param = ui_cit.tableWidget.item(cell.row(), 0).text()
        stat_param = ui_cit.tableWidget.horizontalHeaderItem(cell.column()).text()
        if stat_param in ['Парам.', 'Инт-л']:
            return
        int_ids = pd_stat['Инт-л'].loc[pd_stat['Парам.'] == table_param]
        x, color = [], []
        for int_id in int_ids:
            intl = session.query(CompareInterval).filter(CompareInterval.id == int_id).first()
            x.append(intl.title)
            color.append(intl.color)
        y = pd_stat[stat_param].loc[pd_stat['Парам.'] == table_param]
        fig = plt.figure(figsize=(10, 10), dpi=80)
        ax = plt.subplot()
        ax.bar(x, y, color=color)
        ax.grid(True)
        plt.title(f'{table_param} - {stat_param}')
        fig.tight_layout()
        fig.show()

    def save_table_compare_stat():
        """ Сохранение таблицы сравнения интервалов """
        file_name = QFileDialog.getSaveFileName(None, 'Сохранить таблицу стаистики сравнения интервалов', '', '*.xlsx')[0]
        if file_name:
            for row in pd_stat.index:
                intl = session.query(CompareInterval).filter(CompareInterval.id == pd_stat['Инт-л'][row]).first()
                pd_stat['Инт-л'][row] = intl.title
            pd_stat.to_excel(file_name, index=False)
            ui.label_info.setText(f'Таблица сравнения интервалов сохранена в файл: {file_name}.')
            ui.label_info.setStyleSheet('color: green')

    ui_cit.tableWidget.clicked.connect(click_compare_table)
    ui_cit.pushButton_save.clicked.connect(save_table_compare_stat)

    Compare_Table.exec_()


def get_table_compare_interval():
    """ Рассчёт параметров для интервалов сравнения и отображение в таблице """
    list_param = [ui.listWidget_compare_param.item(i).text() for i in range(ui.listWidget_compare_param.count())]
    pd_compare = pd.DataFrame(columns=['int_id', 'title', 'color']+list_param)
    list_int_id = []
    for i in range(ui.listWidget_compare_int.count()):
        int_id = ui.listWidget_compare_int.itemWidget(ui.listWidget_compare_int.item(i)).property('interval_id')
        pd_compare = pd.concat([pd_compare, get_pamameters_for_interval(int_id, list_param)], ignore_index=True)
        list_int_id.append(int_id)
    return pd_compare, list_int_id, list_param


def draw_compare_interval():
    """ Отрисовка интервалов сравнения """
    pd_compare, list_int_id, list_param = get_table_compare_interval()
    list_stat_param = get_list_stat_checkbox()
    pd_stat = pd.DataFrame(columns=['Парам.', 'Инт-л', 'title', 'color'] + list_stat_param)
    for param in list_param:
        for int_id in list_int_id:
            stat_dict = {}
            interval = session.query(CompareInterval).filter(CompareInterval.id == int_id).first()
            values = pd_compare[param].loc[pd_compare['int_id'] == int_id]
            values = remove_nan(values.tolist())
            stat_dict['Парам.'] = param
            stat_dict['Инт-л'] = interval.id
            stat_dict['title'] = interval.title
            stat_dict['color'] = interval.color
            if len(values) == 0:
                for p in list_stat_param:
                    stat_dict[p] = 0
                pd_stat = pd.concat([pd_stat, pd.DataFrame([stat_dict])], ignore_index=True)
                continue
            stats = describe(values)
            if 'Кол-во' in list_stat_param:
                stat_dict['Кол-во'] = stats.nobs
            if 'Мин' in list_stat_param:
                stat_dict['Мин'] = stats.minmax[0]
            if 'Макс' in list_stat_param:
                stat_dict['Макс'] = stats.minmax[1]
            if 'Ср.арифм.' in list_stat_param:
                stat_dict['Ср.арифм.'] = round(stats.mean, 5)
            if 'Ср.геом.' in list_stat_param:
                stat_dict['Ср.геом'] = round(gmean(values), 5)
            if 'Медиана' in list_stat_param:
                stat_dict['Медиана'] = round(median(values), 5)
            if 'Ассим.' in list_stat_param:
                stat_dict['Ассим.'] = round(stats.skewness, 5)
            if 'Эксцесс' in list_stat_param:
                stat_dict['Эксцесс'] = round(stats.kurtosis, 5)
            if 'Норм.ассим' in list_stat_param:
                nskew = abs(stats.skewness / (6 / stats.nobs) ** 0.5)
                stat_dict['Норм.ассим'] = round(nskew, 5)
            if 'Норм.эксцесс' in list_stat_param:
                nkurt = abs(stats.kurtosis / (24 / stats.nobs) ** 0.5)
                stat_dict['Норм.эксцесс'] = round(nkurt, 5)
            pd_stat = pd.concat([pd_stat, pd.DataFrame([stat_dict])], ignore_index=True)
    print(pd_stat)
    # создание фигуры и основного контейнера для графиков
    fig = plt.figure(figsize=(10, 8))
    grid = fig.add_gridspec(nrows=len(list_param), ncols=len(list_stat_param))
    for i in range(len(list_param)):
        for j in range(len(list_stat_param)):
            ax = fig.add_subplot(grid[i, j])
            ax.bar(pd_stat['title'].loc[pd_stat['Парам.'] == list_param[i]],
                   pd_stat[list_stat_param[j]].loc[pd_stat['Парам.'] == list_param[i]],
                   color=pd_stat['color'].loc[pd_stat['Парам.'] == list_param[i]])
            ax.set_title(list_param[i] + ' ' + list_stat_param[j])
    plt.tight_layout()
    plt.show()

def matrix_compare_interval():
    """ Отрисовка матрицы интервалов сравнения """
    pd_compare, list_int_id, list_param = get_table_compare_interval()
    del pd_compare['int_id']
    sns_plot = sns.pairplot(pd_compare, hue='title', palette=sns.color_palette(pd_compare['color'].unique()))
    sns_plot.fig.suptitle('Матрица интервалов сравнения')
    sns_plot.tight_layout()
    plt.show()

def save_compare_interval():
    """ Сохранение таблицы параметров интервалов сравнения """
    pass


def get_pamameters_for_interval(int_id, list_param):
    """ Получение параметров для интервала сравнения """
    interval = session.query(CompareInterval).filter_by(id=int_id).first()
    pd_interval = pd.DataFrame()
    for param in list_param:
        pd_interval[param] = get_param_for_int(interval.well_id, interval.int_from, interval.int_to, param)
    pd_interval['int_id'] = [int_id] * len(pd_interval.index)
    intl = session.query(CompareInterval).filter_by(id=int_id).first()
    pd_interval['title'] = [intl.title] * len(pd_interval.index)
    pd_interval['color'] = [intl.color] * len(pd_interval.index)
    return pd_interval


def get_param_for_int(w_id, int_from, int_to, tab_param):
    """ Получение списка значений параметра для интервала """
    ui.label_info.setText(f'Получение параметра {tab_param} для интервала {int_from} - {int_to}')
    ui.label_info.setStyleSheet('color: blue')
    ui.progressBar.setMaximum(int((int_to - int_from) * 10))
    progres, d, list_value = 0, int_from, []
    table, param = tab_param.split(' ')[0], tab_param.split(' ')[1]
    tab = get_table(table)
    while d <= int_to:
        progres += 1
        ui.progressBar.setValue(progres)
        value = session.query(literal_column(f'{table}.{param}')).filter(
            tab.depth >= d, tab.depth <= d + 0.1, tab.well_id == w_id
        ).first()
        if value:
            list_value.append(value[0])
        else:
            list_value.append(None)
        d += 0.1
    return list_value


def add_stat_checkbox():
    """ Добавление чекбокса для статистики """
    ui.listWidget_compare_stat.clear()
    stat_list = ['Кол-во', 'Мин', 'Макс', 'Ср.арифм.', 'Ср.геом', 'Медиана', 'Ассим.', 'Эксцесс', 'Норм.ассим', 'Норм.эксцесс']
    for stat in stat_list:
        check_box_widget = QCheckBox(stat)
        list_item = QListWidgetItem()
        ui.listWidget_compare_stat.addItem(list_item)
        ui.listWidget_compare_stat.setItemWidget(list_item, check_box_widget)


def get_list_stat_checkbox():
    """ Получение списка чекбоксов для статистики """
    list_stat = []
    for i in range(ui.listWidget_compare_stat.count()):
        if ui.listWidget_compare_stat.itemWidget(ui.listWidget_compare_stat.item(i)).isChecked():
            list_stat.append(ui.listWidget_compare_stat.itemWidget(ui.listWidget_compare_stat.item(i)).text())
    return list_stat
