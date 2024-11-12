from functions import *


def add_class_lim():
    """ Добавить новую классификацию по пределам в БД """
    Add_Class_Lim = QtWidgets.QDialog()
    ui_cl = Ui_add_class_lim()
    ui_cl.setupUi(Add_Class_Lim)
    Add_Class_Lim.show()
    Add_Class_Lim.setAttribute(QtCore.Qt.WA_DeleteOnClose)  # атрибут удаления виджета после закрытия

    def class_to_db():
        title_class = ui_cl.lineEdit_title.text()
        category = ui_cl.lineEdit_category.text()
        if title_class != '' and category != '':
            if len(category.split(';')) > 1:
                new_class = ClassByLimits(title=title_class, category_names=category)
                try:
                    session.add(new_class)
                    session.commit()
                    comboBox_class_lim_update()
                    Add_Class_Lim.close()
                    ui.label_info.setText(f'Классификация "{title_class}" добавлена в базу данных.')
                    ui.label_info.setStyleSheet('color: green')
                except IntegrityError:
                    ui.label_info.setText(f'Внимание! Ошибка сохранения. Классификация "{title_class}" уже есть.')
                    ui.label_info.setStyleSheet('color: red')
                    session.rollback()
            else:
                ui_cl.lineEdit_category.setText('ВНИМАНИЕ!!! Категорий должно быть больше 1.')

    def cancel_add_class():
        Add_Class_Lim.close()

    ui_cl.buttonBox.accepted.connect(class_to_db)
    ui_cl.buttonBox.rejected.connect(cancel_add_class)
    Add_Class_Lim.exec_()
    comboBox_class_lim_update()


def del_class_lim():
    """ Удалить классификацию по пределам из БД """
    c_id = int(ui.comboBox_class_lim.currentText().split('.')[0])
    name = session.query(ClassByLimits.title).filter(ClassByLimits.id == c_id).first()[0]
    session.query(ClassByLimitsParam).filter(ClassByLimitsParam.class_id == c_id).delete()
    session.query(ClassByLimits).filter(ClassByLimits.id == c_id).delete()
    session.commit()
    ui.label_info.setText(f'Классификация "{name}" удалена.')
    ui.label_info.setStyleSheet('color: green')
    comboBox_class_lim_update()
    display_param_limits()


def display_param_limits():
    """ Показать параметры классификации по пределам в таблице """
    try:
        clear_table(ui.tableWidget_class_lim)
        c_id = int(ui.comboBox_class_lim.currentText().split('.')[0])
        category = session.query(ClassByLimits.category_names).filter(ClassByLimits.id == c_id).first()[0].split(';')
        ui.tableWidget_class_lim.setColumnCount(len(category) + 2)
        cat = [i[0:10] for i in category]
        ui.tableWidget_class_lim.setHorizontalHeaderLabels(['param'] + cat + ['tab'])
        ui.tableWidget_class_lim.horizontalHeader().setStyleSheet('color: rgb(175, 0, 0); text-decoration: underline;')
        params = session.query(ClassByLimitsParam).filter(ClassByLimitsParam.class_id == c_id).all()
        for n, i in enumerate(params):
            ui.tableWidget_class_lim.insertRow(n)
            ui.tableWidget_class_lim.setItem(n, 0, QTableWidgetItem(i.param[0:7]))
            ui.tableWidget_class_lim.item(n, 0).setBackground(QtGui.QColor(255, 239, 211))
            param_lim = i.limits.split(';')
            for k, j in enumerate(param_lim):
                if k == len(param_lim) - 1:
                    ui.tableWidget_class_lim.setItem(n, k + 1, QTableWidgetItem(f'> {j}'))
                    ui.tableWidget_class_lim.item(n, k + 1).setBackground(QtGui.QColor(color_list[k]))
                else:
                    ui.tableWidget_class_lim.setItem(n, k + 1, QTableWidgetItem(f'{j} - {param_lim[k+1]}'))
                    ui.tableWidget_class_lim.item(n, k + 1).setBackground(QtGui.QColor(color_list[k]))
            ui.tableWidget_class_lim.setItem(n, len(param_lim) + 1, QTableWidgetItem(i.table[5:]))
            ui.tableWidget_class_lim.item(n, len(param_lim) + 1).setBackground(QtGui.QColor(255, 239, 211))
        ui.tableWidget_class_lim.resizeColumnsToContents()
    except ValueError:
        pass


def add_param_for_class_lim():
    """ Добавить параметр в классификацию по пределам """
    c_id = int(ui.comboBox_class_lim.currentText().split('.')[0])
    table, table_text, widget = check_tabWidjet()
    param = ui.label_param_for_class_lim.text()
    if param != 'название':
        if session.query(ClassByLimitsParam).filter(ClassByLimitsParam.class_id == c_id,
                                                    ClassByLimitsParam.param == param,
                                                    ClassByLimitsParam.table == table_text).count() == 0:
            str_limits = ui.lineEdit_limits.text()
            category = session.query(ClassByLimits.category_names).filter(ClassByLimits.id == c_id).first()[0]
            if len(list(set(str_limits.split(';')))) == len(category.split(';')):
                try:
                    limits = [float(i) for i in str_limits.split(';')]
                    limits_sort = limits.copy()
                    limits_sort.sort()
                    if limits == limits_sort:
                        new_class_param = ClassByLimitsParam(class_id=c_id, table=table_text, param=param, limits=str_limits)
                        session.add(new_class_param)
                        session.commit()
                        ui.label_info.setText(f'В классификацию "{ui.comboBox_class_lim.currentText().split(". ")[1]}" успешно добавлены пределы для параметра "{param}"')
                        ui.label_info.setStyleSheet('color: green')
                        display_param_limits()
                    else:
                        ui.label_info.setText('Внимание! Ошибка добавления параметра. Значения пределов должны непрерывно возрастать.')
                        ui.label_info.setStyleSheet('color: red')
                except ValueError:
                    ui.label_info.setText('Внимание! Ошибка добавления параметра. Значение предела должно быть числовым.')
                    ui.label_info.setStyleSheet('color: red')
            else:
                ui.label_info.setText('Внимание! Ошибка добавления параметра. Количество пределов не соответствует количеству категорий.')
                ui.label_info.setStyleSheet('color: red')
        else:
            ui.label_info.setText(f'Внимание! Ошибка добавления параметра. Параметр "{param}" уже существует в данной классификации')
            ui.label_info.setStyleSheet('color: red')
    else:
        ui.label_info.setText('Внимание! Выберите параметр.')
        ui.label_info.setStyleSheet('color: red')


def del_param_for_class_lim():
    """ Удалить параметр из классификации по пределам """
    try:
        c_id = int(ui.comboBox_class_lim.currentText().split('.')[0])
        row = ui.tableWidget_class_lim.currentRow()
        param = ui.tableWidget_class_lim.item(row, 0).text()
        session.query(ClassByLimitsParam).filter(ClassByLimitsParam.class_id == c_id, ClassByLimitsParam.param == param).delete()
        session.commit()
        display_param_limits()
        ui.label_info.setText(f'Параметр "{param}" в выбранной классификации успешно удалён.')
        ui.label_info.setStyleSheet('color: green')
    except AttributeError:
        ui.label_info.setText('Ошибка! Параметр не выбран.')
        ui.label_info.setStyleSheet('color: red')


def calc_class_lim():
    """ Рассчитать классификацию по пределам в выбранной скважине в выбранном интервале """
    w_id = get_well_id()    # id скважины
    start, stop = check_start_stop()    # интервал исследований
    c_id = int(ui.comboBox_class_lim.currentText().split('.')[0])   # id классификации по пределам
    class_params = session.query(ClassByLimitsParam).filter(ClassByLimitsParam.class_id == c_id).all()  # все параметры выбранной классификации
    list_name_cat = session.query(ClassByLimits.category_names).filter(ClassByLimits.id == c_id).first()[0].split(';')  # список названий категорий
    list_tab = []       # список названий таблиц параметров
    list_param = []     # список названий параметров
    list_limits = []    # список интервалов для каждого параметра
    for i in class_params:
        list_tab.append(i.table)
        list_param.append(i.param)
        list_limits.append([float(j) for j in i.limits.split(';')])     # список списков интервалов для каждого параметра

    # сбор всех параметров классификации в словари
    dict_param = {}
    for i in range(len(list_param)):
        if ui.checkBox_class_use_ml.isChecked():
            calc_data = session.query(CalculatedData).filter_by(well_id=w_id, title=list_param[i]).all()
            if len(calc_data) > 0:

                ChooseCalcData = QtWidgets.QDialog()
                ui_ccd = Ui_ChooseCalcData()
                ui_ccd.setupUi(ChooseCalcData)
                ChooseCalcData.show()
                ChooseCalcData.setAttribute(QtCore.Qt.WA_DeleteOnClose)  # атрибут удаления виджета после закрытия

                ui_ccd.label.setText(f'Выберите расчетные данные\nдля {list_param[i]}:')

                for calc_data_i in calc_data:
                    ui_ccd.listWidget.addItem(f'{calc_data_i.title} - {calc_data_i.model_title} id{calc_data_i.id}')
                    ui_ccd.listWidget.item(ui_ccd.listWidget.count() - 1).setToolTip(
                        f'Params: {", ".join([i.split(".")[-1] for i in json.loads(calc_data_i.list_params_model)])}\n '
                        f'Wells: {", ".join([i["well"] for i in json.loads(calc_data_i.list_wells_model)])}\n'
                        f'Comment: {calc_data_i.comment}'
                    )

                def choose_calc_data():
                    calc_data_choosed = session.query(CalculatedData).filter_by(id=ui_ccd.listWidget.currentItem().text().split(' id')[-1]).first()
                    dict_param[f'ML_{list_param[i]}'] = json.loads(calc_data_choosed.data)
                    ChooseCalcData.close()

                ui_ccd.pushButton_ok.clicked.connect(choose_calc_data)
                ChooseCalcData.exec_()

        table = get_table(list_tab[i])
        result = session.query(table.depth, literal_column(f'{list_tab[i]}.{list_param[i]}')).filter(
            table.well_id == w_id, literal_column(f'{list_tab[i]}.{list_param[i]}').isnot(None)).all()
        dictionary = {str(key)[:-1] if str(key)[-3] == '.' else str(key): value for key, value in result}
        dict_param[list_param[i]] = dictionary

    data_lim = []   # список списков все результирующие данные по классификации
    d, n, k = start, 0, 0
    ui.progressBar.setMaximum(int((stop - start) / 0.1))
    clear_table(ui.tableWidget)
    ui.tableWidget.setColumnCount(len(list_param) + (3 if list_tab[0] != 'data_las' else 2))    # количество колонок сназваниями образцов или без них
    ui.tableWidget.setHorizontalHeaderLabels((['depth', 'name', 'category'] if list_tab[0] != 'data_las' and not ui.checkBox_class_use_ml.isChecked() else
                                             ['depth', 'category']) + list_param)   # названия колонок
    ui.label_info.setText(f'Процесс расчёта классификации по пределам. {ui.comboBox_area.currentText()} скв.{ui.comboBox_well.currentText()}')
    ui.label_info.setStyleSheet('color: blue')
    while d <= stop:
        d = round(d, 2)
        list_class = [round(d, 1)]  # список результатов классификации для глубины d
        for i in range(len(list_tab)):      # перебор всех параметров классификации
            val = None
            if ui.checkBox_class_use_ml.isChecked():
                if f'ML_{list_param[i]}' in dict_param.keys():
                    val = dict_param[f'ML_{list_param[i]}'][str(d)] if str(d) in dict_param[f'ML_{list_param[i]}'].keys() else val
            if not val or ui.checkBox_class_fact_priority.isChecked():
                val = dict_param[list_param[i]][str(d)] if str(d) in dict_param[list_param[i]].keys() else val
            if val != None:     # если параметр по глубине d существует, определяем его категорию параметра классификации
                lim = check_value_in_limits(val, list_limits[i])
                list_class.append(lim)
        if len(list_class) == len(class_params) + 1:    # если определены все параметры
            ui.tableWidget.insertRow(k)     # создаем новую строку в виджете таблицы
            list_class.append(list_name_cat[choice_category(list_class[1:], len(list_param))])   # вычисление результирующей производной
            if list_tab[0] != 'data_las' and not ui.checkBox_class_use_ml.isChecked():   # если первый параметр не LAS получаем номер образца
                tab = get_table(list_tab[0])
                name_obr = session.query(tab.name).filter(tab.well_id == w_id, tab.depth >= d, tab.depth < d + 0.1).first()[0]
                ui.tableWidget.setItem(k, 1, QTableWidgetItem(str(name_obr)))
                list_class.append(name_obr)
            data_lim.append(list_class)     # добавляем в список результатов итоговый список категорий
            ui.tableWidget.setItem(k, 0, QTableWidgetItem(str(list_class[0])))      # добавляем глубину в виджет
            ui.tableWidget.setItem(k, (2 if list_tab[0] != 'data_las' and not ui.checkBox_class_use_ml.isChecked() else 1), QTableWidgetItem(
                str(list_class[-2 if list_tab[0] != 'data_las' and not ui.checkBox_class_use_ml.isChecked() else -1])))  # добавляем итоговую категорию в виджет
            ui.tableWidget.item(k, (2 if list_tab[0] != 'data_las' and not ui.checkBox_class_use_ml.isChecked() else 1)).setBackground(
                QtGui.QColor(color_list[list_name_cat.index(list_class[-2 if list_tab[0] != 'data_las' and not ui.checkBox_class_use_ml.isChecked() else -1])]))     # цвет ячейки по категории
            list_cat = list_class[1:-2] if list_tab[0] != 'data_las' and not ui.checkBox_class_use_ml.isChecked() else list_class[1:-1]  # список резульирующих категорий по параметрам
            for m, j in enumerate(list_cat):
                if ui.checkBox_pdf_class.isChecked():
                    j = round(j, 2)
                ui.tableWidget.setItem(k, m + (3 if list_tab[0] != 'data_las' and not ui.checkBox_class_use_ml.isChecked() else 2), QTableWidgetItem(str(j)))    # категории по каждому параметру в виджет
                ui.tableWidget.item(k, m + (3 if list_tab[0] != 'data_las' and not ui.checkBox_class_use_ml.isChecked() else 2)).setBackground(QtGui.QColor(color_list[int(j)]))  # цвет ячейки по категории
            k += 1
        d += 0.1
        n += 1
        ui.progressBar.setValue(n)
    ui.tableWidget.resizeColumnsToContents()
    ui.label_table_name.setText(f'Класс-ия по пределам скв.{ui.comboBox_well.currentText()}')   # название таблицы
    ui.label_info.setText(f'Готово! Выполнен расчёт классификации по пределам. {ui.comboBox_area.currentText()} скв.{ui.comboBox_well.currentText()}')
    ui.label_info.setStyleSheet('color: green')

    pd_data = pd.DataFrame(data_lim, columns=['depth'] + list_param + ['category'] + (
        ['name'] if list_tab[0] != 'data_las' and not ui.checkBox_class_use_ml.isChecked() else []))
    if list_tab[0] != 'data_las' and not ui.checkBox_class_use_ml.isChecked():
        pd_data = pd_data[['depth', 'name'] + list_param + ['category']]
    ui.graphicsView.clear()
    for n, i in enumerate(list_name_cat):
        Y = pd_data['depth'].loc[pd_data['category'] == i].values
        if len(Y) > 0:
            color = color_list[n]
            curve = pg.BarGraphItem(x0=0, y=Y, height=0.1, width=n + 1, brush=color, pen=pg.mkPen(color=color))
            ui.graphicsView.addItem(curve)
    ui.graphicsView.getViewBox().invertY(True)
    category_to_resource(list_name_cat)
    if ui.checkBox_save_class_lim.isChecked():  # сохранение результирующей таблицы в файл XLS
        try:
            file_name = f'{ui.comboBox_class_lim.currentText().split(". ")[1]}_{ui.comboBox_area.currentText()}_скв.' \
                        f'{ui.comboBox_well.currentText()}.xlsx'
            fn = QFileDialog.getSaveFileName(caption="Сохранить классификацию в таблицу", directory=file_name,
                                             filter="Excel Files (*.xlsx)")
            pd_data.to_excel(fn[0])
            ui.label_info.setText(f'Таблица сохранена в файл: {fn[0]}')
            ui.label_info.setStyleSheet('color: green')
        except ValueError:
            pass


def add_class_lda():
    """ Добавить новую модель классификации LDA в БД """
    Add_Class_LDA = QtWidgets.QDialog()
    ui_lda = Ui_add_class_lda()
    ui_lda.setupUi(Add_Class_LDA)
    Add_Class_LDA.show()
    Add_Class_LDA.setAttribute(QtCore.Qt.WA_DeleteOnClose)  # атрибут удаления виджета после закрытия

    def class_to_db():
        title_class = ui_lda.lineEdit_title.text()
        category = ui_lda.lineEdit_category.text()
        w_id = get_well_id()
        if title_class != '' and category != '':
            if len(category.split(';')) > 1:
                new_model = ClassByLda(title=title_class, category=category, well_id=w_id)
                session.add(new_model)
                session.commit()
                comboBox_class_lda_update()
                Add_Class_LDA.close()
                ui.label_info.setText(f'Классификация "{title_class}" добавлена в базу данных.')
                ui.label_info.setStyleSheet('color: green')
            else:
                ui_lda.lineEdit_category.setText('ВНИМАНИЕ!!! Категорий должно быть больше 1.')

    def cancel_add_class():
        Add_Class_LDA.close()

    ui_lda.buttonBox.accepted.connect(class_to_db)
    ui_lda.buttonBox.rejected.connect(cancel_add_class)
    Add_Class_LDA.exec_()
    comboBox_class_lim_update()


def del_class_lda():
    """ Удалить модель классификации LDA из БД """
    c_id = int(ui.comboBox_class_lda.currentText().split('.')[0])
    session.query(ClassByLdaMark).filter(ClassByLdaMark.class_id == c_id).delete()
    session.query(ClassByLda).filter(ClassByLda.id == c_id).delete()
    session.commit()
    ui.label_info.setText('Классификация удалена.')
    ui.label_info.setStyleSheet('color: green')
    comboBox_class_lda_update()


def add_int_lda():
    """ Добавление интервала разметки для LDA (дискриминантного анализа) """
    c_id = int(ui.comboBox_class_lda.currentText().split('.')[0])
    mark = ui.comboBox_class_lda_cat.currentText()
    start, stop = check_start_stop()
    d, n = start, 0
    ui.progressBar.setMaximum(int((stop - start) / 0.1))
    while d <= stop:
        d = round(d, 2)
        if session.query(ClassByLdaMark).filter(ClassByLdaMark.depth == d, ClassByLdaMark.class_id == c_id).count() > 0:
            session.query(ClassByLdaMark).filter(ClassByLdaMark.depth == d, ClassByLdaMark.class_id == c_id).update(
                {'mark': mark}, synchronize_session="fetch")
        else:
            new_mark = ClassByLdaMark(class_id=c_id, depth=d, mark=mark)
            session.add(new_mark)
        d = round(d + 0.1, 1)
        n += 1
        ui.progressBar.setValue(n)
    session.commit()
    ui.label_info.setText(f'Добавлен интервал категории "{mark}" c {start} по {stop} метров.')
    ui.label_info.setStyleSheet('color: green')
    update_table_lda_cat()
    update_graph_lda_cat()


def add_param_for_LDA():
    """ Добавить параметр в классификацию LDA """
    table, table_text, widget = check_tabWidjet()
    reset_fake_lda()
    try:
        param = widget.currentItem().text()
        if ui.listWidget_class_lda_param.findItems(f'{param} {table_text}', QtCore.Qt.MatchExactly):
            ui.label_info.setText(f'Внимание! Параметр "{param}" уже добавлен.')
            ui.label_info.setStyleSheet('color: red')
        else:
            ui.listWidget_class_lda_param.addItem(f'{param} {table_text}')
    except AttributeError:
        ui.label_info.setText(f'Внимание! Не выбран параметр.')
        ui.label_info.setStyleSheet('color: red')


def clear_list_param_lda():
    """ Очистить список параметров классификации LDA """
    ui.listWidget_class_lda_param.clear()
    reset_fake_lda()


def draw_LDA():
    """ Построить диаграмму рассеяния для модели анализа LDA """
    if ui.listWidget_class_lda_param.count() >= ui.comboBox_class_lda_cat.count():
        data_train, list_param, list_tab = build_table_train_lda()
        training_sample = data_train[list_param].values.tolist()
        markup = sum(data_train[['mark']].values.tolist(), [])
        clf = LinearDiscriminantAnalysis()
        try:
            trans_coef = clf.fit(training_sample, markup).transform(training_sample)
        except ValueError:
            ui.label_info.setText(f'Ошибка в расчетах LDA! Возможно значения одного из параметров отсутствуют в интервале обучающей выборки.')
            ui.label_info.setStyleSheet('color: red')
            return
        data_trans_coef = pd.DataFrame(trans_coef)
        data_trans_coef['mark'] = data_train[['mark']]

        fig = plt.figure(figsize=(10, 10), dpi=80)
        ax = plt.subplot()
        if ui.listWidget_class_lda_param.count() < 3:
            sns.scatterplot(data=data_trans_coef, x=0, y=100, hue='mark')
        else:
            sns.scatterplot(data=data_trans_coef, x=0, y=1, hue='mark')
        ax.grid()
        ax.xaxis.grid(True, "minor", linewidth=.25)
        ax.yaxis.grid(True, "minor", linewidth=.25)
        title_graph = f'Диаграмма рассеяния для канонических значений для обучающей выборки' \
                      f'\n{ui.comboBox_class_lda.currentText().split(". ")[1]}' \
                      f'\nПараметры: {" ".join(list_param)}' f'\nКоличество образцов: {str(len(data_trans_coef.index))}'
        plt.title(title_graph, fontsize=16)
        fig.show()
        ui.label_info.setText(f'Внимание! Построена диаграмма рассеяния для канонических значений.')
        ui.label_info.setStyleSheet('color: green')
        if ui.checkBox_save_class_lda.isChecked():
            try:
                file_name = f'Обучающая выборка LDA {ui.comboBox_class_lda.currentText().split(". ")[1]}_{" ".join(list_param)}.xlsx'
                fn = QFileDialog.getSaveFileName(caption="Сохранить выборку в таблицу", directory=file_name,
                                                 filter="Excel Files (*.xlsx)")
                data_train.to_excel(fn[0])
                ui.label_info.setText(f'Таблица сохранена в файл: {fn[0]}')
                ui.label_info.setStyleSheet('color: green')
            except ValueError:
                pass
    else:
        ui.label_info.setText(f'Внимание! Количество параметров должно быть не меньше количества категорий в обучающей выборке.')
        ui.label_info.setStyleSheet('color: red')


def calc_verify_lda():
    """ Удалить выбросы из обучающей выборки.
    Прогоняет обучающую выборку по обученной модели, не совпадающие образцы исключаются из модели """
    if ui.listWidget_class_lda_param.count() >= ui.comboBox_class_lda_cat.count():
        data_train, list_param, list_tab = build_table_train_lda()
        training_sample = data_train[list_param].values.tolist()
        markup = sum(data_train[['mark']].values.tolist(), [])
        clf = LinearDiscriminantAnalysis()
        try:
            clf.fit(training_sample, markup)
        except ValueError:
            ui.label_info.setText(f'Ошибка в расчетах LDA! Возможно значения одного из параметров отсутствуют в интервале обучающей выборки.')
            ui.label_info.setStyleSheet('color: red')
            return
        n, k = 0, 0
        ui.progressBar.setMaximum(len(data_train.index))
        for i in data_train.index:
            new_mark = clf.predict([data_train.loc[i].loc[list_param].tolist()])[0]
            if data_train['mark'][i] != new_mark:
                session.query(ClassByLdaMark).filter(ClassByLdaMark.depth == data_train['depth'][i]).update({'fake': 1})
                n += 1
            k += 1
            ui.progressBar.setValue(k)
        session.commit()
        ui.label_info.setText(f'Внимание! Из обучающей выборки удалено {n} образцов.')
        ui.label_info.setStyleSheet('color: green')
        update_table_lda_cat()
        update_graph_lda_cat()
    else:
        ui.label_info.setText(f'Внимание! Количество параметров должно быть не меньше количества категорий в обучающей выборке.')
        ui.label_info.setStyleSheet('color: red')


def calc_lda():
    """ Расчет LDA в выбранном интервале, выбранной скважины  """
    if ui.listWidget_class_lda_param.count() >= ui.comboBox_class_lda_cat.count():
        data_train, list_param, list_tab = build_table_train_lda()
    else:
        ui.label_info.setText(f'Внимание! Количество параметров должно быть не меньше количества категорий в обучающей выборке.')
        ui.label_info.setStyleSheet('color: red')
        return
    training_sample = data_train[list_param].values.tolist()
    markup = sum(data_train[['mark']].values.tolist(), [])
    clf = LinearDiscriminantAnalysis()
    try:
        clf.fit(training_sample, markup)
        trans_coef = clf.fit(training_sample, markup).transform(training_sample)
    except ValueError:
        ui.label_info.setText(f'Ошибка в расчетах LDA! Возможно значения одного из параметров отсутствуют в интервале обучающей выборки.')
        ui.label_info.setStyleSheet('color: red')
        return
    data_trans_coef = pd.DataFrame(trans_coef)
    data_trans_coef['mark'] = data_train[['mark']]
    list_cat = list(clf.classes_)
    if list_tab[0] == 'data_las':
        working_data = pd.DataFrame(columns=['depth', 'mark'] + list_param + list_cat)
    else:
        working_data = pd.DataFrame(columns=['name', 'depth', 'mark'] + list_param + list_cat)
    start, stop = check_start_stop()
    w_id = get_well_id()
    d, n = start, 0
    ui.progressBar.setMaximum(int((stop - start) / 0.1))
    ui.label_info.setText(f'Процесс расчёта LDA. {ui.comboBox_area.currentText()} скв.{ui.comboBox_well.currentText()}')
    ui.label_info.setStyleSheet('color: blue')
    while d <= stop:
        d = round(d, 2)
        dict_value = {}
        for j in range(len(list_param)):
            tab = get_table(list_tab[j])
            val = session.query(literal_column(f'{list_tab[j]}.{list_param[j]}')).filter(tab.well_id == w_id,
                                tab.depth >= d, tab.depth < d + 0.1).first()
            if val:
                if val[0]:
                    dict_value[list_param[j]] = val[0]
        if len(dict_value) == len(list_param):
            dict_trans_coef = {}
            new_trans_coef = clf.transform([list(dict_value.values())])[0]
            for k, i in enumerate(new_trans_coef):
                dict_trans_coef[k] = i
            dict_trans_coef['mark'] = 'test'
            new_mark = clf.predict([list(dict_value.values())])[0]
            probability = clf.predict_proba([list(dict_value.values())])[0]
            for k, i in enumerate(list_cat):
                dict_value[list_cat[k]] = probability[k]
            dict_value['mark'] = new_mark
            dict_value['depth'] = d
            if list_tab[0] != 'data_las':
                tab = get_table(list_tab[0])
                dict_value['name'] = session.query(tab.name).filter(
                    tab.well_id == w_id, tab.depth >= d, tab.depth < d + 0.1).first()[0]

            working_data = pd.concat([working_data, pd.DataFrame(pd.Series(dict_value)).T], ignore_index=True)
            data_trans_coef = pd.concat([data_trans_coef, pd.DataFrame(pd.Series(dict_trans_coef)).T], ignore_index=True)

        d = round(d + 0.1, 1)
        n += 1
        ui.progressBar.setValue(n)
    ui.label_table_name.setText(f'Результаты LDA скв.{ui.comboBox_well.currentText()}')
    build_tableWidget_from_pd(working_data, ui.tableWidget, list_cat)
    ui.label_info.setText(f'Готово! Выполнен расчёт LDA. {ui.comboBox_area.currentText()} скв.{ui.comboBox_well.currentText()}')
    ui.label_info.setStyleSheet('color: green')
    ui.graphicsView.clear()
    for n, i in enumerate(list_cat):
        Y = working_data['depth'].loc[working_data['mark'] == i].tolist()
        if len(Y) > 0:
            color = color_list[n]
            curve = pg.BarGraphItem(x0=0, y=Y, height=0.1, width=n + 1, brush=color, pen=pg.mkPen(color=color))
            ui.graphicsView.addItem(curve)
    ui.graphicsView.getViewBox().invertY(True)

    fig = plt.figure(figsize=(10, 10), dpi=80)
    ax = plt.subplot()
    if ui.comboBox_class_lda_cat.count() < 3:
        sns.scatterplot(data=data_trans_coef, x=0, y=100, hue='mark')
    else:
        sns.scatterplot(data=data_trans_coef, x=0, y=1, hue='mark')
    ax.grid()
    ax.xaxis.grid(True, "minor", linewidth=.25)
    ax.yaxis.grid(True, "minor", linewidth=.25)
    title_graph = f'Диаграмма рассеяния для канонических значений' \
                  f'\n{ui.comboBox_class_lda.currentText().split(". ")[1]}' \
                  f'\nПараметры: {" ".join(list_param)}' f'\nКоличество образцов: {str(len(data_trans_coef.index))}'
    plt.title(title_graph, fontsize=16)
    fig.show()
    category_to_resource(list_cat)

    if ui.checkBox_save_class_lda.isChecked():
        try:
            file_name = f'{ui.comboBox_class_lda.currentText().split(". ")[1]}_{ui.comboBox_area.currentText()}_скв.' \
                        f'{ui.comboBox_well.currentText()}.xlsx'
            fn = QFileDialog.getSaveFileName(caption="Сохранить классификацию в таблицу", directory=file_name,
                                             filter="Excel Files (*.xlsx)")
            working_data.to_excel(fn[0])
            ui.label_info.setText(f'Таблица сохранена в файл: {fn[0]}')
            ui.label_info.setStyleSheet('color: green')
        except ValueError:
            pass


def draw_interp_resourse():
    try:
        if ui.checkBox_interp_resourse.isChecked():
            w_id = get_well_id()
            list_calc_int = session.query(IntervalFromCat.int_from, IntervalFromCat.int_to).all()
            min_depth = np.min([x[0] for x in list_calc_int])
            max_depth = np.max([x[1] for x in list_calc_int])
            dict_s1 = {x.depth: x.s1 for x in session.query(DataPirolizKern.depth, DataPirolizKern.s1).filter(
                DataPirolizKern.well_id == w_id,
                DataPirolizKern.depth >= min_depth,
                DataPirolizKern.depth <= max_depth
            ).all() if x.s1}
            dict_s2 = {x.depth: x.s2 for x in session.query(DataPirolizKern.depth, DataPirolizKern.s2).filter(
                DataPirolizKern.well_id == w_id,
                DataPirolizKern.depth >= min_depth,
                DataPirolizKern.depth <= max_depth
            ).all() if x.s2}
            curve_s1 = interpolate_dict_for_resource(min_depth, max_depth, dict_s1)
            curve_s2 = interpolate_dict_for_resource(min_depth, max_depth, dict_s2)
            X_s1_int = [val for key, val in curve_s1.items()]
            Y_s1_int = [key for key, val in curve_s1.items()]
            X_s2_int = [val for key, val in curve_s2.items()]
            Y_s2_int = [key for key, val in curve_s2.items()]

            X_s1 = sum(list(map(list, session.query(DataPirolizKern.s1).filter(DataPirolizKern.well_id == w_id,
                                          DataPirolizKern.s1 != None).order_by(DataPirolizKern.depth).all())), [])
            Y_s1 = sum(list(map(list, session.query(DataPirolizKern.depth).filter(DataPirolizKern.well_id == w_id,
                                          DataPirolizKern.s1 != None).order_by(DataPirolizKern.depth).all())), [])
            X_s2 = sum(list(map(list, session.query(DataPirolizKern.s2).filter(DataPirolizKern.well_id == w_id,
                                                                               DataPirolizKern.s2 != None).order_by(
                DataPirolizKern.depth).all())), [])
            Y_s2 = sum(list(map(list, session.query(DataPirolizKern.depth).filter(DataPirolizKern.well_id == w_id,
                                                                                  DataPirolizKern.s2 != None).order_by(
                DataPirolizKern.depth).all())), [])

            ui.graphicsView.clear()
            color_s1, color_s2 = 'blue', 'red'
            dash = choice_dash()
            width = choice_width()
            curve_graph_s1 = pg.PlotCurveItem(x=X_s1_int, y=Y_s1_int, pen=pg.mkPen(color=color_s1, width=width, dash=dash))
            curve_graph_s2 = pg.PlotCurveItem(x=X_s2_int, y=Y_s2_int, pen=pg.mkPen(color=color_s2, width=width, dash=dash))

            curve_bar_s1 = pg.BarGraphItem(x0=0, y=Y_s1, height=0.1, width=X_s1, brush=color_s1, pen=pg.mkPen(color=color_s1, width=0.4))
            curve_bar_s2 = pg.BarGraphItem(x0=0, y=Y_s2, height=0.1, width=X_s2, brush=color_s2, pen=pg.mkPen(color=color_s2, width=0.4))

            try:
                ui.graphicsView.addItem(curve_graph_s1)
                curve_graph_s1.getViewBox().invertY(True)
                ui.graphicsView.addItem(curve_graph_s2)
                curve_graph_s2.getViewBox().invertY(True)
                ui.graphicsView.addItem(curve_bar_s1)
                curve_bar_s1.getViewBox().invertY(True)
                ui.graphicsView.addItem(curve_bar_s2)
                curve_bar_s2.getViewBox().invertY(True)
            except TypeError:
                ui.label_info.setText(f'Внимание! Ошибка. Образцы не привязаны к глубине.')
                ui.label_info.setStyleSheet('color: red')
    except Exception as e:
        ui.label_info.setText(f'Внимание! Ошибка. {e}')
        ui.label_info.setStyleSheet('color: red')


def calc_resource():
    try:

        # d, n = get_n_cat_column()
        # start, stop = check_start_stop()
        # list_cat_for_calc = []
        # for i in ui.cat_resource.findChildren(QtWidgets.QCheckBox):
        #     if i.isChecked():
        #         list_cat_for_calc.append(i.text())
        # list_calc_int = []
        # list_int = []
        # for i in range(ui.tableWidget.rowCount()):
        #     if stop > float(ui.tableWidget.item(i, d).text()) > start:
        #         if ui.tableWidget.item(i, n).text() in list_cat_for_calc:
        #             if len(list_int) == 0 and i != 0:
        #                 value = (float(ui.tableWidget.item(i, d).text()) + float(ui.tableWidget.item(i - 1, d).text())) / 2
        #                 list_int.append(round(value, 2))
        #             else:
        #                 list_int.append(float(ui.tableWidget.item(i, d).text()))
        #         else:
        #             if len(list_int) > 0:
        #                 value = (float(ui.tableWidget.item(i, d).text()) + float(ui.tableWidget.item(i - 1, d).text())) / 2
        #                 list_int.append(round(value, 2))
        #                 list_calc_int.append([list_int[0], list_int[-1]])
        #                 list_int = []
        # if len(list_int) > 0:
        #     list_calc_int.append([list_int[0], list_int[-1]])
        start, stop = check_start_stop()
        w_id = get_well_id()
        list_calc_int = session.query(IntervalFromCat.int_from, IntervalFromCat.int_to).all()
        if ui.checkBox_interp_resourse.isChecked():
            min_depth = np.min([x[0] for x in list_calc_int])
            max_depth = np.max([x[1] for x in list_calc_int])
            dict_s1 = {x.depth: x.s1 for x in session.query(DataPirolizKern.depth, DataPirolizKern.s1).filter(
                DataPirolizKern.well_id == w_id,
                DataPirolizKern.depth >= min_depth,
                DataPirolizKern.depth <= max_depth
            ).all() if x.s1}
            dict_s2 = {x.depth: x.s2 for x in session.query(DataPirolizKern.depth, DataPirolizKern.s2).filter(
                DataPirolizKern.well_id == w_id,
                DataPirolizKern.depth >= min_depth,
                DataPirolizKern.depth <= max_depth
            ).all() if x.s2}
            curve_s1 = interpolate_dict_for_resource(min_depth, max_depth, dict_s1)
            curve_s2 = interpolate_dict_for_resource(min_depth, max_depth, dict_s2)
        list_Qhs1, list_Qhs2, list_Ro, list_Ro_param, list_h, list_s1, list_s2 = [], [], [], [], [], [], []
        list_col = ['h', 'int_ot', 'int_do', 'Qhs1', 'Qhs2', 's1', 's2', 'Ro', 'Ro_param']

        # дополнительные параметры в таблицу ресурсов
        list_column, list_param, list_tab = [], [], []
        for i in range(ui.listWidget_param_resource_tab.count()):
            item = ui.listWidget_param_resource_tab.item(i).text().split(' ')
            list_param.append(item[0])
            list_tab.append(item[1])
            list_column.append(ui.listWidget_param_resource_tab.item(i).text())
        list_col += list_column

        resource_table = pd.DataFrame(columns=list_col)
        for i in list_calc_int:
            # проверка интервала исследований
            if start < i[1] < stop or start < i[0] < stop:
                h0 = i[0] if i[0] > start else start
                h1 = i[1] if i[1] < stop else stop

                h = h1 - h0
                s1 = np.mean(del_none_from_list(sum(list(map(list, session.query(DataPirolizKern.s1).filter(
                    DataPirolizKern.well_id == w_id, DataPirolizKern.depth >= h0, DataPirolizKern.depth <= h1).all())), [])))
                s2 = np.mean(del_none_from_list(sum(list(map(list, session.query(DataPirolizKern.s2).filter(
                    DataPirolizKern.well_id == w_id, DataPirolizKern.depth >= h0, DataPirolizKern.depth <= h1).all())), [])))
                ggk = np.mean(del_none_from_list(sum(list(map(list, session.query(DataLas.GGK).filter(
                    DataLas.well_id == w_id, DataLas.depth >= h0, DataLas.depth <= h1).all())), [])))
                sgk = np.mean(del_none_from_list(sum(list(map(list, session.query(DataLit.SGK).filter(
                    DataLit.well_id == w_id, DataLit.depth >= h0, DataLit.depth <= h1).all())), [])))
                density = np.mean(del_none_from_list(sum(list(map(list, session.query(DataLit.density).filter(
                    DataLit.well_id == w_id, DataLit.depth >= h0, DataLit.depth <= h1).all())), [])))
                if not np.isnan(density):
                    Ro = density
                    Ro_param = 'density'
                elif not np.isnan(ggk):
                    Ro = ggk
                    Ro_param = 'ggk'
                elif not np.isnan(sgk):
                    Ro = sgk
                    Ro_param = 'sgk'
                else:
                    Ro = list_Ro[-1]
                    Ro_param = list_Ro_param[-1]
                    mes = f'{round(h, 2)} м. {h0} - {h1}'
                    set_info(mes, 'red')
                    mes = 'Данные по плотности отсутствуют.'
                    set_info(mes, 'red')
                    mes = 'Значения для расчетов взяты из предыдущего интервала.'
                    set_info(mes, 'red')
                    mes = ''
                    set_info(mes, 'blue')
                if np.isnan(s1) or np.isnan(s2):
                    if ui.checkBox_interp_resourse.isChecked():
                        s1 = np.mean([val for key, val in curve_s1.items() if key >= h0 and key <= h1])
                        s2 = np.mean([val for key, val in curve_s2.items() if key >= h0 and key <= h1])
                    else:
                        s1 = list_s1[-1]
                        s2 = list_s2[-1]
                    mes = f'{round(h, 2)} м. {h0} - {h1}'
                    set_info(mes, 'red')
                    mes = 'S1 и S2 отсутствуют.'
                    set_info(mes, 'red')
                    if ui.checkBox_interp_resourse.isChecked():
                        mes = 'Значения для расчетов - интерполяция.'
                    else:
                        mes = f'Значения для расчетов взяты из предыдущего интервала.'
                    set_info(mes, 'red')
                    mes = ''
                    set_info(mes, 'blue')
                Qhs1 = h * Ro * s1
                Qhs2 = h * Ro * s2
                mes = f'{round(h, 2)} м. {h0} - {h1}'
                set_info(mes, 'blue')
                mes = f'Ro ({Ro_param}) = {round(Ro, 2)}'
                set_info(mes, 'blue')
                mes = f'S1 = {round(s1, 2)}'
                set_info(mes, 'blue')
                mes = f'S2 = {round(s2, 2)}'
                set_info(mes, 'blue')
                mes = f'Qhs1 = {round(Qhs1, 2)}'
                set_info(mes, 'blue')
                mes = f'Qhs2 = {round(Qhs2, 2)}'
                set_info(mes, 'blue')
                mes = ''
                set_info(mes, 'blue')
                list_Ro.append(Ro)
                list_Ro_param.append(Ro_param)
                list_Qhs1.append(Qhs1)
                list_Qhs2.append(Qhs2)
                list_h.append(h)
                list_s1.append(s1)
                list_s2.append(s2)
                dict_int = {'h': h, 'int_ot': h0, 'int_do': h1, 'Qhs1': Qhs1, 'Qhs2': Qhs2, 's1': s1, 's2': s2, 'Ro': Ro, 'Ro_param': Ro_param}

                # дополнительные параметры
                for j in range(len(list_param)):
                    table = get_table(list_tab[j])
                    value = np.mean(del_none_from_list(sum(list(map(list, session.query(literal_column(f'{list_tab[j]}.{list_param[j]}')).filter(
                    table.well_id == w_id, table.depth >= h0, table.depth <= h1).all())), [])))
                    dict_int[list_column[j]] = value

                resource_table = pd.concat([resource_table, pd.DataFrame(pd.Series(dict_int)).T], ignore_index=True)
        if ui.checkBox_save_table_resource.isChecked():
            try:
                list_cat_for_calc = []
                for i in ui.cat_resource.findChildren(QtWidgets.QCheckBox):
                    if i.isChecked():
                        list_cat_for_calc.append(i.text())
                file_name = f'Ресурсы_{"_".join(list_cat_for_calc)}_{ui.comboBox_area.currentText()}_скв.' \
                            f'{ui.comboBox_well.currentText()}.xlsx'
                fn = QFileDialog.getSaveFileName(caption="Сохранить расчёты ресурсов в таблицу",
                                                 directory=file_name,
                                                 filter="Excel Files (*.xlsx)")
                resource_table.to_excel(fn[0])
                ui.label_info.setText(f'Таблица сохранена в файл: {fn[0]}')
                ui.label_info.setStyleSheet('color: green')
            except ValueError:
                pass
        mes = ''
        set_info(mes, 'green')
        mes = f'Суммарная мощность - {round(sum(list_h), 2)} м.'
        set_info(mes, 'green')
        mes = f'Суммарные ресурсы:'
        set_info(mes, 'green')
        mes = f'Qhs1 = {round(sum(list_Qhs1), 2)}'
        set_info(mes, 'green')
        mes = f'Qhs2 = {round(sum(list_Qhs2), 2)}'
        set_info(mes, 'green')
        mes = ''
        set_info(mes, 'green')
    except IndexError:
        ui.label_info.setText(f'Внимание! Для данной скважины отсутствуют параметры для расчёта ресурсов.')
        ui.label_info.setStyleSheet('color: red')
    except UnboundLocalError:
        ui.label_info.setText(f'Внимание! Для расчёта ресурсов необходима таблица результатов классификации. Выполните расчёт классификации заново.')
        ui.label_info.setStyleSheet('color: red')


def add_param_resource():
    """ Добавление дополнительного параметра для добавления в таблицу ресурсов """
    table, table_text, widget = check_tabWidjet()
    try:
        param = widget.currentItem().text()
        if ui.listWidget_param_resource_tab.findItems(f'{param} {table_text}', QtCore.Qt.MatchExactly):
            ui.label_info.setText(f'Внимание! Параметр "{param}" уже добавлен.')
            ui.label_info.setStyleSheet('color: red')
        else:
            ui.listWidget_param_resource_tab.addItem(f'{param} {table_text}')
            ui.label_info.setText(f'Параметр {param} добавлен.')
            ui.label_info.setStyleSheet('color: green')
    except AttributeError:
        ui.label_info.setText(f'Внимание! Не выбран параметр.')
        ui.label_info.setStyleSheet('color: red')


def add_all_param_resource():
    """ Добавление всех параметров выбранной таблицы для добавления в таблицу ресурсов """
    table, table_text, widget = check_tabWidjet()
    no_add = ''
    for i in range(widget.count()):
        param = widget.item(i).text()
        if ui.listWidget_param_resource_tab.findItems(f'{param} {table_text}', QtCore.Qt.MatchExactly):
            no_add += f'{param}, '
            ui.label_info.setText(f'Внимание! Параметры {no_add} уже добавлены.')
            ui.label_info.setStyleSheet('color: red')
        else:
            ui.listWidget_param_resource_tab.addItem(f'{param} {table_text}')


def clear_param_resource():
    """ Очистка списка выбранных параметров """
    ui.listWidget_param_resource_tab.clear()


def del_param_resource():
    """ Удалить выбранный параметр """
    ui.listWidget_param_resource_tab.takeItem(ui.listWidget_param_resource_tab.currentRow())


def add_constr():
    """ добавить классификацию в конструктор """
    classification = ui.comboBox_class_lim.currentText()
    c_id = int(classification.split('. ')[0])
    c_title = classification.split('. ')[1]
    category = session.query(ClassByLimits.category_names).filter(ClassByLimits.id == c_id).first()[0].split(';')
    ui.gridLayout_c = QtWidgets.QGridLayout()
    list_label = []
    for i in ui.widget_constr.findChildren(QtWidgets.QLabel):
        list_label.append(i.text())
    if classification in list_label:
        ui.label_info.setText(f'Внимание! Классификация "{c_title}" уже добавлена.')
        ui.label_info.setStyleSheet('color: red')
    else:
        ui.label_c = QtWidgets.QLabel()
        ui.label_c.setText(classification)
        ui.gridLayout_c.addWidget(ui.label_c)
        for n, i in enumerate(category):
            ui.checkBox_c = QtWidgets.QCheckBox()
            ui.checkBox_c.setText(i)
            ui.checkBox_c.setStyleSheet(f'background-color:{color_list[n]}')
            ui.gridLayout_c.addWidget(ui.checkBox_c)
        ui.widget_c = QtWidgets.QWidget()
        ui.gridLayout_constr.addWidget(ui.widget_c)
        ui.widget_c.setLayout(ui.gridLayout_c)
        ui.label_info.setText(f'Внимание! Классификация "{c_title}" добавлена в конструктор.')
        ui.label_info.setStyleSheet('color: green')


def calc_constr():
    w_id = get_well_id()  # id скважины
    start, stop = check_start_stop()  # интервал исследований
    int_to_calc = np.arange(start, stop, 0.1)
    for i in ui.widget_constr.findChildren(QtWidgets.QWidget):
        l = i.findChild(QtWidgets.QLabel)
        if l:
            c_id = int(l.text().split('.')[0])  # id классификации по пределам
            ui.label_info.setText(f'Выполняется расчёт классификации "{l.text().split(".")[1]}".')
            ui.label_info.setStyleSheet('color: blue')
            class_params = session.query(ClassByLimitsParam).filter(
                ClassByLimitsParam.class_id == c_id).all()  # все параметры выбранной классификации
            list_name_cat = session.query(ClassByLimits.category_names).filter(
                ClassByLimits.id == c_id).first()[0].split(';')  # список названий категорий
            list_tab = []  # список названий таблиц параметров
            list_param = []  # список названий параметров
            list_limits = []  # список интервалов для каждого параметра
            for c in class_params:
                list_tab.append(c.table)
                list_param.append(c.param)
                list_limits.append([float(j) for j in c.limits.split(';')])  # список списков интервалов для каждого параметра
            list_check = []  # список выбранных категорий
            for j in i.findChildren(QtWidgets.QCheckBox):
                if j.isChecked():
                    list_check.append(j.text())
            if len(list_check) > 0:
                new_int_to_calc = []
                ui.progressBar.setMaximum(len(int_to_calc))
                for n, d in enumerate(int_to_calc):
                    d = round(d, 2)
                    list_class = []  # список результатов классификации для глубины d
                    for i in range(len(list_tab)):  # перебор всех параметров классификации
                        tab = get_table(list_tab[i])
                        val = session.query(literal_column(f'{list_tab[i]}.{list_param[i]}')).filter(
                            tab.well_id == w_id, tab.depth >= d, tab.depth < d + 0.1,
                            literal_column(f'{list_tab[i]}.{list_param[i]}') != None).first()  # значение параметра по глубине d
                        if val:  # если параметр по глубине d существует, определяем его категорию параметра классификации
                            lim = check_value_in_limits(val[0], list_limits[i])
                            list_class.append(lim)
                    if len(list_class) == len(class_params):  # если определены все параметры
                        if list_name_cat[choice_category(list_class, len(list_param))] in list_check:
                            new_int_to_calc.append(d)
                    ui.progressBar.setValue(n + 1)
                int_to_calc = new_int_to_calc
            else:
                data_lim = []  # список списков все результирующие данные по классификации
                d = start
                n = 0
                k = 0
                ui.progressBar.setMaximum(int((stop - start) / 0.1))
                clear_table(ui.tableWidget)
                ui.tableWidget.setColumnCount(len(list_param) + (
                    3 if list_tab[0] != 'data_las' else 2))  # количество колонок сназваниями образцов или без них
                ui.tableWidget.setHorizontalHeaderLabels(
                    (['depth', 'name', 'category'] if list_tab[0] != 'data_las' else
                     ['depth', 'category']) + list_param)  # названия колонок
                ui.label_info.setText(
                    f'Процесс расчёта классификации по пределам. {ui.comboBox_area.currentText()} скв.{ui.comboBox_well.currentText()}')
                ui.label_info.setStyleSheet('color: blue')
                while d <= stop:
                    d = round(d, 2)
                    list_class = [round(d, 1)]  # список результатов классификации для глубины d
                    for i in range(len(list_tab)):  # перебор всех параметров классификации
                        tab = get_table(list_tab[i])
                        val = session.query(literal_column(f'{list_tab[i]}.{list_param[i]}')).filter(
                            tab.well_id == w_id, tab.depth >= d, tab.depth < d + 0.1,
                            literal_column(
                                f'{list_tab[i]}.{list_param[i]}') != None).first()  # значение параметра по глубине d
                        if val:  # если параметр по глубине d существует, определяем его категорию параметра классификации
                            lim = check_value_in_limits(val[0], list_limits[i])
                            list_class.append(lim)
                    if len(list_class) == len(class_params) + 1:  # если определены все параметры
                        ui.tableWidget.insertRow(k)  # создаем новую строку в виджете таблицы
                        if d in int_to_calc:
                            list_class.append(
                                list_name_cat[choice_category(list_class[1:], len(list_param))])  # вычисление результирующей производной
                        else:
                            list_class.append('Не вошёл')
                        if list_tab[0] != 'data_las':  # если первый параметр не LAS получаем номер образца
                            tab = get_table(list_tab[0])
                            name_obr = session.query(tab.name).filter(tab.well_id == w_id, tab.depth >= d,
                                                                      tab.depth < d + 0.1).first()[0]
                            ui.tableWidget.setItem(k, 1, QTableWidgetItem(str(name_obr)))
                            list_class.append(name_obr)
                        data_lim.append(list_class)  # добавляем в список результатов итоговый список категорий
                        ui.tableWidget.setItem(k, 0, QTableWidgetItem(str(list_class[0])))  # добавляем глубину в виджет
                        ui.tableWidget.setItem(k, (2 if list_tab[0] != 'data_las' else 1), QTableWidgetItem(
                            str(list_class[-2 if list_tab[
                                                     0] != 'data_las' else -1])))  # добавляем итоговую категорию в виджет
                        if d in int_to_calc:
                            ui.tableWidget.item(k, (2 if list_tab[0] != 'data_las' else 1)).setBackground(
                            QtGui.QColor(color_list[list_name_cat.index(
                                list_class[-2 if list_tab[0] != 'data_las' else -1])]))  # цвет ячейки по категории
                        list_cat = list_class[1:-2] if list_tab[0] != 'data_las' else list_class[1:-1]  # список резульирующих категорий по параметрам
                        for m, j in enumerate(list_cat):
                            j = round(j, 2) if ui.checkBox_pdf_class.isChecked() else j
                            ui.tableWidget.setItem(k, m + (3 if list_tab[0] != 'data_las' else 2),
                                                   QTableWidgetItem(str(j)))  # категории по каждому параметру в виджет
                            if d in int_to_calc:
                                ui.tableWidget.item(k, m + (3 if list_tab[0] != 'data_las' else 2)).setBackground(
                                    QtGui.QColor(color_list[int(j)]))  # цвет ячейки по категории
                        k += 1
                    d += 0.1
                    n += 1
                    ui.progressBar.setValue(n)
                ui.tableWidget.resizeColumnsToContents()
                ui.label_table_name.setText(
                    f'Класс-ия по пределам скв.{ui.comboBox_well.currentText()}')  # название таблицы
                ui.label_info.setText(
                    f'Готово! Выполнен расчёт классификации по пределам. {ui.comboBox_area.currentText()} скв.{ui.comboBox_well.currentText()}')
                ui.label_info.setStyleSheet('color: green')

                pd_data = pd.DataFrame(data_lim, columns=['depth'] + list_param + ['category'] + (
                    ['name'] if list_tab[0] != 'data_las' else []))
                if list_tab[0] != 'data_las':
                    pd_data = pd_data[['depth', 'name'] + list_param + ['category']]
                ui.graphicsView.clear()
                for n, i in enumerate(list_name_cat):
                    Y = pd_data['depth'].loc[pd_data['category'] == i]
                    if len(Y) > 0:
                        color = color_list[n]
                        curve = pg.BarGraphItem(x0=0, y=Y, height=0.1, width=n + 1, brush=color,
                                                pen=pg.mkPen(color=color))
                        ui.graphicsView.addItem(curve)
                Y = pd_data['depth'].loc[pd_data['category'] == 'Не вошёл']
                if len(Y) > 0:
                    curve = pg.BarGraphItem(x0=0, y=Y, height=0.1, width=0.5, brush='grey',
                                            pen=pg.mkPen(color='grey'))
                    ui.graphicsView.addItem(curve)
                ui.graphicsView.getViewBox().invertY(True)
                category_to_resource(list_name_cat)
                if ui.checkBox_save_class_lim.isChecked():  # сохранение результирующей таблицы в файл XLS
                    try:
                        file_name = f'{ui.comboBox_class_lim.currentText().split(". ")[1]}_{ui.comboBox_area.currentText()}_скв.' \
                                    f'{ui.comboBox_well.currentText()}.xlsx'
                        fn = QFileDialog.getSaveFileName(caption="Сохранить классификацию в таблицу",
                                                         directory=file_name,
                                                         filter="Excel Files (*.xlsx)")
                        pd_data.to_excel(fn[0])
                        ui.label_info.setText(f'Таблица сохранена в файл: {fn[0]}')
                        ui.label_info.setStyleSheet('color: green')
                    except ValueError:
                        pass
                return


def clear_constr():
    """ Очистить конструктор классификаций """
    for i in ui.widget_constr.findChildren(QtWidgets.QWidget):
        i.deleteLater()
    ui.label_info.setText('Внимание! Конструктор очищен.')
    ui.label_info.setStyleSheet('color: green')