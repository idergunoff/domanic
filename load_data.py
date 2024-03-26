from functions import *
from user_interval import user_interval_list_update
from calculated_data import update_list_calculated_data


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
    user_interval_list_update()



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
        user_interval_list_update()
        update_list_calculated_data()


def load_data_from_las():
    """Загрузка данных из las-файлов"""
    try:
        file_name = QFileDialog.getOpenFileName(filter='*.las')[0]
        # version, start_depth, stop_depth, null_value, param, data_row = read_las_info(file_name)
        las = ls.read(file_name)
    except FileNotFoundError:
        return
    add_slots(las.well['STRT'].value, las.well['STOP'].value)
    well_interval()
    w_id = get_well_id()
    param_result = ''
    no_param = ''

    # print(las.well['WELL'].value, las.well['STRT'].value, las.well['STOP'].value, las.well['NULL'].value)

    param_las = [curve.mnemonic for curve in las.curves]
    param_las_db = param_las.copy()
    param_las_db = ['Ag' if i == 'AG' else i for i in param_las_db]
    param_las_db = ['Ang' if i == 'ANG' else i for i in param_las_db]
    param_las_db = ['Mgl' if i == 'MGL' else i for i in param_las_db]
    param_las_db = ['NNKb' if i == 'NNKB' else i for i in param_las_db]
    param_las_db = ['NNKm' if i == 'NNKM' else i for i in param_las_db]
    param_las_db = ['Rp' if i == 'RP' else i for i in param_las_db]
    param_las_db = ['PHIg' if i == 'PHIG' else i for i in param_las_db]
    param_las_db = ['LITOc' if i == 'LITOC' else i for i in param_las_db]
    param_las_db = ['Kgl' if i == 'KGL' else i for i in param_las_db]
    param_las_db = ['FLUIDc' if i == 'FLUIDC' else i for i in param_las_db]
    param_las_db = ['COLLc' if i == 'COLLC' else i for i in param_las_db]
    param_las_db = ['DEPT' if i == 'DEPTH' else i for i in param_las_db]
    # print(param_las)
    list_columns = DataLas.__table__.columns.keys()
    for n, i in enumerate(param_las_db):
        if i != 'DEPT':
            if i in list_columns:
                try:
                    load_param_from_lasio(i, list(las['DEPT']), list(las[param_las[n]]), w_id)
                except KeyError:
                    load_param_from_lasio(i, list(las['DEPTH']), list(las[param_las[n]]), w_id)
                param_result += f' {i}'
            else:
                no_param += f' {i}'
    #
    #
    # if type(param) is list:
    #     for n, p in enumerate(param):
    #         result = load_param_from_las(p, null_value, file_name, data_row, n, w_id)
    #         if result:
    #             param_result += ' ' + p
    #         else:
    #             no_param += ' ' + p
    # else:
    #     result = load_param_from_las(param, null_value, file_name, data_row, 0, w_id)
    #     if result:
    #         param_result += ' ' + param
    #     else:
    #         no_param += ' ' + param
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


def load_param_from_lasio(param, depth, data, well_id):
    """Загрузка параметров из ласио"""
    for i in range(len(depth)):
        session.query(DataLas).filter(DataLas.well_id == well_id, DataLas.depth == depth[i]).update(
                            {param: data[i]}, synchronize_session="fetch")
    return True


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


def load_age():
    """ Загрузка возраста """
    w_id = get_well_id()
    try:
        file_name = QFileDialog.getOpenFileName(
            caption='Выберите файл excel, в котором перый столбец это начало интервала, второй столбец конец '
                    'инетервала, третий столбец возраст данного интервала',
            filter='*.xls *.xlsx')[0]
        ui.label_info.setText('Загрузка возраста...')
        ui.label_info.setStyleSheet('color: blue')
        data_age = pd.read_excel(file_name, header=None)
        for i_age_row in data_age.index:
            start = round(data_age[0][i_age_row], 1)
            stop = round(data_age[1][i_age_row],  1)
            age = data_age[2][i_age_row]
            ui.progressBar.setMaximum(int((stop - start)/0.1))
            step = 0
            while start <= stop:
                start = round(start, 1)
                if session.query(DataAge).filter_by(well_id=w_id, depth=start).first():
                    session.query(DataAge).filter_by(well_id=w_id, depth=start).update({'age': age}, synchronize_session='fetch')
                else:
                    new_age = DataAge(well_id=w_id, depth=start, age=age)
                    session.add(new_age)
                start += 0.1
                step += 1
                ui.progressBar.setValue(step)
        session.commit()
        ui.label_info.setText('Данные о возрасте загружены')
        ui.label_info.setStyleSheet('color: green')
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