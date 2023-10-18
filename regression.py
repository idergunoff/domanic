import datetime

from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import ElasticNet, Lasso, LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor

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


def add_regression_well():
    """ Добавление скважины в регрессионный анализ """
    start, stop = check_start_stop()
    if session.query(RegressionWell).filter_by(analysis_id=get_reg_analysis_id(), well_id=get_well_id()).count() == 0:
        new_reg_well = RegressionWell(analysis_id=get_reg_analysis_id(), well_id=get_well_id(), int_from=start, int_to=stop)
        session.add(new_reg_well)
        set_label_info(f'Скважина "{ui.comboBox_well.currentText()}" ({str(start)}-{str(stop)}) добавлена в регрессионный анализ.', 'green')
    else:
        session.query(RegressionWell).filter_by(analysis_id=get_reg_analysis_id(), well_id=get_well_id()).update(
            {'int_from': start, 'int_to': stop}, synchronize_session="fetch"
        )
        set_label_info(f'Для скважины "{ui.comboBox_well.currentText()}" изменён интервал ({str(start)}-{str(stop)}).', 'green')
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


def update_list_features_regression():
    """ Обновление списка признаков в регрессионном анализе """
    ui.listWidget_reg_param.clear()
    for f in session.query(RegressionFeature).filter_by(analysis_id=get_reg_analysis_id()).all():
        ui.listWidget_reg_param.addItem(f'{f.table_features}.{f.param_features} id{f.id}')


def add_feature_regression():
    """ Добавление признака в регрессионный анализ """
    table, table_text, widget = check_tabWidjet()
    if session.query(RegressionFeature).filter_by(analysis_id=get_reg_analysis_id(),
                                                  table_features=table_text,
                                                  param_features=widget.currentItem().text()).count() == 0:
        new_reg_feature = RegressionFeature(analysis_id=get_reg_analysis_id(),
                                            table_features=table_text,
                                            param_features=widget.currentItem().text())
        session.add(new_reg_feature)
        session.commit()
        set_label_info(f'Признак "{widget.currentItem().text()} ({table_text})" добавлен в регрессионный анализ.', 'green')
    else:
        set_label_info(f'Признак "{widget.currentItem().text()} ({table_text})" уже добавлен в регрессионный анализ.', 'red')
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
        widget.setCurrentItem(widget.item(i))
        add_feature_regression()


def clear_list_features_regression():
    """ Очистка списка признаков в регрессионном анализе """
    session.query(RegressionFeature).filter_by(analysis_id=get_reg_analysis_id()).delete()
    session.commit()
    update_list_features_regression()


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
    print(data_train)
    training_sample = data_train[list_param].values.tolist()
    target = sum(data_train[['target']].values.tolist(), [])

    scaler = StandardScaler()
    training_sample = scaler.fit_transform(training_sample)

    # Сохранить параметры масштабирования
    scaler_params = {
        'mean': scaler.mean_,
        'std': scaler.scale_
    }

    Form_Regmod = QtWidgets.QDialog()
    ui_frm = Ui_Form_regression()
    ui_frm.setupUi(Form_Regmod)
    Form_Regmod.show()
    Form_Regmod.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    def calc_regression_model():
        start_time = datetime.datetime.now()
        model = ui_frm.comboBox_model_ai.currentText()

        x_train, x_test, y_train, y_test = train_test_split(
            training_sample, target, test_size=0.2, random_state=42
        )

        if model == 'LinearRegression':
            model_regression = LinearRegression(fit_intercept=ui_frm.checkBox_fit_intercept.isChecked())
            model_name = 'LR'
            # selector = RFE(model_regression, n_features_to_select=0.5, step=1)
            # selector = selector.fit(x_train, y_train)
            # print(selector.support_)
            # print(len(selector.ranking_))

        if model == 'DecisionTreeRegressor':
            spl = 'random' if ui_frm.checkBox_splitter_rnd.isChecked() else 'best'
            model_regression = DecisionTreeRegressor(splitter=spl)
            model_name = 'DTR'
            # selector = RFE(model_regression, n_features_to_select=0.5, step=1)
            # selector = selector.fit(training_sample, target)
            # print(selector.support_)

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
                validation_fraction=ui_frm.doubleSpinBox_valid_mlp.value()
            )
            model_name = 'MLPR'

        if model == 'GradientBoostingRegressor':
            model_regression = GradientBoostingRegressor(
                n_estimators=ui_frm.spinBox_n_estimators.value(),
                learning_rate=ui_frm.doubleSpinBox_learning_rate.value(),
            )
            # selector = RFE(model_regression, n_features_to_select=0.5, step=1)
            # selector = selector.fit(training_sample, target)
            # print(selector.support_)
            model_name = 'GBR'

        if model == 'ElasticNet':
            model_regression = ElasticNet(
                alpha=ui_frm.doubleSpinBox_alpha.value(),
                l1_ratio=ui_frm.doubleSpinBox_l1_ratio.value()
            )
            model_name = 'EN'
            # selector = RFE(model_regression, n_features_to_select=0.5, step=1)
            # selector = selector.fit(training_sample, target)
            # print(selector.support_)

        if model == 'Lasso':
            model_regression = Lasso(alpha=ui_frm.doubleSpinBox_alpha.value())
            model_name = 'Lss'
            # selector = RFE(model_regression, n_features_to_select=0.5, step=1)
            # selector = selector.fit(training_sample, target)
            # print(selector.support_)

        model_regression.fit(x_train, y_train)

        y_pred = model_regression.predict(x_test)

        accuracy = round(model_regression.score(x_test, y_test), 5)
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
                         f' Mean Squared Error:\n {mse}, \n время обучения: {train_time}')
            sns.scatterplot(data=data_graph, x='y_test', y='y_pred', ax=axes[0, 0])
            sns.regplot(data=data_graph, x='y_test', y='y_pred', ax=axes[0, 0])
            sns.scatterplot(data=data_graph, x='y_test', y='y_remain', ax=axes[1, 0])
            sns.regplot(data=data_graph, x='y_test', y='y_remain', ax=axes[1, 0])
            axes[0, 1].bar(ipm_name_params, imp_params)
            axes[0, 1].set_xticklabels(ipm_name_params, rotation=90)
            sns.histplot(data=data_graph, x='y_remain', kde=True, ax=axes[1, 1])
            fig.tight_layout()
            fig.show()
        except AttributeError:
            fig, axes = plt.subplots(nrows=2, ncols=2)
            fig.set_size_inches(15, 10)
            fig.suptitle(f'Модель {model}:\n точность: {accuracy} '
                         f' Mean Squared Error:\n {mse}, \n время обучения: {train_time}')
            sns.scatterplot(data=data_graph, x='y_test', y='y_pred', ax=axes[0, 0])
            sns.regplot(data=data_graph, x='y_test', y='y_pred', ax=axes[0, 0])
            sns.scatterplot(data=data_graph, x='y_test', y='y_remain', ax=axes[1, 0])
            sns.regplot(data=data_graph, x='y_test', y='y_remain', ax=axes[1, 0])
            sns.histplot(data=data_graph, x='y_remain', kde=True, ax=axes[1, 1])
            fig.tight_layout()
            fig.show()
        # result = QtWidgets.QMessageBox.question(
        #     MainWindow,
        #     'Сохранение модели',
        #     f'Сохранить модель {model}?',
        #     QtWidgets.QMessageBox.Yes,
        #     QtWidgets.QMessageBox.No)
        # if result == QtWidgets.QMessageBox.Yes:
        #     # Сохранение модели в файл с помощью pickle
        #     path_model = f'models/regression/{model_name}_{round(accuracy, 3)}_{datetime.datetime.now().strftime("%d%m%y")}.pkl'
        #     path_scaler = f'models/regression/{model_name}_{round(accuracy, 3)}_{datetime.datetime.now().strftime("%d%m%y")}_scaler.pkl'
        #     with open(path_model, 'wb') as f:
        #         pickle.dump(model_regression, f)
        #     with open(path_scaler, 'wb') as f:
        #         pickle.dump(scaler_params, f)
        #
        #     new_trained_model = TrainedModelReg(
        #         analysis_id=get_regmod_id(),
        #         title=f'{model_name}_{round(accuracy, 3)}_{datetime.datetime.now().strftime("%d%m%y")}',
        #         path_model=path_model,
        #         path_scaler=path_scaler,
        #         list_params=json.dumps(list_param),
        #     )
        #     session.add(new_trained_model)
        #     session.commit()
        #     update_list_trained_models_regmod()
        # else:
        #     pass

    ui_frm.pushButton_calc_model.clicked.connect(calc_regression_model)
    Form_Regmod.exec_()


def remove_trained_regression_model():
    """ Удаление обученной модели регрессионного анализа """
    pass


def calc_regression_model():
    """ Расчёт модели регрессионного анализа """
    pass