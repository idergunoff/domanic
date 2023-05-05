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
            ui.listWidget_compare_param.addItem(f'{param} {table_text}')
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
   """ Рассчёт параметров для интервалов сравнения и отображение в таблице """
   pass


def draw_compare_interval():
   """ Отрисовка интервалов сравнения """
   pass


def matrix_compare_interval():
   """ Отрисовка матрицы интервалов сравнения """
   pass


def save_compare_interval():
   """ Сохранение таблицы параметров интервалов сравнения """
   pass