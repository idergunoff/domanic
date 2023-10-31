from functions import *


def update_list_calculated_data():
    """  Обновление списка расчетных данных """

    ui.listWidget_calc_data.clear()
    for calc_data in session.query(CalculatedData).filter_by(well_id=get_well_id()).all():
        ui.listWidget_calc_data.addItem(f'{calc_data.title} id{calc_data.id}')


def show_calc_data():
    """ Отображение выбранных расчетных данных """
    calc_data = get_calc_data()
    if calc_data:
        show_info_calc_data(calc_data)
        draw_graph_calc_data(calc_data)
        show_table_calc_data(calc_data)
        list_depth = [float(key) for key in json.loads(calc_data.data).keys()]
        ui.doubleSpinBox_start.setValue(min(list_depth))
        ui.doubleSpinBox_stop.setValue(max(list_depth))


def show_info_calc_data(calc_data):
    """ Отобразить информацию о расчетных данных """
    ui.textEdit_calc_data_info.clear()
    ui.textEdit_calc_data_info.append(
        f'<p><b>Model:</b> {calc_data.model_title}</p>'
        f'<p><b>Model parameters:</b> {", ".join([i.split(".")[-1] for i in json.loads(calc_data.list_params_model)])}</p>'
        f'<p><b>Model wells:</b> {", ".join([i["well"] for i in json.loads(calc_data.list_wells_model)])}</p>'
        f'<p><b>Comment</b>: {calc_data.comment}</p>'
    )


def draw_graph_calc_data(calc_data):
    """ Отобразить график расчетных данных """
    depth = [float(key) for key in (json.loads(calc_data.data).keys())]
    param = list(json.loads(calc_data.data).values())

    ui.graphicsView.clear()
    color = choice_color()
    dash = choice_dash()
    width = choice_width()
    curve = pg.PlotCurveItem(x=param, y=depth, pen=pg.mkPen(color=color, width=width, dash=dash))

    ui.graphicsView.addItem(curve)
    curve.getViewBox().invertY(True)


def show_table_calc_data(calc_data):
    """ Отобразить таблицу расчетных данных """
    data_dict = json.loads(calc_data.data)
    ui.tableWidget.setRowCount(len(data_dict))
    ui.tableWidget.setColumnCount(2)

    # Заполнение данных
    for row, (key, value) in enumerate(data_dict.items()):
        ui.tableWidget.setItem(row, 0, QTableWidgetItem(str(key)))
        ui.tableWidget.setItem(row, 1, QTableWidgetItem(str(value)))

    # Заголовки столбцов
    ui.tableWidget.verticalHeader().hide()
    ui.tableWidget.resizeColumnsToContents()
    ui.label_table_name.setText(f'Расчетный {calc_data.title} по скв. {ui.comboBox_well.currentText()}')


def delete_calc_data():
    """ Удаление выбранных расчетных данных """
    calc_data = get_calc_data()
    session.delete(calc_data)
    session.commit()
    update_list_calculated_data()


def cut_calc_data():
    """ Обрезка выбранных расчетных данных """
    start, stop = check_start_stop()
    calc_data = get_calc_data()
    dict_data = json.loads(calc_data.data)
    for key in dict_data.copy().keys():
        if float(key) < start or float(key) > stop:
            del dict_data[key]
    session.query(CalculatedData).filter_by(id=calc_data.id).update({'data': json.dumps(dict_data)})
    session.commit()
    show_table_calc_data(calc_data)
    draw_graph_calc_data(calc_data)