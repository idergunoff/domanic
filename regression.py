from functions import *


def get_reg_analysis_id():
    """ Возвращает id регрессионного анализа """
    return ui.comboBox_reg_analysis.currentText().split(' id')[-1]


def add_regression_analysis():
    """ Добавление регрессионного анализа """
    title_text = ui.lineEdit_string.text()
    if title_text != '':
        new_reg_analysis = RegressionAnalysis(title=title_text, target_param='data_piroliz_kern.toc')
        session.add(new_reg_analysis)
        session.commit()
        set_label_info(f'Добавлен новый регрессионный анализ "{title_text}"', 'green')
        update_list_regression_analysis()
    else:
        set_label_info('Введите название модели в текстовое поле в верхней правой части главного окна.', 'red')
        QMessageBox.critical(MainWindow, 'Ошибка!', 'Введите название модели в текстовое поле в верхней правой части главного окна.')



def remove_regression_analysis():
    """ Удаление регрессионного анализа """
    an = session.query(RegressionAnalysis).filter_by(id=get_reg_analysis_id()).first()
    an_title = an.title
    session.delete(an)
    session.commit()
    update_list_regression_analysis()
    set_label_info(f'Регрессионный анализ "{an_title}" удалён.', 'green')


def update_list_regression_analysis():
    """ Обновление списка регрессионного анализа """
    ui.comboBox_reg_analysis.clear()
    for an in session.query(RegressionAnalysis).all():
        ui.comboBox_reg_analysis.addItem(f'{an.title} id{an.id}')
    set_target_param()
    update_list_regression_well()
    update_list_features_regression()


def set_target_param():
    """ Установка параметра целевой переменной """
    if ui.comboBox_reg_analysis.currentText():
        an = session.query(RegressionAnalysis).filter_by(id=get_reg_analysis_id()).first()
        ui.label_target_table.setText(an.target_param.split('.')[0])
        ui.label_target_param.setText(an.target_param.split('.')[1])


def update_new_target_param():
    """ Обновление параметра целевой переменной """
    table, table_text, widget = check_tabWidjet()
    session.query(RegressionAnalysis).filter_by(id=get_reg_analysis_id()).update(
        {'target_param': f'{table_text}.{widget.currentItem().text()}'},
        synchronize_session='fetch'
    )
    session.commit()
    set_label_info('Параметр целевой переменной обновлен.', 'green')
    set_target_param()
    ui.label_reg_n_target.setText(str(check_regression_count_target()))


def add_regression_well():
    """ Добавление скважины в регрессионный анализ """
    start, stop = check_start_stop()

    ### вариант с возможностью добавления только одного интервала для скважины. не подходит если использовать пользовательские интервалы
    # if session.query(RegressionWell).filter_by(analysis_id=get_reg_analysis_id(), well_id=get_well_id()).count() == 0:
    #     new_reg_well = RegressionWell(analysis_id=get_reg_analysis_id(), well_id=get_well_id(), int_from=start, int_to=stop)
    #     session.add(new_reg_well)
    #     set_label_info(f'Скважина "{ui.comboBox_well.currentText()}" ({str(start)}-{str(stop)}) добавлена в регрессионный анализ.', 'green')
    # else:
    #     session.query(RegressionWell).filter_by(analysis_id=get_reg_analysis_id(), well_id=get_well_id()).update(
    #         {'int_from': start, 'int_to': stop}, synchronize_session="fetch"
    #     )
    #     set_label_info(f'Для скважины "{ui.comboBox_well.currentText()}" изменён интервал ({str(start)}-{str(stop)}).', 'green')
    if ui.checkBox_reg_well_user_int.isChecked():
        for i in range(ui.listWidget_user_int.count()):
            item = ui.listWidget_user_int.item(i)
            if isinstance(item, QListWidgetItem):
                checkbox = ui.listWidget_user_int.itemWidget(item)
                if isinstance(checkbox, QCheckBox) and checkbox.isChecked():
                    int = session.query(UserInterval).filter_by(id=checkbox.property('interval_id')).first()
                    new_reg_well = RegressionWell(analysis_id=get_reg_analysis_id(), well_id=int.well_id, int_from=int.int_from, int_to=int.int_to)
                    session.add(new_reg_well)
    else:
        new_reg_well = RegressionWell(analysis_id=get_reg_analysis_id(), well_id=get_well_id(), int_from=start, int_to=stop)
        session.add(new_reg_well)
        set_label_info(f'Скважина "{ui.comboBox_well.currentText()}" ({str(start)}-{str(stop)}) добавлена в регрессионный анализ.', 'green')
    session.commit()
    update_list_regression_well()


def remove_regression_well():
    """ Удаление скважины из регрессионного анализа """
    try:
        text_well = ui.listWidget_reg_well.currentItem().text()
    except AttributeError:
        QMessageBox.critical(MainWindow, 'Ошибка!', 'Не выбрана скважина.')
        set_label_info('Выберите скважину.', 'red')
        return
    session.query(RegressionWell).filter_by(id=ui.listWidget_reg_well.currentItem().text().split(' id')[-1]).delete()
    session.commit()
    update_list_regression_well()
    set_label_info(f'Скважина "{text_well}" удалена.', 'green')


def update_list_regression_well():
    """ Обновление списка скважин в регрессионном анализе """
    ui.listWidget_reg_well.clear()
    for n, well in enumerate(session.query(RegressionWell).filter_by(analysis_id=get_reg_analysis_id())):
        ui.listWidget_reg_well.addItem(f'скв.{well.well.title} ({well.int_from}-{well.int_to}) id{well.id}')
        ui.listWidget_reg_well.item(n).setToolTip(well.well.area.title)
    ui.label_reg_n_target.setText(str(check_regression_count_target()))
    ui.listWidget_reg_well.setCurrentRow(0)


def update_list_features_regression():
    """ Обновление списка признаков в регрессионном анализе """
    ui.listWidget_reg_param.clear()
    for f in session.query(RegressionFeature).filter_by(analysis_id=get_reg_analysis_id()).all():
        ui.listWidget_reg_param.addItem(f'{f.table_features}.{f.param_features} id{f.id}')
    ui.label_reg_n_features.setText(str(ui.listWidget_reg_param.count()))


def check_regression_count_target():
    """ Проверка количества образцов целевой переменной """
    an = session.query(RegressionAnalysis).filter_by(id=get_reg_analysis_id()).first()
    n_target = 0
    for w in session.query(RegressionWell).filter_by(analysis_id=get_reg_analysis_id()).all():
        tab = get_table(an.target_param.split('.')[0])
        n_target += session.query(literal_column(an.target_param)).filter(
            tab.well_id == w.well.id,
            tab.depth >= w.int_from,
            tab.depth <= w.int_to,
            literal_column(an.target_param) != None
        ).count()
    return n_target


def add_features_regression_to_db(table_text, param):
    """ Добавление признаков в регрессионный анализ """
    if session.query(RegressionFeature).filter_by(analysis_id=get_reg_analysis_id(),
                                                  table_features=table_text,
                                                  param_features=param).count() == 0:
        new_reg_feature = RegressionFeature(analysis_id=get_reg_analysis_id(),
                                            table_features=table_text,
                                            param_features=param)
        session.add(new_reg_feature)
        session.commit()
        set_label_info(f'Признак "{param} ({table_text})" добавлен в регрессионный анализ.', 'green')
    else:
        set_label_info(f'Признак "{param} ({table_text})" уже добавлен в регрессионный анализ.', 'red')


def add_feature_regression():
    """ Добавление признака в регрессионный анализ """
    table, table_text, widget = check_tabWidjet()
    add_features_regression_to_db(table_text, widget.currentItem().text())
    update_list_features_regression()


def remove_feature_regression():
    """ Удаление признака из регрессионного анализа """
    try:
        session.query(RegressionFeature).filter_by(id=ui.listWidget_reg_param.currentItem().text().split(' id')[-1]).delete()
        session.commit()
        update_list_features_regression()
    except AttributeError:
        QMessageBox.critical(MainWindow, 'Ошибка!', 'Не выбран признак.')
        set_label_info('Выберите признак.', 'red')
        return


def add_all_table_to_features_regression():
    """ Добавление всей таблицы в признаки регрессионного анализа """
    table, table_text, widget = check_tabWidjet()
    for i in range(widget.count()):
        add_features_regression_to_db(table_text, widget.item(i).text())
    update_list_features_regression()


def clear_list_features_regression():
    """ Очистка списка признаков в регрессионном анализе """
    session.query(RegressionFeature).filter_by(analysis_id=get_reg_analysis_id()).delete()
    session.commit()
    update_list_features_regression()


def show_features_regression():
    """ Отображение признака регрессионного анализа """
    r_well = session.query(RegressionWell).filter_by(id=ui.listWidget_reg_well.currentItem().text().split(' id')[-1]).first()
    ui.comboBox_region.setCurrentText(r_well.well.area.region.title)
    ui.comboBox_area.setCurrentText(r_well.well.area.title)
    ui.comboBox_well.setCurrentText(r_well.well.title)
    param = session.query(RegressionFeature).filter_by(id=ui.listWidget_reg_param.currentItem().text().split(' id')[-1]).first()
    try:
        widget = get_listwidget_by_table(param.table_features)
    except AttributeError:
        return
    try:
        widget.setCurrentItem(widget.findItems(param.param_features, Qt.MatchExactly)[0])
    except IndexError:
        QMessageBox.critical(MainWindow, 'Ошибка!', f'В скважине {r_well.well.title} нет параметра {param.param_features}.')
        set_label_info(f'В скважине {r_well.well.title} нет параметра {param.param_features}.', 'red')



def build_train_table():
    """ Сборка таблицы для обучения модели регрессионного анализа """
    an = session.query(RegressionAnalysis).filter_by(id=get_reg_analysis_id()).first()
    list_column = ['well', 'depth', 'target']
    for i in an.regression_features:
        list_column.append(f'{i.table_features}.{i.param_features}')

    data_train = pd.DataFrame(columns=list_column)
    for well in an.wells:
        ui.progressBar.setMaximum(int((well.int_to - well.int_from) / 0.1))
        depth, k = well.int_from, 0
        while depth < well.int_to:
            depth = round(depth, 2)
            ui.progressBar.setValue(k)
            target_table = get_table(an.target_param.split('.')[0])
            target_value = session.query(literal_column(f'{an.target_param}')).filter(
                target_table.well_id == well.well.id,
                target_table.depth >= depth,
                target_table.depth < depth + 0.1,
                literal_column(f'{an.target_param}') != None
            ).first()
            if not target_value:
                depth += 0.1
                k += 1
                continue
            dict_depth = {'well': well.well.title, 'depth': depth, 'target': target_value}
            for p in an.regression_features:
                table = get_table(p.table_features)
                p_value = session.query(literal_column(f'{p.table_features}.{p.param_features}')).filter(
                    table.well_id == well.well.id,
                    table.depth >= depth,
                    table.depth < depth + 0.1,
                    literal_column(f'{p.table_features}.{p.param_features}') != None
                ).first()
                if p_value:
                    dict_depth[f'{p.table_features}.{p.param_features}'] = p_value
            if len(dict_depth) == len(an.regression_features) + 3:
                data_train = pd.concat([data_train, pd.DataFrame(dict_depth)], ignore_index=True)
            depth += 0.1
            k += 1
    return data_train, list_column[3:]


def train_regression_model():
    """ Обучение модели регрессионного анализа """
    data_train, list_param = build_train_table()

    show_regression_form(data_train, list_param)



def show_regression_form(data_train, list_param):
    training_sample = data_train[list_param].values.tolist()
    target = sum(data_train[['target']].values.tolist(), [])
    training_sample_copy = training_sample.copy()

    Form_Regmod = QtWidgets.QDialog()
    ui_frm = Ui_Form_regression()
    ui_frm.setupUi(Form_Regmod)
    Form_Regmod.show()
    Form_Regmod.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    ui_frm.spinBox_pca.setMaximum(len(list_param))
    ui_frm.spinBox_pca.setValue(len(list_param) // 2)
    ui_frm.label_info.setText(f'Обучение модели на {len(data_train.index)} образцах')


    def calc_knn():
        """ Расчет выбросов методом KNN """
        pass

        # data_knn = data_train.copy()
        # data_knn.drop(['well', 'depth'], axis=1, inplace=True)
        #
        # scaler = StandardScaler()
        # training_sample = scaler.fit_transform(data_knn)
        #
        # # Инициализация KNN модели
        # knn = NearestNeighbors(
        #     n_neighbors=ui_frm.spinBox_lof_neighbor.value())  # n_neighbors=2 потому что первым будет сама точка
        # knn.fit(training_sample)
        #
        # # Расстояния и индексы k-ближайших соседей
        # distances, indices = knn.kneighbors(training_sample)
        #
        # # Расстояния до k-того соседа
        # k_distances = distances[:, -1]
        #
        # # Рассчитайте среднее и стандартное отклонение
        # mean_distance = np.mean(k_distances)
        # std_distance = np.std(k_distances)
        #
        # # Установите порог
        # threshold = mean_distance + 2 * std_distance  # Например, среднее + 2 стандартных отклонения
        #
        # label_knn = [-1 if x > threshold else 1 for x in k_distances]
        #
        # tsne = TSNE(n_components=2, perplexity=30, learning_rate=200, random_state=42)
        # train_tsne = tsne.fit_transform(training_sample)
        # data_tsne = pd.DataFrame(train_tsne)
        # data_tsne['knn'] = label_knn
        # print(data_tsne)
        #
        # pca = PCA(n_components=2)
        # data_pca = pca.fit_transform(training_sample)
        # data_pca = pd.DataFrame(data_pca)
        # data_pca['knn'] = label_knn
        # print(data_pca)
        # colors = ['red' if label == -1 else 'blue' for label in label_knn]
        # # Визуализация
        #
        # fig, ax = plt.subplots(nrows=1, ncols=3)
        # fig.set_size_inches(25, 10)
        # sns.scatterplot(data=data_tsne, x=0, y=1, hue='knn', s=200, palette={-1: 'red', 1: 'blue'}, ax=ax[0])
        # sns.scatterplot(data=data_pca, x=0, y=1, hue='knn', s=200, palette={-1: 'red', 1: 'blue'}, ax=ax[1])
        # ax[2].bar(range(len(label_knn)), k_distances, color=colors)
        # # plt.scatter(data_tsne[0][labels == 1, 0], X[labels == 1, 1], color='blue', label='Normal')
        # # plt.scatter(X[labels == -1, 0], X[labels == -1, 1], color='red', label='Outlier')
        # plt.legend()
        # fig.tight_layout()
        # plt.show()


    def calc_lof():
        """ Расчет выбросов методом LOF """

        data_lof = data_train.copy()
        data_lof.drop(['well', 'depth'], axis=1, inplace=True)

        scaler = StandardScaler()
        training_sample = scaler.fit_transform(data_lof)
        n_LOF = ui_frm.spinBox_lof_neighbor.value()

        tsne = TSNE(n_components=2, perplexity=30, learning_rate=200, random_state=42)
        train_tsne = tsne.fit_transform(training_sample)

        pca = PCA(n_components=2)
        data_pca = pca.fit_transform(training_sample)

        colors, data_pca, data_tsne, factor_lof, label_lof = calc_lof_model(data_pca, n_LOF, train_tsne,
                                                                            training_sample)

        Form_LOF = QtWidgets.QDialog()
        ui_lof = Ui_LOF_form()
        ui_lof.setupUi(Form_LOF)
        Form_LOF.show()
        Form_LOF.setAttribute(QtCore.Qt.WA_DeleteOnClose)


        def set_title_lof_form(label_lof):
            ui_lof.label_title_window.setText('Расчет выбросов. Метод LOF (Locally Outlier Factor)\n'
                                              f'Выбросов: {label_lof.tolist().count(-1)} из {len(label_lof)}')

        set_title_lof_form(label_lof)
        ui_lof.spinBox_lof_n.setValue(n_LOF)

        # Визуализация
        draw_lof_tsne(data_tsne, ui_lof)
        draw_lof_pca(data_pca, ui_lof)
        draw_lof_bar(colors, factor_lof, label_lof, ui_lof)


        def calc_lof_in_window():
            colors, data_pca_pd, data_tsne_pd, factor_lof, label_lof = calc_lof_model(data_pca, ui_lof.spinBox_lof_n.value(), train_tsne,
                                                                                training_sample)
            draw_lof_tsne(data_tsne_pd, ui_lof)
            draw_lof_pca(data_pca_pd, ui_lof)
            draw_lof_bar(colors, factor_lof, label_lof, ui_lof)

            set_title_lof_form(label_lof)

        def calc_clean_regression():
            _, _, _, _, label_lof = calc_lof_model(data_pca, ui_lof.spinBox_lof_n.value(), train_tsne, training_sample)
            data_train_clean = data_train.copy()
            lof_index = [i for i, x in enumerate(label_lof) if x == -1]
            data_train_clean.drop(lof_index, axis=0, inplace=True)
            print(data_train_clean)
            Form_Regmod.close()
            show_regression_form(data_train_clean, list_param)

        ui_lof.spinBox_lof_n.valueChanged.connect(calc_lof_in_window)
        ui_lof.pushButton_clean_lof.clicked.connect(calc_clean_regression)
        # ui_lof.pushButton_lof.clicked.connect(calc_lof_in_window)

        Form_LOF.exec_()



    def draw_lof_bar(colors, factor_lof, label_lof, ui_lof):
        clear_horizontalLayout(ui_lof.horizontalLayout_bar)
        figure_bar = plt.figure()
        canvas_bar = FigureCanvas(figure_bar)
        ui_lof.horizontalLayout_bar.addWidget(canvas_bar)
        plt.bar(range(len(label_lof)), factor_lof, color=colors)
        figure_bar.suptitle(f'коэффициенты LOF')
        figure_bar.tight_layout()
        canvas_bar.show()


    def draw_lof_pca(data_pca, ui_lof):
        clear_horizontalLayout(ui_lof.horizontalLayout_pca)
        figure_pca = plt.figure()
        canvas_pca = FigureCanvas(figure_pca)
        figure_pca.clear()
        ui_lof.horizontalLayout_pca.addWidget(canvas_pca)
        sns.scatterplot(data=data_pca, x=0, y=1, hue='lof', s=100, palette={-1: 'red', 1: 'blue'})
        plt.grid()
        figure_pca.suptitle(f'PCA')
        figure_pca.tight_layout()
        canvas_pca.draw()


    def draw_lof_tsne(data_tsne, ui_lof):
        clear_horizontalLayout(ui_lof.horizontalLayout_tsne)
        figure_tsne = plt.figure()
        canvas_tsne = FigureCanvas(figure_tsne)
        figure_tsne.clear()
        ui_lof.horizontalLayout_tsne.addWidget(canvas_tsne)
        sns.scatterplot(data=data_tsne, x=0, y=1, hue='lof', s=100, palette={-1: 'red', 1: 'blue'})
        plt.grid()
        figure_tsne.suptitle(f't-SNE')
        figure_tsne.tight_layout()
        canvas_tsne.draw()


    def calc_lof_model(data_pca, n_LOF, train_tsne, training_sample):
        lof = LocalOutlierFactor(n_neighbors=n_LOF)
        label_lof = lof.fit_predict(training_sample)
        factor_lof = -lof.negative_outlier_factor_

        data_tsne_pd = pd.DataFrame(train_tsne)
        data_tsne_pd['lof'] = label_lof

        data_pca_pd = pd.DataFrame(data_pca)
        data_pca_pd['lof'] = label_lof

        colors = ['red' if label == -1 else 'blue' for label in label_lof]

        return colors, data_pca_pd, data_tsne_pd, factor_lof, label_lof


    def calc_regression_model():
        start_time = datetime.datetime.now()
        model = ui_frm.comboBox_model_ai.currentText()

        pipe_steps = []

        scaler = StandardScaler()
        training_sample = scaler.fit_transform(training_sample_copy)

        pipe_steps.append(('scaler', scaler))

        # Сохранить параметры масштабирования
        scaler_params = {
            'mean': scaler.mean_,
            'std': scaler.scale_
        }

        x_train, x_test, y_train, y_test = train_test_split(
            training_sample, target, test_size=0.2, random_state=42
        )

        # if ui_frm.checkBox_pca.isChecked():
        #     n_comp = 'mle' if ui_frm.checkBox_pca_mle.isChecked() else ui_frm.spinBox_pca.value()
        #     pca = PCA(n_components=n_comp)
        #     # pca = TSNE(n_components=4)
        #     x_train = pca.fit_transform(x_train)
        #     x_test = pca.transform(x_test)
        #     print('x_train', x_train)
        #     print('x_test', x_test)

        model_name, model_regression = choose_regression_model(model, ui_frm)

        if ui_frm.checkBox_pca.isChecked():
            n_comp = 'mle' if ui_frm.checkBox_pca_mle.isChecked() else ui_frm.spinBox_pca.value()
            pca = PCA(n_components=n_comp)
            training_sample = pca.fit_transform(training_sample)

            ## Save PCA
            if n_comp == 'mle':
                training_sample_pca = pd.DataFrame(training_sample)
            else:
                training_sample_pca = pd.DataFrame(training_sample, columns=[f'pca_{i}' for i in range(n_comp)])
            data_pca = data_train.copy()
            data_pca = pd.concat([data_pca, training_sample_pca], axis=1)
            print(data_pca)
            data_pca.to_excel('table_pca.xlsx')

            pipe_steps.append(('pca', pca))

        pipe_steps.append(('model', model_regression))

        pipe = Pipeline(pipe_steps)

        if ui_frm.checkBox_cross_val.isChecked():
            data_train_cross = data_train.copy()
            kf = KFold(n_splits=ui_frm.spinBox_n_cross_val.value(), shuffle=True, random_state=0)
            list_train, list_test, n_cross = [], [], 1
            for train_index, test_index in kf.split(training_sample):
                list_train.append(train_index.tolist())
                list_test.append(test_index.tolist())
                list_test_to_table = ['x' if i in test_index.tolist() else 'o' for i in range(len(data_train.index))]
                data_train_cross[f'sample {n_cross}'] = list_test_to_table
                n_cross += 1
            scores_cv = cross_val_score(pipe, training_sample, target, cv=kf)
            n_max = np.argmax(scores_cv)
            print(n_max)
            train_index, test_index = list_train[n_max], list_test[n_max]
            x_train, x_test = training_sample[train_index], training_sample[test_index]
            y_train = [target[i] for i in train_index]
            y_test = [target[i] for i in test_index]
            if ui_frm.checkBox_cross_val_save.isChecked():
                fn = QFileDialog.getSaveFileName(caption="Сохранить выборку в таблицу",
                                                 directory='table_cross_val.xlsx',
                                                 filter="Excel Files (*.xlsx)")
                data_train_cross.to_excel(fn[0])

            # print("Оценки на каждом разбиении:", scores_cv)
            # print("Средняя оценка:", scores_cv.mean())
            # print("Стандартное отклонение оценок:", scores_cv.std())

        cv_text = (
            f'\nКРОСС-ВАЛИДАЦИЯ\nОценки на каждом разбиении:\n {" / ".join(str(round(val, 2)) for val in scores_cv)}'
            f'\nСредн.: {round(scores_cv.mean(), 2)} '
            f'Станд. откл.: {round(scores_cv.std(), 2)}') if ui_frm.checkBox_cross_val.isChecked() else ''

        pipe.fit(x_train, y_train)

        y_pred = pipe.predict(x_test)

        accuracy = round(pipe.score(x_test, y_test), 5)
        mse = round(mean_squared_error(y_test, y_pred), 5)

        train_time = datetime.datetime.now() - start_time
        set_info(f'Модель {model}:\n точность: {accuracy} '
                 f' Mean Squared Error:\n {mse}, \n время обучения: {train_time}', 'blue')
        y_remain = [round(y_test[i] - y_pred[i], 5) for i in range(len(y_pred))]

        data_graph = pd.DataFrame({
            'y_test': y_test,
            'y_pred': y_pred,
            'y_remain': y_remain
        })
        try:
            ipm_name_params, imp_params = [], []
            for n, i in enumerate(model_regression.feature_importances_):
                if i >= np.mean(model_regression.feature_importances_):
                    ipm_name_params.append(list_param[n])
                    imp_params.append(i)

            fig, axes = plt.subplots(nrows=2, ncols=2)
            fig.set_size_inches(15, 10)
            fig.suptitle(f'Модель {model}:\n точность: {accuracy} '
                         f' Mean Squared Error:\n {mse}, \n время обучения: {train_time}' + cv_text)
            sns.scatterplot(data=data_graph, x='y_test', y='y_pred', ax=axes[0, 0])
            sns.regplot(data=data_graph, x='y_test', y='y_pred', ax=axes[0, 0])
            sns.scatterplot(data=data_graph, x='y_test', y='y_remain', ax=axes[1, 0])
            sns.regplot(data=data_graph, x='y_test', y='y_remain', ax=axes[1, 0])
            if ui_frm.checkBox_cross_val.isChecked():
                axes[0, 1].bar(range(len(scores_cv)), scores_cv)
                axes[0, 1].set_title('Кросс-валидация')
            else:
                axes[0, 1].bar(ipm_name_params, imp_params)
                axes[0, 1].set_xticklabels(ipm_name_params, rotation=90)
            sns.histplot(data=data_graph, x='y_remain', kde=True, ax=axes[1, 1])
            fig.tight_layout()
            fig.show()
        except AttributeError:
            fig, axes = plt.subplots(nrows=2, ncols=2)
            fig.set_size_inches(15, 10)
            fig.suptitle(f'Модель {model}:\n точность: {accuracy} '
                         f' Mean Squared Error:\n {mse}, \n время обучения: {train_time}' + cv_text)
            sns.scatterplot(data=data_graph, x='y_test', y='y_pred', ax=axes[0, 0])
            sns.regplot(data=data_graph, x='y_test', y='y_pred', ax=axes[0, 0])
            sns.scatterplot(data=data_graph, x='y_test', y='y_remain', ax=axes[1, 0])
            sns.regplot(data=data_graph, x='y_test', y='y_remain', ax=axes[1, 0])
            if ui_frm.checkBox_cross_val.isChecked():
                axes[0, 1].bar(range(len(scores_cv)), scores_cv)
                axes[0, 1].set_title('Кросс-валидация')
            sns.histplot(data=data_graph, x='y_remain', kde=True, ax=axes[1, 1])
            fig.tight_layout()
            fig.show()

        if not ui_frm.checkBox_save.isChecked():
            return
        result = QtWidgets.QMessageBox.question(
            MainWindow,
            'Сохранение модели',
            f'Сохранить модель {model}?',
            QtWidgets.QMessageBox.Yes,
            QtWidgets.QMessageBox.No)
        if result == QtWidgets.QMessageBox.Yes:
            # Сохранение модели в файл с помощью pickle
            path_model = f'models/regression/{model_name}_{round(accuracy, 3)}_{datetime.datetime.now().strftime("%d%m%y")}.pkl'
            path_scaler = f'models/regression/{model_name}_{round(accuracy, 3)}_{datetime.datetime.now().strftime("%d%m%y")}_scaler.pkl'
            with open(path_model, 'wb') as f:
                pickle.dump(pipe, f)
            with open(path_scaler, 'wb') as f:
                pickle.dump(scaler_params, f)

            an = session.query(RegressionAnalysis).filter_by(id=get_reg_analysis_id()).first()
            list_well = [{'id': well.well_id, 'area': well.well.area.title, 'well': well.well.title,
                          'from': well.int_from, 'to': well.int_to} for well in an.wells]

            new_trained_model = TrainedRegModel(
                title=f'{model_name}_{round(accuracy, 3)}_{datetime.datetime.now().strftime("%d%m%y")}',
                path_model=path_model,
                path_scaler=path_scaler,
                target_param=an.target_param,
                list_params=json.dumps(list_param),
                list_wells=json.dumps(list_well)
            )
            session.add(new_trained_model)
            session.commit()
            update_list_trained_regression_models()
        else:
            pass


    ui_frm.pushButton_calc_model.clicked.connect(calc_regression_model)
    ui_frm.pushButton_knn.clicked.connect(calc_knn)
    ui_frm.pushButton_lof.clicked.connect(calc_lof)
    Form_Regmod.exec_()


def choose_regression_model(model, ui_frm):
    if model == 'LinearRegression':
        model_regression = LinearRegression(fit_intercept=ui_frm.checkBox_fit_intercept.isChecked())
        model_name = 'LR'

    if model == 'DecisionTreeRegressor':
        spl = 'random' if ui_frm.checkBox_splitter_rnd.isChecked() else 'best'
        model_regression = DecisionTreeRegressor(splitter=spl, random_state=0)
        model_name = 'DTR'

    if model == 'KNeighborsRegressor':
        model_regression = KNeighborsRegressor(
            n_neighbors=ui_frm.spinBox_neighbors.value(),
            weights='distance' if ui_frm.checkBox_knn_weights.isChecked() else 'uniform',
            algorithm=ui_frm.comboBox_knn_algorithm.currentText()
        )
        model_name = 'KNNR'

    if model == 'SVR':
        model_regression = SVR(kernel=ui_frm.comboBox_svr_kernel.currentText(),
                               C=ui_frm.doubleSpinBox_svr_c.value())
        model_name = 'SVR'

    if model == 'MLPRegressor':
        layers = tuple(map(int, ui_frm.lineEdit_layer_mlp.text().split()))
        model_regression = MLPRegressor(
            hidden_layer_sizes=layers,
            activation=ui_frm.comboBox_activation_mlp.currentText(),
            solver=ui_frm.comboBox_solvar_mlp.currentText(),
            alpha=ui_frm.doubleSpinBox_alpha_mlp.value(),
            max_iter=5000,
            early_stopping=ui_frm.checkBox_e_stop_mlp.isChecked(),
            validation_fraction=ui_frm.doubleSpinBox_valid_mlp.value(),
            random_state=0
        )
        model_name = 'MLPR'

    if model == 'GradientBoostingRegressor':
        model_regression = GradientBoostingRegressor(
            n_estimators=ui_frm.spinBox_n_estimators.value(),
            learning_rate=ui_frm.doubleSpinBox_learning_rate.value(),
            random_state=0
        )
        model_name = 'GBR'

    if model == 'ElasticNet':
        model_regression = ElasticNet(
            alpha=ui_frm.doubleSpinBox_alpha.value(),
            l1_ratio=ui_frm.doubleSpinBox_l1_ratio.value(),
            random_state=0
        )
        model_name = 'EN'

    if model == 'Lasso':
        model_regression = Lasso(alpha=ui_frm.doubleSpinBox_alpha.value())
        model_name = 'Lss'

    return model_name, model_regression

def update_list_trained_regression_models():
    ui.listWidget_trained_reg_model.clear()
    for reg_model in session.query(TrainedRegModel).all():
        ui.listWidget_trained_reg_model.addItem(f'{reg_model.target_param.split(".")[-1]} - {reg_model.title} id{reg_model.id}')
        ui.listWidget_trained_reg_model.item(ui.listWidget_trained_reg_model.count() - 1).setToolTip(
            f'Target param: {reg_model.target_param}\n '
            f'Params: {", ".join([i.split(".")[-1] for i in json.loads(reg_model.list_params)])}\n '
            f'Wells: {", ".join([i["well"] for i in json.loads(reg_model.list_wells)])}'
        )


def remove_trained_regression_model():
    """ Удаление обученной модели регрессионного анализа """
    model = session.query(TrainedRegModel).filter_by(id=ui.listWidget_trained_reg_model.currentItem().text().split(' id')[-1]).first()
    os.remove(model.path_model)
    os.remove(model.path_scaler)
    session.delete(model)
    session.commit()
    update_list_trained_regression_models()
    set_label_info(f'Модель {model.title} удалена', 'blue')


def calc_regression_model():
    """ Расчёт модели регрессионного анализа """
    pass