from functions import *


def comboBox_region_update():
    """Обновление выпадающего списка регионов"""
    ui.comboBox_region.clear()
    for i in session.query(Region).order_by(Region.title).all():
        ui.comboBox_region.addItem(i.title)
    comboBox_area_update()


def comboBox_area_update():
    """Обновление выпадающего списка площадей"""
    ui.comboBox_area.clear()
    for i in session.query(Area).join(Region).filter(Region.title == ui.comboBox_region.currentText()). \
            order_by(Area.title).all():
        ui.comboBox_area.addItem(i.title)
    comboBox_well_update()


def comboBox_well_update():
    """Обновление выпадающего списка скважин"""
    ui.comboBox_well.clear()
    for i in session.query(Well).join(Area).join(Region). \
            filter(Area.title == ui.comboBox_area.currentText(), Region.title == ui.comboBox_region.currentText()). \
            order_by(Well.title).all():
        ui.comboBox_well.addItem(i.title)
    well_interval()


def add_region():
    """Добавить ноывый регион в БД"""
    Add_Region = QtWidgets.QDialog()
    ui_ar = Ui_add_region()
    ui_ar.setupUi(Add_Region)
    Add_Region.show()
    Add_Region.setAttribute(QtCore.Qt.WA_DeleteOnClose)  # атрибут удаления виджета после закрытия

    def region_to_db():
        name_region = ui_ar.lineEdit.text()
        if name_region != '':
            new_region = Region(title=name_region)
            try:
                session.add(new_region)
                session.commit()
                comboBox_region_update()
                Add_Region.close()
                ui.label_info.setText(f'Регион "{name_region}" добавлен в базу данных.')
                ui.label_info.setStyleSheet('color: green')
            except IntegrityError:
                ui.label_info.setText(f'Внимание! Ошибка сохранения. Регион "{name_region}" уже есть.')
                ui.label_info.setStyleSheet('color: red')
                session.rollback()

    def cancel_add_region():
        Add_Region.close()

    ui_ar.buttonBox.accepted.connect(region_to_db)
    ui_ar.buttonBox.rejected.connect(cancel_add_region)
    Add_Region.exec_()


def add_area():
    """Добавить ноывую площадь в БД"""
    Add_Area = QtWidgets.QDialog()
    ui_aa = Ui_add_area()
    ui_aa.setupUi(Add_Area)
    Add_Area.show()
    Add_Area.setAttribute(QtCore.Qt.WA_DeleteOnClose)  # атрибут удаления виджета после закрытия
    ui_aa.label_region.setText(ui.comboBox_region.currentText())
    id_region = session.query(Region).filter(Region.title == ui.comboBox_region.currentText()).one()
    ui_aa.id_region.setText(str(id_region.id))

    def area_to_db():
        name_area = ui_aa.lineEdit.text()
        if name_area != '':
            if session.query(Area).join(Region).filter(Region.title == ui.comboBox_region.currentText(),
                                                       Area.title == name_area).count() == 0:
                new_area = Area(title=name_area, region_id=int(ui_aa.id_region.text()))
                try:
                    session.add(new_area)
                    session.commit()
                    comboBox_area_update()
                    Add_Area.close()
                    ui.label_info.setText(f'Площадь "{name_area}" добавлена в базу данных.')
                    ui.label_info.setStyleSheet('color: green')
                except IntegrityError:
                    ui.label_info.setText(f'Внимание! Ошибка сохранения. Не выбран регион.')
                    ui.label_info.setStyleSheet('color: red')
                    session.rollback()
                    Add_Area.close()
            else:
                ui.label_info.setText(f'Внимание! Ошибка сохранения. Площадь "{name_area}" '
                                      f'уже есть в регионе {ui.comboBox_region.currentText()}.')
                ui.label_info.setStyleSheet('color: red')

    def cancel_add_area():
        Add_Area.close()

    ui_aa.buttonBox.accepted.connect(area_to_db)
    ui_aa.buttonBox.rejected.connect(cancel_add_area)
    Add_Area.exec_()


def add_well():
    """Добавить ноывую скважину в БД"""
    Add_Well = QtWidgets.QDialog()
    ui_aw = Ui_add_well()
    ui_aw.setupUi(Add_Well)

    Add_Well.show()
    Add_Well.setAttribute(QtCore.Qt.WA_DeleteOnClose)  # атрибут удаления виджета после закрытия
    ui_aw.label_region.setText(ui.comboBox_region.currentText())
    ui_aw.label_area.setText(ui.comboBox_area.currentText())
    id_area = session.query(Area).join(Region).filter(Region.title == ui.comboBox_region.currentText(),
                                                      Area.title == ui.comboBox_area.currentText()).one()
    ui_aw.id_area.setText(str(id_area.id))

    def well_to_db():
        name_well = ui_aw.lineEdit.text()
        if name_well != '':
            if session.query(Well).join(Area).filter(Area.title == ui.comboBox_area.currentText(),
                                                     Well.title == name_well).count() == 0:
                new_well = Well(title=name_well, area_id=int(ui_aw.id_area.text()))
                try:
                    session.add(new_well)
                    session.commit()
                    comboBox_well_update()
                    Add_Well.close()
                    ui.label_info.setText(f'Скважина "{name_well}" добавлена в базу данных.')
                    ui.label_info.setStyleSheet('color: green')
                except IntegrityError:
                    ui.label_info.setText(f'Внимание! Ошибка сохранения. Не выбрана площадь.')
                    ui.label_info.setStyleSheet('color: red')
                    session.rollback()
                    Add_Well.close()
            else:
                ui.label_info.setText(f'Внимание! Ошибка сохранения. Скважина "{name_well}" '
                                      f'уже есть на площади {ui.comboBox_area.currentText()}.')
                ui.label_info.setStyleSheet('color: red')

    def cancel_add_well():
        Add_Well.close()

    ui_aw.buttonBox.accepted.connect(well_to_db)
    ui_aw.buttonBox.rejected.connect(cancel_add_well)
    Add_Well.exec_()


def well_interval():
    """Считать макс/мин выбранной скважины, установить значения в спинбоксы"""
    ui.doubleSpinBox_start.setValue(0)
    ui.doubleSpinBox_stop.setValue(0)
    if ui.comboBox_well.currentText():
        w_id = get_well_id()
        starts, stops = [], []
        for i in [DataPirolizKern, DataPirolizExtr, DataChromKern, DataChromExtr, DataLas, DataLit]:
            start, stop = select_start_stop_depth(w_id, i)
            if start:
                if start[0] or stop[0]:
                    starts.append(start[0])
                    stops.append(stop[0])
        if len(starts) > 0:
            ui.doubleSpinBox_stop.setValue(max(stops))
            ui.doubleSpinBox_start.setValue(min(starts))
        check_list_param()


def load_data_from_las():
    """Загрузка данных из las-файлов"""
    try:
        file_name = QFileDialog.getOpenFileName(filter='*.las')[0]
        version, start_depth, stop_depth, null_value, param, data_row = read_las_info(file_name)
    except FileNotFoundError:
        return
    add_slots(start_depth, stop_depth)
    well_interval()
    w_id = get_well_id()
    param_result = ''
    no_param = ''
    if type(param) is list:
        for n, p in enumerate(param):
            result = load_param_from_las(p, null_value, file_name, data_row, n, w_id)
            if result:
                param_result += ' ' + p
            else:
                no_param += ' ' + p
    else:
        result = load_param_from_las(param, null_value, file_name, data_row, 0, w_id)
        if result:
            param_result += ' ' + param
        else:
            no_param += ' ' + param
    ui.label_info.setText('Обновление базы данных. Это может занять некоторое время...')
    ui.label_info.setStyleSheet('color: blue')
    session.commit()
    if no_param == '':
        ui.label_info.setText(f'Загружены параметры:{param_result} из файла: {file_name}')
    else:
        ui.label_info.setText(f'Загружены параметры:"{param_result}" из файла: {file_name}, параметры "{no_param}" '
                              f'отсутствуют в базе данных. Проверьте LAS-файл.')
    ui.label_info.setStyleSheet('color: green')
    well_interval()


def load_data_pir():
    """ Загрузка данных пиролиза керна """
    try:
        file_name = QFileDialog.getOpenFileName(filter='*.xls *.xlsx')[0]
        load_param_pir_chrom(file_name, DataPirolizKern, False)
        well_interval()
    except FileNotFoundError:
        return


def load_data_lit():
    """ Загрузка данных по литологии """
    try:
        file_name = QFileDialog.getOpenFileName(filter='*.xls *.xlsx')[0]
        load_param_pir_chrom(file_name, DataLit, False)
        well_interval()
    except FileNotFoundError:
        return


def load_data_pir_extr():
    """ Загрузка данных пиролиза после экстракции """
    try:
        file_name = QFileDialog.getOpenFileName(filter='*.xls *.xlsx')[0]
        load_param_pir_chrom(file_name, DataPirolizExtr, False)
        well_interval()
    except FileNotFoundError:
        return


def load_data_chrom():
    """ Загрузка данных хроматографии керна """
    try:
        file_name = QFileDialog.getOpenFileName(filter='*.xls *.xlsx')[0]
        load_param_pir_chrom(file_name, DataChromKern, True)
        well_interval()
    except FileNotFoundError:
        return


def load_data_chrom_extr():
    """ Загрузка данных хроматографии экстракта """
    try:
        file_name = QFileDialog.getOpenFileName(filter='*.xls *.xlsx')[0]
        load_param_pir_chrom(file_name, DataChromExtr, True)
        well_interval()
    except FileNotFoundError:
        return


def load_depth_name():
    """ Привязка образцов по глубине """
    w_id = get_well_id()
    try:
        file_name = QFileDialog.getOpenFileName(filter='*.xls *.xlsx')[0]
        ui.label_info.setText('Привязка образцов по глубине...')
        ui.label_info.setStyleSheet('color: blue')
        ui.progressBar.setMaximum(5)
        for n, i in enumerate([DataPirolizKern, DataPirolizExtr, DataChromKern, DataChromExtr, DataLit]):
            load_depth_name_param(file_name, w_id, i)
            ui.progressBar.setValue(n + 1)
        ui.label_info.setText('Готово')
        ui.label_info.setStyleSheet('color: green')
        well_interval()
    except FileNotFoundError:
        return


def del_param():
    """ Удаление параметра в выбранном интервале """
    w_id = get_well_id()
    table, table_text, widget = check_tabWidjet()
    start, stop = check_start_stop()
    try:
        param = widget.currentItem().text()
    except AttributeError:
        return
    d = start
    n = 0
    ui.progressBar.setMaximum(int((stop - start) / 0.1))
    while d <= stop:
        d = round(d, 2)
        session.query(table).filter(table.well_id == w_id, table.depth >= d, table.depth < d + 0.1).update(
            {param: None}, synchronize_session="fetch")
        d += 0.1
        n += 1
        ui.progressBar.setValue(n)
    session.commit()
    well_interval()


def draw_param_las():
    """ Отривсовка параметра LAS при клике в списке параметров  """
    draw_param_table(ui.listWidget_las, DataLas, 'data_las')
    draw_param_graph(ui.listWidget_las, DataLas, 'data_las')
    calc_stat()
    ui.label_param_for_class_lim.setText(ui.listWidget_las.currentItem().text())


def draw_param_lit():
    """ Отривсовка параметра литологии при клике в списке параметров  """
    draw_param_table(ui.listWidget_lit, DataLit, 'data_lit')
    draw_param_graph(ui.listWidget_lit, DataLit, 'data_lit')
    calc_stat()
    ui.label_param_for_class_lim.setText(ui.listWidget_lit.currentItem().text())


def draw_param_pir_kern():
    """ Отривсовка параметра пиролиз керна при клике в списке параметров  """
    draw_param_table(ui.listWidget_pir_kern, DataPirolizKern, 'data_piroliz_kern')
    draw_param_graph(ui.listWidget_pir_kern, DataPirolizKern, 'data_piroliz_kern')
    calc_stat()
    ui.label_param_for_class_lim.setText(ui.listWidget_pir_kern.currentItem().text())


def draw_param_pir_extr():
    """ Отривсовка параметра пиролиз керна после экстракции при клике в списке параметров  """
    draw_param_table(ui.listWidget_pir_extr, DataPirolizExtr, 'data_piroliz_extr')
    draw_param_graph(ui.listWidget_pir_extr, DataPirolizExtr, 'data_piroliz_extr')
    calc_stat()
    ui.label_param_for_class_lim.setText(ui.listWidget_pir_extr.currentItem().text())


def draw_param_chrom_kern():
    """ Отривсовка параметра хроматографии керна при клике в списке параметров  """
    draw_param_table(ui.listWidget_chrom_kern, DataChromKern, 'data_chrom_kern')
    draw_param_graph(ui.listWidget_chrom_kern, DataChromKern, 'data_chrom_kern')
    calc_stat()
    ui.label_param_for_class_lim.setText(ui.listWidget_chrom_kern.currentItem().text())


def draw_param_chrom_extr():
    """ Отривсовка параметра хроматографии керна после экстракции при клике в списке параметров  """
    draw_param_table(ui.listWidget_chrom_extr, DataChromExtr, 'data_chrom_extr')
    draw_param_graph(ui.listWidget_chrom_extr, DataChromExtr, 'data_chrom_extr')
    calc_stat()
    ui.label_param_for_class_lim.setText(ui.listWidget_chrom_extr.currentItem().text())