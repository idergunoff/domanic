from functions import *


def add_user_interval():
    """ Добавление пользовательского интервала """
    title = ui.lineEdit_string.text() if ui.lineEdit_string.text() else '---'
    message = f'Добавление пользовательского интервала для скважины № {ui.comboBox_well.currentText()} ' \
              f'({ui.comboBox_area.currentText()} площадь).\nИнтервал - "{title}" ' \
              f'от {ui.doubleSpinBox_start.value()} до {ui.doubleSpinBox_stop.value()} м, ' \
              f'цвет - {ui.pushButton_color.text()}'
    result = QtWidgets.QMessageBox.question(ui.listWidget_user_int, 'Добавление интервала', message, QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
    if result == QtWidgets.QMessageBox.Yes:
        new_user_interval = UserInterval(well_id=get_well_id(),
                                         int_from=ui.doubleSpinBox_start.value(),
                                         int_to=ui.doubleSpinBox_stop.value(),
                                         color=ui.pushButton_color.text(),
                                         title=title
                                         )
        session.add(new_user_interval)
        session.commit()
        ui.label_info.setText(f'Добавлен интервала "{title}" для скважины № {ui.comboBox_well.currentText()} '
                              f'({ui.comboBox_area.currentText()} площадь) {ui.doubleSpinBox_start.value()} - '
                              f'{ui.doubleSpinBox_stop.value()} м')
        ui.label_info.setStyleSheet('color: green')
        user_interval_list_update()
    elif result == QtWidgets.QMessageBox.No:
        pass


def add_user_interval_from_category():
    """ Добавление пользовательского интервала из категорий классификации """
    for n, int in enumerate(session.query(IntervalFromCat).all()):
        new_user_interval = UserInterval(well_id=get_well_id(),
                                         int_from=int.int_from,
                                         int_to=int.int_to,
                                         color=get_random_color(),
                                         title='cat_' + str(n + 1)
                                         )
        session.add(new_user_interval)
    session.commit()
    user_interval_list_update()


def edit_user_interval():
    """ Редактирование пользовательского интервала """
    for i in range(ui.listWidget_user_int.count()):
        item = ui.listWidget_user_int.item(i)
        if isinstance(item, QListWidgetItem):
            checkbox = ui.listWidget_user_int.itemWidget(item)
            if isinstance(checkbox, QCheckBox) and checkbox.isChecked():
                interv = session.query(UserInterval).filter_by(id=checkbox.property('interval_id')).first()

                Edit_User_Int = QtWidgets.QDialog()
                ui_eui = Ui_edit_user_int()
                ui_eui.setupUi(Edit_User_Int)

                Edit_User_Int.show()
                Edit_User_Int.setAttribute(QtCore.Qt.WA_DeleteOnClose)  # атрибут удаления виджета после закрытия
                ui_eui.doubleSpinBox_start.setValue(interv.int_from)
                ui_eui.doubleSpinBox_stop.setValue(interv.int_to)
                ui_eui.lineEdit_title.setText(interv.title)
                ui_eui.pushButton_color.setText(interv.color)
                ui_eui.pushButton_color.setStyleSheet(f'background-color: {interv.color}')

                def edit_user_int_color():
                    button_color = ui_eui.pushButton_color.palette().color(ui_eui.pushButton_color.backgroundRole())
                    color = QColorDialog.getColor(button_color)
                    ui_eui.pushButton_color.setStyleSheet(f"background-color: {color.name()};")
                    ui_eui.pushButton_color.setText(color.name())

                def edit_user_int():
                    new_start = ui_eui.doubleSpinBox_start.value()
                    new_stop = ui_eui.doubleSpinBox_stop.value()
                    new_color = ui_eui.pushButton_color.text()
                    new_title = ui_eui.lineEdit_title.text() if ui_eui.lineEdit_title.text() else '---'
                    session.query(UserInterval).filter_by(id=interv.id).update({
                        UserInterval.int_from: new_start,
                        UserInterval.int_to: new_stop,
                        UserInterval.color: new_color,
                        UserInterval.title: new_title}, synchronize_session='fetch')
                    session.commit()
                    user_interval_list_update()
                    check_draw_user_intervals()
                    Edit_User_Int.close()
                    ui.label_info.setText(f'Интервал "{new_title}" изменён.')
                    ui.label_info.setStyleSheet('color: green')

                def cancel_edit_user_int():
                    Edit_User_Int.close()

                ui_eui.pushButton_color.clicked.connect(edit_user_int_color)
                ui_eui.buttonBox.accepted.connect(edit_user_int)
                ui_eui.buttonBox.rejected.connect(cancel_edit_user_int)
                Edit_User_Int.exec_()
                # title = ui.lineEdit_string.text() if ui.lineEdit_string.text() else '---'
                # message = f'Вы действительно хотите интервал с\n"{int.title} {int.int_from}-{int.int_to} м. ' \
                #           f'{int.color}"\nна\n"{title} {ui.doubleSpinBox_start.value()}-' \
                #           f'{ui.doubleSpinBox_stop.value()} м. {ui.pushButton_color.text()}"?'
                # result = QtWidgets.QMessageBox.question(ui.listWidget_user_int, 'Добавление интервала', message,
                #                                         QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
                # if result == QtWidgets.QMessageBox.Yes:
                #     session.query(UserInterval).filter_by(id=checkbox.property('interval_id')).update({
                #         'title': title,
                #         'int_from': ui.doubleSpinBox_start.value(),
                #         'int_to': ui.doubleSpinBox_stop.value(),
                #         'color': ui.pushButton_color.text()
                #     }, synchronize_session='fetch')
                #     session.commit()
                #     ui.label_info.setText(f'Интервал "{title}" изменён.')
                #     ui.label_info.setStyleSheet('color: green')
                #     user_interval_list_update()
                # elif result == QtWidgets.QMessageBox.No:
                #     pass
                return


def delete_user_interval():
    """ Удаление пользовательского интервала """
    for i in range(ui.listWidget_user_int.count()):
        item = ui.listWidget_user_int.item(i)
        if isinstance(item, QListWidgetItem):
            checkbox = ui.listWidget_user_int.itemWidget(item)
            if isinstance(checkbox, QCheckBox) and checkbox.isChecked():
                message = f'Вы действительно хотите удалить интервал "{checkbox.text()}"?'
                result = QtWidgets.QMessageBox.question(ui.listWidget_user_int, 'Удаление интервала', message,
                                                        QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
                if result == QtWidgets.QMessageBox.Yes:
                    session.query(UserInterval).filter_by(id=checkbox.property('interval_id')).delete()
                    ui.label_info.setText(f'Интервала "{checkbox.text()}" успешно удалён.')
                    ui.label_info.setStyleSheet('color: green')
                elif result == QtWidgets.QMessageBox.No:
                    pass
    session.commit()
    user_interval_list_update()
    check_draw_user_intervals()


def user_interval_list_update():
    """ Обновление списка пользовательских интервалов """
    ui.listWidget_user_int.clear()
    intervals = session.query(UserInterval).filter_by(well_id=get_well_id()).order_by(UserInterval.int_from).all()
    for int in intervals:
        check_box_widget = QCheckBox(f'{int.title} {int.int_from} - {int.int_to} м')
        check_box_widget.setStyleSheet(f'background-color:{int.color}')
        check_box_widget.setProperty('interval_id', int.id)
        # check_box_widget.clicked.connect(choose_current_user_interval)
        check_box_widget.clicked.connect(check_draw_user_intervals)
        list_item = QListWidgetItem()
        # list_item.setSizeHint(check_box_widget.sizeHint())  # установить размер элемента
        ui.listWidget_user_int.addItem(list_item)
        ui.listWidget_user_int.setItemWidget(list_item, check_box_widget)


def user_interval_to_work():
    """ Отправка пользовательского интервала в категории для расчета """
    del_category_to_resource()
    for i in range(ui.listWidget_user_int.count()):
        item = ui.listWidget_user_int.item(i)
        if isinstance(item, QListWidgetItem):
            checkbox = ui.listWidget_user_int.itemWidget(item)
            if isinstance(checkbox, QCheckBox) and checkbox.isChecked():
                int = session.query(UserInterval).filter_by(id=checkbox.property('interval_id')).first()
                new_checkbox = QtWidgets.QCheckBox()
                font = QtGui.QFont()
                font.setPointSize(9)
                new_checkbox.setFont(font)
                new_checkbox.setText(checkbox.text())
                ui.gridLayout_resourse.addWidget(new_checkbox)
                new_checkbox.setStyleSheet(f'background-color:{int.color}')
                new_checkbox.setProperty('interval_id', int.id)
                new_checkbox.clicked.connect(user_interval_to_db)


def draw_user_interval(int):
    """ Отрисовка пользовательского интервала """
    vb = ui.graphicsView.getViewBox()
    xMin, xMax = vb.viewRange()[0]
    yMin, yMax = vb.viewRange()[1]
    l_from = pg.PlotCurveItem(x=[xMin, xMax], y=[int.int_from, int.int_from], pen=pg.mkPen(color=int.color, width=1.5, dash=[8, 2]))
    l_to = pg.PlotCurveItem(x=[xMin, xMax], y=[int.int_to, int.int_to], pen=pg.mkPen(color=int.color, width=1.5, dash=[8, 2]))
    poly_item = pg.FillBetweenItem(curve1=l_from, curve2=l_to, brush=int.color+'40')
    ui.graphicsView.addItem(l_from)
    ui.graphicsView.addItem(l_to)
    ui.graphicsView.addItem(poly_item)
    # ui.graphicsView.setXRange(xMin, xMax)
    # ui.graphicsView.setYRange(yMin, yMax)
    ui.graphicsView.setRange(xRange=[xMin, xMax], padding=0)
    globals()[f'user_int_from' + int.title] = l_from
    globals()[f'user_int_to' + int.title] = l_to
    globals()[f'user_int_poly' + int.title] = poly_item


def choose_all_user_interval():
    """ Выбор всех пользовательских интервалов """
    if ui.checkBox_choose_all_user_int.isChecked():
        all_user_interval_set_checked(True)
    else:
        all_user_interval_set_checked(False)
    check_draw_user_intervals()


def all_user_interval_set_checked(check: bool):
    for i in range(ui.listWidget_user_int.count()):
        item = ui.listWidget_user_int.item(i)
        if isinstance(item, QListWidgetItem):
            checkbox = ui.listWidget_user_int.itemWidget(item)
            if isinstance(checkbox, QCheckBox):
                checkbox.setChecked(check)


def check_draw_user_intervals():
    """Проверка и отрисовка пользовательских интервалов"""
    clear_globals('user_int_')
    for i in range(ui.listWidget_user_int.count()):
        item = ui.listWidget_user_int.item(i)
        if isinstance(item, QListWidgetItem):
            checkbox = ui.listWidget_user_int.itemWidget(item)
            if isinstance(checkbox, QCheckBox) and checkbox.isChecked():
                int = session.query(UserInterval).filter_by(id=checkbox.property('interval_id')).first()
                draw_user_interval(int)


# def choose_current_user_interval():
#     """ Выбор текущего пользовательского интервала """
#     for i in range(ui.listWidget_user_int.count()):
#         item = ui.listWidget_user_int.item(i)
#         if isinstance(item, QListWidgetItem):
#             checkbox = ui.listWidget_user_int.itemWidget(item)
#             if isinstance(checkbox, QCheckBox) and checkbox.isChecked():
#                 int = session.query(UserInterval).filter_by(id=checkbox.property('interval_id')).first()
#                 ui.doubleSpinBox_start.setValue(int.int_from)
#                 ui.doubleSpinBox_stop.setValue(int.int_to)
#                 ui.doubleSpinBox_start.setValue(int.int_from)
#                 ui.lineEdit_string.setText(int.title)
#                 ui.pushButton_color.setStyleSheet(f"background-color: {int.color};")
#                 ui.pushButton_color.setText(int.color)
#                 return


def user_interval_to_db():
    session.query(IntervalFromCat).delete()
    text_int = 'Выбраны интервалы: '
    text_int_res = 'Расчёт русурсов в интервалах: '
    for i in ui.cat_resource.findChildren(QtWidgets.QCheckBox):
        if i.isChecked():
            interv = session.query(UserInterval).filter_by(id=i.property('interval_id')).first()
            text_int += f'{interv.title}, '
            new_int = IntervalFromCat(int_from=interv.int_from, int_to=interv.int_to)
            session.add(new_int)
            text_int_res += f'\n{str(interv.int_from)} - {str(interv.int_to)} м.'
    session.commit()
    ui.label_int.setText(text_int)
    ui.label_int_resource.setText(text_int_res)


def clear_globals(start_key: str):
    for key, value in globals().items():
        if key.startswith(start_key):
            ui.graphicsView.removeItem(globals()[key])
